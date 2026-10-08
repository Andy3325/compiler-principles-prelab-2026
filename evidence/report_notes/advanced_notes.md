# 进阶实验：在主机运行的 Ascend 设备中端 lowering 与后端限制

本文件供共同报告整合使用；所有路径均相对于实验根目录。原实验日期：2026-10-03（Asia/Shanghai），机制深化日期：2026-10-04。本部分完成了 **在 x86_64 主机上实际执行 Ascend 设备中端转换 + 后端受限部分的官方文档/源码探索**，并非生成 host CPU 代码，没有 NPU 数值执行结果。历史文件名 `07-host-lowered.mlir` 保留不变，其中 host 指编译器运行位置，不是代码生成目标。本轮没有重跑原编译命令或改变 6 次处理、18 项核验统计。

## 1. 问题、材料与版本控制

研究问题是：`C[i]=A[i]+B[i]` 的一段向量加法，在 MLIR 中端如何逐步加入核类型、片上存储地址、异步流水同步以及调用接口，而不改变其输入输出关系？本地四页《预备工作 - 了解你的编译器.pdf》第 2 页指定 VecAdd，并允许环境困难时通过官方文档和方言设计探索完成相应部分。本实验没有因缺少设备而跳过中端。

查阅了作业给出的快速入门、CANN 编译器入口、官方仓库与 FAQ。当前快速入门仍提供 `16xi16` VecAdd，没有迁移到其他算子。保存的上游 `master` 快照为 `37c6ebc33d1789500014e6a7b2b62164b3cb566b`，但实际运行工具不是该快照构建：为避免本机 7.6 GiB 内存下全量构建 LLVM，采用官方项目在 PyPI 发布的 Linux wheel `ascendnpu-ir==1.1.0`，独立解包到 WSL 用户缓存。官网版本配套说明和官方仓库 wheel 构建文件均给出该包的依据。

实际 `--version` 返回：

```text
bishengir-opt 1.1.0 (.../bishengir 428ab8fdab46 2026-04-30)
llvm 19.1.7 e4ce5939f6e1
Release build
```

工具对应完整 commit 是 `428ab8fdab46a879c7349caba4cde705bc8c9bb6`（标签 `v1.1.0-post2`），因此实际实验使用 `src/mlir/official-tool-1.1.0/` 中这一版本的原始 VecAdd，流水线解释也优先依据此版本源码。工具源码与 `master` 中的 `add.mlir` SHA-256 均为 `bf6be387f569d6178346e4beabf9dcc156ea8cdc862a8e5c5f5ce8e9119b1750`，已实际核对相同。**不能将报告写成“运行了当前 master 编译器”。**

wheel 为 `ascendnpu_ir-1.1.0-cp310-cp310-manylinux_2_28_x86_64.whl`，142831025 字节，SHA-256 为 `0dc9e8436de8373a4bb68a8fcbfd346c8a0d3160cb338047cbdf4ecfdb1776ab`。下载后已校验；未全局安装或替换系统 LLVM。该工具基于 LLVM 19.1.7 构建，与基础实验系统 LLVM 14 是两个独立工具来源，不混用其 MLIR 解析器。

证据：`artifacts/mlir/sources/{source-manifest,tool-source-manifest,wheel-provenance,website-manifest}.json`，`bishengir-opt-version.stdout.txt`、`bishengir-compile-version.stdout.txt`。源码与许可原件在 `src/mlir/official*/`，官网 HTML 快照在 `artifacts/mlir/sources/web-*.html`。本目录只保存用到的少量上游文件，没有将整套 LLVM 源码或 wheel 缓存放入提交物。

## 2. 环境与实际边界

主机执行环境是 WSL2 Ubuntu 22.04.5 LTS、x86_64、Python 3.10.12，内核 `6.6.87.2-microsoft-standard-WSL2`。Windows 工作目录映射为 `<PROJECT>`。Ascend 工具显式调用路径为 `<USER_HOME>/.cache/compiler-coursework/ascendnpu-ir-1.1.0/unpacked/ascendnpuir/bin/`；没有修改全局 PATH，所以环境探测中的 PATH 查找仍显示 `bishengir-opt:NOT_FOUND`，这不等同于独立缓存中的程序不可用。

