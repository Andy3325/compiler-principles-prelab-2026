# 基础任务 2 实验分析与报告整合材料

## 已实际完成的范围

在 Ubuntu-22.04 / WSL2 上，以 LLVM/Clang 14.0.0、RISC-V GCC 11.4.0、QEMU user 6.2.0 完成两个示例的三个独立实现。目标统一为 little-endian ELF64、RV64GC、LP64D。`readelf -h -A` 中三类对象均为 RISC-V，Flags=0x5（RVC、double-float ABI）。运行库由相同目标选项构建。执行方式为 `qemu-riscv64 <静态可执行文件>`，无需设备或目标动态库路径；不是真实 RISC-V 硬件实测。

最终构建与执行日志：`artifacts/sysy/build.log`。100 个整数用例与 60 个浮点用例，每例执行 source/llvm/asm 三份程序，**480/480 执行通过，0 失败，全部退出状态为 0**。浮点容差虽然定义为绝对误差不超过 `1e-6+2e-6*|expected|`，实际 180 次浮点执行的三个输出值均与 binary32 oracle 数值精确一致。最终结论来自 `summary.json` 和 480 份 `logs/*.json`，不是仅凭三者彼此输出一致。

另有 3 个有意注入错误的汇编变体（短路、余数、浮点转换各一项），**3/3 被 oracle 拒绝**。这是测试灵敏度实验，独立保存在 `mutations/summary.json`；不能把它们记为最终实现的失败，或捏造为开发中偶遇的 bug。

## 设计理由与覆盖

`control_matrix` 读入 `n stop gate divisor` 和 6 个增量。二维数组初值为 `{{1,2},{-3,4,5}}`，第一行未写的第三个元素必须为 0。读入增量后，它调用 `fold` 对前 n 个位置作带位置权重的前缀求和；遇到零执行 continue，遇到非零 stop 执行 break。每个位置权重为一开始的序号，因此把二维索引、增量顺序或循环更新位置弄错会改变输出，而非被普通求和掩盖。输出第一个整数在前缀和上加全局 bias=7 和局部同名 bias=3，以观察作用域。

额外输出 `calls tag q r`：tick 每次增加全局 calls，两个含 &&/|| 的条件影响 tag，末尾 q/r 是第二个数组元素对 divisor 的有符号商和余数。仅检测布尔结果无法证明短路正确；副作用计数使不应执行的 RHS 调用变得可见。gate=0 时两处 RHS 均被跳过，calls=0、tag=6；gate非零且末元素非负时 calls=1；gate非零且末元素负时 calls=2。第一元素正负改变 tag 最低位，故还验证 RHS 返回值的比较。

`float_stats` 将 float 数组元素 x 与 scale 相乘，加整数索引 offset，仅累加正结果，最后加 0.25，输出浮点和、向零截断的整数及除以 n+1 的归一化值。它同时检验 float 常量、数组、比较、四则中的乘加除、int-to-float、float-to-int、float 形参和返回值，而无需再加入一批结构相同的例子。

先验覆盖表详见 `report/coverage.md`。<= 对应 fold 的 `i <= n-1`，>= 对应 sum_positive 的 `n >= i+1`；<、>、==、!=、!、&&、|| 均在两个程序中出现。一元负用于负初值，一元正 `return +x` 映射为原值返回，没有必要虚构一条“取正”机器指令。

## LLVM IR：SSA、phi 与地址

整数示例另外定义无参 void 函数 `separator()` 统一输出空格，以覆盖用户定义的无参、无返回值函数及空 return；它的 IR 是 `define void`/`ret void`，汇编以16字节栈帧保存 ra，再调用运行库 putch。此处无须为同一种结构再建额外示例。

文件 `src/llvm/control_matrix.ll`、`float_stats.ll` 是手写 LLVM 14 typed-pointer IR。它们先经 llvm-as 和 opt -verify 检查，再经 llc 输出目标文件。Clang 自动输出仅存于 `artifacts/sysy/reference/`，不计入手写工作量。

fold 中循环头用两条 phi 显式合并 i 与 sum：入口值为 0，回边来自 step。body 在取元素后递增 i，因此 continue 也推进索引；step 的 phi 从 body 的 continue 边取旧 sum，从 accum 边取新 sum。break 直接指向 exit，返回循环头当前 sum，使 stop 所在元素不参与累加。循环上界改写为 n-1，n=0 时 limit=-1，首次 `icmp sle 0,-1` 为 false，仍正确执行零次。

