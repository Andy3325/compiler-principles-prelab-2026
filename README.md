# 编译原理预备实验

研究 GCC/Clang 完整编译流程、SysY 程序的 LLVM IR / RISC-V 等价实现，以及 AscendNPU IR / MLIR 中端 lowering。包含实验源码、独立预期测试、构建脚本、报告 LaTeX 和精选实验记录。

报告入口为 `report/main.tex`。朱泽帅负责工具链与 LLVM IR，张宸笛负责 RISC-V 汇编；进阶实验、示例设计、语义验证及报告由两人共同完成。完整成员字段与分工以报告为准。

## 实验范围与已验证结果

| 实验 | 已验证结果 | 公开记录 |
|---|---|---|
| GCC / Clang 工具链 | 两翻译单元，O0、O2、O2-g 六种构建，60/60 次功能测试通过；预处理、IR、汇编、ELF、符号及重定位分析 | `evidence/toolchain/` |
| 受控优化实验 | 向量化、循环展开、函数内联九种配置，90/90 次功能测试通过；另有 12/12 次 GDB 边界路径观测 | `evidence/toolchain/extended_exploration/` |
| SysY / LLVM IR / RISC-V | 两个示例，100 个整数与 60 个浮点逻辑用例，三种实现共 480/480 次 QEMU 执行通过；3 个语义错误变体全部检出 | `evidence/sysy/` |
| AscendNPU IR | 官方 VecAdd；6 次主机侧处理完成，18/18 项解析与结构核验通过；逐层 IR 与完整主机中端快照 | `evidence/mlir/` |
| 昇腾设备后端 | 缺少 hivmc / CANN 和昇腾设备，未生成设备目标文件，未执行设备测试 | `evidence/mlir/06-full-compile.stderr.txt` |

程序执行数与 IR 结构检查数分开统计。`bishengir-compile` 即使退出 0，诊断仍报告缺少 `hivmc` 且未生成 kernel，因此不计为设备编译成功。未开展真实 RISC-V / 昇腾硬件性能测量。

## 工程目录与证据索引

以下索引承接原附录“实验源码与复现证据索引”。`artifacts/` 是脚本生成的本地原始结果目录；公开精选副本在 `evidence/`。

| 内容 | 路径与用途 |
|---|---|
| 工具链程序 | `src/toolchain/`：C 主程序、头文件、跨翻译单元函数与受控实验变体 |
| SysY 示例 | `src/sysy/`：`control_matrix.sy`、`float_stats.sy`；`src/llvm/` 与 `src/riscv/`：对应手写 IR 与汇编 |
| SysY 运行时 | `runtime/`：sylib.c/h、MIT 许可、固定上游提交、语言及运行时来源说明；规范全文只在本地保留，公开提供来源链接 |
| MLIR / AscendNPU IR | `src/mlir/`：官方 VecAdd、固定版本源码子集及许可；`evidence/mlir/`：阶段 IR、diff、快照、核验和诊断；完整日志由脚本生成至 `artifacts/mlir/` |
| 测试与 oracle | `tests/`：完整输入、预期及独立 oracle；原始 `artifacts/toolchain/test_results.json`、`artifacts/sysy/` 的精选副本在 `evidence/` 同名子目录 |
| 构建与验证 | `scripts/reproduce.sh` 为便携入口；`scripts/run_all.sh` 为基础入口；`scripts/build_report.ps1` 为原 Windows 报告构建；`scripts/build_public_report.py` 支持无校徽的公开构建 |
| 本地 Windows 入口 | 原 `scripts/run_all.ps1` 含本机 Python 路径，仅本地保留；公开复现采用下文独立命令，不依赖该文件 |
| 汇总记录 | 原 `artifacts/combined_validation.json`、`artifacts/environment/versions.txt` 的公开副本位于 `evidence/`；`artifacts/report_review/` 页面渲染由 `inspect_report.py` 重建 |
| 报告与分析 | `report/*.tex`、必要配图；三个展开分析笔记的脱敏副本在 `evidence/report_notes/` |
| 实验输出图 | `materials/experiment-output/`：十张原图的逐字节副本、逐图来源索引和 SHA-256；04、05、06、10用于附录B |

## 实验输出摘录与报告补充

[实验材料索引](materials/experiment-output/README.md)逐张说明十张图的用途、原始文件和证据边界，[图片清单](materials/experiment-output/manifest.json)记录尺寸与 SHA-256。它们是命令输出和文件摘录的排版图，不是原生终端截屏；没有改写图中的输出或命令。