本 WSL 环境查不到 `hivmc`、`npu-smi`，`/usr/local/Ascend` 以及 `/dev/davinci*`、`/dev/devmm_svm`、`/dev/hisi_hdc` 均不存在。因而能够在 x86 主机上运行文本 IR 变换，但不能完成本环境下的设备后端编译、CANN runtime 链接与上板执行。这里报告的是 WSL 可见状态，不据此推断所有外部机器的设备状况。官方兼容表给出 AscendNPU IR 1.1.0 与 CANN 9.0.0 的配套关系；本机并未安装这一 CANN 组合。

证据：`artifacts/mlir/environment.stdout.txt`、`probe-results.json`，以及工具自带的完整 `--help` 输出。使用的每个 pass 名都出现在实际工具帮助中。

## 3. 输入语义和方言分工

官方 `add.mlir` 有三个 `memref<16xi16, #hivm.address_space<gm>>` 参数，分别作为输入 A、输入 B、输出 C；它们是 16 个 16 位整数的连续区间。函数带 `hacc.entry` 和 `#hacc.function_kind<DEVICE>`。三次 `memref.alloc` 申请 UB 区域的临时缓冲，随后依次执行两个 `hivm.hir.load`、一个 `hivm.hir.vadd` 和一个 `hivm.hir.store`。

官方 host 程序给出 A=`0,1,...,15`、B 全为 1，因此期望 C=`1,2,...,16`；这些数值处于 i16 可表示范围内。这是**源码规定的输入和可独立计算的期望值**，不是本机 NPU 运行输出。

此例入口已经是 HIVM，GM 与 UB 已显式出现，不能画成实际运行过 `Torch → HFusion → HIVM`。MLIR 在同一模块中同时容纳 `func`、`memref`、`arith`、HACC 和 HIVM，所谓多层 lowering 也不意味着每一步必须更换全部方言。HACC 表达设备函数和入口等异构属性，HIVM 则表达面向硬件的计算、搬运和同步。官方架构文档中的 HFusion 是 Linalg named operations 的扩展层，面向相对硬件无关的融合与调度；这是理解较高入口的背景，**没有作为本例实测阶段**。

与基础实验手写 LLVM IR 相比，这里可保留整块向量加法、地址空间与流水依赖，而无需在开始时展开为逐元素 load/add/store 或机器指令。渐进降低的意义在于让各类优化在仍保留所需语义的层级进行。

## 4. 两条互相核对的真实实验路径

首先用 `bishengir-opt` 单独执行一组有辨识力的 pass，隔离每个变换的作用。其次执行官方完整 `bishengir-compile`，打印真实流水线的 IR；并用 `hacc-append-device-spec` 与 `optimize-hivm-pipeline` 独立生成在主机生成的设备中端 IR。所有命令、退出码、诊断和产物存在性记录在 `artifacts/mlir/ascend-results.json`。单独 pass 链用于解释；完整流水线快照用于说明编译器实际经过的次序，二者不可混为一条完全相同的调用过程。

以下省略公共工具目录和文件目录，完整可复现命令在 `scripts/mlir_run_ascend.py`：

```bash
bishengir-opt add.mlir -o 01-parsed.mlir
bishengir-opt add.mlir --hivm-infer-func-core-type -o 02-core.mlir
bishengir-opt 02-core.mlir --hivm-plan-memory -o 03-memory.mlir
bishengir-opt 03-memory.mlir --hivm-inject-sync -o 04-sync.mlir
bishengir-opt 04-sync.mlir --convert-hivm-to-std -o 05-standard.mlir
bishengir-opt add.mlir --hacc-append-device-spec=target=Ascend910B1 \
  --optimize-hivm-pipeline -o 07-host-lowered.mlir
```

