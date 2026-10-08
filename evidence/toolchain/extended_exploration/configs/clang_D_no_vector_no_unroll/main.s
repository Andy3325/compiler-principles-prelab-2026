	.text
	.file	"main.c"
	.globl	alternating_sum                 # -- Begin function alternating_sum
	.p2align	4, 0x90
	.type	alternating_sum,@function
alternating_sum:                        # @alternating_sum
	.cfi_startproc
# %bb.0:
	xorl	%eax, %eax
	testl	%edi, %edi
	jle	.LBB0_3
# %bb.1:
	movl	$-5, %r8d
	movl	$5, %edx
	xorl	%esi, %esi
	.p2align	4, 0x90
.LBB0_2:                                # =>This Inner Loop Header: Depth=1
	testb	$1, %sil
	movl	%r8d, %ecx
	cmovel	%edx, %ecx
	addl	%ecx, %eax
	addl	$1, %esi
	addl	$-3, %r8d
	addl	$3, %edx
	cmpl	%esi, %edi
	jne	.LBB0_2
.LBB0_3:
	retq
.Lfunc_end0:
	.size	alternating_sum, .Lfunc_end0-alternating_sum
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
	pushq	%rbx
	.cfi_def_cfa_offset 24
	pushq	%rax
	.cfi_def_cfa_offset 32
	.cfi_offset %rbx, -24
	.cfi_offset %rbp, -16
	leaq	4(%rsp), %rsi
	movl	$.L.str, %edi
	xorl	%eax, %eax
	callq	__isoc99_scanf
	cmpl	$1, %eax
	jne	.LBB1_1
# %bb.2:
	movl	4(%rsp), %eax
	cmpl	$21, %eax
	jae	.LBB1_3
# %bb.4:
	xorl	%ebx, %ebx
	movl	$0, %ebp
	testl	%eax, %eax
	je	.LBB1_7
# %bb.5:
	xorl	%ebp, %ebp
	movl	$-5, %ecx
	movl	$5, %edx
	xorl	%esi, %esi
	.p2align	4, 0x90
.LBB1_6:                                # =>This Inner Loop Header: Depth=1
	testb	$1, %sil
	movl	%ecx, %edi
	cmovel	%edx, %edi
	addl	%edi, %ebp
	addl	$1, %esi
	addl	$-3, %ecx
	addl	$3, %edx
	cmpl	%esi, %eax
	jne	.LBB1_6
.LBB1_7:
	movl	%ebp, %edi
	callq	add_bonus
	movl	4(%rsp), %esi
	movl	$.L.str.3, %edi
	movl	%ebp, %edx
	movl	%eax, %ecx
	xorl	%eax, %eax
	callq	printf
.LBB1_8:
	movl	%ebx, %eax
	addq	$8, %rsp
	.cfi_def_cfa_offset 24
	popq	%rbx
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
	retq
.LBB1_1:
	.cfi_def_cfa_offset 32
	movq	stderr(%rip), %rcx
	movl	$.L.str.1, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$1, %ebx
	jmp	.LBB1_8
.LBB1_3:
	movq	stderr(%rip), %rcx
	movl	$.L.str.2, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$2, %ebx
	jmp	.LBB1_8
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
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
