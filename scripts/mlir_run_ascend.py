"""Execute official HIVM VecAdd with the verified AscendNPU IR wheel on WSL."""
import difflib
import json
import re
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/mlir"
BIN = Path.home() / ".cache/compiler-coursework/ascendnpu-ir-1.1.0/unpacked/ascendnpuir/bin"
SRC = ROOT / "src/mlir/official-tool-1.1.0/bishengir/test/Integration/HIVM/VecAdd/add.mlir"
results = []
def run(name, tool, args, output=None):
    command = [str(BIN / tool)] + list(map(str,args))
    if output:
        (ART / output).unlink(missing_ok=True)
        command += ["-o", str(ART / output)]
    p = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    (ART / f"{name}.stdout.txt").write_text(p.stdout, encoding="utf-8")
    (ART / f"{name}.stderr.txt").write_text(p.stderr, encoding="utf-8")
    exists = bool(output and (ART / output).exists())
    errors = [line for line in p.stderr.splitlines() if "[ERROR]" in line or "error:" in line]
    complete = p.returncode == 0 and exists and not errors
    status = "HOST_TRANSFORM_PASSED" if complete else "BLOCKED_BACKEND_MISSING" if "Cannot find hivmc" in p.stderr else "FAILED"
    item = {"name": name, "command": shlex.join(command), "exit_code": p.returncode, "output": output if exists else None, "output_exists": exists, "diagnostic_errors": errors, "status": status}
    results.append(item)
    (ART / "ascend-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(item), flush=True)
    if p.returncode:
        print(p.stderr[:3000], flush=True)
    return p.returncode

run("01-parse", "bishengir-opt", [SRC], "01-parsed.mlir")
run("02-core", "bishengir-opt", [SRC, "--hivm-infer-func-core-type"], "02-core.mlir")
run("03-plan-memory", "bishengir-opt", [ART / "02-core.mlir", "--hivm-plan-memory"], "03-memory.mlir")
run("04-sync", "bishengir-opt", [ART / "03-memory.mlir", "--hivm-inject-sync"], "04-sync.mlir")
run("05-to-std", "bishengir-opt", [ART / "04-sync.mlir", "--convert-hivm-to-std"], "05-standard.mlir")
run("06-full-compile", "bishengir-compile", [SRC, "--enable-hivm-compile", "--target=Ascend910B1", "--mlir-disable-threading", "--mlir-print-ir-after-all", "--mlir-print-ir-module-scope"], "06-kernel.o")
run("07-full-host-pipeline", "bishengir-opt", [SRC, "--hacc-append-device-spec=target=Ascend910B1", "--optimize-hivm-pipeline", "--mlir-disable-threading", "--mlir-print-ir-after=hivm-infer-func-core-type,hivm-plan-memory,hivm-inject-sync,hivm-graph-sync-solver,convert-hivm-to-std", "--mlir-print-ir-module-scope"], "07-host-lowered.mlir")
for a,b in [(SRC,ART/"01-parsed.mlir"),(ART/"01-parsed.mlir",ART/"02-core.mlir"),(ART/"02-core.mlir",ART/"03-memory.mlir"),(ART/"03-memory.mlir",ART/"04-sync.mlir"),(ART/"04-sync.mlir",ART/"05-standard.mlir")]:
    if a.exists() and b.exists():
        text = "".join(difflib.unified_diff(a.read_text().splitlines(True), b.read_text().splitlines(True), fromfile=a.name, tofile=b.name))
        (ART / f"{b.stem}.diff").write_text(text, encoding="utf-8")

# These are verbatim IR snapshots extracted from the compiler's actual stderr.
# A full device binary was NOT produced; preserve that separate blocked result.
raw = (ART / "06-full-compile.stderr.txt").read_text()
chunks = re.split(r"(?m)^(// -----// IR Dump After[^\n]+)\n", raw)
snapshots = []
for n in range(1, len(chunks), 2):
    header, body = chunks[n:n+2]
    match = re.search(r"\(([-a-z0-9]+)\)", header)
    pass_name = match.group(1) if match else "unknown"
    if pass_name not in {"hivm-infer-func-core-type", "hivm-plan-memory", "hivm-graph-sync-solver", "convert-hivm-to-std"}:
        continue
    # A final backend diagnostic follows the last whole module dump.
    body = re.split(r"(?m)^\[ERROR\]", body)[0].rstrip() + "\n"
    out = f"compiler-snapshots/{len(snapshots)+1:02d}-{pass_name}.mlir"
    path = ART / out
    path.parent.mkdir(exist_ok=True)
    path.write_text(header + "\n" + body, encoding="utf-8")
    snapshots.append({"pass": pass_name, "path": out, "source_log": "06-full-compile.stderr.txt"})
(ART / "compiler-snapshot-index.json").write_text(json.dumps(snapshots, indent=2), encoding="utf-8")
if any(r["status"] == "FAILED" for r in results):
    raise SystemExit(1)
