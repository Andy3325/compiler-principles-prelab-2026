"""Create two source-backed VecAdd mechanism figures; never execute a compiler.

Inputs are the preserved official IR/log and matching-commit source files.
Outputs are confined to report/figures/vecadd-* and artifacts/mechanism/vecadd-*.
Coordinates encode operation order, not time or measured hardware performance.
Figure workflow reference: Kassis et al., Scientific Agent Skills (2026),
https://doi.org/10.48550/arXiv.2609.00065 (visualization procedure only).
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/mechanism"
FIG = ROOT / "report/figures"
COMMIT = "428ab8fdab46a879c7349caba4cde705bc8c9bb6"
UPSTREAM = f"https://raw.githubusercontent.com/Ascend/AscendNPU-IR/{COMMIT}/"
SOURCES = {
    "PlanMemory.cpp": "bishengir/lib/Dialect/HIVM/Transforms/PlanMemory.cpp",
    "PlanMemory.h": "bishengir/include/bishengir/Dialect/HIVM/Transforms/PlanMemory.h",
    "PlanMemory.md": "docs/source/zh_cn/developer_guide/features/PlanMemory/PlanMemory.md",
    "GetPipe.cpp": "bishengir/lib/Dialect/HIVM/IR/OpPipeInterface/GetPipe.cpp",
    "SyncSolverIRTranslator.cpp": "bishengir/lib/Dialect/HIVM/Transforms/GraphSyncSolver/SyncSolverIRTranslator.cpp",
    "InferFuncCoreType.cpp": "bishengir/lib/Dialect/HIVM/Transforms/InferFuncCoreType.cpp",
    "MemoryDependentAnalyzer.cpp": "bishengir/lib/Dialect/HIVM/Transforms/InjectSync/MemoryDependentAnalyzer.cpp",
}
OFFICIAL = ROOT / "src/mlir/official-tool-1.1.0"
OLD = ROOT / "artifacts/mlir"
BLUE, ORANGE, PURPLE, INK = "#0072B2", "#A65B00", "#884F99", "#293542"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
            "bytes": path.stat().st_size}


def dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text(ax, x, y, value, size=9.5, **kwargs):
    options = {"ha":"center", "va":"center", "color":INK}
    options.update(kwargs)
    ax.text(x, y, value, fontsize=size, **options)


def arrow(ax, start, end, color=INK, style="-", width=1.25):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10,
                                linewidth=width, color=color, linestyle=style))


def box(ax, x, y, label, width=15, height=10, color=INK, fill="#F6F8FA", size=9.5):
    ax.add_patch(FancyBboxPatch((x-width/2, y-height/2), width, height,
                               boxstyle="round,pad=0.2,rounding_size=1.2",
                               facecolor=fill, edgecolor=color, linewidth=1.05))
    text(ax, x, y, label, size=size)


def canvas(height):
    fig, ax = plt.subplots(figsize=(7.2, height))
    fig.subplots_adjust(left=.012, right=.988, bottom=.01, top=.99)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def save(fig, stem):
    paths = []
    for ext in ("pdf", "png"):
        path = FIG / f"{stem}.{ext}"
        # Fixed canvas preserves predictable final print dimensions.
        fig.savefig(path, dpi=300, facecolor="white", metadata={"Creator": Path(__file__).name})
        paths.append(path)
    plt.close(fig)
    return paths


def lifetime_figure():
    fig, ax = canvas(3.45)
    text(ax, 1, 97, "(a) 数据流：逻辑值与 UB 区域", size=10, ha="left")
    for x, y, label, color in [(8,84,"A_GM",BLUE), (28,84,"A_UB",BLUE),
                               (8,67,"B_GM",ORANGE), (28,67,"B_UB",ORANGE),
                               (49,75.5,"vadd",INK), (70,75.5,"C_UB",PURPLE),
                               (91,75.5,"C_GM",PURPLE)]:
        box(ax, x, y, label, color=color)
    for y in (84,67):
        arrow(ax, (16,y), (20,y))
        text(ax, 18, y+6, "load", size=8)
    arrow(ax, (36,84), (41,78))
    arrow(ax, (36,67), (41,73))
    arrow(ax, (57,75.5), (62,75.5))
    arrow(ax, (78,75.5), (83,75.5))
    text(ax, 80.5, 82, "store", size=8)
    text(ax, 1, 54, "(b) 内容活跃区间：首次写入 → 最后读取", size=10, ha="left")
    xpos = [38,54,70,89]
    for x, label in zip(xpos, ["load A", "load B", "vadd", "store C"]):
        ax.plot([x,x], [12,45], color="#D7DEE3", linewidth=.75, zorder=0)
        text(ax, x, 47, label, size=8.8)
    ax.add_patch(Rectangle((68,11), 4, 33, facecolor="#F6E8C9", edgecolor="none", zorder=0))
    for y, label, start, end, color, marker in [
        (37, "A_UB  [0,32)",38,70,BLUE,"o"),
        (26, "B_UB  [32,64)",54,70,ORANGE,"s"),
        (15, "C_UB  [0,32)",70,89,PURPLE,"D")]:
        text(ax, 2, y, label, size=9, ha="left")
        ax.plot([start,end],[y,y], color=color, linewidth=3, solid_capstyle="butt")
        ax.plot([start,end],[y,y], linestyle="none", marker=marker, markersize=5,
                markeredgecolor="white", markeredgewidth=.5, color=color)
    text(ax, 50, 4, "A 最后读 / C 首次写位于同一 vadd；复用需该算子的原地执行许可", size=8.8)
    return save(fig, "vecadd-lifetime")


def pipeline_figure():
    fig, ax = canvas(3.35)
    for x, title, color in [(18,"MTE2  ·  GM → UB",BLUE),
                             (50,"V  ·  向量计算",PURPLE),
                             (82,"MTE3  ·  UB → GM",ORANGE)]:
        text(ax, x, 97, title, size=10)
        ax.plot([x,x],[16,90], color=color, alpha=.25, linewidth=1.5, zorder=0)
    box(ax, 18, 84, "load A；load B", width=26, height=10, color=BLUE)
    box(ax, 18, 67, "set_flag · ID0", width=26, height=9, color=BLUE)
    box(ax, 50, 67, "wait_flag · ID0", width=26, height=9, color=PURPLE)
    arrow(ax, (18,79), (18,72))
    arrow(ax, (31.5,67), (36.5,67), color=BLUE, width=1.6)
    text(ax, 50, 78, "MTE2 → V：等待两次输入搬运完成", size=8.5)
    box(ax, 50, 51, "vadd", width=26, height=9, color=PURPLE)
    arrow(ax, (50,62), (50,56))
    box(ax, 50, 35, "set_flag · ID0", width=26, height=9, color=PURPLE)
    box(ax, 82, 35, "wait_flag · ID0", width=26, height=9, color=ORANGE)
    arrow(ax, (50,46), (50,40))
    arrow(ax, (63.5,35), (68.5,35), color=PURPLE, width=1.6)
    text(ax, 81, 46, "V → MTE3：等待加法完成", size=8.5)
    box(ax, 82, 19, "store C", width=26, height=9, color=ORANGE)
    arrow(ax, (82,30), (82,24))
    arrow(ax, (82,14), (82,10.2))
    box(ax, 50, 6, "pipe_barrier[PIPE_ALL]  →  return", width=91, height=8, size=9)
    # No horizontal scale: these are dependency edges, not measured pipe durations.
    text(ax, 18, 42, "纵向：本流水先后\n横向：事件依赖\n非运行时间轴", size=9)
    return save(fig, "vecadd-pipeline")


def main():
    ART.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    input_paths = [OLD / name for name in ("01-parsed.mlir", "03-memory.mlir", "04-sync.mlir",
                                          "06-full-compile.stderr.txt", "07-host-lowered.mlir")]
    input_paths += sorted((OLD / "compiler-snapshots").glob("*.mlir"))
    snapshots_before = {str(p): sha(p) for p in input_paths}
    memory = (OLD / "03-memory.mlir").read_text(encoding="utf-8")
    constants = {k:int(v) for k,v in re.findall(r"(%[\w]+) = arith.constant (\d+) : i64", memory)}
    casts = re.findall(r"(%\w+) = hivm.hir.pointer_cast\((%\w+)\) : memref<16xi16", memory)
    offsets = {k:constants[v] for k,v in casts}
    operations = []
    for n,line in enumerate(memory.splitlines(),1):
        m = re.search(r"hivm.hir.(load|vadd|store) ins\((.*?) : .*? outs\((.*?) :",line)
        if m:
            operations.append({"ordinal":len(operations)+1,"line":n,"operation":m[1],
                               "inputs":m[2].split(", "),"outputs":m[3].split(", ")})
    assert [o["operation"] for o in operations] == ["load", "load", "vadd", "store"]
    a,b,c = operations[0]["outputs"][0],operations[1]["outputs"][0],operations[2]["outputs"][0]
    assert operations[2]["inputs"] == [a,b] and operations[3]["inputs"] == [c]
    assert [offsets[v] for v in (a,b,c)] == [0,32,0]
    sync = (OLD / "04-sync.mlir").read_text(encoding="utf-8")
    assert sync.count("hivm.hir.set_flag") == sync.count("hivm.hir.wait_flag") == 2
    assert sync.count("hivm.hir.pipe_barrier[<PIPE_ALL>]") == 1
    planner = (ART / "vecadd-sources/PlanMemory.cpp").read_text(encoding="utf-8")
    assert "mlir::isa<hivm::VAddOp" in planner and "// above ops can be inplaced in isa" in planner
    pipeline_path = OFFICIAL / "bishengir/lib/Dialect/HIVM/Pipelines/HIVMPipelines.cpp"
    autosync_path = OFFICIAL / "docs/source/zh_cn/developer_guide/features/AutoSync/AutoSync.md"
    source_records = []
    for filename, relative in SOURCES.items():
        path = ART / "vecadd-sources" / filename
        item = record(path)
        item.update({"commit":COMMIT,"url":UPSTREAM+relative})
        source_records.append(item)
    for path in (pipeline_path, autosync_path):
        item = record(path)
        item.update({"commit":COMMIT,"url":UPSTREAM+path.relative_to(OFFICIAL).as_posix()})
        source_records.append(item)
    dump(ART / "vecadd-source-manifest.json", source_records)
    passes = {"hivm-infer-func-core-type", "hivm-plan-memory", "hivm-graph-sync-solver", "convert-hivm-to-std"}
    pass_order = []
    for n,line in enumerate((OLD / "06-full-compile.stderr.txt").read_text(encoding="utf-8").splitlines(),1):
        m = re.search(r"IR Dump After .*? \(([^)]+)\)",line)
        if m and m[1] in passes:
            pass_order.append({"line":n,"pass":m[1],"header":line})
    dump(ART / "vecadd-pass-order.json", {"source":record(OLD / "06-full-compile.stderr.txt"),
        "selected_passes_in_actual_order":pass_order,"interpretation":"Selected log headers; intervening passes omitted. Two memory planning invocations have different roles."})
    evidence = {"method":"Read-only extraction from preserved IR; no compiler or device commands executed.",
                "inputs":[record(p) for p in input_paths],"operations":operations,
                "buffer_offsets_bytes":{name:offsets[v] for name,v in [("A_UB",a),("B_UB",b),("C_UB",c)]},
                "content_lifetimes_by_operation_ordinal":{"A_UB":[1,3],"B_UB":[2,3],"C_UB":[3,4]},
                "same_operation_boundary":"A/B last read and C first write occur in vadd (ordinal 3). This is not a proof based solely on disjoint lifetimes.",
                "inplace_basis":{"source":"vecadd-sources/PlanMemory.cpp","line_ranges":{"layout_offset_compatibility":[83,112],"gen_kill_same_scope_time":[856,880],"VAdd_ISA_whitelist":[891,907],"same_op_gen_kill_and_capacity":[936,978],"storage_entry_merge_before_address_plan":[1084,1135]},
                                 "scope":"Compiler's matching-version operator contract plus actual use-def/order; no device execution or universal allocator proof."},
                "sync_event_pairs":[{"source_pipe":"MTE2","wait_pipe":"V","event":"EVENT_ID0"},{"source_pipe":"V","wait_pipe":"MTE3","event":"EVENT_ID0"}],
                "barrier":"PIPE_ALL", "diagram_axes":"Logical operation order and happens-before only; no measured durations."}
    dump(ART / "vecadd-mechanism-evidence.json", evidence)
    font_candidates = [Path("C:/Windows/Fonts/msyh.ttc"),Path("/mnt/c/Windows/Fonts/msyh.ttc")]
    font_path = next((p for p in font_candidates if p.exists()), None)
    if font_path is None:
        raise FileNotFoundError("Microsoft YaHei font not found; choose an installed Chinese font explicitly.")
    font_manager.fontManager.addfont(str(font_path))
    family = font_manager.FontProperties(fname=str(font_path)).get_name()
    plt.rcParams.update({"font.family":family,"pdf.fonttype":42,"ps.fonttype":42,
                         "font.size":9.5,"axes.unicode_minus":False,"savefig.facecolor":"white"})
    paths = lifetime_figure() + pipeline_figure()
    unchanged = all(sha(Path(p)) == checksum for p,checksum in snapshots_before.items())
    assert unchanged, "An existing input changed during generation."
    dump(ART / "vecadd-figure-manifest.json", {"generated_utc":datetime.now(timezone.utc).isoformat(),
        "command":[sys.executable,str(Path(__file__).resolve())], "generator":record(Path(__file__).resolve()),
        "python":platform.python_version(),"matplotlib":matplotlib.__version__,"font":str(font_path),
        "figures":[record(p) for p in paths],"canvas_inches":{"vecadd-lifetime":[7.2,3.45],"vecadd-pipeline":[7.2,3.35]},
        "png_dpi":300,"pdf_fonttype":42,"existing_inputs_unchanged":unchanged,
        "disclaimer":"Source-backed schematic, not simulated/measured runtime; generated without invoking compiler or device."})
    print(json.dumps({"outputs":[str(p) for p in paths],"existing_inputs_unchanged":unchanged},ensure_ascii=False))


if __name__ == "__main__":
    main()
