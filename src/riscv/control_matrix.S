# HAND-WRITTEN GNU RISC-V RV64GC / LP64D, independently assembled.
# All stack frames are multiples of 16. All used s registers are preserved.
    .option nopic
    .section .data
    .balign 4
    .globl calls
calls: .word 0
    .globl bias
bias: .word 7
    .section .rodata
    .balign 4
initial: .word 1, 2, 0, -3, 4, 5
    .text
    .balign 2
    .globl tick
    .type tick,@function
tick:
    la t0, calls
    lw t1, 0(t0)
    addiw t1, t1, 1
    sw t1, 0(t0)
    ret
    .size tick,.-tick

    .globl cell
    .type cell,@function
cell:
    li t0, 3
    mulw t0, a1, t0
    addw t0, t0, a2
    slli t0, t0, 2             # byte offset = 4 * (3*row + col)
    add t0, a0, t0
    lw a0, 0(t0)
    ret
    .size cell,.-cell

    .globl fold
    .type fold,@function
fold:
    addi sp, sp, -64
    sd ra, 56(sp)
    sd s0, 48(sp)
    sd s1, 40(sp)
    sd s2, 32(sp)
    sd s3, 24(sp)
    sd s4, 16(sp)
    sd s5, 8(sp)
    mv s0, a0                  # array pointer (64 bit)
    addiw s1, a1, -1           # inclusive limit = n - 1
    mv s2, a2                  # stop
    li s3, 0                   # i
    li s4, 0                   # sum
.Lfold_loop:
    bgt s3, s1, .Lfold_exit
    mv a0, s0
    li t0, 3
    divw a1, s3, t0
    remw a2, s3, t0
    call cell
    mv s5, a0
    addiw s3, s3, 1
    beqz s5, .Lfold_loop       # continue precedes break, including stop=0
    beq s5, s2, .Lfold_exit
    mulw t0, s5, s3
    addw s4, s4, t0
    j .Lfold_loop
.Lfold_exit:
    mv a0, s4
    ld s5, 8(sp)
    ld s4, 16(sp)
    ld s3, 24(sp)
    ld s2, 32(sp)
    ld s1, 40(sp)
    ld s0, 48(sp)
    ld ra, 56(sp)
    addi sp, sp, 64
    ret
    .size fold,.-fold

    .globl separator
    .type separator,@function
separator:
    addi sp, sp, -16
    sd ra, 8(sp)
    li a0, 32
    call putch
    ld ra, 8(sp)
    addi sp, sp, 16
    ret
    .size separator,.-separator

    .globl main
    .type main,@function
main:
    addi sp, sp, -128
    sd ra, 120(sp)
    sd s0, 112(sp)
    sd s1, 104(sp)
    sd s2, 96(sp)
    sd s3, 88(sp)
    sd s4, 80(sp)
    sd s5, 72(sp)
    sd s6, 64(sp)
    sd s7, 56(sp)
    la t0, initial
    li t1, 0
.Linitialize:
    slli t2, t1, 2
    add t3, t0, t2
    lw t4, 0(t3)
    add t3, sp, t2
    sw t4, 0(t3)
    addiw t1, t1, 1
    li t2, 6
    blt t1, t2, .Linitialize
    call getint
    mv s0, a0
    call getint
    mv s1, a0
    call getint
    mv s2, a0
    call getint
    mv s3, a0
    li s4, 0
.Lread:
    call getint
    slli t0, s4, 2
    add t0, sp, t0
    lw t1, 0(t0)
    addw t1, t1, a0
    sw t1, 0(t0)
    addiw s4, s4, 1
    li t0, 6
    blt s4, t0, .Lread
    li s5, 0
    beqz s2, .Lsc_or           # skip tick when left operand of && is false
    lw a0, 0(sp)
    call tick
    blez a0, .Lsc_or
    addiw s5, s5, 1
.Lsc_or:
    beqz s2, .Lsc_add2         # skip the entire right operand of ||
    lw a0, 20(sp)
    bgez a0, .Lsc_not          # skip nested && call when last >= 0
    call tick
    beqz a0, .Lsc_not
.Lsc_add2:
    addiw s5, s5, 2
.Lsc_not:
    bnez s2, .Lcompute
    addiw s5, s5, 4
.Lcompute:
    mv a0, sp
    mv a1, s0
    mv a2, s1
    call fold
    la t0, bias
    lw t0, 0(t0)
    addw a0, a0, t0
    addiw a0, a0, 3            # inner-scope bias; global bias remains 7
    call putint
    call separator
    la t0, calls
    lw a0, 0(t0)
    call putint
    call separator
    mv a0, s5
    call putint
    call separator
    lw t0, 4(sp)
    divw s6, t0, s3            # signed division, truncates toward zero
    remw s7, t0, s3
    mv a0, s6
    call putint
    call separator
    mv a0, s7
    call putint
    li a0, 10
    call putch
    li a0, 0
    ld s7, 56(sp)
    ld s6, 64(sp)
    ld s5, 72(sp)
    ld s4, 80(sp)
    ld s3, 88(sp)
    ld s2, 96(sp)
    ld s1, 104(sp)
    ld s0, 112(sp)
    ld ra, 120(sp)
    addi sp, sp, 128
    ret
    .size main,.-main
    .section .note.GNU-stack,"",@progbits