短路不使用一个 eager `and/or` 指令把已经计算完的两个值相连，而是把 RHS 放入只在需要时可达的基本块。第一个 && 跳过 tick 时，sc.first.merge 的 phi 取0；执行 RHS 时取 zext 后的比较值。|| 的左侧为真直接到 sc.add.two，左侧为假才检查末元素和嵌套 &&，sc.second.merge 再合并标签。LLVM 的 phi 按到达的前驱边选值，不是运行时“同时计算所有候选”。

`cell([3 x i32]* a, i32 row, i32 col)` 的 GEP 先按整行 [3 x i32] 跨越 row，再按 i32 跨越 col，地址等价于 `base + 4*(3*row+col)`。main 的完整数组是 `[2 x [3 x i32]]`，访问需先加0跳过外层指针，再提供行、列两个索引。`inbounds` 依赖有效域中的合法下标，未声称提供越界检测。指针和索引用 i64，元素与 SysY int 仍为 i32。

浮点 IR 对每个乘、加、除分别使用 fmul/fadd/fdiv，不设置 fast 或 contract 标记；用 sitofp 转换整数索引及分母，用 fptosi 实现截断。循环 sum 是 float phi，条件是有序比较 `fcmp ogt`；NaN 不在有效域中，不据此宣称完整异常浮点支持。

## 手写汇编与 ABI

RISC-V integer 参数使用 a0–a7，返回值使用 a0；数组参数在 RV64 下为64位地址，整数数据仍以 lw/sw 和 addw/mulw/divw/remw 操作。LW 会符号扩展，word 指令产生的32位结果同样符号扩展到 XLEN，与本实验 i32 传参一致。fold 跨 cell 调用仍需保存数组指针、n-1、stop、索引、累加值，故使用 s 寄存器并在64字节栈帧中保存/恢复它们及 ra。整数 main 用128字节栈帧，其中低24字节存局部二维数组；运行库调用不能破坏 s 寄存器中的标签、除数或待输出结果。

LP64D 的整数和浮点参数寄存器分开计数。`affine(float x,float scale,int offset)` 分别使用 fa0、fa1、a0，而不是把 offset 放到 a2；`sum_positive(float* a,int n,float scale)` 分别使用 a0、a1、fa0。float 返回在 fa0；该寄存器在调用 putch/putint 后不可假设还保留原值，因此 main 把浮点结果与归一化值保存在 fs1/fs2，且通过 fsd/fld 保存整个64位被调用者保存寄存器。

float 函数栈帧分别64与80字节，所有帧均为16的倍数，满足标准 ABI 的128-bit栈对齐。静态初值由成对 ld 复制，已将 float_initial 明确声明为8字节对齐，避免依赖链接地址巧合。浮点每步使用 .s 指令；没有 fmadd.s。`fcvt.w.s ..., rtz` 明确选择向零截断，默认浮点舍入模式 RNE 对0.75会给出1，与 SysY 截断语义不同。

实际 `float_stats.asm.undefined.txt` 含 getfloat/getint/putch/putfloat/putint，链接 map 开头明确显示 `libsylib.a(sylib.o)` 满足程序的 getint 引用，然后该运行库再由 libc 解析 scanf/printf。这是运行库真实参与链接的证据，不是仅声明几个同名符号。

## 独立预期结果与代表用例

整数 oracle 用数学式 `10 + Σ(k+1)*a[k]`，求和范围是首个非零 stop 之前的前缀，不复用 LLVM CFG 或汇编循环。calls/tag 由 gate、首末元素的真值公式直接得出。商用绝对值整除后补符号，余数由 `a-q*b` 得到，避免误用 Python 的负数向下取整。5个手工算例断言先检查 oracle，再运行固定种子 `24115602412565` 的生成用例。浮点 oracle 使用 Python struct 对每个基本运算显式舍入为 binary32，不能拿默认 binary64 的长表达式直接当标准答案。

下面输入是完整整数输入；输出按“加偏置后的和、tick次数、标签、商、余数”排列。每一行 source/llvm/asm 均一致且退出0。

| 意图 | 完整输入 | 实际输出 |
|---|---|---|
| 零次循环、gate=0跳过副作用 | `0 40 0 3 0 0 0 0 0 0` | `10 0 6 0 2` |
| 6次范围、部分初始化为0、continue | `6 40 1 3 0 0 0 0 0 0` | `53 1 1 0 2` |
| 第一个元素立即break | `6 1 1 -3 0 0 0 0 0 0` | `10 1 1 0 2` |
| 第四个位置break，负gate视为真 | `6 -3 -1 3 0 0 0 0 0 0` | `15 1 1 0 2` |
| 两次tick、末元素变为-1 | `6 40 1 3 0 0 0 0 0 -6` | `17 2 3 0 2` |
| 负数除余语义 | `6 40 0 3 0 -7 0 0 0 0` | `39 0 6 -1 -2` |

