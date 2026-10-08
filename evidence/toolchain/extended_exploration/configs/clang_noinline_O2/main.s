	.text
	.file	"main_noinline.c"
	.globl	alternating_sum                 # -- Begin function alternating_sum
	.p2align	4, 0x90
	.type	alternating_sum,@function
alternating_sum:                        # @alternating_sum
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	pushq	%r14
	.cfi_def_cfa_offset 24
	pushq	%rbx
	.cfi_def_cfa_offset 32
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	.cfi_offset %rbp, -16
	testl	%edi, %edi
	jle	.LBB0_1
# %bb.3:
	movl	%edi, %r14d
	xorl	%ebx, %ebx
	xorl	%ebp, %ebp
	.p2align	4, 0x90
.LBB0_4:                                # =>This Inner Loop Header: Depth=1
	movl	%ebp, %edi
	callq	scale_and_bias
	movl	%eax, %ecx
	negl	%ecx
	testb	$1, %bpl
	cmovel	%eax, %ecx
	addl	%ecx, %ebx
	addl	$1, %ebp
	cmpl	%ebp, %r14d
	jne	.LBB0_4
	jmp	.LBB0_2
.LBB0_1:
	xorl	%ebx, %ebx
.LBB0_2:
	movl	%ebx, %eax
	popq	%rbx
	.cfi_def_cfa_offset 24
	popq	%r14
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
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
                                        # kill: def $edi killed $edi def $rdi
	leal	(%rdi,%rdi,2), %eax
	addl	$5, %eax
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
	pushq	%r15
	.cfi_def_cfa_offset 24
	pushq	%r14
	.cfi_def_cfa_offset 32
	pushq	%rbx
	.cfi_def_cfa_offset 40
	pushq	%rax
	.cfi_def_cfa_offset 48
	.cfi_offset %rbx, -40
	.cfi_offset %r14, -32
	.cfi_offset %r15, -24
	.cfi_offset %rbp, -16
	leaq	4(%rsp), %rsi
	movl	$.L.str, %edi
	xorl	%eax, %eax
	callq	__isoc99_scanf
	cmpl	$1, %eax
	jne	.LBB2_1
# %bb.2:
	movl	4(%rsp), %r15d
	cmpl	$21, %r15d
	jae	.LBB2_3
# %bb.4:
	xorl	%r14d, %r14d
	movl	$0, %ebp
	testl	%r15d, %r15d
	je	.LBB2_7
# %bb.5:
	xorl	%ebp, %ebp
	xorl	%ebx, %ebx
	.p2align	4, 0x90
.LBB2_6:                                # =>This Inner Loop Header: Depth=1
	movl	%ebx, %edi
	callq	scale_and_bias
	movl	%eax, %ecx
	negl	%ecx
	testb	$1, %bl
	cmovel	%eax, %ecx
	addl	%ecx, %ebp
	addl	$1, %ebx
	cmpl	%ebx, %r15d
	jne	.LBB2_6
.LBB2_7:
	movl	%ebp, %edi
	callq	add_bonus
	movl	4(%rsp), %esi
	movl	$.L.str.3, %edi
	movl	%ebp, %edx
	movl	%eax, %ecx
	xorl	%eax, %eax
	callq	printf
.LBB2_8:
	movl	%r14d, %eax
	addq	$8, %rsp
	.cfi_def_cfa_offset 40
	popq	%rbx
	.cfi_def_cfa_offset 32
	popq	%r14
	.cfi_def_cfa_offset 24
	popq	%r15
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
	retq
.LBB2_1:
	.cfi_def_cfa_offset 48
	movq	stderr(%rip), %rcx
	movl	$.L.str.1, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$1, %r14d
	jmp	.LBB2_8
.LBB2_3:
	movq	stderr(%rip), %rcx
	movl	$.L.str.2, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$2, %r14d
	jmp	.LBB2_8
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