上面 6 条主机命令均退出 0、没有错误诊断、实际产生目标 IR。重新用相同官方解析器解析 6 个产物和 5 个完整编译器快照均成功。由工具打印的完整编译器最终 MLIR，与独立主机执行的完整设备中端流水线 `07-host-lowered.mlir` 去掉快照说明行后逐字一致；这是本实验实际到达后端入口的交叉证据。

| 产物 | alloc | HIVM load/add/store | pointer_cast | set/wait/barrier | 模板调用 | 核心变化 |
|---|---:|---|---:|---|---:|---|
| 01-parsed | 3 | 2/1/1 | 0 | 0/0/0 | 0 | 官方输入成功解析 |
| 02-core | 3 | 2/1/1 | 0 | 0/0/0 | 0 | 模块及函数推导为 AIV |
| 03-memory | 0 | 2/1/1 | 3 | 0/0/0 | 0 | UB 分配转为固定偏移并复用 |
| 04-sync | 0 | 2/1/1 | 3 | 2/2/1 | 0 | 插入跨流水事件和返回前 barrier |
| 05-standard | 0 | 0/0/0 | 4 | 2/2/1 | 4 | 向量及搬运操作改为模板调用 |
| 07-host-lowered | 0 | 0/0/0 | 4 | 2/2/1 | 4 | 完整流水线结果，额外目标属性及 mask 初始化 |

统计来自 `artifacts/mlir/stage-operation-counts.csv`，是 IR 静态操作计数，**不是指令执行次数或性能测量**。完整编译器原始打印见 `06-full-compile.stderr.txt`；有用快照及顺序索引见 `compiler-snapshots/`、`compiler-snapshot-index.json`。两次 `hivm-plan-memory` 出现于完整日志，不能声称每次都产生同一种效果；后一次才把本例局部 UB 分配落实为地址。

## 5. 三个主要发现

### 5.1 核类型和存储空间已经逐渐落实

`hivm-infer-func-core-type` 为函数加入 `hivm.func_core_type=AIV`，模块也标记 AIV。这符合纯向量加法的操作集合。本例没有矩阵乘法，因此没有观察到 AIC/AIV 混合核拆分，也没有通过多核调度获得的性能结果。

原始三个 UB 缓冲各有 16×2=32 字节。内存规划后，前两输入缓冲分别从偏移 0 和 32 构造；输出再次使用偏移 0：

```mlir
%c32_i64 = arith.constant 32 : i64
%c0_i64 = arith.constant 0 : i64
%0 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
// input A -> %0
%1 = hivm.hir.pointer_cast(%c32_i64) : memref<16xi16, #hivm.address_space<ub>>
// input B -> %1
%2 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
// vadd inputs %0, %1; output %2
```

三个逻辑缓冲没有分配到三个独立区域，而是让结果 C 与输入 A 共址。**A 的最后读和 C 的首次写都在同一个 vadd；不能单凭“生命周期不重叠”证明这种复用安全。** A 在 vadd 后不再读取，加上匹配版本规划器对 VAdd 的原地执行许可，共同支持这一解释；本轮新增源码证据详见第 10 节。静态 IR 中两段非重叠物理区域为 `[0,32)`、`[32,64)`，相对于三段独立 32 字节区间的朴素方案，地址规划占用从 96 字节降至 64 字节。这里是**该 IR 的静态地址复用**，没有测量 NPU 实际峰值内存或速度。这里的 0 是 UB 地址空间内偏移，不能解释为普通 CPU 的空指针。

证据：`03-memory.mlir`、`03-memory.diff`；工具版本对应 `HIVMPipelines.cpp` 第 359–371 行在局部内存规划后处理同步。

### 5.2 IR 顺序被落实为硬件流水依赖

单独 `hivm-inject-sync` 后观察到：

```mlir
hivm.hir.set_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
// UB output pointer creation
hivm.hir.wait_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
// hivm.hir.vadd
hivm.hir.set_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
hivm.hir.wait_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
// hivm.hir.store
hivm.hir.pipe_barrier[<PIPE_ALL>]
```

