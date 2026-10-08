# 第三方来源与再分发范围

## SysY 运行库

`runtime/sylib.c`、`runtime/sylib.h` 原样来自 https://github.com/yuhuifishash/SysY ，提交 `d3639373ddc894dd0d20b307d0bf1fe92b6f685b`，原路径 `lib/`。MIT 原文保留于 `runtime/LICENSE.upstream`；来源、SHA-256 与接口差异见 `runtime/README.md`。这些文件不是学生原创，也不声称是课程平台提供的指定版本。

SysY2022 规范全文没有纳入上述 MIT 声明。规范 PDF / 文本只在本地保留，不上传；原始入口与镜像提交 `7e7778d1546b850dd720ef30fff528c18737d183` 见 `runtime/README.md`，需要时从来源取得并遵守原权利条件。

## AscendNPU IR / LLVM

上游 https://github.com/Ascend/AscendNPU-IR ：

- `src/mlir/official/`：master 快照 `37c6ebc33d1789500014e6a7b2b62164b3cb566b`。
- `src/mlir/official-tool-1.1.0/`：匹配实际工具的快照 `428ab8fdab46a879c7349caba4cde705bc8c9bb6`。
- `evidence/mechanism/vecadd-sources/`：同版本源码及文档副本，同目录附 LICENSE / NOTICE。
- `evidence/mlir/`：生成 IR、诊断与来源记录，同目录附 LICENSE / NOTICE。

各源码子集保留原 Apache-2.0 LICENSE、NOTICE（含 LLVM Exceptions 等第三方说明）与版权头；固定 URL 和哈希见 `src/mlir/SOURCES.md` 及 evidence 中的 manifest。原源码未改；公开日志副本只归一化本机路径。

官方 wheel 不随仓库分发，脚本从固定 PyPI URL 下载并校验 SHA-256。CANN、hivmc、设备运行时与硬件不包含在仓库中。

## 报告配图与格式

机制图和结构图由工程脚本生成，数据与 provenance 保留。fig3.png、fig6.png、fig7.png 为报告作者提供的替换配图，不声称来自 Ascend / LLVM 上游。报告格式由已提供模板适配，原来源注释保留；课程原模板与课件未加入仓库。

`materials/experiment-output/` 的十张PNG为既有命令/文件摘录的排版图，按原字节归档。其中的官方VecAdd与IR片段保留第三方归属，继续适用上文Ascend来源与许可。截图中的历史异机过程有部分缺失日志，准确核验范围见同目录README。当前图6改用原工程生成的 `vecadd-lifetime.pdf`，原 `fig6.png` 保留但不再用于报告；修正只涉及无依据的GM范围、UB半开区间和操作顺序标注。

`report/figures/nku.png` 未发现再分发授权，只在本地保留；含该校徽的原 PDF 不上传。公开构建在临时副本省略图片，不改本地报告。

## 本项目内容

实验程序、手写 LLVM IR / RISC-V 汇编、验证脚本及分析报告与第三方源码分开标识。本次不为整个工程授予统一许可证，第三方文件继续适用各自原许可和版权声明。