浮点例 `n=1, scale=1, a=[0.5]` 的输入文件采用精确十六进制数；实际输出 `0x1.8p-1 0 0x1.8p-2`，即0.75、0、0.375。`n=3, scale=0.1, a=[0.1,0.2,0.3]` 按 binary32 取整后的结果是3.309999942779541与0.8274999856948853，实际输出 `0x1.a7ae14p+1 3 0x1.a7ae14p-1`；不能简单声称精确实数3.31在二进制32位中可表示。

3个变异反例：删除第一个短路跳转，使零gate算例实际变成 `10 1 7 0 2`；把 remw 换为 divw，使负被除数算例实际变成 `39 0 6 -1 -1`；把 rtz 改为 rne，使0.75截断算例实际变成 `0x1.8p-1 1 0x1.8p-2`。三者退出码仍0，说明仅检查“程序成功运行”远远不够。

## 真实问题、修正及局限

1. 官方规范入口和USTC副本返回登录HTML。检查文件内容而非只看.pdf文件名后，保留失败响应，并从固定提交镜像取得9页语言定义与4页运行库文档。运行库及规范来源、哈希和许可见 `runtime/README.md`，不是将镜像误写成课程直接提供。
2. 对照完整 SysY 文法时发现 C 允许的带括号布尔子条件并非此文法的 `PrimaryExp -> '(' Exp ')'`，因为 Exp 仅是 AddExp。原写法 RHS 外层条件括号已去掉，依赖 && 比 || 优先的规则。Clang以C编译不会发现这种偏差，这正是源码必须再核对 SysY 规范的原因。语义和oracle不变，修正后全套已重新构建运行。
3. 上游头文件含计时全局的暂定定义；构建显式使用-fcommon保持原文件。上游scanf忽略返回值的警告实际出现在build.log，本实验输入全部满足有效域，不把这些警告描述为本实验修复了上游输入鲁棒性。
4. 汇编自审发现用ld复制初值应保证8字节对齐，已将.balign4改为.balign8并重新运行。此前没有观测到崩溃，属于消除潜在依赖的审查修正，不能写成“定位了运行崩溃”。
5. 成员分工按2026-10-08的报告版本更新：朱泽帅主要负责完整编译工具链实验及LLVM IR编程；张宸笛主要负责RISC-V汇编编程；AscendNPU IR / MLIR进阶实验及SysY设计、运行库链接、三种实现的构建与语义等价验证、结果分析和报告工作由两人共同完成。未实现完整SysY编译器；源程序运行采用Clang对其C兼容子集编译，IR和汇编则独立手写、独立构建。未测非法输入、整数溢出、除零、NaN/Inf或张量扩展；QEMU不用于真实硬件性能比较。

## 复现入口

PowerShell：

```powershell
wsl -d Ubuntu-22.04 -- bash '<PROJECT>/scripts/sysy_build_test.sh'
```

构建脚本会重建6个可执行文件，检查IR，保存链接map/ELF属性/未定义符号/反汇编，生成160份输入与预期结果并运行480次最终实现，以及3次独立变异检查。`source-sha256.txt` 绑定最终源码与oracle；所有原始执行记录可按结果CSV中的 program/case/implementation 回查。

## 2026-10-04 定点机制深化（不改变原始实验）

本轮只替换正文重复规则、长 IR 代码框、验证路径图与零散文件索引，加入两个有语义作用的机制图；已有源码、480次执行数据、3个变异日志不修改。当时报告所用的成员分工于2026-10-08按小组最新口径更新，姓名为朱泽帅、张宸笛。

### CFG 与 SSA 的核验依据

脚本 scripts/generate_sysy_mechanism_figures.py 从 src/llvm/control_matrix.ll 提取函数和真实终结指令，得到 fold 的7个块与9条边。图采用人工排版，但块名、边、phi前驱及来值可用性逐项断言，不是凭源程序画出的假想CFG。完整解析输出见 artifacts/mechanism/sysy-mechanism-analysis.json，来源哈希和图哈希见 sysy-figure-manifest.json。

边的全集为 entry→loop、loop→body/exit、body→step/check.break、check.break→exit/accum、accum→step、step→loop。continue 是 body→step，break 是 check.break→exit，back edge 是 step→loop；不存在名为 continue 或 break 的额外块。

