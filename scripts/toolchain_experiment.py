#!/usr/bin/env python3
"""Run and record the native x86-64 compiler pipeline, without downloading tools."""
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "toolchain"
OUT = ROOT / "artifacts" / "toolchain"
OUT.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, LC_ALL="C", TZ="Asia/Shanghai")
events = []


def stamp():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(command, stem, *, input_text=None, expected_exit=0):
    started = stamp()
    result = subprocess.run(command, cwd=ROOT, input=input_text, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=ENV, timeout=60)
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".command.txt").write_text(shlex.join(map(str, command)) + "\n", encoding="utf-8")
    stem.with_suffix(".stdout.txt").write_text(result.stdout, encoding="utf-8")
    stem.with_suffix(".stderr.txt").write_text(result.stderr, encoding="utf-8")
    stem.with_suffix(".exit.txt").write_text(str(result.returncode) + "\n", encoding="utf-8")
    if input_text is not None:
        stem.with_suffix(".stdin.txt").write_text(input_text, encoding="utf-8")
    events.append({"started": started, "finished": stamp(), "command": list(map(str, command)),
                   "exit": result.returncode, "log": str(stem.relative_to(ROOT))})
    write_json(OUT / "commands.json", events)
    if result.returncode != expected_exit:
        raise RuntimeError(f"{shlex.join(map(str, command))}: exit {result.returncode}; {result.stderr}")
    return result


def compile_pipeline(compiler, level, debug):
    name = f"{compiler.replace('-14', '')}_{level}" + ("_g" if debug else "")
    folder = OUT / name
    folder.mkdir(exist_ok=True)
    flags = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-march=x86-64", "-mtune=generic",
             "-fno-pie", f"-{level}"] + (["-g"] if debug else [])
    # Driver dry-run reveals distribution defaults; it is labelled and not counted as a build.
    run([compiler, *flags, "-###", "-no-pie", str(SOURCE / "main.c"), str(SOURCE / "bonus.c"),
         "-o", str(folder / "driver_dry_run_only")], folder / "inspect_driver_dry_run")
    run([compiler, *flags, "-dM", "-E", str(SOURCE / "main.c")], folder / "inspect_preprocessor_macros")
    for unit in ("main", "bonus"):
        run([compiler, *flags, "-E", str(SOURCE / f"{unit}.c"), "-o", str(folder / f"{unit}.i")],
            folder / f"01_preprocess_{unit}")
        run([compiler, *flags, "-S", str(folder / f"{unit}.i"), "-o", str(folder / f"{unit}.s")],
            folder / f"02_compile_{unit}")
        run([compiler, "-c", str(folder / f"{unit}.s"), "-o", str(folder / f"{unit}.o")],
            folder / f"03_assemble_{unit}")
    executable = folder / "demo"
    run([compiler, "-no-pie", str(folder / "main.o"), str(folder / "bonus.o"),
         f"-Wl,-Map,{folder / 'link.map'}", "-o", str(executable)], folder / "04_link")
    if name == "clang_O0":
        failed = run([compiler, "-no-pie", str(folder / "main.o"),
                      "-o", str(folder / "missing_bonus_expected_failure")],
                     folder / "negative_control_missing_bonus", expected_exit=1)
        if "undefined reference" not in failed.stderr or "add_bonus" not in failed.stderr:
            raise AssertionError("The negative link control did not fail for the expected missing symbol.")
    if compiler == "clang-14":
        for unit in ("main", "bonus"):
            ir = folder / f"{unit}.ll"
            run([compiler, *flags, "-S", "-emit-llvm", str(SOURCE / f"{unit}.c"), "-o", str(ir)],
                folder / f"05_emit_ir_{unit}")
            run(["llvm-as-14", str(ir), "-o", str(folder / f"{unit}.bc")], folder / f"06_verify_ir_{unit}")
    for label, target in (("main_object", folder / "main.o"), ("bonus_object", folder / "bonus.o"),
                          ("executable", executable)):
        run(["readelf", "-hSWsrd", str(target)], folder / f"inspect_{label}_readelf")
        run(["nm", "-a", str(target)], folder / f"inspect_{label}_nm")
        run(["objdump", "-drwC", "-Mintel", str(target)], folder / f"inspect_{label}_objdump")
    run(["size", "-A", str(executable)], folder / "inspect_size")
    run(["file", str(executable)], folder / "inspect_file")
    run(["ldd", str(executable)], folder / "inspect_ldd")
    return name, folder


def expectation_cases():
    # Independent oracle: adjacent terms cancel to -3; an odd tail contributes 6*k+5.
    cases = []
    for n in (0, 1, 2, 5, 6, 10, 20):
        k, odd = divmod(n, 2)
        total = -3 * k if not odd else 3 * k + 5
        cases.append({"name": f"valid_{n}", "input": f"{n}\n",
                      "stdout": f"n={n} alternating={total} adjusted={total + 11}\n",
                      "stderr": "", "exit": 0})
    for label, value in (("negative", -1), ("too_large", 21)):
        cases.append({"name": label, "input": f"{value}\n", "stdout": "",
                      "stderr": "n must be in [0, 20]\n", "exit": 2})
    cases.append({"name": "not_integer", "input": "abc\n", "stdout": "",
                  "stderr": "expected one integer\n", "exit": 1})
    return cases


