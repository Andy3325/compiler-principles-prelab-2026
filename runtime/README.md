# SysY 运行库与语言定义来源

## 采用的真实运行库

本地课程目录未找到 `sylib.c`、`sylib.h` 或运行库归档。采用公开 RISC-V SysY 项目保留的 SysY 运行库源文件，**不是本实验自行编写的 stdio 包装**，也不声称它是从课程平台取得的指定二进制版本。

- 仓库：<https://github.com/yuhuifishash/SysY>
- 固定提交：`d3639373ddc894dd0d20b307d0bf1fe92b6f685b`
- 原文件：`lib/sylib.c`、`lib/sylib.h`
- 原始地址：<https://raw.githubusercontent.com/yuhuifishash/SysY/d3639373ddc894dd0d20b307d0bf1fe92b6f685b/lib/sylib.c>
- 许可：该仓库 MIT LICENSE 已原样保留为 `LICENSE.upstream`，包括上游署名。这里的 `sylib.c/h` 未改动。
- sylib.c SHA-256：`dd334643a5dcd61d1825eae977e838adc25ec5142538c24e969828e6e48da926`
- sylib.h SHA-256：`1c3da9a394977976eb4cd2547e5fc900172579e5050ffc5352e991cf283c480d`
- 获取并验证：2026-10-03，北京时间。

原始头文件把计时全局变量写成暂定定义。因此源码与运行库均以 `-fcommon` 编译，保留上游文件不变。运行库以 `riscv64-linux-gnu-gcc -march=rv64gc -mabi=lp64d` 交叉编译成静态归档，再与三份独立实现链接。`artifacts/sysy/*.map` 可追踪引用到 `libsylib.a(sylib.o)`；`*.undefined.txt` 保存链接前的运行库未定义符号。

已按 SysY2022 运行库规范核对本实验使用的 `getint():int`、`getfloat():float`、`putint(int):void`、`putfloat(float):void`、`putch(int):void` 接口。该源码的 `getfloat` 采用 scanf `%a`，`putfloat` 采用 printf `%a`，实际浮点输出为十六进制；规范文档示例用十进制展示。测试按数值比较并明确保留这种文本格式差异，不能宣称逐字输出等同文档示例。计时析构函数每次在 stderr 输出 `TOTAL: 0H-0M-0S-0us`，这是未调用计时接口的累计值，**不是本程序耗时测量**。

## 规范文件

- 原始官方语言定义入口：<https://gitlab.eduxiji.net/nscscc/compiler2022/-/blob/master/SysY2022语言定义-V1.pdf>
- 原始官方运行库入口：<https://gitlab.eduxiji.net/nscscc/compiler2022/-/blob/master/SysY2022运行时库-V1.pdf>
- 本次官方项目入口和 USTC 保存副本入口均重定向至登录页。对 USTC 的实际下载返回 HTML，已以正确扩展名保留于 `artifacts/sysy/language-download-login.html`、`runtime-download-login.html`；未冒充 PDF。
- 最终从保存原文的公开仓库镜像取得 PDF：<https://github.com/william-dan/SysY2022-ARMv7-Compiler/tree/7e7778d1546b850dd720ef30fff528c18737d183>
- 固定提交：`7e7778d1546b850dd720ef30fff528c18737d183`，分别为根目录 `SysY2022语言定义-V1.pdf`（9页）与 `SysY2022运行时库-V1.pdf`（4页），本地改为英文文件名。
- 这两个 PDF 为竞赛规范原文的镜像副本，不是镜像作者自定语言；原文、PDF 文字抽取、来源及 SHA-256 均保留，未对规范文档另行声称 MIT 授权。

语言定义明确支持 32-bit int/float、多维数组、隐式类型转换及短路。其文法将 `Exp` 与 `Cond` 分开，`PrimaryExp -> '(' Exp ')'` 不提供任意带括号的条件表达式；因此源码使用 `gate == 0 || a[1][2] < 0 && tick(a[1][2]) != 0`，依赖规定的优先级，不写 C 中常见但该文法没有的 `(... && ...)` 子条件括号。

课程总体要求提及“张量类型”，但未附具体定义。本工程没有伪造张量扩展语法；多维数组按 SysY2022 行优先数组实现，不宣称其等于课程自定张量类型。

## 其他一手规范

- LLVM 14 Language Reference：<https://releases.llvm.org/14.0.0/docs/LangRef.html>（phi、GEP、sdiv/srem、sitofp/fptosi）。
- RISC-V psABI：<https://riscv-non-isa.github.io/riscv-elf-psabi-doc/>（整数/硬浮点传参、16-byte栈对齐、callee-saved寄存器、NaN-boxing）。