对本例，MTE2 对应输入搬运流水，V 为向量计算流水，MTE3 对应输出搬运流水。文本中 load 在 vadd 前，并不自动等于不同硬件流水上的异步搬运已完成。第一组事件将“两次输入搬运完成”与“向量运算可以开始”连接，第二组将“结果计算完成”与“输出搬运可以开始”连接；返回前的 PIPE_ALL 用于结束前的全流水同步。两组都使用 EVENT_ID0，但源/目的流水对不同，不能把它解释成没有区分方向的全局唯一事件号。

单独 pass 使用 `hivm-inject-sync`，**完整默认流水线日志实际调用的是 `hivm-graph-sync-solver`**。此例两种方案得到相同的关键事件对，但不可宣称它们对所有程序等价或默认流水线固定选择 InjectSync。工具对应源码 `HIVMPipelines.cpp` 第 51–68 行明确按配置选择 GraphSyncSolver 或 InjectSync；在本例没有观察到核间 `sync_block`。

证据：`04-sync.mlir`、`04-sync.diff`、`compiler-snapshots/04-hivm-graph-sync-solver.mlir`。同步操作的 event、set_pipe、wait_pipe 字段由工具匹配版本的 `HIVMSynchronizationOps.td` 第 43–80 行定义，官方 AutoSync 文档解释依赖分析及同步插入。

### 5.3 向量/搬运语义变成模板函数接口，尚未变成设备 LLVM IR

`convert-hivm-to-std` 后，两个 load、一个 vadd 和一个 store 分别对应以下四次调用：

```mlir
call @load_gm_to_ubuf_1d_int16_t(...)  // twice
call @vadd_1d_int16_t(...)
call @store_ubuf_to_gm_1d_int16_t(...)
```

声明中固定长度 memref 经 `memref.cast` 转为携带动态长度/stride/offset 的接口形式；例如 `vadd_1d_int16_t` 接受 UB memref 参数。计算、拷贝的入口签名、核心属性与 always_inline 标志在此变得明确，后续可以链接模板 bitcode 与完成底层代码生成。第四个 vadd 参数来自新构造的零长度额外缓冲占位；它不是新增的第四个向量输入，也不意味着又分配一段 32 字节数据区。

尽管 pass 名包含 “Standard”，本例结果仍含 `hivm.hir.pointer_cast`、set/wait/barrier 和 memref，并不是纯 LLVM dialect，更不是已输出 `.ll` 或机器指令。主机执行的完整设备中端流水线还加入 `hivm.hir.set_mask_norm`、`hivm.storage_aligned`、设备规格和兼容打印属性。这就是本次实际保存的低层 MLIR 后端入口 `07-host-lowered.mlir`。LLVM IR 转换、bitcode 链接和 NPU 指令生成属于后续 `hivmc` 路径；这里只做官方架构/源码研究，未取得该 VecAdd 的设备 LLVM IR。

证据：`05-standard.mlir`、`05-standard.diff`、`07-host-lowered.mlir`，匹配版本 `HIVMToStandard.cpp` 第 949–1001 行及第 1755 行。更高层 HFusion 与更低层 hivmc 的职责依据官方架构文档，但不把网站架构图作为本机执行证明。

## 6. 真实失败与验收陷阱

实际运行了官方完整命令并启用逐 pass 打印：

```bash
bishengir-compile add.mlir --enable-hivm-compile --target=Ascend910B1 \
  --mlir-disable-threading --mlir-print-ir-after-all \
  --mlir-print-ir-module-scope -o 06-kernel.o
```

日志开头先记录无法查询 `hivmc --version`，仍继续在主机执行设备中端变换；最后再次报 `[ERROR] Cannot find hivmc under $PATH`。实际进程退出码为 **0**，但 `06-kernel.o` **不存在**。故验收规则必须同时检查退出码、错误诊断和目标文件，不能按单一退出码宣称设备编译成功。

