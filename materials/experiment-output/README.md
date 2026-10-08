# 实验输出图归档与证据索引

本目录保存已有十张 PNG 的逐字节副本，全部由命令输出和实际文件摘录排版而成，**不是桌面或终端软件直接截屏**。图片仍保留原标题、命令和路径；本轮只整理材料，没有重新执行实验，也没有改写图片。原文件位于本地 `实验截图_发组员/`，复制前后十张图的 SHA-256 全部一致，尺寸和完整校验值见 [manifest.json](manifest.json)。

报告附录 B 选用 04、05、06、10；01、02、03、07、08、09 仅在仓库保存，供查阅。下表的公开链接指向仓库实际存在的源码、输入、汇总或 IR。`artifacts/...` 用代码文字标示本地原记录定位，不伪装成已上传的链接。

## 实验记录与证据边界

01 和 02 的编译、链接与 60/60 结果属于 **2026-10-03 原工具链实验**。01 的四阶段命令、退出码和宏展开产物可以与原记录核对；02 的符号解析、链接负例和运行输出也可核对。旧 x86 可执行文件确含 GLIBC_2.34 依赖，但图中关于“当前 Ubuntu 20.04、GLIBC 2.31”的异机运行失败，所引用的 `logs/toolchain-current-host.txt` 未随本地材料保留，不能当成本轮实测结果。

04、05 的输入、整数输出、十六进制浮点输出与三种实现的已有原始 JSON 及独立预期一致。但是图片所称 “Fresh QEMU rerun” 及旧说明所称 Ubuntu 20.04 异机重跑，缺少配套的 `logs/qemu-rerun-summary.json`、`logs/qemu-rerun-all.json` 和 `deliverables/实验截图/rerun_qemu.py`。06 中时间为 2026-10-07 的“新一轮 480 次重跑”因此**不能独立核验，不计为新增测试**。

完整 **160 个输入、480 次执行、480 次通过、0 次失败**的结论依据原实验 `artifacts/sysy/summary.json`、`artifacts/sysy/results.csv` 和 `artifacts/sysy/logs/` 中逐次运行记录；公开归档可查 [SysY 汇总](../../evidence/sysy/summary.json)、[480 行运行结果 CSV](../../evidence/sysy/results.csv) 及[总核验记录](../../evidence/combined_validation.json)。结果仅适用于已测输入，不能替代形式化等价证明；QEMU 执行不能用作真实 RISC-V 硬件性能依据。

07、08、10 中 `/home/iodwad/...` 是异机的用户名、工程和工具缓存路径，与当前 Windows/WSL 环境不同。相关工具版本、IR、主机处理状态和后端诊断可由现有源文件核对，这些路径不能直接作为本机命令。逐图视觉检查未发现凭据、Token 或私网 IP；为保留证据原貌，没有修改图片中的路径。

AscendNPU IR 的结果是**主机侧中端变换**：六次处理完成，18/18 项解析与结构核验通过。设备编译虽然记录进程退出码为 0，但同时诊断缺少 `hivmc`，未生成设备对象，也未运行设备程序。没有设备端数值或性能结果。见[主机核验汇总](../../evidence/mlir/verification-summary.json)、[各阶段结果](../../evidence/mlir/ascend-results.json)和[设备后端诊断](../../evidence/mlir/06-full-compile.stderr.txt)。

## 十张输出图

