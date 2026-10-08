#!/usr/bin/env python3
"""Collect LLVM 14 optimization diagnostics without rebuilding the original study.

All new outputs are confined to artifacts/toolchain/mechanism. The original
programs, scripts, 60 execution results, and original stage artifacts are hashed
before and after collection. This script does not execute any test program.
"""
import datetime as dt
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "artifacts" / "toolchain"
OUT = OLD / "mechanism"
SOURCE = ROOT / "src" / "toolchain" / "main.c"
ENV = dict(os.environ, LC_ALL="C", TZ="Asia/Shanghai")
FLAGS = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-march=x86-64",
         "-mtune=generic", "-fno-pie", "-O2"]
REMARKS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize",
           "-Rpass-analysis=loop-vectorize"]
commands = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protected_hashes():
    paths = list((ROOT / "src" / "toolchain").glob("*"))
    paths += [ROOT / "scripts" / f"toolchain_{name}" for name in ("run.sh", "experiment.py", "audit.py")]
    paths += [p for p in OLD.rglob("*") if p.is_file() and OUT not in p.parents]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths) if p.is_file()}


def run(label, args):
    command = list(map(str, args))
    started = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
    result = subprocess.run(command, cwd=ROOT, env=ENV, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    for suffix, text in (("command", shlex.join(command) + "\n"), ("stdout", result.stdout),
                         ("stderr", result.stderr), ("exit", str(result.returncode) + "\n")):
        (OUT / f"{label}.{suffix}.txt").write_text(text, encoding="utf-8")
    commands.append({"started": started, "command": command, "exit": result.returncode, "label": label})
    save_json("commands.json", commands)
    if result.returncode:
        raise RuntimeError(f"{label} exited {result.returncode}; see retained stderr")
    return result


def record_flags(filename):
    return ["-fsave-optimization-record=yaml", f"-foptimization-record-file={OUT / filename}",
            "-foptimization-record-passes=loop-vectorize|loop-unroll|inline"]


def function_bodies_without_metadata(path):
    """Compare executable IR bodies only; do not claim all metadata is irrelevant."""
    kept, in_function = [], False
    for line in path.read_text().splitlines():
        if line.startswith("define "):
            in_function = True
        if in_function:
            line = re.sub(r", ![A-Za-z0-9_.]+ ![0-9]+", "", line)
            line = re.sub(r" !dbg ![0-9]+", "", line)
            if line.strip():
                kept.append(line)
        if line == "}":
            in_function = False
    return kept


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = protected_hashes()
    save_json("protected_before.json", before)
    original_summary = json.loads((OLD / "summary.json").read_text())
    if original_summary["test_count"] != 60 or original_summary["passed"] != 60:
        raise AssertionError("Expected the unchanged original 60/60 study")
    run("version", ["clang-14", "--version"])
    run("llvm_version", ["llvm-as-14", "--version"])
    run("system", ["uname", "-a"])
    run("help", ["clang-14", "--help"])
    run("gcc_version", ["gcc", "--version"])
    gcc_options = run("gcc_O2_optimizer_options", ["gcc", *FLAGS, "-Q", "--help=optimizers"])
    gcc_vectorizer_states = {}
    for option in ("-ftree-loop-vectorize", "-ftree-slp-vectorize", "-fvect-cost-model"):
        match = re.search(r"^\s*" + re.escape(option) + r"\S*\s+(.+)$", gcc_options.stdout, re.M)
        gcc_vectorizer_states[option] = match.group(1).strip() if match else "NOT_AVAILABLE"
    # These match the original source-to-IR and preprocessed-source-to-assembly
    # commands; only diagnostic/recording flags and destination paths are new.
    run("emit_ir_remarks", ["clang-14", *FLAGS, *REMARKS, *record_flags("ir.opt.yaml"),
                            "-S", "-emit-llvm", SOURCE, "-o", OUT / "main.remarks.ll"])
    run("emit_asm_remarks", ["clang-14", *FLAGS, *REMARKS, *record_flags("asm.opt.yaml"),
                             "-S", OLD / "clang_O2" / "main.i", "-o", OUT / "main.remarks.s"])
    run("verify_new_ir", ["llvm-as-14", OUT / "main.remarks.ll", "-o", OUT / "main.remarks.bc"])
    # A real pass boundary snapshot connects scalar recurrence to vector PHIs.
    # The dump is diagnostic text on stderr, not a separately executed pipeline.
    run("loop_vectorize_trace", ["clang-14", *FLAGS, *REMARKS,
        "-mllvm", "-print-before=loop-vectorize", "-mllvm", "-print-after=loop-vectorize",
        "-mllvm", "-filter-print-funcs=alternating_sum", "-S", "-emit-llvm", SOURCE,
        "-o", OUT / "main.trace.ll"])
    # Remarks attach locations. Confirm the generated object code separately
    # instead of silently treating differing IR/assembly text as identical.
    run("assemble_new_diagnostic_output", ["clang-14", "-c", OUT / "main.remarks.s", "-o", OUT / "main.remarks.o"])
    run("extract_original_text", ["objcopy", "--dump-section", f".text={OUT / 'original_main.text.bin'}",
                                  OLD / "clang_O2" / "main.o", OUT / "original_main.copy.o"])
    run("extract_new_text", ["objcopy", "--dump-section", f".text={OUT / 'remarks_main.text.bin'}",
                             OUT / "main.remarks.o", OUT / "remarks_main.copy.o"])
    old_body = function_bodies_without_metadata(OLD / "clang_O2" / "main.ll")
    new_body = function_bodies_without_metadata(OUT / "main.remarks.ll")
    (OUT / "function_bodies_ignoring_metadata.diff").write_text("".join(difflib.unified_diff(
        [line + "\n" for line in old_body], [line + "\n" for line in new_body],
        fromfile="original IR function bodies", tofile="diagnostic IR function bodies")), encoding="utf-8")
    checks = {
        "ir_byte_identical_to_original": sha(OUT / "main.remarks.ll") == sha(OLD / "clang_O2" / "main.ll"),
        "assembly_byte_identical_to_original": sha(OUT / "main.remarks.s") == sha(OLD / "clang_O2" / "main.s"),
        "trace_final_ir_byte_identical_to_original": sha(OUT / "main.trace.ll") == sha(OLD / "clang_O2" / "main.ll"),
        "ir_function_bodies_equal_ignoring_metadata": old_body == new_body,
        "main_object_text_byte_identical_to_original": sha(OUT / "original_main.text.bin") == sha(OUT / "remarks_main.text.bin"),
    }
    if not checks["ir_function_bodies_equal_ignoring_metadata"] or not checks["main_object_text_byte_identical_to_original"]:
        raise AssertionError("Diagnostics changed function bodies or object code; investigate before writing conclusions")
    # Keep the complete YAML. Extract only directly observed function/VF/IC facts.
    vectorized = []
    record_text = (OUT / "ir.opt.yaml").read_text()
    for record in record_text.split("--- "):
        if not re.search(r"^Pass:\s+loop-vectorize$", record, re.M) or not re.search(r"^Name:\s+Vectorized$", record, re.M):
            continue
        def field(pattern):
            match = re.search(pattern, record, re.M)
            return match.group(1).strip("'\"") if match else None
        vectorized.append({"function": field(r"^Function:\s+(.+)$"),
                           "vectorization_factor": field(r"- VectorizationFactor:\s+(.+)$"),
                           "interleave_count": field(r"- InterleaveCount:\s+(.+)$")})
    save_json("observed_remarks.json", vectorized)
    after = protected_hashes()
    save_json("protected_after.json", after)
    if before != after:
        raise AssertionError("Protected original study changed during collection")
    save_json("new_artifact_sha256.json", {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUT.iterdir())
              if p.is_file() and p.name not in {"new_artifact_sha256.json", "summary.json"}})
    summary = {"collected_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
               "original_test_count": original_summary["test_count"], "original_passed": original_summary["passed"],
               "new_test_executions": 0, "protected_original_files": len(before), "original_files_unchanged": True,
               "observed_vectorized_loops": vectorized, "diagnostic_artifact_comparisons": checks,
               "gcc_O2_queried_optimizer_options": gcc_vectorizer_states,
               "scope": "Diagnostic recompilations and pass-boundary snapshots only; no speed measurement."}
    save_json("summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
