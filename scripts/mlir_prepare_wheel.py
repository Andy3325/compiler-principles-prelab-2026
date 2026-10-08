"""Download and unpack the pinned official Linux wheel without system installation.

Run this script with WSL Python 3.10. The wheel stays in the Linux user cache,
not in the submission directory; its source and digest are recorded here.
"""
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".cache/compiler-coursework/ascendnpu-ir-1.1.0"
NAME = "ascendnpu_ir-1.1.0-cp310-cp310-manylinux_2_28_x86_64.whl"
URL = "https://files.pythonhosted.org/packages/c1/af/9c3c3fb493d11572d64a2a0ca4511a1236da5aecf8ff9b54f4184a58d801/" + NAME
SHA = "0dc9e8436de8373a4bb68a8fcbfd346c8a0d3160cb338047cbdf4ecfdb1776ab"

CACHE.mkdir(parents=True, exist_ok=True)
wheel = CACHE / NAME
if not wheel.exists():
    print("Downloading", URL, flush=True)
    urllib.request.urlretrieve(URL, wheel)
digest = hashlib.file_digest(wheel.open("rb"), "sha256").hexdigest() if hasattr(hashlib, "file_digest") else hashlib.sha256(wheel.read_bytes()).hexdigest()
assert digest == SHA, (digest, SHA)
dest = CACHE / "unpacked"
with zipfile.ZipFile(wheel) as z:
    z.extractall(dest)
    for member in z.infolist():
        mode = member.external_attr >> 16
        if mode:
            os.chmod(dest / member.filename, mode)
record = {"url": URL, "filename": NAME, "sha256": digest, "bytes": wheel.stat().st_size, "unpacked": str(dest), "wheel_version": "1.1.0"}
(ROOT / "artifacts/mlir/sources/wheel-provenance.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps(record, indent=2), flush=True)
for p in dest.rglob("bishengir*"):
    if p.is_file():
        print(p, p.stat().st_size, flush=True)
