# 基础任务 1：可核对的实验笔记（供共同报告整合）

本节所有路径均相对于作业根目录 `<PROJECT>`。原实验实际完成时间为 2026-10-03（北京时间）；准确时间见 `artifacts/toolchain/summary.json`。2026-10-04 新增的机制诊断独立保存在 `artifacts/toolchain/mechanism/`，不更改原实验记录。

## 1. 问题、设计与独立预期

问题是：同一个有循环、条件与函数调用的 C 程序，经过预处理、编译、汇编、链接后形成什么；`-O2` 与 `-g` 分别改变哪些产物？

本实验只使用一个两翻译单元程序。`src/toolchain/main.c` 定义局部辅助函数 `scale_and_bias`、循环函数 `alternating_sum` 和入口 `main`；`bonus.c` 定义独立编译的 `add_bonus`；`demo.h` 定义宏和函数声明。两个翻译单元提供可观察的链接依赖，避免用多个相似程序堆积工作量。

程序接受一个可用 C `int` 表示的整数，计算域为 `0 <= n <= 20`：令第 i 项为 `3*i+5`，偶数下标相加、奇数下标相减，再调用另一翻译单元的函数加 11。该域中没有除零、越界和有符号整数溢出。非整数 `abc` 返回 1，范围外的 -1 和 21 返回 2；这些错误出口也纳入验证。没有宣称支持任意超长或超范围整数文本。

预期不由编译结果生成。相邻两项 `(6j+5)-(6j+8)=-3`，故 n=2k 时 sum=-3k，n=2k+1 时 sum=-3k+(6k+5)=3k+5，最终值为 sum+11。脚本在任何编译命令前保存 `artifacts/toolchain/expectations.json` 及时间戳。有效输入与结果为：

| n | alternating | adjusted |
|---:|---:|---:|
| 0 | 0 | 11 |
| 1 | 5 | 16 |
| 2 | -3 | 8 |
| 5 | 11 | 22 |
| 6 | -9 | 2 |
| 10 | -15 | -4 |
| 20 | -30 | -19 |

这七个有效用例覆盖零次、一/两次、奇偶次和上边界循环，加上三个错误用例，每个构建 10 例。各次执行均保存 stdin、stdout、stderr 与进程退出码，不能把预期错误退出 1/2 误算为实验失败。

## 2. 环境与受控因素

环境为 Windows 上的 Ubuntu 22.04 WSL2，Linux 内核 `6.6.87.2-microsoft-standard-WSL2`，原生 x86-64 执行（本节不是 QEMU 执行）。工具为 GCC 11.4.0、Clang 14.0.0、LLVM assembler 14.0.0、GNU Binutils 2.38、Python 3.10.12。原始工具输出在 `artifacts/toolchain/environment/`。

Windows `D:\...` 对应 WSL `/mnt/d/...`，源码和最终产物均直接保留在作业目录。共同固定选项为 `-std=c11 -Wall -Wextra -Werror -march=x86-64 -mtune=generic -fno-pie`，链接用 `-no-pie`，未启用 LTO。每个编译器分别比较 `-O0`、`-O2`、`-O2 -g`，同一编译器的相邻比较只改变指定优化或调试选项。

注意这台机器的 GCC 驱动还带发行版默认安全选项，例如 `-fstack-protector-strong -fstack-clash-protection -fcf-protection`（`gcc_O2/inspect_driver_dry_run.stderr.txt:12`）。`gcc_O2/inspect_preprocessor_macros.stdout.txt:111` 存在 `_FORTIFY_SOURCE 2`，O0 宏表没有该定义；Clang O2 宏表也没有该定义。GCC 的 O2 预处理输出因系统头文件的条件展开而明显变大，并观察到 `__printf_chk`；这也是优化选项作用于整个驱动流程的实际现象。因此跨编译器数值仅用于描述产物，不能被解释为仅由优化算法造成的公平性能比较。

`inspect_driver_dry_run` 是 `-###` 的驱动计划，明确不计为实际构建；真正执行的各阶段命令与退出码另存在 `01_preprocess_*` 至 `04_link`。Clang 的 IR 另用 `-S -emit-llvm` 导出，并全部通过 `llvm-as-14` 组装验证。