这个行为有版本对应源码支持：`src/mlir/official-tool-1.1.0/bishengir/lib/Tools/bishengir-compile/BiShengIRCompileMain.cpp` 第 307–311 行在 `runExternalHIVMC` 失败后发出 warning，仍返回 `OwningModuleRef(mod)`。这解释了“主机上执行的设备中端可产出模块”与“外部设备后端没有完成”为什么能够同时发生。报告不将退出 0 直接解释为工具的全部职责已完成。

另一个源码审查发现是，原始官方 `main.cpp` 第 185–189 行只逐项打印 Expect/Result，随后无条件打印 `[success] compare output success`；它没有在循环中对每个元素做相等断言。因此即使将来上板运行，也应逐项比较真实输出并检查设备 API 返回值，不能单凭这条 success 文本验收。这是**对官方例程的源码观察**，没有在本机制造设备失败或伪造输出。

官方 FAQ 要求完整 CANN 环境、设备编译工具和 CANN runtime host 程序才能端到端上板。当前 CANN、hivmc 和设备都没有在此 WSL 中就绪；为取得后端二进制而全量构建 LLVM 或安装完整大型 CANN 不属于本实验最小环境配置。本次保留中端真实成功和后端真实受限证据，设备端部分按作业允许方式完成文档探索。没有 NPU 正确性测试通过数，也没有任何硬件性能结论。

## 7. 可重复执行与交付证据

已有源码完整时，从 WSL 在实验根目录执行：

```bash
python3 scripts/mlir_prepare_wheel.py
python3 scripts/mlir_probe.py
python3 scripts/mlir_run_ascend.py
python3 scripts/mlir_verify.py
```

若需重新下载官方原件，联网运行 `python3 scripts/mlir_fetch_sources.py` 和 `python3 scripts/mlir_fetch_sources.py --tool-version`。prepare 脚本使用用户缓存，wheel 内容和 SHA 固定，不需要管理员权限。run 脚本会重新生成指定的 MLIR/日志，并明确标记 `BLOCKED_BACKEND_MISSING`；此状态不是通过。脚本本身退出 0 只表示这组包含预期阻塞的采证流程完成，是否生成设备二进制应读取 JSON 中的独立状态。

`verification-summary.json` 当前为 **18/18 项证据一致性检查通过**：包括 11 份 IR 的重新解析、两版本 VecAdd 原件相同、在主机生成的设备中端 IR与完整编译器最终快照相同，以及设备失败没有被计为成功。该数字不代表 18 次设备测试；实际主机变换命令是 6 条，NPU 程序执行是 0 次。

建议报告中的一句精确结论：**“在 x86_64 WSL 上，使用官方 AscendNPU IR 1.1.0 完成 VecAdd 的核类型推导、UB 地址规划、跨流水同步和模板调用 lowering，并保存主机执行的完整设备中端流水线与逐 pass 快照；因缺少 hivmc/CANN 和可见设备，未生成 NPU 二进制或进行设备执行，后续层级通过版本匹配源码及官方文档进行探索。”**

## 8. 可直接用于参考文献的来源

1. AscendNPU IR，编译与执行示例，https://ascendnpu-ir.gitcode.com/zh_cn/sources/introduction/quick_start/examples_zh.html ，访问日期 2026-10-03。
2. Huawei，CANN 编译器，https://www.hiascend.com/cann/bisheng ，访问日期 2026-10-03。
3. Ascend，VecAdd 官方源码（本次工具匹配版本），https://github.com/Ascend/AscendNPU-IR/tree/428ab8fdab46a879c7349caba4cde705bc8c9bb6/bishengir/test/Integration/HIVM/VecAdd 。
4. AscendNPU IR，FAQ，https://ascendnpu-ir.gitcode.com/en/faq/faq.html ，访问日期 2026-10-03。
5. AscendNPU IR，架构设计，https://ascendnpu-ir.gitcode.com/zh_cn/sources/introduction/architecture_zh.html ，访问日期 2026-10-03。
6. AscendNPU IR，PyPI 1.1.0 元数据和 wheel，https://pypi.org/project/ascendnpu-ir/1.1.0/ ，访问日期 2026-10-03。
7. Ascend，HIVM 流水线（精确源码版本），https://github.com/Ascend/AscendNPU-IR/blob/428ab8fdab46a879c7349caba4cde705bc8c9bb6/bishengir/lib/Dialect/HIVM/Pipelines/HIVMPipelines.cpp 。
8. Ascend，设备编译器驱动（精确源码版本），https://github.com/Ascend/AscendNPU-IR/blob/428ab8fdab46a879c7349caba4cde705bc8c9bb6/bishengir/lib/Tools/bishengir-compile/BiShengIRCompileMain.cpp 。

