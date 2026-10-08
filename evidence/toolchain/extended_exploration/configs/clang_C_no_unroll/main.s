	.text
	.file	"main.c"
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4                               # -- Begin function alternating_sum
.LCPI0_0:
	.long	0                               # 0x0
	.long	1                               # 0x1
	.long	2                               # 0x2
	.long	3                               # 0x3
.LCPI0_1:
	.long	5                               # 0x5
	.long	5                               # 0x5
	.long	5                               # 0x5
	.long	5                               # 0x5
.LCPI0_2:
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
.LCPI0_3:
	.long	4                               # 0x4
	.long	4                               # 0x4
	.long	4                               # 0x4
	.long	4                               # 0x4
	.text
	.globl	alternating_sum
	.p2align	4, 0x90
	.type	alternating_sum,@function
alternating_sum:                        # @alternating_sum
	.cfi_startproc
# %bb.0:
	xorl	%eax, %eax
	testl	%edi, %edi
	jle	.LBB0_7
# %bb.1:
	movl	$0, %r8d
	cmpl	$4, %edi
	jb	.LBB0_5
# %bb.2:
	movl	%edi, %r8d
	andl	$-4, %r8d
	movdqa	.LCPI0_0(%rip), %xmm1           # xmm1 = [0,1,2,3]
	pxor	%xmm0, %xmm0
	movdqa	.LCPI0_1(%rip), %xmm2           # xmm2 = [5,5,5,5]
	movdqa	.LCPI0_2(%rip), %xmm3           # xmm3 = [4294967291,4294967291,4294967291,4294967291]
	movdqa	.LCPI0_3(%rip), %xmm4           # xmm4 = [4,4,4,4]
	movl	%r8d, %eax
	.p2align	4, 0x90
.LBB0_3:                                # =>This Inner Loop Header: Depth=1
	movdqa	%xmm1, %xmm5
	paddd	%xmm1, %xmm5
	paddd	%xmm1, %xmm5
	movdqa	%xmm3, %xmm6
	psubd	%xmm5, %xmm6
	paddd	%xmm2, %xmm5
	movdqa	%xmm1, %xmm7
	pslld	$31, %xmm7
	psrad	$31, %xmm7
	pand	%xmm7, %xmm6
	pandn	%xmm5, %xmm7
	por	%xmm6, %xmm7
	paddd	%xmm7, %xmm0
	paddd	%xmm4, %xmm1
	addl	$-4, %eax
	jne	.LBB0_3
# %bb.4:
	pshufd	$238, %xmm0, %xmm1              # xmm1 = xmm0[2,3,2,3]
	paddd	%xmm0, %xmm1
	pshufd	$85, %xmm1, %xmm0               # xmm0 = xmm1[1,1,1,1]
	paddd	%xmm1, %xmm0
	movd	%xmm0, %eax
	cmpl	%edi, %r8d
	je	.LBB0_7
.LBB0_5:
	leal	(%r8,%r8,2), %esi
	movl	$-5, %ecx
	subl	%esi, %ecx
	leal	(%r8,%r8,2), %esi
	addl	$5, %esi
	.p2align	4, 0x90
.LBB0_6:                                # =>This Inner Loop Header: Depth=1
	testb	$1, %r8b
	movl	%ecx, %edx
	cmovel	%esi, %edx
	addl	%edx, %eax
	addl	$1, %r8d
	addl	$-3, %ecx
	addl	$3, %esi
	cmpl	%r8d, %edi
	jne	.LBB0_6
.LBB0_7:
	retq
.Lfunc_end0:
	.size	alternating_sum, .Lfunc_end0-alternating_sum
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4                               # -- Begin function main
.LCPI1_0:
	.long	0                               # 0x0
	.long	1                               # 0x1
	.long	2                               # 0x2
	.long	3                               # 0x3
.LCPI1_1:
	.long	5                               # 0x5
	.long	5                               # 0x5
	.long	5                               # 0x5
	.long	5                               # 0x5
.LCPI1_2:
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
.LCPI1_3:
	.long	4                               # 0x4
	.long	4                               # 0x4
	.long	4                               # 0x4
	.long	4                               # 0x4
	.text
	.globl	main
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
	je	.LBB1_11
# %bb.5:
	xorl	%ebp, %ebp
	movl	$0, %ecx
	cmpl	$4, %eax
	jb	.LBB1_9
# %bb.6:
	movl	%eax, %ecx
	andl	$-4, %ecx
	movdqa	.LCPI1_0(%rip), %xmm1           # xmm1 = [0,1,2,3]
	pxor	%xmm0, %xmm0
	movdqa	.LCPI1_1(%rip), %xmm2           # xmm2 = [5,5,5,5]
	movdqa	.LCPI1_2(%rip), %xmm3           # xmm3 = [4294967291,4294967291,4294967291,4294967291]
	movdqa	.LCPI1_3(%rip), %xmm4           # xmm4 = [4,4,4,4]
	movl	%ecx, %edx
	.p2align	4, 0x90
.LBB1_7:                                # =>This Inner Loop Header: Depth=1
	movdqa	%xmm1, %xmm5
	paddd	%xmm1, %xmm5
	paddd	%xmm1, %xmm5
	movdqa	%xmm3, %xmm6
	psubd	%xmm5, %xmm6
	paddd	%xmm2, %xmm5
	movdqa	%xmm1, %xmm7
	pslld	$31, %xmm7
	psrad	$31, %xmm7
	pand	%xmm7, %xmm6
	pandn	%xmm5, %xmm7
	por	%xmm6, %xmm7
	paddd	%xmm7, %xmm0
	paddd	%xmm4, %xmm1
	addl	$-4, %edx
	jne	.LBB1_7
# %bb.8:
	pshufd	$238, %xmm0, %xmm1              # xmm1 = xmm0[2,3,2,3]
	paddd	%xmm0, %xmm1
	pshufd	$85, %xmm1, %xmm0               # xmm0 = xmm1[1,1,1,1]
	paddd	%xmm1, %xmm0
	movd	%xmm0, %ebp
	cmpl	%ecx, %eax
	je	.LBB1_11
.LBB1_9:
	leal	(%rcx,%rcx,2), %esi
	movl	$-5, %edx
	subl	%esi, %edx
	leal	(%rcx,%rcx,2), %esi
	addl	$5, %esi
	.p2align	4, 0x90
.LBB1_10:                               # =>This Inner Loop Header: Depth=1
	testb	$1, %cl
	movl	%edx, %edi
	cmovel	%esi, %edi
	addl	%edi, %ebp
	addl	$1, %ecx
	addl	$-3, %edx
	addl	$3, %esi
	cmpl	%ecx, %eax
	jne	.LBB1_10
.LBB1_11:
	movl	%ebp, %edi
	callq	add_bonus
	movl	4(%rsp), %esi
	movl	$.L.str.3, %edi
	movl	%ebp, %edx
	movl	%eax, %ecx
	xorl	%eax, %eax
	callq	printf
.LBB1_12:
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
	jmp	.LBB1_12
.LBB1_3:
	movq	stderr(%rip), %rcx
	movl	$.L.str.2, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$2, %ebx
	jmp	.LBB1_12
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
