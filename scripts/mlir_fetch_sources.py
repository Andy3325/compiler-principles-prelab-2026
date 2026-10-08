"""Fetch a pinned subset of the official repository; do not clone LLVM sources."""
import concurrent.futures
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "37c6ebc33d1789500014e6a7b2b62164b3cb566b"
DEST = ROOT / "src/mlir/official"
ART = ROOT / "artifacts/mlir/sources"
FILES = [
    "LICENSE", "NOTICE", "README.md", ".gitmodules", "CMakeLists.txt",
    "build-tools/build.sh", ".github/workflows/wheel-x86_64.yml",
    "bishengir/python/wheel/pyproject.toml",
    "bishengir/test/Integration/HIVM/VecAdd/add.mlir",
    "bishengir/test/Integration/HIVM/VecAdd/main.cpp",
    "bishengir/test/Integration/HIVM/VecAdd/README.md",
    "bishengir/test/Integration/HIVM/VecAdd/README_zh.md",
    "bishengir/test/Integration/HIVM/VecAdd/CMakeLists.txt",
    "bishengir/lib/Dialect/HIVM/Pipelines/HIVMPipelines.cpp",
    "bishengir/lib/Dialect/HIVM/Pipelines/ConvertToHIVMPipeline.cpp",
    "bishengir/lib/Tools/bishengir-compile/PassPipeline.cpp",
    "bishengir/lib/Tools/hivmc/A3/PassPipelineA3.cpp",
    "bishengir/lib/Conversion/HIVMToStandard/HIVMToStandard.cpp",
    "bishengir/lib/Conversion/HIVMToLLVM/HIVMToLLVM.cpp",
    "bishengir/include/bishengir/Dialect/HIVM/Transforms/Passes.td",
    "bishengir/include/bishengir/Dialect/HIVM/IR/HIVMDMAOps.td",
    "bishengir/include/bishengir/Dialect/HIVM/IR/HIVMVectorOps.td",
    "bishengir/include/bishengir/Dialect/HIVM/IR/HIVMSynchronizationOps.td",
    "bishengir/include/bishengir/Tools/bishengir-compile/Options.td",
    "bishengir/test/Conversion/HIVMToStandard/HIVMToStandard/convert-hivm-to-standard.mlir",
    "bishengir/test/Conversion/HIVMToLLVM/convert-to-llvm.mlir",
    "docs/source/en/introduction/quick_start/version_compatibility.md",
    "docs/source/zh_cn/introduction/quick_start/examples.md",
    "docs/source/zh_cn/introduction/quick_start/installing_guide.md",
    "docs/source/zh_cn/introduction/architecture.md",
    "docs/source/zh_cn/faq/faq.md",
    "docs/source/zh_cn/developer_guide/features/auto_sync.md",
    "docs/source/zh_cn/developer_guide/passes/hivm_passes.md",
    "docs/source/en/developer_guide/conversion/interface_api.md",
]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "compiler-coursework-source-audit"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()

def fetch(path):
    url = f"https://raw.githubusercontent.com/Ascend/AscendNPU-IR/{COMMIT}/{path}"
    data = get(url)
    target = DEST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {"path": path, "url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

def main():
    global COMMIT, DEST, FILES
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-version", action="store_true", help="Fetch exact sources matching the verified binary, not master snapshot")
    args = parser.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    label = "source-manifest"
    if args.tool_version:
        COMMIT = "428ab8fdab46a879c7349caba4cde705bc8c9bb6"
        DEST = ROOT / "src/mlir/official-tool-1.1.0"
        label = "tool-source-manifest"
        tree_data = get(f"https://api.github.com/repos/Ascend/AscendNPU-IR/git/trees/{COMMIT}?recursive=1")
        (ART / "tool-commit-tree.json").write_bytes(tree_data)
        paths = {x["path"] for x in json.loads(tree_data)["tree"] if x["type"] == "blob"}
        FILES = [p for p in FILES if p in paths]
        FILES += sorted(p for p in paths if p.startswith("bishengir/lib/Tools/bishengir-compile/") and p.endswith(".cpp") and p not in FILES)
        FILES += sorted(p for p in paths if p.startswith("bishengir/test/bishengir-compile/hivm/") and p.endswith(".mlir"))
        FILES += [p for p in ["docs/source/zh_cn/developer_guide/features/AutoSync/AutoSync.md"] if p in paths]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(fetch, FILES))
    (ART / f"{label}.json").write_text(json.dumps({"commit": COMMIT, "files": manifest}, indent=2), encoding="utf-8")
    if args.tool_version:
        print(f"Saved {len(manifest)} tool-matching official files, commit {COMMIT}")
        return
    for label, url in {
        "pypi-1.1.0": "https://pypi.org/pypi/ascendnpu-ir/1.1.0/json",
        "github-commit": f"https://api.github.com/repos/Ascend/AscendNPU-IR/commits/{COMMIT}",
        "github-releases": "https://api.github.com/repos/Ascend/AscendNPU-IR/releases",
        "github-tags": "https://api.github.com/repos/Ascend/AscendNPU-IR/tags",
    }.items():
        (ART / f"{label}.json").write_bytes(get(url))
    website_sources = []
    for label, url in {
        "quick-start": "https://ascendnpu-ir.gitcode.com/zh_cn/sources/introduction/quick_start/examples_zh.html",
        "faq": "https://ascendnpu-ir.gitcode.com/en/faq/faq.html",
        "installation": "https://ascendnpu-ir.gitcode.com/zh_cn/sources/introduction/quick_start/installing_guide_zh.html",
        "architecture": "https://ascendnpu-ir.gitcode.com/zh_cn/sources/introduction/architecture_zh.html",
        "cann-entry": "https://www.hiascend.com/cann/bisheng",
    }.items():
        data = get(url)
        (ART / f"web-{label}.html").write_bytes(data)
        website_sources.append({"path": f"web-{label}.html", "url": url, "sha256": hashlib.sha256(data).hexdigest()})
    (ART / "website-manifest.json").write_text(json.dumps(website_sources, indent=2), encoding="utf-8")
    print(f"Saved {len(manifest)} pinned official files, commit {COMMIT}")

if __name__ == "__main__":
    main()