def metrics(name, folder):
    assembly = (folder / "main.s").read_text()
    ir_path = folder / "main.ll"
    ir = ir_path.read_text() if ir_path.exists() else None
    sections = (folder / "inspect_size.stdout.txt").read_text().splitlines()
    sizes = {}
    for line in sections:
        pieces = line.split()
        if len(pieces) == 3 and pieces[1].isdigit():
            sizes[pieces[0]] = int(pieces[1])
    # Parse disassembler output, rather than treating assembler directives as instructions.
    disasm = (folder / "inspect_main_object_objdump.stdout.txt").read_text()
    instructions = [line for line in disasm.splitlines()
                    if re.match(r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*[a-z]", line)]
    nm = (folder / "inspect_main_object_nm.stdout.txt").read_text()
    row = {"variant": name, "main_i_bytes": (folder / "main.i").stat().st_size,
           "main_s_bytes": (folder / "main.s").stat().st_size,
           "main_o_bytes": (folder / "main.o").stat().st_size,
           "executable_bytes": (folder / "demo").stat().st_size,
           "text_bytes": sizes.get(".text", 0),
           "debug_section_bytes": sum(size for sec, size in sizes.items() if sec.startswith(".debug")),
           "main_object_instruction_count": len(instructions),
           "main_object_scale_symbol": bool(re.search(r"\b[tT] scale_and_bias$", nm, re.M)),
           "ir_alloca_count": len(re.findall(r"= alloca\b", ir)) if ir else None,
           "ir_phi_count": len(re.findall(r"= phi\b", ir)) if ir else None,
           "ir_scale_definition": bool(re.search(r"^define.*@scale_and_bias\(", ir, re.M)) if ir else None,
           "ir_scale_call_count": len(re.findall(r"\bcall\b[^\n]*@scale_and_bias\(", ir)) if ir else None}
    run(["objcopy", "--dump-section", f".text={folder / 'executable.text.bin'}", str(folder / "demo")],
        folder / "inspect_extract_text")
    row["text_sha256"] = hashlib.sha256((folder / "executable.text.bin").read_bytes()).hexdigest()
    return row


def main():
    cases = expectation_cases()
    write_json(OUT / "expectations.json", {"created_before_compilation": stamp(),
        "derivation": "For n=2k, paired terms give -3k; for n=2k+1, -3k+(6k+5)=3k+5. adjusted=sum+11.",
        "cases": cases})
    env_commands = [("uname", ["uname", "-a"]), ("os_release", ["cat", "/etc/os-release"]),
                    ("gcc", ["gcc", "--version"]), ("clang", ["clang-14", "--version"]),
                    ("llvm_as", ["llvm-as-14", "--version"]), ("ld", ["ld", "--version"]),
                    ("as", ["as", "--version"]), ("python", ["python3", "--version"])]
    for label, command in env_commands:
        run(command, OUT / "environment" / label)
    run(["clang-14", "-std=c11", "-Xclang", "-ast-dump", "-Xclang", "-ast-dump-filter",
         "-Xclang", "alternating_sum", "-fsyntax-only", str(SOURCE / "main.c")],
        OUT / "frontend_ast_alternating_sum")
    results, rows = [], []
    for compiler in ("gcc", "clang-14"):
        for level, debug in (("O0", False), ("O2", False), ("O2", True)):
            name, folder = compile_pipeline(compiler, level, debug)
            for case in cases:
                actual = run([str(folder / "demo")], folder / "tests" / case["name"],
                             input_text=case["input"], expected_exit=case["exit"])
                passed = actual.stdout == case["stdout"] and actual.stderr == case["stderr"]
                results.append({"variant": name, "case": case["name"], "passed": passed,
                                "actual_exit": actual.returncode, "expected_exit": case["exit"],
                                "expected_stdout": case["stdout"], "actual_stdout": actual.stdout,
                                "expected_stderr": case["stderr"], "actual_stderr": actual.stderr})
                if not passed:
                    raise AssertionError(f"{name}/{case['name']}: output mismatch")
            rows.append(metrics(name, folder))
    write_json(OUT / "test_results.json", results)
    write_json(OUT / "metrics.json", rows)
    with (OUT / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(SOURCE.iterdir()) if path.is_file()}
    write_json(OUT / "source_sha256.json", hashes)
    summary = {"completed_at": stamp(), "variants": len(rows), "test_count": len(results),
               "passed": sum(item["passed"] for item in results), "failed": sum(not item["passed"] for item in results),
               "negative_link_control": "PASS: omitting bonus.o fails with undefined reference to add_bonus; excluded from execution-test count",
               "target": "x86_64 Linux, WSL2, dynamically linked non-PIE, generic x86-64 ISA",
               "timing_performance_claim": "No performance benchmark was performed. Sizes and static counts are not speed measurements."}
    write_json(OUT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