## 3. 复现入口与阶段产物

PowerShell 运行：

```powershell
wsl -d Ubuntu-22.04 -- bash '<PROJECT>/scripts/toolchain_run.sh'
```

脚本 `scripts/toolchain_experiment.py` 不下载或安装工具；重复执行会重建本实验自己的 `artifacts/toolchain/` 文件。每次构建保存 `main.i/bonus.i`、`main.s/bonus.s`、`main.o/bonus.o`、可执行文件 `demo`、`link.map` 和检查输出。六组目录为 `gcc_O0`、`gcc_O2`、`gcc_O2_g`、`clang_O0`、`clang_O2`、`clang_O2_g`。Clang 三组还保存 `main.ll/bonus.ll` 与 `.bc`。

四阶段命令的简写（`CFLAGS` 为上述固定选项与当前优化/调试选项；真实完整命令在对应 `.command.txt`）：

```sh
clang-14 $CFLAGS -E src/toolchain/main.c -o main.i
clang-14 $CFLAGS -S main.i -o main.s
clang-14 -c main.s -o main.o
# bonus.c 同样独立执行前三步，然后一起链接：
clang-14 -no-pie main.o bonus.o -Wl,-Map,link.map -o demo
```

这些步骤由编译器驱动调用前端/汇编器/链接器；不是说每个外部阶段都等同于单一理论阶段。预处理后的 token 经词法/语法分析及类型、声明等语义检查，前端形成 IR；优化改变 IR，后端选择指令、分配寄存器并生成目标汇编，汇编器编码为带符号与重定位的目标文件，最后由链接器组合文件和运行库。

保存的 AST 片段 `artifacts/toolchain/frontend_ast_alternating_sum.stdout.txt:6-50` 直接出现带 `int` 类型的 `VarDecl`、`ForStmt`、`CallExpr`、`IfStmt`、`CompoundAssignOperator` 与隐式类型转换，帮助定位语法结构和类型信息。AST 的内存地址是本次进程地址，复现时可能变化，没有把这些地址作为稳定标识符。

## 4. 预处理、IR 与汇编的真实对应

`clang_O0/main.i:8` 开始插入 `stdio.h` 内容，`main.i:558-560` 保留头文件里的函数声明；`main.i:564-566` 将宏展开为 `return 3 * x + (12 - 7);`，`main.i:590` 将上界展开为 20。源代码注释已消失；行标记保留文件/行号来源。重要区别是，预处理仍保留 `(12 - 7)`，没有将它计算为 5。

`clang_O0/main.ll:72-78` 中辅助函数已是 `mul ... 3` 与 `add ... 5`，`clang_O0/main.s:70-71` 对应 `imull $3`、`addl $5`。因此常量表达式折叠在 O0 已观察到，不能将它归功于 O2。

在 O0 IR，`alternating_sum` 的局部变量用 `alloca/load/store` 保存（`main.ll:18-68`），循环入口、条件、正负分支、递增和退出由基本块与 `br` 连接，`main.ll:36` 调用 `scale_and_bias`。O0 汇编中 `main.s:18-48` 的比较、跳转、加减与回边对应源程序的循环/条件；`main.s:24` 仍实际调用辅助函数。

O2 后 `scale_and_bias` 的定义和调用在 Clang IR 中都消失（定义/调用计数 1→0），而 `3*i+5` 的计算融合到循环中；GCC、Clang 的 O2 对象符号表也都不再有该静态函数。由代码体进入调用者及符号消失共同支持“本例发生了内联”，不是仅凭文件变小推断。

Clang O2 的整个 `main.ll` 中 `alloca` 计数从 9 减至 1，`phi` 从 0 增至 16（包括 `main` 与循环函数的所有定义）。保留的 `alloca` 用于 `scanf` 需要地址的局部输入变量；其他循环状态更多由 SSA 值承接。O0 也属于合法 LLVM IR：SSA 值仍唯一，只是可变源变量大量通过内存表达。

