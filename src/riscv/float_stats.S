# HAND-WRITTEN RV64GC / LP64D. fa0/fa1 carry named float arguments.
# fs0/fs1 are saved as full 64-bit FP registers; single results are NaN-boxed.
    .option nopic
    .section .rodata
    .balign 8                 # initialization uses aligned 64-bit ld pairs
float_initial: .float 1.0, -2.0, 0.5, 0.0
shift: .float 0.25
    .text
    .balign 2
    .globl affine
    .type affine,@function
affine:
    fmul.s fa0, fa0, fa1
    fcvt.s.w ft0, a0
    fadd.s fa0, fa0, ft0       # separate multiply then add, no fmadd.s
    ret
    .size affine,.-affine

    .globl sum_positive
    .type sum_positive,@function
sum_positive:
    addi sp, sp, -64
    sd ra, 56(sp)
    sd s0, 48(sp)
    sd s1, 40(sp)
    sd s2, 32(sp)
    fsd fs0, 24(sp)
    fsd fs1, 16(sp)
    mv s0, a0                  # a[] pointer in a0
    mv s1, a1                  # integer n in a1
    li s2, 0
    fmv.s fs0, fa0             # scale is first float argument
    fmv.w.x fs1, zero          # sum = +0.0f
.Lfloat_loop:
    addiw t0, s2, 1
    blt s1, t0, .Lfloat_exit  # n >= i+1 is the source loop condition
    slli t0, s2, 2
    add t0, s0, t0
    flw fa0, 0(t0)
    fmv.s fa1, fs0
    mv a0, s2                  # affine's int offset uses a0, not a2
    call affine
    fmv.w.x ft0, zero
    flt.s t0, ft0, fa0
    beqz t0, .Lfloat_step
    fadd.s fs1, fs1, fa0
.Lfloat_step:
    addiw s2, s2, 1
    j .Lfloat_loop
.Lfloat_exit:
    fmv.s fa0, fs1
    fld fs1, 16(sp)
    fld fs0, 24(sp)
    ld s2, 32(sp)
    ld s1, 40(sp)
    ld s0, 48(sp)
    ld ra, 56(sp)
    addi sp, sp, 64
    ret
    .size sum_positive,.-sum_positive

    .globl main
    .type main,@function
main:
    addi sp, sp, -80
    sd ra, 72(sp)
    sd s0, 64(sp)
    sd s1, 56(sp)
    sd s2, 48(sp)
    fsd fs0, 40(sp)
    fsd fs1, 32(sp)
    fsd fs2, 24(sp)
    la t0, float_initial
    ld t1, 0(t0)
    ld t2, 8(t0)
    sd t1, 0(sp)
    sd t2, 8(sp)
    call getint
    mv s0, a0
    call getfloat
    fmv.s fs0, fa0
    li s1, 0
.Lfloat_read:
    bge s1, s0, .Lfloat_compute
    call getfloat
    slli t0, s1, 2
    add t0, sp, t0
    fsw fa0, 0(t0)
    addiw s1, s1, 1
    j .Lfloat_read
.Lfloat_compute:
    mv a0, sp
    mv a1, s0
    fmv.s fa0, fs0
    call sum_positive
    la t0, shift
    flw ft0, 0(t0)
    fadd.s fs1, fa0, ft0
    fcvt.w.s s2, fs1, rtz      # SysY float->int truncates; default RNE is wrong
    addiw t0, s0, 1
    fcvt.s.w ft0, t0
    fdiv.s fs2, fs1, ft0
    fmv.s fa0, fs1
    call putfloat
    li a0, 32
    call putch
    mv a0, s2
    call putint
    li a0, 32
    call putch
    fmv.s fa0, fs2
    call putfloat
    li a0, 10
    call putch
    li a0, 0
    fld fs2, 24(sp)
    fld fs1, 32(sp)
    fld fs0, 40(sp)
    ld s2, 48(sp)
    ld s1, 56(sp)
    ld s0, 64(sp)
    ld ra, 72(sp)
    addi sp, sp, 80
    ret
    .size main,.-main
    .section .note.GNU-stack,"",@progbits