01、02的工具链记录来自2026-10-03原实验。04、05的样例输出可由原实验日志及独立预期核对，精选的六份原始 JSON 公开副本见 `evidence/sysy/logs/`。完整480/480结论由原 `summary.json`、480行CSV及逐项日志支持。图片及旧索引所称 Ubuntu 20.04 异机重跑的专用日志、脚本没有随本地材料保留，因此不将06中2026-10-07的重跑计为另一轮已核验执行，也不将其与原480次相加。07、08、10中的异机缓存路径与附录A的构建环境分开说明；不据图片认定异机重编译或独立复现已经核验。

第四章的新增Listing逐字节摘自真实 `artifacts/mlir/03-memory.mlir` 第3–11行和 `04-sync.mlir` 第9–17行，摘录与来源哈希见 `report/listings/PROVENANCE.json`。图6使用现有生成源 `scripts/generate_vecadd_mechanism_figures.py` 对应的正确矢量图 `report/figures/vecadd-lifetime.pdf`：仅UB标注 `[0,32)`、`[32,64)`，GM不附加无依据的偏移，横向为操作顺序；A最后读取与C首次写入仍位于同一vadd。原 `fig6.png` 保留为历史配图，因闭区间、GM范围和时间轴标注有误，不再作为报告当前图6。

附录B选用整数样例、浮点样例、整体验证汇总及Ascend后端限制四张输出图，其余六张仅在仓库归档。主机中端处理与设备端未执行的边界保持不变。

## 环境与依赖

原实验使用 Windows + WSL2 Ubuntu 22.04.5 LTS，x86_64，Linux 6.6.87.2；GCC 11.4.0、Clang / LLVM 14.0.0、RISC-V GCC 11.4.0、GNU Binutils 2.38、QEMU 6.2.0、Python 3.10.12、辅助 MLIR 14.0.0。Ascend 专用工具为官方 `ascendnpu-ir` 1.1.0 wheel，对应提交 `428ab8fdab46a879c7349caba4cde705bc8c9bb6`，内部 LLVM 19.1.7，与基础实验 LLVM 14 分开使用。

RISC-V 统一为 **RV64GC / LP64D / Linux ELF64 RISC-V**；SysY int 为 32 位，指针为 64 位，浮点参数遵循硬浮点调用约定。手写 IR 使用 LLVM 14 typed-pointer 语法。

Ubuntu 22.04 依赖安装（需要管理员权限和网络）：

```bash
sudo apt-get update
sudo apt-get install build-essential clang-14 llvm-14 llvm-14-tools \
  gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu libc6-dev-riscv64-cross \
  qemu-user mlir-14-tools python3 python3-pip gdb
```

报告原环境为 TeX Live 2025 / XeTeX、latexmk 4.87，使用 ctex、geometry、graphicx、booktabs、tabularx、listings、hyperref、titlesec、tikz、xurl、needspace 等包。Linux 可安装 `latexmk texlive-xetex texlive-lang-chinese texlive-latex-extra texlive-science`。Windows 原报告使用系统中文字体；Linux 公开构建临时副本采用 Fandol，版面可能有细微差异。

可选图表重建 / PDF 检查的 Python 依赖：

```bash
python3 -m pip install matplotlib Pillow PyMuPDF
```

`generate_vecadd_mechanism_figures.py` 依赖 Windows / WSL 可见的 Microsoft YaHei。仓库已提供必要配图，编译报告无需重生成图像。

## 构建与运行

在 Ubuntu / WSL 中：

```bash
git clone https://github.com/Andy3325/compiler-principles-prelab-2026.git
cd compiler-principles-prelab-2026
bash scripts/reproduce.sh
```

该入口采集环境，运行六种工具链构建、三种 SysY 实现与错误变体测试，再执行 Ascend 主机侧处理和核验。首次联网下载约 143 MB 的固定 wheel，校验 SHA-256 `0dc9e8436de8373a4bb68a8fcbfd346c8a0d3160cb338047cbdf4ecfdb1776ab`，解压到 `~/.cache/compiler-coursework/ascendnpu-ir-1.1.0/`；不安装 CANN，不修改系统 LLVM。

单独运行基础实验：

```bash
bash scripts/collect_environment.sh
bash scripts/toolchain_run.sh
bash scripts/sysy_build_test.sh
```

基础构建完成后，运行受控优化与 GDB 边界实验：

```bash
python3 scripts/toolchain_mechanism.py
python3 scripts/toolchain_extended_experiment.py
python3 scripts/toolchain_extended_boundary.py
# 或从头运行全部实验
bash scripts/reproduce.sh --extended
```

GDB 边界实验核查 Clang 14 / O2 基线函数字节与 CFG，其他版本可能主动拒绝继续；这是版本约束，不是通用性能基准。