## 5. 目标文件、重定位与运行库链接

以下以 Clang O0 为易读主例：

- `inspect_main_object_readelf.stdout.txt:8` 的类型为 `REL`，`.text` 存指令，`.rodata.str1.1` 存格式/错误字符串，`.symtab` 和 `.strtab` 存符号及名字；`.rela.text` 存尚待解析的地址修补信息（节表见 23-34 行）。本例局部变量主要在栈上，对象没有专门的全局可写数据定义，不能凭常见 ELF 图示臆造本例的 `.data` 变量。
- 符号表在同一文件 69-77 行列出内部 `scale_and_bias`、全局 `alternating_sum/main`，以及 `UND` 的 `scanf/fputs/add_bonus/printf` 等引用。`.rela.text` 的 54、56 行分别有 `R_X86_64_PLT32 add_bonus - 4` 与 `printf - 4`，说明尚需链接器根据最终符号位置修正 PC 相对调用。
- `link.map:187-192` 显示 main.o 与 bonus.o 被放入 `.text`，`add_bonus` 获得地址 `0x401290`；最终符号表 `inspect_executable_readelf.stdout.txt:141` 也在 section 14 定义该符号。另一翻译单元的函数由本次静态链接解析。
- 为验证该依赖，故意省去 bonus.o 后链接器返回 1 并报告 `undefined reference to add_bonus`，证据为 `negative_control_missing_bonus.stderr.txt:1-3`。这是预先设计的负对照，未计入 60 次程序执行通过数。
- 链接 map 的 42-66 行显示 crt 启动文件、GCC 支持文件及 libc；最终 ELF 的 `DT_NEEDED` 依赖 `libc.so.6`（readelf 输出 62 行）。`printf` 等动态符号仍为 UND，并在 `.rela.plt` 保留 `R_X86_64_JUMP_SLOT`（95-97 行），由运行时动态链接器绑定共享 libc 的实现。因此“链接成功”不等于“把所有 libc 代码复制到了可执行文件”。

可执行文件的 ELF 类型由 `REL` 变为 `EXEC`，入口 `0x401060` 及程序头已存在（最终 readelf 输出 8-18 行）；入口首先是启动代码而非直接把 `main` 地址当作 ELF 入口。

## 6. 优化和调试对照的实际结果

数据直接来自 `artifacts/toolchain/metrics.csv`（以字节计）。`.text` 是链接后整个可执行文件的该节，包括启动代码；指令条数是 `objdump` 对 main.o 代码节的静态反汇编行数，包含填充 nop，不是动态执行次数。

| 变体 | main.o 字节 | 可执行文件字节 | 可执行 `.text` 字节 | `.debug*` 字节合计 | main.o 静态指令条数 |
|---|---:|---:|---:|---:|---:|
| GCC O0 | 2504 | 16248 | 581 | 0 | 97 |
| GCC O2 | 2544 | 16216 | 520 | 0 | 66 |
| GCC O2 -g | 10888 | 21080 | 520 | 4239 | 66 |
| Clang O0 | 2160 | 16152 | 575 | 0 | 84 |
| Clang O2 | 3624 | 16120 | 868 | 0 | 154 |
| Clang O2 -g | 7368 | 19136 | 868 | 2315 | 154 |

GCC O2 的循环（`gcc_O2/main.s:17-25`）以 `term=5` 起步，每轮 `addl $3` 更新项，避免每轮调用和显式乘 3；原正负分支由 `testb $1` 与 `cmove` 实现。这支持内联、归纳变量改写和条件选择的观察。本例 GCC O2 汇编没有向量循环，不能把 Clang 的向量化结论套给 GCC。

Clang O2 在 `alternating_sum` 中实际生成 `<4 x i32>` 向量、两组累加器以及一次处理八个下标的循环（`clang_O2/main.ll:29-56`），用 `select` 选择正负项，`llvm.vector.reduce.add.v4i32` 做归约；53-81 行还保留剩余元素的标量路径。汇编 `main.s:70-100` 中的 `paddd/pand/pcmpeqd/pshufd` 与这些向量操作对应。IR 元数据 `main.ll:217` 也明确标记 `llvm.loop.isvectorized`。