| 编号与图片 | 主要内容 | 用途 | 可公开核查的源记录 |
|---|---|---|---|
| [01](01-toolchain-stages.png) | Clang 14 预处理、编译、汇编、链接及宏展开 | 仅仓库 | [工具链程序](../../src/toolchain/)、[原实验汇总](../../evidence/toolchain/summary.json) |
| [02](02-toolchain-link-and-test.png) | `add_bonus` 符号解析、缺失目标文件的负例、原 60/60 测试 | 仅仓库 | [bonus.c](../../src/toolchain/bonus.c)、[测试结果](../../evidence/toolchain/test_results.json) |
| [03](03-three-implementations.png) | 两例的 SysY、LLVM IR、RISC-V 三种实现及 ELF 目标 | 仅仓库 | [SysY](../../src/sysy/)、[手写 LLVM IR](../../src/llvm/)、[手写 RISC-V](../../src/riscv/)、[源码校验值](../../evidence/sysy/source-sha256.txt) |
| [04](04-control_matrix-rerun.png) | 整数例 `53 1 1 0 2` 与独立预期 | 附录 B 与仓库 | [输入](../../tests/inputs/control_matrix.initial_full.in)、[预期](../../tests/inputs/control_matrix.initial_full.expected.json)、[结果 CSV](../../evidence/sysy/results.csv) |
| [05](05-float_stats-rerun.png) | 浮点例的十六进制输出与独立预期 | 附录 B 与仓库 | [输入](../../tests/inputs/float_stats.fractional.in)、[预期](../../tests/inputs/float_stats.fractional.expected.json)、[结果 CSV](../../evidence/sysy/results.csv) |
| [06](06-qemu-summary.png) | 原实验 480/480 与未独立核验的异机重跑摘录 | 附录 B 与仓库 | [原实验汇总](../../evidence/sysy/summary.json)、[结果 CSV](../../evidence/sysy/results.csv)、[总核验记录](../../evidence/combined_validation.json) |
| [07](07-vecadd-source.png) | 官方 VecAdd 的两次 load、vadd、store 与固定工具版本 | 仅仓库 | [官方 add.mlir](../../src/mlir/official-tool-1.1.0/bishengir/test/Integration/HIVM/VecAdd/add.mlir)、[工具版本](../../evidence/mlir/bishengir-opt-version.stdout.txt) |
| [08](08-memory-plan.png) | A=0、B=32、C=0 字节的 UB 偏移及存储复用 | 仅仓库 | [内存规划 IR](../../evidence/mlir/03-memory.mlir)、[阶段结果](../../evidence/mlir/ascend-results.json) |
| [09](09-sync-and-template.png) | 跨流水同步以及两次 load、一次 add、一次 store 的模板调用 | 仅仓库 | [同步 IR](../../evidence/mlir/04-sync.mlir)、[模板转换 IR](../../evidence/mlir/05-standard.mlir) |
| [10](10-verification-and-backend.png) | 主机结构核验通过与设备后端缺失 | 附录 B 与仓库 | [核验汇总](../../evidence/mlir/verification-summary.json)、[后端诊断](../../evidence/mlir/06-full-compile.stderr.txt)、[阶段结果](../../evidence/mlir/ascend-results.json) |

## 本地原记录定位

- 01：`artifacts/toolchain/clang_O0/` 各阶段 `.command.txt`、`.exit.txt` 及 `main.i`（第 566 行）。
- 02：同目录的 `inspect_main_object_nm.stdout.txt`、`inspect_bonus_object_nm.stdout.txt`、`negative_control_missing_bonus.stderr.txt`、`demo`，以及 `artifacts/toolchain/test_results.json`。
- 03：`artifacts/sysy/bin/` 中六个 ELF。现有 `control_matrix.source` 的 ELF64、RISC-V、flags=0x5 及图示 build-id 可以直接核对；图中 `deliverables/实验截图/bin/` 副本和对应检查日志未保留，不能独立核验该次复制及补执行权限操作。
- 04：`artifacts/sysy/logs/control_matrix.initial_full.{source,llvm,asm}.json`。
- 05：`artifacts/sysy/logs/float_stats.fractional.{source,llvm,asm}.json`。
- 06：`artifacts/sysy/summary.json`、`artifacts/sysy/results.csv`、`artifacts/sysy/logs/`、`artifacts/combined_validation.json`，仅作为原实验的完整结果链。
- 07：`src/mlir/official-tool-1.1.0/bishengir/test/Integration/HIVM/VecAdd/add.mlir` 与 `artifacts/mlir/bishengir-opt-version.stdout.txt`。
- 08：`artifacts/mlir/03-memory.mlir`、`artifacts/mlir/ascend-results.json`。
- 09：`artifacts/mlir/04-sync.mlir`、`artifacts/mlir/05-standard.mlir`。
- 10：`artifacts/mlir/verification-summary.json`、`artifacts/mlir/ascend-results.json`、`artifacts/mlir/06-full-compile.stderr.txt`。

以上逐图完整路径、尺寸和 SHA-256 同时记录于 manifest。缺失的 `logs/` 与 `deliverables/` 材料没有创建链接，也没有编造替代日志。需要重新执行实验时，使用[项目根 README](../../README.md)中的真实构建与验证脚本；图 06 的旧 `rerun_qemu.py` 命令不是本仓库当前可用入口。

## 来源与本地保留材料

官方 AscendNPU IR 源码及其图片摘录不属于本小组原创，来源、版本及许可见 [MLIR 来源说明](../../src/mlir/SOURCES.md)、[LICENSE](../../src/mlir/official-tool-1.1.0/LICENSE) 与 [NOTICE](../../src/mlir/official-tool-1.1.0/NOTICE)。其他第三方源码按仓库的原始许可及归属声明使用。

原目录中的 `一页讲解.pdf` 和 `讲解与截图索引.md` 仅本地保留，没有复制到公开归档：旧说明存在缺失日志对应的未核验断言及已失效的相对路径。本目录 README 和 manifest 给出重新核查后的准确索引；所有本地原材料均保留。