## 9. 完成度与主报告建议

| 作业要求 | 本次状态 | 可引用证据 |
|---|---|---|
| 官方 VecAdd 输入、计算、输出 | 源码分析完成 | 两份固定 commit 原件、主机输入/期望定义 |
| 版本与 pass 核实 | 实际工具核实完成 | version/help、wheel/source manifests |
| lowering 与优化、关键 IR 和差异 | 主机实际完成 | 01–05、07 IR，5 份 compiler snapshots，4 份主要 diff |
| 数据搬运、内存空间、同步分析 | 基于真实 IR 完成 | GM/UB、0/32 地址、事件对、模板函数 |
| 后续 LLVM/设备指令关系 | 官方文档/匹配源码探索 | 架构说明、设备驱动源码 |
| 设备编译与执行 | 受真实环境阻塞 | `06-full-compile.stderr.txt`、缺失 kernel.o、环境日志 |

主报告已采用信息逐层显式化表、数据流/内容生命周期图和流水 happens-before 图；原操作计数表与完整命令留在本记录。阶段正文区分单独 InjectSync 观察与完整流水线 GraphSyncSolver，不把更高层 HFusion 画成实际经历的入口。

## 10. 机制深化：同一操作边界的原地复用

本轮新增官方原件位于 `artifacts/mechanism/vecadd-sources/`，没有修改旧 `src/mlir/` 副本。下载来源、固定 commit、字节数与 SHA-256 全部在 `vecadd-source-manifest.json`。关键 `PlanMemory.cpp` SHA-256 为 `95ddc758ef2d6932405e44dd0011969c36c70bc38e2fde2ba7bd57ffc0732f74`。

### 10.1 真实 use-def 与内容活跃区间

按四个数据操作编号：1 = load A，2 = load B，3 = vadd，4 = store C。脚本直接读取 `03-memory.mlir` 的操作数和定义，得到 A 在 1 写、3 读，B 在 2 写、3 读，C 在 3 写、4 读。图中使用“内容活跃区间”，不是 memref SSA 句柄的存在区间，亦不是设备时间线。

- A_UB：`%0`，pointer_cast offset 0，最后读为操作 3。
- B_UB：`%1`，pointer_cast offset 32，最后读为操作 3。
- C_UB：`%2`，pointer_cast offset 0，首次写也是操作 3。
- 在操作粒度上，A/C 有共同端点。把区间任意画成不相交半开区间，不会自动证明同一算子内部的读写可以原地重叠。

### 10.2 匹配版本 planner 的具体机制

以下行号都属于 `vecadd-sources/PlanMemory.cpp`，固定 commit `428ab8fdab46a879c7349caba4cde705bc8c9bb6`。