Clang 还将 `alternating_sum` 内联到 main：O2 的 main 中没有对它的 call，存在另一套归约/尾部循环（`main.ll:91-183`）；外部可调用的 `alternating_sum` 定义仍保留。main 已知 `n<=20`，其向量主体进一步出现按范围选择的常量向量（`main.ll:148`），因此不能将 main 的控制流直接等同于原始逐项循环。增加的向量路径与保留的函数体解释了为何本例 Clang O2 `.text` 比 O0 大；静态产物不能据此推断快慢。

`add_bonus` 在 O2 仍有声明与 call（`clang_O2/main.ll:174,188`），因为它处在独立翻译单元，当前单元编译时没有函数定义，且未开启 LTO。此次未发生跨翻译单元内联。

对于 `-g`，GCC O2 与 O2-g 的 `.text` SHA256 都为 `b8e7a7f14d4434715b37db60119f6ff3f29a42754316553aa27dd41052861739`；Clang 两者都为 `52930e2adcc12fa27d9fb091972b584d7c143fed235d8eeb0f0568b819f90133`。因此本例中调试选项没有改变链接后 `.text` 字节；文件变大对应新增 `.debug_info/.debug_line/...` 等段及相关元数据，不能把整个增量都等同于 `.debug*` 字节之和，更不能外推为所有程序加 `-g` 都绝无代码变化。真实原始字节保存在各目录 `executable.text.bin`。

## 7. 验证结论与限制

`summary.json` 和 `test_results.json` 记录六个构建共 60 次执行，60 次输出/错误输出/退出码三者均符合独立预期，失败 0。O0/O2/O2-g 在所测有效域与错误出口中行为一致。另有一个预期失败的缺失符号链接负对照，和六份 Clang IR 模块（main/bonus × 三组）通过 `llvm-as-14`。独立核验脚本 `scripts/toolchain_audit.py` 逐一核对原始输入/输出/退出码与汇总，核对实际文件大小、源代码哈希、代码段哈希、调试对照及 IR 组装日志，结果保存在 `artifacts/toolchain/audit.json`；统一入口脚本自动执行该核验。

本节没有测执行时间、能耗或真实硬件性能；文件大小、代码节大小及静态指令数都是结构证据。编译器版本、发行版默认选项、链接方式会影响具体结果；重新生成的调试文件大小还可能随路径变化。最终交付以源文件哈希、完整命令、原始日志和 JSON/CSV 为准。主报告建议保留一张 6 行表及关键 IR/汇编片段，将其余证据放入工程，避免重复粘贴整个源码。

## 8. 2026-10-04 机制深化：独立新诊断及复现

新增入口为 `scripts/toolchain_mechanism.py`，在 PowerShell 中运行：

```powershell
wsl -d Ubuntu-22.04 -- python3 '<PROJECT>/scripts/toolchain_mechanism.py'
```

脚本只把新编译产物与证据写到 `artifacts/toolchain/mechanism/`，不调用任何测试程序。原程序、原三个脚本和原工具链全部产物共 996 个文件，在运行前后逐个 SHA-256 核对一致。原测试仍是 60/60，新增测试执行次数是 0。`summary.json` 和 `protected_before.json/protected_after.json` 可核对这一范围。此处的 996 是被保护文件数，不是测试用例数。

仍使用 Ubuntu Clang `14.0.0-1ubuntu1.1`，目标 x86_64-pc-linux-gnu。新 IR 命令匹配原 `clang_O2/05_emit_ir_main.command.txt`，新汇编命令匹配原 `clang_O2/02_compile_main.command.txt`：共同编译选项 `-std=c11 -Wall -Wextra -Werror -march=x86-64 -mtune=generic -fno-pie -O2` 不变，只更换输出路径并添加以下诊断/记录选项：

