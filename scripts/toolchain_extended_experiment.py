#!/usr/bin/env python3
"""Controlled x86-64 optimization experiments; never overwrite the baseline study.

Run with Python 3 in Ubuntu WSL. All generated outputs are below
artifacts/toolchain/extended_exploration. No timing benchmark is performed.
"""
import csv
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src/toolchain"
OLD = ROOT / "artifacts/toolchain"
OUT = OLD / "extended_exploration"
ENV = dict(os.environ, LC_ALL="C", TZ="Asia/Shanghai")
COMMON = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-march=x86-64", "-mtune=generic", "-fno-pie"]
CONFIGS = [
    ("clang_A_O2", "clang-14", ["-O2"], False),
    ("clang_B_no_vector", "clang-14", ["-O2", "-fno-vectorize", "-fno-slp-vectorize"], False),
    ("clang_C_no_unroll", "clang-14", ["-O2", "-fno-unroll-loops"], False),
    ("clang_D_no_vector_no_unroll", "clang-14", ["-O2", "-fno-vectorize", "-fno-slp-vectorize", "-fno-unroll-loops"], False),
    ("gcc_A_O2", "gcc", ["-O2"], False),
    ("gcc_B_O2_vector", "gcc", ["-O2", "-ftree-loop-vectorize", "-ftree-slp-vectorize"], False),
    ("gcc_C_O3", "gcc", ["-O3"], False),
    ("gcc_D_O3_no_vector", "gcc", ["-O3", "-fno-tree-loop-vectorize", "-fno-tree-slp-vectorize"], False),
    ("clang_noinline_O2", "clang-14", ["-O2"], True),
]
COMMANDS = []