| 行号 / 函数 | 真实源码行为 | 对本例可支持的解释 |
|---|---|---|
| 83–112，`getStaticOffset` / `isReusableByOffset` | 比较各输入与输出 memref 的布局 offset；无显式 strided layout 返回 0 | 本例 identity layout 的 offset 均为 0；不是要求已规划的 UB 起始地址 0 与 32 相同 |
| 683–704，`UpdateOperandGenInfo` | 首次写从 DEFINED 进入 GENED 并加入 gen 集合 | C 内容由 vadd 首次生成，而不是因 alloc 句柄存在就已有内容 |
| 715–739，`UpdateOpKillInfo`；774–783，`AllDeadAfter` | 对已生成缓冲结合活跃性、别名与作用域判断 dead-after | A/B 在 vadd 后无后续读取，允许出现在该操作 kill 集合 |
| 856–880，`GenerateBufferLife` | 同一操作 gen 的 allocTime 和 kill 的 freeTime 使用相同 scopeTime | 首次写/最后读共享逻辑时刻；不是由不同操作天然分开的生命周期 |
| 891–907，`IsReuseHIVMOp` | VAdd 等明确在 ISA 可原地执行名单；要求无内联 broadcast / transpose，且通过布局 offset 检查 | 算子许可是同操作复用额外必需的依据 |
| 936–978，`GenerateInplaceList` | 同一操作 gen/kill 配对；被复用容量大于等于新结果；排除 ignoreInplace | 本例 A/C 各 32 字节，容量条件成立 |
| 1084–1126，`MergeInplaceSE` | 合并存储条目的生命周期、原地缓冲集合并更新映射 | 两个逻辑值可以映射到同一存储条目 |
| 1128–1135，`PlanLocalMemAddress` | 先合并原地条目，再做后续地址规划 | 观察到相同地址有源码机制解释，而不只是按地址相等倒推 |

精简原始片段（保留逻辑，省略无关分支）：

```cpp
// IsReuseHIVMOp, lines 897–903
if (mlir::isa<hivm::VAddOp, hivm::VSubOp, hivm::VMaxOp, hivm::VMinOp,
              hivm::VOrOp, hivm::VAndOp, hivm::VMulOp>(op) &&
    !hasInlineBroadcastOrTransposeAttr(op)) {
  // above ops can be inplaced in isa
  return true;
}
```

本例同形状、同元素宽度、相同 UB 空间、32 字节整块重叠且无广播/转置，数据流允许输入 A 被当前 vadd 消费后由 C 替代；数学式中没有要求稍后再读取旧 A。**这依赖官方算子原地执行契约，不应仅凭逐元素公式推导任意向量化实现都安全。** 未做 NPU 指令执行、形式化证明或任意部分重叠实验；也未声称 planner 必定选择 A 而不可能选择 B，或者该布局是通用全局最优解。实际输出选择了 A，对这一实例已有 use-def 和源代码支持。

## 11. 同步语义、实际 pass 次序与解释边界

工具匹配 `AutoSync.md` 第 17–29 行解释 set 在源流水前序完成后触发事件，wait 在目的流水阻塞后续工作，barrier 约束指定流水的前序完成。两对事件都用 ID0，但它们分别属于 MTE2→V、V→MTE3。图中 load A/B 合并在一个框是排版缩写，不表示一条指令。PIPE_ALL 是本例核内全部流水约束，不是跨所有设备核的 global barrier，也不代表 CPU 已验证 NPU 输出。

`HIVMDMAOps.td` 的 LoadOp 明确带 `PIPE_MTE2`（第 62–65 行），StoreOp 带 `PIPE_MTE3`（145–146 行）；实际事件配对进一步指明 V 上的加法依赖。新增源码 `GetPipe.cpp` 是 CopyOp 的流水推导，不把它误作 LoadOp/StoreOp trait 的定义证据。

从原始 `06-full-compile.stderr.txt` **只读提取**的实际关键次序已另存 `vecadd-pass-order.json`：

| 原日志行 | pass | 对应快照 / 解释 |
|---:|---|---|
| 319 | hivm-infer-func-core-type | AIV 显式化 |
| 463 | hivm-plan-memory | 前次为 global workspace 模式，本例局部 alloc 仍存在 |
| 2015 | hivm-plan-memory | 局部 UB 地址规划，0/32/0 |
| 2069 | hivm-graph-sync-solver | 完整驱动实际同步方案 |
| 2345 | convert-hivm-to-std | 算子转设备模板调用，仍保留其他设备信息 |

