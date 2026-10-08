"""Capture actual Ascend tool/environment probes on WSL; never treats failure as pass."""
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/mlir"
BIN = Path.home() / ".cache/compiler-coursework/ascendnpu-ir-1.1.0/unpacked/ascendnpuir/bin"
def run(name, argv):
    p = subprocess.run(argv, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (ART / f"{name}.stdout.txt").write_text(p.stdout, encoding="utf-8")
    (ART / f"{name}.stderr.txt").write_text(p.stderr, encoding="utf-8")
    item = {"name": name, "command": shlex.join(map(str,argv)), "exit_code": p.returncode}
    print(json.dumps(item), flush=True)
    return item

commands = [
    ("environment", ["bash", "-lc", "uname -a; cat /etc/os-release; python3 --version; free -h; df -h /; for t in bishengir-opt bishengir-compile hivmc npu-smi; do command -v $t || echo $t:NOT_FOUND; done; ls /usr/local/Ascend /dev/davinci* /dev/devmm_svm /dev/hisi_hdc 2>&1; true"]),
    ("bishengir-opt-version", [str(BIN / "bishengir-opt"), "--version"]),
    ("bishengir-compile-version", [str(BIN / "bishengir-compile"), "--version"]),
    ("bishengir-opt-help", [str(BIN / "bishengir-opt"), "--help"]),
    ("bishengir-compile-help", [str(BIN / "bishengir-compile"), "--help"]),
]
results = [run(name, argv) for name, argv in commands]
(ART / "probe-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