def stamp():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(ROOT))


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args, stem, *, input_text=None, allow_exit=None, cwd=ROOT):
    args = list(map(str, args))
    stem.parent.mkdir(parents=True, exist_ok=True)
    old_exit = Path(str(stem) + ".exit.txt")
    if old_exit.exists() and old_exit.read_text().strip() not in ("0", ""):
        archive = OUT / "attempts" / "unused_include_flag" / stem.name
        archive.mkdir(parents=True, exist_ok=True)
        for previous in stem.parent.glob(stem.name + ".*.txt"):
            shutil.copy2(previous, archive / previous.name)
    started = stamp()
    result = subprocess.run(args, cwd=cwd, env=ENV, input=input_text, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    for suffix, content in (("command", shlex.join(args) + "\n"), ("stdout", result.stdout),
                            ("stderr", result.stderr), ("exit", str(result.returncode) + "\n")):
        Path(str(stem) + "." + suffix + ".txt").write_text(content, encoding="utf-8")
    if input_text is not None:
        Path(str(stem) + ".stdin.txt").write_text(input_text, encoding="utf-8")
    COMMANDS.append({"started": started, "finished": stamp(), "cwd": str(cwd), "command": args,
                     "exit": result.returncode, "log": relative(stem),
                     "environment_overrides": {"LC_ALL": "C", "TZ": "Asia/Shanghai"}})
    save(OUT / "commands.json", COMMANDS)
    if result.returncode and (allow_exit is None or result.returncode not in allow_exit):
        raise RuntimeError(f"{relative(stem)} failed: {result.returncode}; retained stderr")
    return result


def protected_hashes():
    paths = [p for p in OLD.rglob("*") if p.is_file() and OUT not in p.parents]
    paths += [p for p in SRC.iterdir() if p.is_file()]
    paths += [ROOT / "scripts" / f"toolchain_{x}" for x in ("experiment.py", "mechanism.py", "audit.py", "run.sh")]
    return {relative(p): sha(p) for p in sorted(paths) if p.is_file()}


def cases():
    # Independent oracle: one adjacent pair (6k+5)-(6k+8) = -3.
    result = []
    for n in (0, 1, 2, 5, 6, 10, 20):
        k, odd = divmod(n, 2)
        total = 3 * k + 5 if odd else -3 * k
        result.append(dict(name=f"valid_{n}", input=f"{n}\n", stdout=f"n={n} alternating={total} adjusted={total+11}\n", stderr="", exit=0))
    for label, n in (("negative", -1), ("too_large", 21)):
        result.append(dict(name=label, input=f"{n}\n", stdout="", stderr="n must be in [0, 20]\n", exit=2))
    result.append(dict(name="not_integer", input="abc\n", stdout="", stderr="expected one integer\n", exit=1))
    return result


def llvm_functions(text):
    result = {}
    for match in re.finditer(r"^define\b[^\n]*@([^ (]+)\([^\n]*\).*?^}", text, re.M | re.S):
        body = match.group(0)
        labels = re.findall(r"^([A-Za-z0-9_.$-]+):", body, re.M)
        opening_lines = body.split("{", 1)[1].splitlines()
        first = next((line for line in opening_lines if line.strip() and not line.lstrip().startswith(";")), "")
        count = len(labels) + (0 if re.match(r"^[A-Za-z0-9_.$-]+:", first) else 1)
        result[match.group(1)] = {
            "basic_blocks": count, "explicit_labels": labels,
            "conditional_branches": len(re.findall(r"^\s*br i1\b", body, re.M)),
            "all_branches": len(re.findall(r"^\s*br\b", body, re.M)),
            "phi_nodes": len(re.findall(r"= phi\b", body)),
            "has_vector_integer_type": bool(re.search(r"<\d+ x i\d+>", body)),
            "vector_reduce_add_calls": len(re.findall(r"\bcall\b[^\n]*@llvm\.vector\.reduce\.add", body)),
            "scale_calls": len(re.findall(r"\bcall\b[^\n]*@scale_and_bias\(", body)),
        }
        assignments = dict(re.findall(r"^\s*(%[A-Za-z0-9_.$-]+) = (.+)$", body, re.M))
        recurrences = []
        for phi, expression in assignments.items():
            if not expression.startswith("phi i32 "):
                continue
            def add_chain(value, seen):
                if value == phi:
                    return []
                if value in seen:
                    return None
                rhs = assignments.get(value, "")
                if not re.match(r"add(?:\s+(?:nuw|nsw))* i32\b", rhs):
                    return None
                for dependency in re.findall(r"%[A-Za-z0-9_.$-]+", rhs):
                    tail = add_chain(dependency, seen | {value})
                    if tail is not None:
                        return [f"{value} = {rhs}"] + tail
                return None
            for incoming in re.findall(r"\[\s*(%[A-Za-z0-9_.$-]+)\s*,", expression):
                chain = add_chain(incoming, set())
                # Distinguish term accumulation from induction by requiring two
                # SSA-valued operands somewhere in the returning add chain.
                if chain and any(len(re.findall(r"%[A-Za-z0-9_.$-]+", item.split(" = ",1)[1])) >= 2 for item in chain):
                    recurrences.append({"phi": f"{phi} = {expression}", "incoming":incoming, "add_chain":chain})
        result[match.group(1)]["scalar_phi_add_recurrences"] = recurrences
    return result


def remarks(path):
    records = []
    for record in path.read_text().split("--- "):
        if not re.search(r"^Pass:\s+", record, re.M):
            continue
        def field(key):
            m = re.search(r"^" + key + r":\s+(.+)$", record, re.M)
            return m.group(1).strip("'\"") if m else None
        records.append({"kind": record.splitlines()[0], "pass": field("Pass"), "name": field("Name"),
                        "function": field("Function"),
                        "unroll_count": (re.search(r"- UnrollCount:\s+['\"]?(\d+)", record).group(1)
                                         if re.search(r"- UnrollCount:\s+['\"]?(\d+)", record) else None),
                        "vectorization_factor": (re.search(r"- VectorizationFactor:\s+['\"]?(\d+)", record).group(1)
                                                   if re.search(r"- VectorizationFactor:\s+['\"]?(\d+)", record) else None),
                        "interleave_count": (re.search(r"- InterleaveCount:\s+['\"]?(\d+)", record).group(1)
                                              if re.search(r"- InterleaveCount:\s+['\"]?(\d+)", record) else None),
                        "raw": record})
    return records


INSN = re.compile(r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z][a-z0-9]*)\s*(.*)$")