```text
-Rpass=loop-vectorize
-Rpass-missed=loop-vectorize
-Rpass-analysis=loop-vectorize
-fsave-optimization-record=yaml
-foptimization-record-passes=loop-vectorize|loop-unroll|inline
-foptimization-record-file=<新目录中的 ir.opt.yaml 或 asm.opt.yaml>
```

实际完整命令、工作目录对应脚本、标准输出、标准错误、退出状态逐条保存在新目录的 `*.command.txt/*.stdout.txt/*.stderr.txt/*.exit.txt` 及 `commands.json` 中。没有把手写摘要当作原始 remark。选项依据 Clang 14 官方使用手册与 LLVM 14 向量化文档，实际 `clang-14 --help` 输出也已保存。

为连接“归约识别前”与“向量化后”，另在相同编译选项上实际使用：

```text
-mllvm -print-before=loop-vectorize
-mllvm -print-after=loop-vectorize
-mllvm -filter-print-funcs=alternating_sum
```

这是实际 O2 编译过程中 `LoopVectorizePass` 的诊断快照，保存在 `loop_vectorize_trace.stderr.txt`；不是自行拼接或独立调用一串猜测的优化 pass。最终 IR 保存为 `main.trace.ll`，单独验证的 remarks IR 也通过 `llvm-as-14`。

### 8.1 原始 remarks 及所在函数

`emit_ir_remarks.stderr.txt:1-5` 实际包含：

```text
remark: vectorized loop (vectorization width: 4, interleaved count: 2)
remark: the cost-model indicates that interleaving is not beneficial
remark: vectorized loop (vectorization width: 4, interleaved count: 1)
```

三条源位置均为 `src/toolchain/main.c:13:5`，因此不能仅用源行区分。完整 YAML 的 `Function` 字段提供上下文：

| 原始证据 | Function | Pass / Name | 观察 |
|---|---|---|---|
| `ir.opt.yaml:1-25` | alternating_sum | inline / Inlined | scale_and_bias 已内联。 |
| `ir.opt.yaml:147-172` | main | inline / Inlined | alternating_sum 已内联到 main。 |
| `ir.opt.yaml:174-185` | alternating_sum | loop-vectorize / Vectorized | VF=4，IC=2。 |
| `ir.opt.yaml:186-193` | main | loop-vectorize / InterleavingNotBeneficial | 明确报告该现场增加交错无收益。 |
| `ir.opt.yaml:194-205` | main | loop-vectorize / Vectorized | VF=4，IC=1。 |
| `ir.opt.yaml:206-215` | main | loop-unroll / FullyUnrolled | UnrollCount=5。 |

`observed_remarks.json` 是从 YAML 自动提取的 VF/IC/Function 小结。没有 `loop-vectorize` 的 Missed 记录；这只表示本次记录没有这一类诊断，不代表所有可能优化已执行。YAML 中的 `inline/NoDefinition` 是另一 pass 的真实 missed 记录，其中 `add_bonus` 的定义不可见，与未开启 LTO 的跨单元边界一致。

### 8.2 为什么“有依赖”仍能向量化

源循环中的 `sum` 依赖上一迭代结果，`i` 也由前一迭代增加一得到；不能把本例说成“无 loop-carried dependence”。O0 IR 的变量以栈槽表达，单看它不足以说明向量器最终接收的形态。`loop_vectorize_trace.stderr.txt:18-30` 中真实的 pass 前状态是：

```llvm
8:
  %9 = phi i32 [ %17, %8 ], [ 0, %3 ]
  %10 = phi i32 [ %18, %8 ], [ 0, %3 ]
  ; %11/%12 form +(3*i+5), %15 forms -(3*i+5)
  %16 = select i1 %14, i32 %12, i32 %15
  %17 = add i32 %16, %9
  %18 = add nuw nsw i32 %10, 1
```

该摘录只去掉位置元数据，并用注释略去中间纯运算；完整版本未删改保留在原始 trace。归约环是 `%9 -> %17 -> %9`，其初值为 0；每一项 `%16` 仅由当前索引 `%10` 决定，不依赖部分和。另一个环 `%10 -> %18 -> %10` 是归纳变量。辅助函数内联后，loop 内没有外部调用或可观察副作用，正负分支先变成 `select`，因此可以先计算多项再合并累计和。

