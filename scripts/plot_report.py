"""Plot measured structure only; does not infer execution performance."""
from pathlib import Path
import json, hashlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
font = Path("C:/Windows/Fonts/simhei.ttf")
if font.exists():
    font_manager.fontManager.addfont(str(font))
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(font)).get_name()
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "axes.unicode_minus": False})

source = ROOT / "artifacts" / "toolchain" / "metrics.json"
rows = json.loads(source.read_text(encoding="utf-8"))
selected = [r for r in rows if not r["variant"].endswith("_g")]
fig, axes = plt.subplots(1, 2, figsize=(9, 3.25), layout="constrained")
colors = ["#6B315F", "#467690", "#6B315F", "#467690"]
for ax, key, title in zip(axes, ["text_bytes", "main_object_instruction_count"],
                         ["可执行文件 .text 段（字节）", "main.o 静态机器指令数"]):
    values = [r[key] for r in selected]
    bars = ax.bar([r["variant"].replace("_", "\n") for r in selected], values, color=colors,
                  edgecolor="black", linewidth=.5)
    for i, bar in enumerate(bars):
        if i%2: bar.set_hatch("//")
    ax.bar_label(bars, fontsize=9)
    ax.set_ylim(0, max(values)*1.19)
    ax.set_title(title, fontsize=11)
    ax.grid(axis="y", alpha=.18)
    ax.set_axisbelow(True)
fig.savefig(OUT/"toolchain_metrics.pdf")
fig.savefig(OUT/"toolchain_metrics.png",dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4.2), layout="constrained")
ax.set(xlim=(0, 10), ylim=(0, 5)); ax.axis("off")
def box(x,y,w,h,text,color="#F1E8EF"):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04",facecolor=color,
                               edgecolor="#6B315F",linewidth=1))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=10)
def arrow(a,b): ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="->",color="#44515D",lw=1.2))
for y, label, compiler in [(3.8,"SysY 源程序\nC 兼容子集执行", "Clang 14"),
                            (2.25,"手写 LLVM IR\n独立控制流 / SSA", "llvm-as + llc"),
                            (.7,"手写 RISC-V 汇编\nRV64GC / LP64D", "GNU assembler")]:
    box(.1,y,2.35,.85,label)
    box(3.3,y,2.2,.85,compiler,"#EBF1F8")
    arrow((2.5,y+.42),(3.25,y+.42))
    arrow((5.55,y+.42),(6.2,2.67))
box(6.2,2.25,1.55,.85,"目标文件\n+ SysY 运行库")
box(8.35,2.25,1.45,.85,"Linux ELF\nQEMU 执行")
arrow((7.8,2.67),(8.3,2.67))
box(6.2,.4,3.6,.85,"独立 Python oracle\n精确整数 / binary32 与浮点容差","#FFF3D6")
arrow((9.07,2.2),(9.07,1.3))
ax.text(6.95,3.5,"统一目标 ABI",ha="center",fontsize=9,color="#44515D")
fig.savefig(OUT/"equivalence_pipeline.pdf")
fig.savefig(OUT/"equivalence_pipeline.png",dpi=180)
plt.close(fig)
(OUT/"provenance.json").write_text(json.dumps({"source":"artifacts/toolchain/metrics.json",
 "sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"filter":"exclude _g variants for structural comparison",
 "chart_units":["bytes","static instruction count"],"performance_claim":False,
 "matplotlib":matplotlib.__version__,"schematic":"Design/verification pipeline, not measured timing"},indent=2),encoding="utf-8")
print("Wrote two PDF/PNG figures and provenance.")