- %i 的前驱和值是 (entry,0) 与 (step,%next)。%next 定义于 body；body 支配 step，因此每一条进入 step 的路径都已完成索引递增。
- %sum 的前驱和值是 (entry,0) 与 (step,%sum.next)。每次进入回边前，step 的 phi 已产生一个确定的下一轮累计值。
- %sum.next 的前驱和值是 (body,%sum) 与 (accum,%added)。继续路径的旧 %sum 来自支配 body 的 loop；累加路径的 %added 在 accum 内先于终结指令定义。LLVM将phi来值的使用归于对应的入边，所以 added 不必支配整个step。
- loop支配exit；exit直接ret %sum。正常退出取所有已完成迭代之和，break退出取不含当前stop元素的和，零次循环取入口0。因两类出口都使用同一已定义的SSA值，不需要新加exit phi。
- accum不支配step，step位于accum的支配边界；手写phi将两条路径的逻辑源变量版本合流。本轮没有运行mem2reg或宣称这些phi由某个SSA构造pass插入。

真实LLVM分析日志：sysy-verify.txt 中退出0，sysy-dominators.txt 中退出0；domtree的fold片段为 entry→loop，loop直接支配body/exit，body直接支配step/check.break，check.break直接支配accum。文中列出的支配关系与日志一致。图右面只截取main首个&&的三个真实块，明确省略之后||，不能把它当作整个main的CFG。

短路的实质是控制判断先决定是否发生tick的可观察写入。先call再select的错误中，tick副作用先于选择发生，select无法撤销写入；这是一条单线程执行语义约束，不是内存屏障意义的多核happens-before。

### 实际调用现场及栈槽语义

affine为叶函数，真实指令仅fmul.s、fcvt.s.w、fadd.s、ret，无sp修改、无call、无任何保存槽。参数x/scale/offset分别为fa0/fa1/a0；返回fa0。特别地，第三个源参数offset使用第一个整数参数寄存器，整数与硬浮点寄存器独立分配。

sum_positive是真正的非叶函数。入口addi sp,sp,-64。以新sp为基准：
56..63保存ra，48..55保存s0，40..47保存s1，32..39保存s2，24..31保存fs0，16..23保存fs1，0..15未使用；没有局部数组或寄存器溢出槽。所有保存都有匹配恢复；64=4×16满足栈对齐。图中的8字节格按真实sd/fsd宽度，而非按float本身4字节绘制。

跨call affine活跃的当前值为s0=array、s1=n、s2=i、fs0=scale、fs1=sum。栈槽保存的是调用者进入sum_positive前的旧寄存器值，不是每轮sum的副本。affine实际不修改s/fs；当前循环值依此约定在寄存器中保留，返回值v覆盖fa0。t0中本轮数组地址在call前已用完，ft0则被affine用于int→float临时量，不能依赖其跨call保存。sum_positive退出时先把当前fs1复制到fa0，再恢复调用者fs1等寄存器，最后恢复ra与sp并返回。

32位整数机制由最终control_matrix.S中的lw/sw、addiw/addw/mulw/divw/remw支撑；本源码没有subw，递减界限实际使用addiw立即数-1。LW的符号扩展与W指令的32位计算结果扩展维持SysY int在RV64寄存器中的表示；64位地址add必须保留完整指针。有效域排除语言有符号溢出，不把机器低32位行为推广为语言溢出定义。

新增一手ISA资料已于2026-10-04实际浏览，正文使用riscv-isa引用，由总报告统一维护：
- RISC-V RV64I 2.1: https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html
- RISC-V M 2.0: https://docs.riscv.org/reference/isa/v20260120/unpriv/m-st-ext.html
原有LLVM14 LangRef与RISC-V psABI引用继续使用，不改变版本与平台结论。

### 测试辨识力的边界

新表直接读取旧mutations/summary.json：
1. eager_and使零gate例从正确10 0 6 0 2变为10 1 7 0 2；calls与tag均揭示了本不该发生的RHS。
2. wrong_remainder将remw替成divw，-5/3的余数位置输出-1而非-2。
3. round_to_nearest将rtz替成rne，0.75输出整数1而非0，两个浮点输出仍然正确。
三种变体都退出0，说明“进程运行成功”不是语义正确性的判据。二维数组现有测试覆盖六个位置及位置权重，但没有实际注入wrong row stride，因此该mutation的检出状态明确为未检验，不杜撰第四个负对照。

### 新命令与复现范围

PowerShell生成命令：
<USER_HOME>\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts/generate_sysy_mechanism_figures.py

脚本内仅运行以下两个LLVM分析命令（路径使用WSL挂载路径）：
opt-14 -verify -disable-output src/llvm/control_matrix.ll
opt-14 -enable-new-pm=0 -analyze -domtree src/llvm/control_matrix.ll

新测试执行数=0，新程序编译数=0，输入文件前后SHA-256一致。输出图为 report/figures/llvm-fold-cfg.pdf/.png 与 riscv-call-frame.pdf/.png，均为Matplotlib生成的机制线图，PDF保存可缩放矢量文字与线条，PNG用于检查。图脚本没有修改任何原始数据或运行日志。
