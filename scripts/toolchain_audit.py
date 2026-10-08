#!/usr/bin/env python3
"""Check summaries against retained raw evidence, without rebuilding anything."""
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "toolchain"


def read_json(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


results = read_json("test_results.json")
summary = read_json("summary.json")
expectations = read_json("expectations.json")
commands = read_json("commands.json")
require(expectations["created_before_compilation"] <= commands[0]["started"],
        "Expected results must precede the run.")
require(len(results) == 60 == summary["test_count"] == summary["passed"], "Expected 60 passing executions.")
require(summary["failed"] == 0, "Summary reports a failed test.")
cases = {case["name"]: case for case in expectations["cases"]}
for item in results:
    stem = OUT / item["variant"] / "tests" / item["case"]
    case = cases[item["case"]]
    for stream in ("stdout", "stderr"):
        raw = stem.with_suffix(f".{stream}.txt").read_text(encoding="utf-8")
        require(raw == item[f"actual_{stream}"] == item[f"expected_{stream}"] == case[stream],
                f"Raw {stream} mismatch: {stem}")
    require(int(stem.with_suffix(".exit.txt").read_text()) == item["actual_exit"] == case["exit"],
            f"Exit mismatch: {stem}")
    require(stem.with_suffix(".stdin.txt").read_text() == case["input"], f"Input mismatch: {stem}")
    require(item["passed"], f"Result reports failure: {stem}")
metrics = read_json("metrics.json")
for row in metrics:
    folder = OUT / row["variant"]
    for source, column in (("main.i", "main_i_bytes"), ("main.s", "main_s_bytes"),
                           ("main.o", "main_o_bytes"), ("demo", "executable_bytes")):
        require((folder / source).stat().st_size == row[column], f"Size mismatch: {folder / source}")
    code = (folder / "executable.text.bin").read_bytes()
    require(len(code) == row["text_bytes"], f"Code section size mismatch: {folder}")
    require(hashlib.sha256(code).hexdigest() == row["text_sha256"], f"Code hash mismatch: {folder}")
    for unit in ("main", "bonus"):
        for suffix in ("i", "s", "o"):
            require((folder / f"{unit}.{suffix}").is_file(), f"Missing stage: {folder}/{unit}.{suffix}")
    require((folder / "04_link.exit.txt").read_text().strip() == "0", f"Link failed: {folder}")
    if row["variant"].startswith("clang"):
        for unit in ("main", "bonus"):
            require((folder / f"06_verify_ir_{unit}.exit.txt").read_text().strip() == "0",
                    f"IR assembly failed: {folder}/{unit}")
by_name = {row["variant"]: row for row in metrics}
for compiler in ("gcc", "clang"):
    require(by_name[f"{compiler}_O2"]["text_sha256"] == by_name[f"{compiler}_O2_g"]["text_sha256"],
            f"Debug option changed .text in {compiler}; update the report.")
for relative, digest in read_json("source_sha256.json").items():
    require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"Source changed: {relative}")
negative = OUT / "clang_O0" / "negative_control_missing_bonus"
require(negative.with_suffix(".exit.txt").read_text().strip() == "1", "Missing negative link failure.")
require("undefined reference to `add_bonus'" in negative.with_suffix(".stderr.txt").read_text(),
        "Negative link failed for an unexpected reason.")
audit = {"audited_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
         "status": "PASS", "raw_executions_checked": len(results), "build_variants_checked": len(metrics),
         "clang_ir_modules_checked": 6, "negative_link_control_checked": 1,
         "debug_text_hash_pairs_checked": 2, "source_hashes_checked": len(read_json("source_sha256.json"))}
(OUT / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(audit, ensure_ascii=False, indent=2))
