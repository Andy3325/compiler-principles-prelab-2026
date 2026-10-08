"""Verify saved experimental evidence, including negative device-build evidence."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/mlir"
OPT = Path.home() / ".cache/compiler-coursework/ascendnpu-ir-1.1.0/unpacked/ascendnpuir/bin/bishengir-opt"
checks = []
def check(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})
    if not ok:
        print("FAIL", name, detail)

master = ROOT / "src/mlir/official/bishengir/test/Integration/HIVM/VecAdd/add.mlir"
versioned = ROOT / "src/mlir/official-tool-1.1.0/bishengir/test/Integration/HIVM/VecAdd/add.mlir"
check("VecAdd identical between recorded master and binary source commit", master.read_bytes() == versioned.read_bytes(), hashlib.sha256(versioned.read_bytes()).hexdigest())
results = json.loads((ART / "ascend-results.json").read_text())
host_runs = [r for r in results if r["name"] != "06-full-compile"]
check("six host transformation commands passed", len(host_runs) == 6 and all(r["status"] == "HOST_TRANSFORM_PASSED" for r in host_runs))
device = next(r for r in results if r["name"] == "06-full-compile")
check("device compile accurately marked blocked", device["status"] == "BLOCKED_BACKEND_MISSING" and not (ART / "06-kernel.o").exists())
snapshot_index = json.loads((ART / "compiler-snapshot-index.json").read_text())
files = [ART / r["output"] for r in host_runs] + [ART / s["path"] for s in snapshot_index]
parse_log = []
for path in files:
    p = subprocess.run([str(OPT), str(path), "-o", "/dev/null"], text=True, capture_output=True)
    check(f"IR reparse {path.relative_to(ART)}", p.returncode == 0, p.stderr.strip())
    parse_log.append({"file": str(path.relative_to(ART)), "exit_code": p.returncode, "stderr": p.stderr})
(ART / "reparse-results.json").write_text(json.dumps(parse_log, indent=2), encoding="utf-8")

rows = []
for path in [ART / "01-parsed.mlir", ART / "02-core.mlir", ART / "03-memory.mlir", ART / "04-sync.mlir", ART / "05-standard.mlir", ART / "07-host-lowered.mlir"]:
    s = path.read_text()
    count = lambda op: len(re.findall(r"(?<![\w.])" + re.escape(op) + r"(?![\w.])", s))
    row = {"file":path.name, "alloc":count("memref.alloc"), "load":count("hivm.hir.load"), "vadd":count("hivm.hir.vadd"), "store":count("hivm.hir.store"), "pointer_cast":count("hivm.hir.pointer_cast"), "set_flag":count("hivm.hir.set_flag"), "wait_flag":count("hivm.hir.wait_flag"), "pipe_barrier":count("hivm.hir.pipe_barrier"), "template_calls":len(re.findall(r"\bcall @",s))}
    rows.append(row)
with (ART / "stage-operation-counts.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
memory = (ART / "03-memory.mlir").read_text()
check("UB output aliases first input allocation", len(re.findall(r"pointer_cast\(%c0_i64\)", memory)) == 2 and "pointer_cast(%c32_i64)" in memory)
sync = (ART / "04-sync.mlir").read_text()
check("MTE2 to Vector and Vector to MTE3 event pairs exist", sync.count("[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]") == 2 and sync.count("[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]") == 2)
check("template lowering retains four calls and removes tile load/add/store", rows[4]["template_calls"] == 4 and rows[4]["load"] == rows[4]["vadd"] == rows[4]["store"] == 0)

final_dump = (ART / snapshot_index[-1]["path"]).read_text().split("\n",1)[1].strip()
host_output = (ART / "07-host-lowered.mlir").read_text().strip()
check("standalone full host pipeline equals final compiler dump", final_dump == host_output)
summary = {"host_transform_commands_passed": len(host_runs), "device_binary_generated": False, "device_execution": "NOT_RUN_NO_CANN_OR_DEVICE", "checks_passed": sum(c["passed"] for c in checks), "checks_total": len(checks), "checks": checks}
(ART / "verification-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
if not all(c["passed"] for c in checks):
    raise SystemExit(1)