def machine_functions(text):
    functions, name = {}, None
    for line in text.splitlines():
        m = re.match(r"^([0-9a-f]+) <([^>]+)>:", line)
        if m:
            name = m.group(2)
            functions[name] = []
        m = INSN.match(line)
        if m and name:
            functions[name].append((int(m.group(1), 16), m.group(2), m.group(3)))
    result = {}
    for name, insns in functions.items():
        addresses = {a for a, _, _ in insns}
        leaders = {insns[0][0]} if insns else set()
        branches = conditional = calls = 0
        for i, (address, op, args) in enumerate(insns):
            is_branch = op.startswith("j") or op.startswith("loop")
            if is_branch:
                branches += 1
                conditional += op not in ("jmp", "jmpq")
                target = re.match(r"([0-9a-f]+)\s+<", args)
                if target and int(target.group(1), 16) in addresses:
                    leaders.add(int(target.group(1), 16))
            if (is_branch or op.startswith("ret")) and i + 1 < len(insns):
                leaders.add(insns[i+1][0])
            calls += op.startswith("call")
        result[name] = {"instructions": len(insns), "branches": branches,
                        "conditional_branches": conditional, "calls": calls,
                        "machine_basic_blocks_including_padding": len(leaders)}
    return result


def section_text(target, prefix):
    path = Path(str(prefix) + ".text.bin")
    run(["objcopy", "--dump-section", f".text={path}", target, Path(str(prefix) + ".copy.o")],
        Path(str(prefix) + "_extract"))
    return sha(path)


def code_sections(target, prefix):
    """Hash every ELF section with SHF_EXECINSTR, including GCC .text.startup."""
    headers = run(["readelf", "-SW", target], Path(str(prefix) + "_section_headers")).stdout
    found = {}
    for line in headers.splitlines():
        m = re.match(r"\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)\s+\S+\s+(\S+)", line)
        if m and "X" in m.group(3):
            section, size = m.group(1), int(m.group(2), 16)
            path = Path(str(prefix) + section.replace(".", "_") + ".bin")
            run(["objcopy", "--dump-section", f"{section}={path}", target, Path(str(prefix) + section.replace(".", "_") + ".copy.o")],
                Path(str(prefix) + section.replace(".", "_") + "_extract"))
            found[section] = {"size": size, "sha256": sha(path)}
    if not found:
        raise AssertionError(f"No executable sections found in {target}")
    return found