这里解释的是整数加法归约的可识别结构。LLVM 14 官方“Reductions”说明这种跨迭代 sum 会被识别并改为向量累计、退出时再归约；“If Conversion”说明分支可转为单条指令流。本例同时有 pass 前标量 phi 环、成功 remark、pass 后向量 phi/归约，足以支持“被向量器作为归约处理”的结论，但没有打开 LLVM 内部调试版去追踪识别器的每个分支或声称验证其通用算法。

正确性域必须保留：本程序主入口限制 n<=20，所有计算均远离 i32 溢出。LLVM IR 中没有 `nsw/nuw` 的整数 `add` 是模 2^32 运算；本例重新分组的结果与域内数学整数求和一致。不能据此宣称 C 的有符号溢出有定义，也不能把整数归约的分组规则照搬到要求逐步舍入的任意浮点归约。

### 8.3 VF、IC、lane、横向归约与 scalar remainder

对独立函数 `alternating_sum`：pass 后快照 `loop_vectorize_trace.stderr.txt:49-77` 中有两个 `<4 x i32>` 累加器 `%10/%11`、四通道索引 `%12`，并从 `%12+4` 得到第二组索引。这直接对应 VF=4、IC=2。

令 `t(i)` 为符号已由奇偶选择确定的 `3*i+5`。向量迭代 k 中，lane j（j=0..3）分别把 `t(8k+j)` 和 `t(8k+4+j)` 累入两组累计器，每个向量循环共覆盖八次源迭代。最终原始 O2 IR 的第二组常量 17 是后续简化 `3*(i+4)+5` 的结果；两组索引的奇偶相同，因为相差 4。循环退出先把两组累计器按 lane 相加，`llvm.vector.reduce.add.v4i32` 再对这四个 i32 做横向加法并返回一个 i32；不是生成四个线程，也不是逐 lane 输出四个答案。

pass 后快照第 46-47 行实际是 `urem n,8` 与 `n-remainder`，最终原始 O2 IR `clang_O2/main.ll:26` 已简化成 `and n,-8`。向量主路仅处理八整倍数的前缀：n<8 则全走标量路；n>=8 则先归约向量部分，再从 m=8*floor(n/8) 及其部分和启动标量尾路。尾部从 m 累到 n-1，没有丢项。本例未见尾部再次向量化，不把 LLVM 支持 epilogue vectorization 误说成此处执行过。

`main` 是不同现场。内联后主程序对 n 的检查提供 0..20 范围；VF=4、IC=1 的向量批次最多五个。YAML 实际的 `FullyUnrolled/5` 与原始 O2 IR `main.ll:122-150` 的 switch/常量向量/归约对应：向量批次的不同累计结果已常量化，仍有按 n%4 处理的标量尾路（`main.ll:153-170`）。外部可调用的独立函数定义仍存在，不能将 main 的四项阈值与独立函数的八项阈值混为一谈，也不能把两类展开都称作同一次 unroll pass。

### 8.4 新旧证据的一致性与代码大小边界

开启诊断会保留 `!dbg` / `.loc` 等位置信息，因此 `main.remarks.ll`、`main.remarks.s`、`main.trace.ll` 和原文本的 SHA-256 不同。脚本没有隐瞒这一点，`summary.json` 的三个完整文本比对项均为 false。另有两个更精确的核验：

1. 新旧 LLVM 函数体去掉 metadata attachment 后逐行相同（`function_bodies_ignoring_metadata.diff` 为空）。这项检查不声称所有元数据都没有语义，只比较明确说明过的代码体范围。
2. 新汇编实际组装后的 main.o `.text` 与原 main.o `.text` 字节相同，SHA-256 都是 `0eaaf6cfca895fb88b5b278a12e77b87713271cef9af68c9b0f79728e6f3ca73`。原对象只被读取，objcopy 明确写到新目录副本，不覆盖原文件。

这使新 remarks、pass 边界快照能与原 O2 的结构分析相连，同时保留原完整 60/60 测试与文件大小表。机器码相同不等于本轮新增测试通过，本轮执行测试数仍是零。