对应 `HIVMPipelines.cpp`：第 178 行核推导；第 219–225 行 global workspace 规划；第 364 行 local planning；第 367/369 行还有 lower-to-loops/decompose；第 371 行 normal sync pipeline；第 51–68 行按选项选择 GSS 或 InjectSync；第 395 行模板转换。不是声称这五个名字覆盖完整 pipeline。核推导源码按设备操作约束推导核类别并跳过 host 函数（`InferFuncCoreType.cpp` 第 40–80 行），pipeline 注释举出的一个真实后继依赖是 AutoBlockify 的物理核数量依赖 core type（第 179–180 行）。**本例没有 AutoBlockify 效果证据，不把这条源代码设计依赖改写成本例多核优化结果。**

内存规划使物理别名关系显式化，后续同步需保持这些存储访问的正确依赖；GraphSyncSolver 的 IR translator 能回溯别名并接纳 PointerCast 作为根（新增文件第 136–140、187–193 行）。InjectSync 的 `MemoryDependentAnalyzer.cpp` 第 45–57、74 行起显式比较地址空间与区域重叠，但它不是本例完整 driver 的 GSS 算法，不能据此声称二者实现相同。调序实验本轮未执行：现有真实 pipeline、快照和源码已足够解释自然依赖，不增加无辨识力的编译次数。

## 12. 两张图的生成、检查与本轮命令

新增生成脚本 `scripts/generate_vecadd_mechanism_figures.py` 只读取旧 IR/日志与源码；不调用编译器，不创建设备执行结果。它检查实际操作次序和 use-def、偏移、事件配对，提取实际 pass 日志行，生成两张机制图，并记录输入/输出 hash、Python/Matplotlib 版本、字体和尺寸。

本轮实际执行的生成命令（PowerShell，在工程根目录）：

```powershell
& '<USER_HOME>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'scripts\generate_vecadd_mechanism_figures.py'
```

输出：`report/figures/vecadd-lifetime.{pdf,png}` 与 `vecadd-pipeline.{pdf,png}`；PDF 使用嵌入 TrueType 字体，PNG 为 300 dpi，白色背景。PDF 尺寸分别为 7.2×3.45、7.2×3.35 inch；正文按 textwidth 缩放。图形工作流参考 scientific-visualization / matplotlib 技能及 Kassis et al., *Scientific Agent Skills* (2026), DOI `10.48550/arXiv.2609.00065`；这一参考仅影响制图程序，不是 Ascend 技术结论的依据。

新增证据索引：

- `artifacts/mechanism/vecadd-source-manifest.json`：七份新增官方原件及两份已有匹配源码的来源、commit、SHA。
- `artifacts/mechanism/vecadd-mechanism-evidence.json`：实际 IR use-def、操作行号、内容生命周期、offset 与源码对应。
- `artifacts/mechanism/vecadd-pass-order.json`：旧完整驱动日志中关键 pass 的真实先后与原行号。
- `artifacts/mechanism/vecadd-figure-manifest.json`：生成命令、工具版本、输入不变检查、图件 SHA 与尺寸。

原件获取使用 PowerShell `Invoke-WebRequest -Uri <manifest 中的固定 raw URL> -OutFile <artifacts/mechanism/vecadd-sources/文件>`；完整 URL 和下载后的 hash 可用于逐份复现。新增 source 文件保留上游版权/许可头。主报告删除了旧的大命令、文件名和操作计数表，改放两个机制图与信息显式化核心表；这些历史细节仍保留在本记录，已有复现脚本均未修改。

新增主报告参考文献键：`ascendplan`（PlanMemory.cpp）、`ascendsync`（AutoSync.md）、`ascendpipeline`（HIVMPipelines.cpp），全部链接固定 commit 的官方 GitHub 页面。官网在线同步页面另已浏览核验：<https://ascendnpu-ir.gitcode.com/zh_cn/sources/developer_guide/features/AutoSync/AutoSync_zh.html>。网站“默认 InjectSync”措辞不用于覆盖本机日志已观察到的 GSS；版本内行为始终以实际日志及匹配源码为准。