def compile_config(name, compiler, opts, noinline):
    folder = OUT / "configs" / name
    folder.mkdir(parents=True, exist_ok=True)
    source = SRC / "variants/main_noinline.c" if noinline else SRC / "main.c"
    flags = COMMON + opts + (["-I", str(SRC)] if noinline else [])
    preprocessed_flags = COMMON + opts
    sources = {relative(p): sha(p) for p in (source, SRC / "bonus.c", SRC / "demo.h")}
    save(folder / "source_sha256.json", sources)
    run([compiler, *flags, "-###", "-no-pie", source, SRC / "bonus.c", "-o", folder / "dry_run_only"], folder / "driver")
    run([compiler, *flags, "-dM", "-E", source], folder / "macros")
    if compiler == "gcc":
        run([compiler, *flags, "-Q", "--help=optimizers"], folder / "optimizer_options")
    for unit, unit_source in (("main", source), ("bonus", SRC / "bonus.c")):
        run([compiler, *flags, "-E", unit_source, "-o", folder / f"{unit}.i"], folder / f"01_preprocess_{unit}")
        run([compiler, *preprocessed_flags, "-S", folder / f"{unit}.i", "-o", folder / f"{unit}.s"], folder / f"02_compile_{unit}")
        run([compiler, "-c", folder / f"{unit}.s", "-o", folder / f"{unit}.o"], folder / f"03_assemble_{unit}")
    run([compiler, "-no-pie", folder / "main.o", folder / "bonus.o", f"-Wl,-Map,{folder / 'link.map'}", "-o", folder / "demo"], folder / "04_link")
    if compiler == "clang-14":
        remark_flags = ["-Rpass=loop-vectorize|loop-unroll|inline", "-Rpass-missed=loop-vectorize|loop-unroll|inline",
                        "-Rpass-analysis=loop-vectorize|loop-unroll|inline", "-fsave-optimization-record=yaml",
                        "-foptimization-record-passes=loop-vectorize|loop-unroll|inline"]
        for unit, unit_source in (("main", source), ("bonus", SRC / "bonus.c")):
            run([compiler, *flags, "-S", "-emit-llvm", unit_source, "-o", folder / f"{unit}.ll"], folder / f"05_ir_{unit}")
            run(["llvm-as-14", folder / f"{unit}.ll", "-o", folder / f"{unit}.bc"], folder / f"06_verify_ir_{unit}")
        run([compiler, *preprocessed_flags, *remark_flags, f"-foptimization-record-file={folder / 'main.opt.yaml'}",
             "-S", folder / "main.i", "-o", folder / "main.diagnostic.s"], folder / "diagnostic_assembly")
        run([compiler, *flags, *remark_flags, f"-foptimization-record-file={folder / 'ir.opt.yaml'}",
             "-S", "-emit-llvm", source, "-o", folder / "main.diagnostic.ll"], folder / "diagnostic_ir")
        run([compiler, *flags, "-mllvm", "-print-before=loop-vectorize", "-mllvm", "-print-after=loop-vectorize",
             "-S", "-emit-llvm", source, "-o", folder / "main.trace.ll"], folder / "loop_vectorize_trace")
        cfg_dir = folder / "llvm_cfg"
        cfg_dir.mkdir(exist_ok=True)
        run(["opt-14", "-enable-new-pm=0", "-dot-cfg", "-disable-output", folder / "main.ll"], folder / "emit_cfg", cwd=cfg_dir)
        save(folder / "observed_remarks.json", {"ir": remarks(folder / "ir.opt.yaml"), "assembly": remarks(folder / "main.opt.yaml")})
    else:
        run([compiler, *preprocessed_flags, f"-fopt-info-vec-all={folder / 'main.optinfo.txt'}",
             f"-fdump-tree-optimized={folder / 'main.gimple'}", f"-fdump-tree-cfg={folder / 'main.cfg.gimple'}",
             f"-fdump-ipa-inline={folder / 'main.inline.dump'}", "-S", folder / "main.i", "-o", folder / "main.diagnostic.s"], folder / "diagnostic_assembly")
    run([compiler, "-c", folder / "main.diagnostic.s", "-o", folder / "main.diagnostic.o"], folder / "assemble_diagnostic")
    normal_hash = section_text(folder / "main.o", folder / "main_object")
    diag_hash = section_text(folder / "main.diagnostic.o", folder / "diagnostic_object")
    normal_code = code_sections(folder / "main.o", folder / "normal_code")
    diagnostic_code = code_sections(folder / "main.diagnostic.o", folder / "diagnostic_code")
    diag_check = {"main_object_text_sha256": normal_hash, "diagnostic_main_object_text_sha256": diag_hash,
                  "text_field_scope": "Only the section named .text; GCC main resides in .text.startup.",
                  "normal_executable_sections": normal_code, "diagnostic_executable_sections": diagnostic_code,
                  "diagnostics_preserve_main_object_text": normal_hash == diag_hash,
                  "diagnostics_preserve_all_executable_sections": normal_code == diagnostic_code}
    save(folder / "diagnostic_equivalence.json", diag_check)
    if not diag_check["diagnostics_preserve_all_executable_sections"]:
        raise AssertionError(f"{name}: diagnostics changed machine text")
    for label, target in (("main_object", folder / "main.o"), ("bonus_object", folder / "bonus.o"), ("executable", folder / "demo")):
        run(["readelf", "-hSWsrd", target], folder / f"inspect_{label}_readelf")
        run(["nm", "-a", "-S", "--size-sort", target], folder / f"inspect_{label}_nm")
        run(["objdump", "-drwC", "-Mintel", target], folder / f"inspect_{label}_objdump")
    for label, cmd in (("size", ["size", "-A", folder / "demo"]), ("file", ["file", folder / "demo"]), ("ldd", ["ldd", folder / "demo"])):
        run(cmd, folder / f"inspect_{label}")
    metadata = {"configuration": name, "compiler": compiler, "common_flags": COMMON, "optimization_flags": opts,
                "source_compilation_flags": flags, "preprocessed_input_compilation_flags":preprocessed_flags,
                "source": relative(source), "sources": sources,
                "compiler_version": (OUT / "environment" / ("clang.stdout.txt" if compiler == "clang-14" else "gcc.stdout.txt")).read_text(),
                "compiler_version_log":relative(OUT / "environment" / ("clang.stdout.txt" if compiler == "clang-14" else "gcc.stdout.txt")),
                "link_flags": ["-no-pie"], "lto": False, "created": stamp(),
                "diagnostic_equivalence": diag_check,
                "scope": "Sizes and static instruction/branch counts; no execution speed measurements."}
    save(folder / "configuration.json", metadata)
    print(f"BUILT {name}", flush=True)
    return folder


