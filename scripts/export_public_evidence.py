"""Export selected, path-normalized evidence without changing original artifacts."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence"
PATTERNS = [
    "artifacts/combined_validation.json", "artifacts/environment/versions.txt",
    "artifacts/toolchain/*.json", "artifacts/toolchain/metrics.csv",
    "artifacts/toolchain/clang_O0/main.ll", "artifacts/toolchain/clang_O0/main.s",
    "artifacts/toolchain/clang_O2/main.ll", "artifacts/toolchain/clang_O2/main.s",
    "artifacts/toolchain/gcc_O2/main.s",
    "artifacts/toolchain/mechanism/*.json",
    "artifacts/toolchain/mechanism/*.ll", "artifacts/toolchain/mechanism/*.yaml",
    "artifacts/toolchain/extended_exploration/summary.json",
    "artifacts/toolchain/extended_exploration/metrics.json",
    "artifacts/toolchain/extended_exploration/metrics.csv",
    "artifacts/toolchain/extended_exploration/tests/*.json",
    "artifacts/toolchain/extended_exploration/configs/*/main.ll",
    "artifacts/toolchain/extended_exploration/configs/*/main.s",
    "artifacts/toolchain/extended_exploration/configs/*/main.gimple",
    "artifacts/toolchain/extended_exploration/configs/*/*.opt.yaml",
    "artifacts/toolchain/extended_exploration/mechanism/*.json",
    "artifacts/toolchain/extended_exploration/mechanism/*.diff",
    "artifacts/toolchain/extended_exploration/MECHANISM_NOTES.md",
    "artifacts/toolchain/extended_exploration/boundary/boundary_results.json",
    "artifacts/toolchain/extended_exploration/boundary/probe_addresses.json",
    "artifacts/toolchain/extended_exploration/boundary/BOUNDARY_ANALYSIS.md",
    "artifacts/toolchain/extended_exploration/boundary/gdb/*.stdout.txt",
    "artifacts/sysy/summary.json", "artifacts/sysy/results.csv",
    "artifacts/sysy/source-sha256.txt", "artifacts/sysy/*.elf.txt",
    "artifacts/sysy/logs/control_matrix.initial_full.*.json",
    "artifacts/sysy/logs/float_stats.fractional.*.json",
    "artifacts/sysy/*.disasm.txt", "artifacts/sysy/mutations/summary.json",
    "artifacts/mlir/*.mlir", "artifacts/mlir/*.diff",
    "artifacts/mlir/ascend-results.json", "artifacts/mlir/reparse-results.json",
    "artifacts/mlir/verification-summary.json", "artifacts/mlir/stage-operation-counts.csv",
    "artifacts/mlir/compiler-snapshot-index.json",
    "artifacts/mlir/compiler-snapshots/*.mlir",
    "artifacts/mlir/06-full-compile.stderr.txt",
    "artifacts/mlir/bishengir-opt-version.stdout.txt",
    "artifacts/mlir/bishengir-compile-version.stdout.txt",
    "artifacts/mlir/sources/source-manifest.json",
    "artifacts/mlir/sources/tool-source-manifest.json",
    "artifacts/mlir/sources/wheel-provenance.json",
    "artifacts/mechanism/sysy-figure-manifest.json",
    "artifacts/mechanism/vecadd-figure-manifest.json",
    "artifacts/mechanism/vecadd-source-manifest.json",
    "artifacts/mechanism/vecadd-sources/*",
    "report/toolchain_notes.md", "report/sysy_notes.md", "report/advanced_notes.md",
]


def normalize(text):
    # JSON-escaped Windows paths must be replaced before ordinary Windows paths.
    windows = str(ROOT)
    text = text.replace(windows.replace("\\", "\\\\"), "<PROJECT>")
    text = text.replace(windows, "<PROJECT>")
    # Record paths from the original Windows/WSL host, independent of clone location.
    text = re.sub(r"/mnt/d/college_study_materials/junior_year_fall/Compiler Principles/上级大作业预习", "<PROJECT>", text)
    text = re.sub(r"D:(?:\\\\|\\)college_study_materials(?:\\\\|\\)junior_year_fall(?:\\\\|\\)Compiler Principles(?:\\\\|\\)上级大作业预习", "<PROJECT>", text)
    text = re.sub(r"C:(?:\\\\|\\)Users(?:\\\\|\\)[^\\\s\"']+", "<USER_HOME>", text)
    text = re.sub(r"/home/[^/\s\"']+", "<USER_HOME>", text)
    text = re.sub(r"(?m)^Linux \S+ ", "Linux <HOST> ", text)
    return text


def normalize_json(value):
    if isinstance(value, str):
        return normalize(value)
    if isinstance(value, list):
        return [normalize_json(item) for item in value]
    if isinstance(value, dict):
        return {normalize(key): normalize_json(item) for key, item in value.items()}
    return value


def main():
    OUT.mkdir(exist_ok=True)
    paths = sorted({p for pattern in PATTERNS for p in ROOT.glob(pattern) if p.is_file()})
    entries = []
    for source in paths:
        relative = source.relative_to(ROOT)
        dest_relative = (Path("report_notes") / source.name if relative.parts[0] == "report"
                         else Path(*relative.parts[1:]))
        original = source.read_bytes()
        text = original.decode("utf-8-sig")
        if relative.as_posix() == "artifacts/environment/versions.txt":
            text = text.split("\nWSL path\n", 1)[0].rstrip() + "\n"
        if source.suffix == ".json":
            published = (json.dumps(normalize_json(json.loads(text)), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        else:
            text = re.sub(r"/mnt/d/college_study_materials/junior_year_fall/Compiler Principles/(?:\\[A-F0-9]{2})+", "<PROJECT>", text)
            published = normalize(text).encode("utf-8")
        dest = OUT / dest_relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(published)
        entries.append({"source": relative.as_posix(), "published": dest.relative_to(ROOT).as_posix(),
                        "source_sha256": hashlib.sha256(original).hexdigest(),
                        "published_sha256": hashlib.sha256(published).hexdigest(),
                        "bytes": len(published), "normalized": original != published})
    for subdir in ["mlir", "mechanism/vecadd-sources"]:
        for name in ["LICENSE", "NOTICE"]:
            source = ROOT / "src/mlir/official-tool-1.1.0" / name
            target = OUT / subdir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
    manifest = {"description": "Selected copies of existing experimental evidence; no experiments run.",
                "normalization": "Local project/home paths and hostname replaced; environment resources omitted. Numeric results unchanged.",
                "files": entries}
    (OUT / "PUBLIC_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(entries), "bytes": sum(e["bytes"] for e in entries)}))


if __name__ == "__main__":
    main()