单独运行进阶实验：

```bash
mkdir -p artifacts/mlir/sources
python3 scripts/mlir_prepare_wheel.py
python3 scripts/mlir_probe.py
python3 scripts/mlir_run_ascend.py
python3 scripts/mlir_verify.py
```

源码快照已包含；重取可执行 `python3 scripts/mlir_fetch_sources.py` 和 `python3 scripts/mlir_fetch_sources.py --tool-version`。二者分别获取固定 master 与匹配工具的快照，不能混用版本结论。

## 自动验证与报告构建

上述脚本实际执行测试并生成 JSON / CSV。重新汇总或检查已有产物：

```bash
python3 scripts/summarize_validation.py
python3 scripts/mlir_verify.py
python3 scripts/sysy_mutation_check.py
```

整数输出精确比较；浮点按 binary32 逐操作建模，容差为 `1e-6 + 2e-6*abs(expected)`。固定种子 `24115602412565`。整数域为 `0<=n<=6`、`-40<=stop<=40`、`-2<=gate<=2`、非零除数在 `[-7,7]`、6 个增量在 `[-30,30]`；浮点域为 `0<=n<=4`、有限数、`|scale|<=8`、`|a|<=32`。

本地 Windows 已有授权校徽文件时，原构建命令为：

```powershell
powershell -NoProfile -File .\scripts\build_report.ps1
```

公开仓库不分发校徽。在装有 TeX Live / latexmk 的 Windows 或 Linux 上：

```bash
python3 scripts/build_public_report.py
python3 scripts/inspect_report.py
```

公开构建在临时目录运行，缺校徽时仅移除临时封面的图片引用，Linux 使用 Fandol；不改原 `.tex`，成功后输出 `report/main.pdf`。含校徽的本地原 PDF 不上传。`inspect_report.py` 渲染全部页并检查页面边界，不能替代人工视觉检查。

历史 `toolchain_extended_review.py` 依赖本机冻结备份，不是普通复现入口；本地打包及历史完整性审阅脚本不随公开仓库分发。

## 原始产物、公开副本与固定版本

`evidence/` 是已有结果的精选公开副本，保留实验数值、结果、IR 和来源哈希，仅归一化本机工程根、缓存用户名和主机名。`evidence/PUBLIC_MANIFEST.json` 记录原文件与公开副本 SHA-256 及变换说明；这些副本不是重新运行的结果。

`python3 scripts/export_public_evidence.py` 从本地已有 `artifacts/` 导出精选资料，不运行实验。干净克隆应先运行实验再按需导出；仓库已有 evidence 可直接阅读。

未上传但在原本地完整保留：可执行文件、.o/.a/.bc、重复执行日志、完整 API tree / 网页缓存、页面渲染、机器资源与旧备份清单、课程原 PDF / DOC / PPTX、旧 ZIP、规范全文和校徽。截图目录中的旧讲解索引及一页讲解PDF存在未独立核验的异机重跑说明，只在本地保留；以新实验材料索引的核验边界为准。完整原始产物可通过上述脚本生成至 `artifacts/`，不保证时间戳、绝对路径或 ELF 字节逐位一致。

报告附录给出固定实验快照 Commit SHA，可运行 `git checkout <报告中的完整SHA>` 查看。后续用于更新报告链接的文档提交不改变该实验快照；不要将会变化的 main 分支视为固定版本。

## 局限与第三方资料

.sy 为 SysY2022 子集，源版本采用 Clang 的 C 兼容模式；本工程不是完整 SysY 编译器。有限测试不替代形式化等价证明，QEMU 功能正确不代表真实硬件性能。课程张量扩展定义未提供，数组不被冒称为该扩展。

Ascend 实验只证明主机侧中端 IR 处理和结构核验；缺少 hivmc / CANN / NPU，尚未生成可执行设备目标文件，不能判断设备数值正确性或性能。

SysY 运行库来自 [yuhuifishash/SysY](https://github.com/yuhuifishash/SysY/tree/d3639373ddc894dd0d20b307d0bf1fe92b6f685b)，MIT 声明保存在 runtime/LICENSE.upstream。Ascend 示例及源码来自 [Ascend/AscendNPU-IR](https://github.com/Ascend/AscendNPU-IR)，各子集保留 LICENSE、NOTICE 和版权头；它们不是小组原创。规范来源见 runtime/README.md，规范全文未纳入 MIT 再分发范围。

详细来源与许可边界见 [THIRD_PARTY.md](THIRD_PARTY.md)。仓库公开可读不等于所有文件获得同一种再许可；本次不为整个工程新增统一开源许可证。