def measure(name, compiler, opts, noinline, folder, tests):
    disasm = (folder / "inspect_main_object_objdump.stdout.txt").read_text()
    # This exact instruction-line predicate matches the original baseline metric.
    instructions = [line for line in disasm.splitlines() if re.match(r"^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*[a-z]", line)]
    funcs = machine_functions(disasm)
    sizes = {}
    for line in (folder / "inspect_size.stdout.txt").read_text().splitlines():
        pieces = line.split()
        if len(pieces) == 3 and pieces[1].isdigit():
            sizes[pieces[0]] = int(pieces[1])
    nm = (folder / "inspect_main_object_nm.stdout.txt").read_text()
    symbol_sizes = {m.group(2): int(m.group(1), 16) for m in re.finditer(r"^[0-9a-f]+\s+([0-9a-f]+)\s+[tT]\s+(\S+)$", nm, re.M)}
    final_ir = llvm_functions((folder / "main.ll").read_text()) if compiler == "clang-14" else None
    if compiler == "gcc":
        gimple = (folder / "main.gimple").read_text()
        gcc_functions = {}
        for block in re.split(r"^;; Function ", gimple, flags=re.M)[1:]:
            fname = block.split(" ", 1)[0]
            gcc_functions[fname] = {"basic_blocks": len(set(re.findall(r"<bb (\d+)>", block))),
                                    "vector_variable_declarations": len(re.findall(r"^\s*vector\(\d+\)", block, re.M)),
                                    "scale_call_count": len(re.findall(r"= scale_and_bias\s*\(", block))}
        final_ir = gcc_functions
    records = remarks(folder / "ir.opt.yaml") if compiler == "clang-14" else []
    vector_remarks = [r for r in records if r["pass"] == "loop-vectorize" and r["name"] == "Vectorized"]
    unroll_remarks = [r for r in records if r["pass"] == "loop-unroll"]
    main_object_text_sha = sha(folder / "main_object.text.bin")
    executable_text_sha = section_text(folder / "demo", folder / "executable")
    row = {"configuration": name, "compiler": compiler, "optimization_flags": " ".join(opts), "noinline_variant": noinline,
           "text_bytes": sizes.get(".text"), "debug_section_bytes": sum(v for k,v in sizes.items() if k.startswith(".debug")),
           "main_object_instruction_count": len(instructions),
           "main_object_branches": sum(f["branches"] for f in funcs.values()),
           "main_object_conditional_branches": sum(f["conditional_branches"] for f in funcs.values()),
           "main_object_machine_basic_blocks_including_padding": sum(f["machine_basic_blocks_including_padding"] for f in funcs.values()),
           "main_object_text_sha256": main_object_text_sha, "executable_text_sha256": executable_text_sha,
           "main_o_bytes": (folder / "main.o").stat().st_size, "executable_bytes": (folder / "demo").stat().st_size,
           "main_object_scale_symbol": "scale_and_bias" in symbol_sizes,
           "symbol_sizes": symbol_sizes, "machine_functions": funcs, "final_ir_functions": final_ir,
           "vectorized_loops": [{k:v for k,v in r.items() if k != "raw"} for r in vector_remarks],
           "unroll_remarks": [{k:v for k,v in r.items() if k != "raw"} for r in unroll_remarks],
           "inline_remarks": [{k:v for k,v in r.items() if k != "raw"} for r in records if r["pass"] == "inline"],
           "test_count": len(tests), "passed": sum(t["passed"] for t in tests), "failed": sum(not t["passed"] for t in tests),
           "diagnostics_preserve_main_object_text": True}
    diagonal = json.loads((folder / "diagnostic_equivalence.json").read_text())
    row["main_object_text_field_scope"] = "Only ELF .text; GCC main is in .text.startup. See all_code_sections for full code."
    row["all_code_sections"] = diagonal["normal_executable_sections"]
    row["diagnostics_preserve_all_executable_sections"] = diagonal["diagnostics_preserve_all_executable_sections"]
    simd_lines = [line.strip() for line in disasm.splitlines() if INSN.match(line) and re.search(r"\b(?:xmm|ymm|zmm)\d+\b", line)]
    row["simd_register_instruction_count"] = len(simd_lines)
    row["simd_register_instruction_lines"] = simd_lines
    if compiler == "gcc":
        optinfo = (folder / "main.optinfo.txt").read_text()
        positive = [line for line in optinfo.splitlines() if re.search(r"optimized: loop vectorized", line)]
        reasons = [line for line in optinfo.splitlines() if "missed:" in line and ("loop" in line or "not vectorized" in line)]
        row["gcc_vectorized_loop_diagnostics"] = positive
        row["gcc_vectorization_missed_reasons"] = reasons
        row["gcc_observed_vectorization"] = bool(positive) or any(f["vector_variable_declarations"] for f in final_ir.values())
    save(folder / "measurements.json", row)
    return row