Clang O2 代码增大不能只写“向量指令更长”。实际新增/保留结构包括：向量主体、两组累计与横向归约、向量入口判断、标量尾部、main 内联后的展开/分派以及独立函数副本；这些都占静态空间。原始链接后 `.text` 575→868 B、main.o 静态指令 84→154 与这些结构扩展一致。由于未做逐 pass 消融，不能把 293 B 增量全部唯一归于 loop-vectorize；没有时间测量，不能推出加速或减速。

GCC 的配置差异另有直接证据，不能停留于泛泛的“成本模型不同”。新脚本实际运行与原实验相同参数的：

```sh
gcc -std=c11 -Wall -Wextra -Werror -march=x86-64 -mtune=generic -fno-pie -O2 -Q --help=optimizers
```

`gcc_O2_optimizer_options.stdout.txt:222,232` 显示 `-ftree-loop-vectorize`、`-ftree-slp-vectorize` 都是 `[disabled]`；252 行的 `-fvect-cost-model` 值为 `cheap`，但这不能说明未启用的向量 pass 已实际尝试并拒绝了本循环。GCC 11.4 版本化官方文档也明确这两项由 `-O3` 默认开启。故当前 GCC 11.4 O2 与 Clang 14 O2 的首要已知差异是启用的优化集合，而非对同一循环作了相反的成本判断。本轮未构建 O3、不改变旧 O2 数据，也不预测只打开某一个选项后会得到什么代码。

原 GCC 产物仍为归纳变量每轮加 3、`cmove`、没有所见向量循环及 581→520 B 等指标。当前还记录了通用 x86-64 target、Clang `+sse/+sse2` target features、GCC 默认安全参数和 O2 的 `_FORTIFY_SOURCE` 头文件分支。官方文档描述 vector factor / interleave factor 的代价选择，本例也获得 main 的“交错无收益”定性 remark，但没有对应的向量化数值成本，完整 GCC/Clang pipeline 也未逐项对齐。因此不将所有大小差异归于某个未经测量的成本模型，也不宣称 Clang 更优。YAML 中的 inline Cost/Threshold 是内联模型值，不能挪用为 loop-vectorize 的成本。

### 8.5 官方技术来源与主报告引用键

访问日期 2026-10-04；仅使用 LLVM/GCC 官方版本化文档：

- 建议新增 `llvmvector14`：LLVM Project, *Auto-Vectorization in LLVM*, LLVM 14.0.0，<https://releases.llvm.org/14.0.0/docs/Vectorizers.html>。使用 Diagnostics、Reductions、If Conversion、Partial unrolling、Epilogue Vectorization 的机制边界；没有把文档性能图当成本例数据。
- 建议新增 `clangremarks14`：LLVM Project, *Clang Compiler User's Manual*, Clang 14.0.0，<https://releases.llvm.org/14.0.0/tools/clang/docs/UsersManual.html#options-to-emit-optimization-reports>。用于 diagnostics、YAML record 与 pass filter 的选项依据。
- 建议新增 `gccopt11`：GNU Project, *Optimize Options*, GCC 11.4.0，<https://gcc.gnu.org/onlinedocs/gcc-11.4.0/gcc/Optimize-Options.html>。`-O3`、`-ftree-loop-vectorize`、`-ftree-slp-vectorize` 条目与本机 `-Q` 输出互证。
- 复用已有 `llvm`：*LLVM Language Reference Manual*, LLVM 14.0.0，<https://releases.llvm.org/14.0.0/docs/LangRef.html#llvm-vector-reduce-add-intrinsic>。章节正文标题为 `llvm.vector.reduce.add.*`，说明整数向量横向加法返回同元素类型标量；正文不依赖锚点别名才能找到该节。

主报告 `toolchain.tex` 已用紧凑归约片段及 VF/IC 两行表替换旧完整命令块与重复观察，将完整命令/哈希/行号留在本笔记和机制证据目录。参考文献由主任务统一整合，本子任务未编辑 references。
