"""Summarize distinct functional runs and host compiler checks without conflating them."""
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT/name).read_text(encoding="utf-8"))
t = read("artifacts/toolchain/summary.json")
s = read("artifacts/sysy/summary.json")
m = read("artifacts/mlir/verification-summary.json")
assert t["test_count"] == t["passed"] == 60 and t["failed"] == 0, t
assert s["executions"] == s["passed"] == 480 and s["failed"] == 0, s
assert m["host_transform_commands_passed"] == 6, m
assert m["checks_passed"] == m["checks_total"], m
assert m["device_binary_generated"] is False, m
report = {"completed_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
          "toolchain_functional_runs": {"passed": t["passed"], "total": t["test_count"]},
          "sysy_functional_runs": {"passed": s["passed"], "total": s["executions"], "logical_cases":s["logical_cases"]},
          "ascend_host_commands":m["host_transform_commands_passed"],
          "ascend_evidence_checks":{"passed":m["checks_passed"],"total":m["checks_total"]},
          "ascend_device_binary":False,"ascend_device_execution":m["device_execution"],
          "note":"Structural IR checks are separate from program executions. The expected backend blockage is not a successful device compile."}
(ROOT/"artifacts/combined_validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