def additional_mechanism(rows):
    (OUT / "mechanism").mkdir(parents=True, exist_ok=True)
    by_name = {r["configuration"]: r for r in rows}
    evidence = {"gcc": {}, "comparisons": {}}
    llvm_boundaries = {}
    for name, compiler, opts, noinline in CONFIGS:
        folder = OUT / "configs" / name
        if compiler != "gcc":
            trace = (folder / "loop_vectorize_trace.stderr.txt").read_text()
            pieces = re.split(r"^\*\*\* IR Dump (Before|After) LoopVectorizePass on (\S+) \*\*\*\n", trace, flags=re.M)
            snapshots = {}
            for i in range(1, len(pieces), 3):
                when, function, body = pieces[i:i+3]
                snapshots.setdefault(function, {})[when] = body
            llvm_boundaries[name] = {}
            for function, snap in snapshots.items():
                before, after = snap.get("Before", ""), snap.get("After", "")
                llvm_boundaries[name][function] = {
                    "before": llvm_functions(before).get(function), "after":llvm_functions(after).get(function),
                    "printed_function_body_byte_equal": before == after,
                    "trace_log":relative(folder / "loop_vectorize_trace.stderr.txt")}
            continue
        states = {}
        options = (folder / "optimizer_options.stdout.txt").read_text()
        for option in ("-ftree-loop-vectorize", "-ftree-slp-vectorize", "-fvect-cost-model", "-finline-functions", "-finline-small-functions"):
            m = re.search(r"^\s*" + re.escape(option) + r"(?:=\S*)?\s+(.+)$", options, re.M)
            states[option] = m.group(1).strip() if m else "NOT_AVAILABLE"
        evidence["gcc"][name] = {"queried_optimizer_states": states,
                                 "observed_vectorization": by_name[name]["gcc_observed_vectorization"],
                                 "missed_loop_reasons": by_name[name]["gcc_vectorization_missed_reasons"]}
        if name in ("gcc_B_O2_vector", "gcc_C_O3"):
            run([compiler, *COMMON, *opts, f"-fdump-tree-vect-details={folder / 'main.vect-details.gimple'}",
                 "-S", folder / "main.i", "-o", folder / "main.vector_details.s"], folder / "vector_details_dump")
            run([compiler, "-c", folder / "main.vector_details.s", "-o", folder / "main.vector_details.o"], folder / "assemble_vector_details")
            detail_code = code_sections(folder / "main.vector_details.o", folder / "vector_details_code")
            same = detail_code == by_name[name]["all_code_sections"]
            evidence["gcc"][name]["vector_details_preserve_all_executable_sections"] = same
            if not same:
                raise AssertionError(f"{name}: vector-details diagnostics changed executable code")
    for left, right in (("gcc_A_O2", "gcc_B_O2_vector"), ("gcc_B_O2_vector", "gcc_C_O3"), ("gcc_C_O3", "gcc_D_O3_no_vector")):
        a, b = by_name[left], by_name[right]
        fa, fb = OUT / "configs" / left, OUT / "configs" / right
        ta, tb = (fa / "main.gimple").read_text(), (fb / "main.gimple").read_text()
        normalize = lambda t: re.sub(r"\b(?:funcdef_no|decl_uid|cgraph_uid|symbol_order)=\d+", "ID", t)
        diffpath = OUT / "mechanism" / f"{left}_vs_{right}.gimple.diff"
        diffpath.write_text("".join(difflib.unified_diff(normalize(ta).splitlines(True), normalize(tb).splitlines(True),
                                                       fromfile=left, tofile=right)), encoding="utf-8")
        evidence["comparisons"][f"{left}_vs_{right}"] = {
            "all_main_object_code_sections_equal": a["all_code_sections"] == b["all_code_sections"],
            "executable_text_equal": a["executable_text_sha256"] == b["executable_text_sha256"],
            "optimized_gimple_byte_equal": ta == tb,
            "optimized_gimple_equal_ignoring_function_identifier_numbers": normalize(ta) == normalize(tb),
            "normalized_gimple_diff":relative(diffpath),
            "left_optimized_gimple_sha256":sha(fa / "main.gimple"), "right_optimized_gimple_sha256":sha(fb / "main.gimple")}
    save(OUT / "mechanism/additional_evidence.json", evidence)
    save(OUT / "mechanism/llvm_pass_boundary_summary.json", llvm_boundaries)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if "--finalize-only" in sys.argv:
        COMMANDS.extend(json.loads((OUT / "commands.json").read_text()))
        additional_mechanism(json.loads((OUT / "metrics.json").read_text()))
        return
    resume = "--resume" in sys.argv
    if resume and (OUT / "commands.json").exists():
        COMMANDS.extend(json.loads((OUT / "commands.json").read_text()))
    before = json.loads((OUT / "protected_before.json").read_text()) if resume else protected_hashes()
    if not resume:
        save(OUT / "protected_before.json", before)
    original = json.loads((OLD / "summary.json").read_text())
    if original["test_count"] != 60 or original["passed"] != 60:
        raise AssertionError("Original study must retain its independently recorded 60/60 result")
    original_source = (SRC / "main.c").read_text()
    variant_source = (SRC / "variants/main_noinline.c").read_text()
    expected_variant = original_source.replace("static int scale_and_bias(int x)", "static __attribute__((noinline)) int scale_and_bias(int x)")
    if variant_source != expected_variant:
        raise AssertionError("The variant must differ only by the noinline attribute")
    (OUT / "noinline_source.diff").write_text("".join(difflib.unified_diff(original_source.splitlines(True), variant_source.splitlines(True),
                                                   fromfile="src/toolchain/main.c", tofile="src/toolchain/variants/main_noinline.c")), encoding="utf-8")
    expected = cases()
    if not resume:
        save(OUT / "tests/expectations.json", {"created_before_compilation": stamp(), "derivation": "n=2k: -3k; n=2k+1: 3k+5; adjusted=sum+11", "cases": expected})
    for label, command in (("uname", ["uname", "-a"]), ("os_release", ["cat", "/etc/os-release"]),
                           ("clang", ["clang-14", "--version"]), ("gcc", ["gcc", "--version"]),
                           ("llvm_as", ["llvm-as-14", "--version"]), ("opt", ["opt-14", "--version"]),
                           ("ld", ["ld", "--version"]), ("as", ["as", "--version"]), ("objdump", ["objdump", "--version"]),
                           ("python", ["python3", "--version"]), ("clang_help", ["clang-14", "--help"]),
                           ("gcc_help", ["gcc", "--help=optimizers"])):
        if not resume:
            run(command, OUT / "environment" / label)
    all_tests, rows = [], []
    for name, compiler, opts, noinline in CONFIGS:
        folder = OUT / "configs" / name
        if resume and (folder / "tests/results.json").exists():
            results = json.loads((folder / "tests/results.json").read_text())
            all_tests.extend(results)
            metadata = json.loads((folder / "configuration.json").read_text())
            metadata["compiler_version"] = (OUT / "environment" / ("clang.stdout.txt" if compiler == "clang-14" else "gcc.stdout.txt")).read_text()
            metadata["compiler_version_log"] = relative(OUT / "environment" / ("clang.stdout.txt" if compiler == "clang-14" else "gcc.stdout.txt"))
            normal_code = code_sections(folder / "main.o", folder / "normal_code")
            diagnostic_code = code_sections(folder / "main.diagnostic.o", folder / "diagnostic_code")
            diagonal = json.loads((folder / "diagnostic_equivalence.json").read_text())
            diagonal.update(text_field_scope="Only .text; GCC main is in .text.startup.", normal_executable_sections=normal_code,
                            diagnostic_executable_sections=diagnostic_code, diagnostics_preserve_all_executable_sections=normal_code==diagnostic_code)
            if normal_code != diagnostic_code:
                raise AssertionError(f"{name}: executable code sections changed with diagnostics")
            save(folder / "diagnostic_equivalence.json", diagonal)
            metadata["diagnostic_equivalence"] = diagonal
            save(folder / "configuration.json", metadata)
            rows.append(measure(name, compiler, opts, noinline, folder, results))
            print(f"RESUMED {name}: retained {len(results)} previously executed tests", flush=True)
            continue
        folder = compile_config(name, compiler, opts, noinline)
        results = []
        for case in expected:
            result = run([folder / "demo"], folder / "tests" / case["name"], input_text=case["input"], allow_exit=[0, 1, 2])
            passed = (result.stdout == case["stdout"] and result.stderr == case["stderr"] and result.returncode == case["exit"])
            result_row = {"configuration": name, "case": case["name"], "input": case["input"], "passed": passed,
                          "expected_stdout": case["stdout"], "actual_stdout": result.stdout,
                          "expected_stderr": case["stderr"], "actual_stderr": result.stderr,
                          "expected_exit": case["exit"], "actual_exit": result.returncode}
            results.append(result_row)
            all_tests.append(result_row)
            save(OUT / "tests/results.json", all_tests)
        save(folder / "tests/results.json", results)
        rows.append(measure(name, compiler, opts, noinline, folder, results))
        save(OUT / "metrics.json", rows)
        print(f"TESTED {name}: {sum(r['passed'] for r in results)}/{len(results)}", flush=True)
    save(OUT / "tests/results.json", all_tests)
    save(OUT / "metrics.json", rows)
    additional_mechanism(rows)
    simple = [{k:v for k,v in row.items() if not isinstance(v, (dict,list))} for row in rows]
    with (OUT / "metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(dict.fromkeys(k for row in simple for k in row)))
        writer.writeheader()
        writer.writerows(simple)
    by_name = {r["configuration"]:r for r in rows}
    base_metrics = {r["variant"]:r for r in json.loads((OLD / "metrics.json").read_text())}
    baseline_checks = {}
    for new, old in (("clang_A_O2", "clang_O2"), ("gcc_A_O2", "gcc_O2")):
        row, base = by_name[new], base_metrics[old]
        baseline_checks[new] = {"baseline_variant": old, "text_bytes_equal": row["text_bytes"] == base["text_bytes"],
                               "instruction_count_equal": row["main_object_instruction_count"] == base["main_object_instruction_count"],
                               "executable_text_equal": row["executable_text_sha256"] == base["text_sha256"]}
    deltas = {}
    a,b,c,d = [by_name[n] for n in ("clang_A_O2","clang_B_no_vector","clang_C_no_unroll","clang_D_no_vector_no_unroll")]
    for metric in ("text_bytes", "main_object_instruction_count", "main_object_branches", "main_object_machine_basic_blocks_including_padding"):
        deltas[metric] = {"A_minus_B": a[metric]-b[metric], "A_minus_C": a[metric]-c[metric], "A_minus_D": a[metric]-d[metric],
                          "interaction_A_minus_B_minus_C_plus_D": a[metric]-b[metric]-c[metric]+d[metric]}
    save(OUT / "mechanism/comparisons.json", {"baseline_remeasurements": baseline_checks,
                                             "clang_four_configuration_deltas": deltas,
                                             "interaction_interpretation": "Observed configuration interaction, not independent causal pass contributions.",
                                             "measurement_definitions": {"text_bytes":"Executable .text from size -A, includes startup code.",
                                                 "main_object_instruction_count":"All objdump instruction lines in main.o, including alignment NOPs, same regex as baseline.",
                                                 "machine_basic_blocks_including_padding":"Leaders: each disassembled function entry, in-function direct branch targets, instructions after branches/returns; includes alignment padding and is not LLVM/GIMPLE block count.",
                                                 "branches":"j* and loop* instructions in main.o, excluding calls and returns.",
                                                 "final_ir_functions":"LLVM optimized IR counts for Clang; optimized GNU GIMPLE counts for GCC, different representations."}})
    after = protected_hashes()
    save(OUT / "protected_after.json", after)
    if before != after:
        raise AssertionError("Protected baseline files changed")
    summary = {"completed_at":stamp(), "configurations":len(rows), "new_execution_tests":len(all_tests),
               "passed":sum(r["passed"] for r in all_tests), "failed":sum(not r["passed"] for r in all_tests),
               "original_execution_tests":original["test_count"], "original_passed":original["passed"],
               "baseline_unchanged": True, "protected_files":len(before), "baseline_remeasurement_checks":baseline_checks,
               "diagnostic_builds_preserve_code":all(r["diagnostics_preserve_all_executable_sections"] for r in rows),
               "speed_measurement_performed":False}
    save(OUT / "summary.json", summary)
    save(OUT / "artifact_sha256.json", {relative(p):sha(p) for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "artifact_sha256.json"})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["failed"]:
        raise AssertionError("Retained failing tests must be investigated")


if __name__ == "__main__":
    main()
