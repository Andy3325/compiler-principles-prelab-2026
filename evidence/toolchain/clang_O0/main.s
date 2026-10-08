	.text
	.file	"main.c"
	.globl	alternating_sum                 # -- Begin function alternating_sum
	.p2align	4, 0x90
	.type	alternating_sum,@function
alternating_sum:                        # @alternating_sum
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movl	%edi, -4(%rbp)
	movl	$0, -8(%rbp)
	movl	$0, -12(%rbp)
.LBB0_1:                                # =>This Inner Loop Header: Depth=1
	movl	-12(%rbp), %eax
	cmpl	-4(%rbp), %eax
	jge	.LBB0_7
# %bb.2:                                #   in Loop: Header=BB0_1 Depth=1
	movl	-12(%rbp), %edi
	callq	scale_and_bias
	movl	%eax, -16(%rbp)
	movl	-12(%rbp), %eax
	movl	$2, %ecx
	cltd
	idivl	%ecx
	cmpl	$0, %edx
	jne	.LBB0_4
# %bb.3:                                #   in Loop: Header=BB0_1 Depth=1
	movl	-16(%rbp), %eax
	addl	-8(%rbp), %eax
	movl	%eax, -8(%rbp)
	jmp	.LBB0_5
.LBB0_4:                                #   in Loop: Header=BB0_1 Depth=1
	movl	-16(%rbp), %ecx
	movl	-8(%rbp), %eax
	subl	%ecx, %eax
	movl	%eax, -8(%rbp)
.LBB0_5:                                #   in Loop: Header=BB0_1 Depth=1
	jmp	.LBB0_6
.LBB0_6:                                #   in Loop: Header=BB0_1 Depth=1
	movl	-12(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -12(%rbp)
	jmp	.LBB0_1
.LBB0_7:
	movl	-8(%rbp), %eax
	addq	$16, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end0:
	.size	alternating_sum, .Lfunc_end0-alternating_sum
	.cfi_endproc
                                        # -- End function
	.p2align	4, 0x90                         # -- Begin function scale_and_bias
	.type	scale_and_bias,@function
scale_and_bias:                         # @scale_and_bias
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movl	%edi, -4(%rbp)
	imull	$3, -4(%rbp), %eax
	addl	$5, %eax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end1:
	.size	scale_and_bias, .Lfunc_end1-scale_and_bias
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movl	$0, -4(%rbp)
	movabsq	$.L.str, %rdi
	leaq	-8(%rbp), %rsi
	movb	$0, %al
	callq	__isoc99_scanf
	cmpl	$1, %eax
	je	.LBB2_2
# %bb.1:
	movq	stderr, %rsi
	movabsq	$.L.str.1, %rdi
	callq	fputs
	movl	$1, -4(%rbp)
	jmp	.LBB2_6
.LBB2_2:
	cmpl	$0, -8(%rbp)
	jl	.LBB2_4
# %bb.3:
	cmpl	$20, -8(%rbp)
	jle	.LBB2_5
.LBB2_4:
	movq	stderr, %rsi
	movabsq	$.L.str.2, %rdi
	callq	fputs
	movl	$2, -4(%rbp)
	jmp	.LBB2_6
.LBB2_5:
	movl	-8(%rbp), %edi
	callq	alternating_sum
	movl	%eax, -12(%rbp)
	movl	-12(%rbp), %edi
	callq	add_bonus
	movl	%eax, -16(%rbp)
	movl	-8(%rbp), %esi
	movl	-12(%rbp), %edx
	movl	-16(%rbp), %ecx
	movabsq	$.L.str.3, %rdi
	movb	$0, %al
	callq	printf
	movl	$0, -4(%rbp)
.LBB2_6:
	movl	-4(%rbp), %eax
	addq	$16, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	.L.str,@object                  # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"%d"
	.size	.L.str, 3

	.type	.L.str.1,@object                # @.str.1
.L.str.1:
	.asciz	"expected one integer\n"
	.size	.L.str.1, 22

	.type	.L.str.2,@object                # @.str.2
.L.str.2:
	.asciz	"n must be in [0, 20]\n"
	.size	.L.str.2, 22

	.type	.L.str.3,@object                # @.str.3
.L.str.3:
	.asciz	"n=%d alternating=%d adjusted=%d\n"
	.size	.L.str.3, 33

	.ident	"Ubuntu clang version 14.0.0-1ubuntu1.1"
	.section	".note.GNU-stack","",@progbits
	.addrsig
	.addrsig_sym alternating_sum
	.addrsig_sym scale_and_bias
	.addrsig_sym __isoc99_scanf
	.addrsig_sym fputs
	.addrsig_sym add_bonus
	.addrsig_sym printf
	.addrsig_sym stderr
