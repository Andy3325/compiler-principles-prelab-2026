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
	.long	17                              # 0x11
	.long	17                              # 0x11
	.long	17                              # 0x11
	.long	17                              # 0x11
.LCPI0_3:
	.long	1                               # 0x1
	.long	1                               # 0x1
	.long	1                               # 0x1
	.long	1                               # 0x1
.LCPI0_4:
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
	.long	4294967291                      # 0xfffffffb
.LCPI0_5:
	.long	4294967279                      # 0xffffffef
	.long	4294967279                      # 0xffffffef
	.long	4294967279                      # 0xffffffef
	.long	4294967279                      # 0xffffffef
.LCPI0_6:
	.long	8                               # 0x8
	.long	8                               # 0x8
	.long	8                               # 0x8
	.long	8                               # 0x8
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
	cmpl	$8, %edi
	jb	.LBB0_5
# %bb.2:
	movl	%edi, %r8d
	andl	$-8, %r8d
	movdqa	.LCPI0_0(%rip), %xmm2           # xmm2 = [0,1,2,3]
	pxor	%xmm8, %xmm8
	movdqa	.LCPI0_1(%rip), %xmm9           # xmm9 = [5,5,5,5]
	movdqa	.LCPI0_2(%rip), %xmm10          # xmm10 = [17,17,17,17]
	movdqa	.LCPI0_3(%rip), %xmm11          # xmm11 = [1,1,1,1]
	movdqa	.LCPI0_4(%rip), %xmm12          # xmm12 = [4294967291,4294967291,4294967291,4294967291]
	movdqa	.LCPI0_5(%rip), %xmm13          # xmm13 = [4294967279,4294967279,4294967279,4294967279]
	movdqa	.LCPI0_6(%rip), %xmm14          # xmm14 = [8,8,8,8]
	movl	%r8d, %eax
	pxor	%xmm1, %xmm1
	pxor	%xmm15, %xmm15
	.p2align	4, 0x90
.LBB0_3:                                # =>This Inner Loop Header: Depth=1
	movdqa	%xmm2, %xmm0
	paddd	%xmm2, %xmm0
	paddd	%xmm2, %xmm0
	movdqa	%xmm0, %xmm4
	movdqa	%xmm12, %xmm6
	psubd	%xmm0, %xmm6
	movdqa	%xmm13, %xmm7
	psubd	%xmm0, %xmm7
	paddd	%xmm9, %xmm0
	paddd	%xmm10, %xmm4
	movdqa	%xmm2, %xmm3
	pand	%xmm11, %xmm3
	pcmpeqd	%xmm8, %xmm3
	movdqa	%xmm3, %xmm5
	pandn	%xmm6, %xmm5
	pand	%xmm3, %xmm0
	por	%xmm5, %xmm0
	paddd	%xmm0, %xmm1
	pand	%xmm3, %xmm4
	pandn	%xmm7, %xmm3
	por	%xmm4, %xmm3
	paddd	%xmm3, %xmm15
	paddd	%xmm14, %xmm2
	addl	$-8, %eax
	jne	.LBB0_3
# %bb.4:
	paddd	%xmm1, %xmm15
	pshufd	$238, %xmm15, %xmm0             # xmm0 = xmm15[2,3,2,3]
	paddd	%xmm15, %xmm0
	pshufd	$85, %xmm0, %xmm1               # xmm1 = xmm0[1,1,1,1]
	paddd	%xmm0, %xmm1
	movd	%xmm1, %eax
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
	.long	5                               # 0x5
	.long	4294967288                      # 0xfffffff8
	.long	11                              # 0xb
	.long	4294967282                      # 0xfffffff2
.LCPI1_1:
	.long	92                              # 0x5c
	.long	4294967192                      # 0xffffff98
	.long	116                             # 0x74
	.long	4294967168                      # 0xffffff80
.LCPI1_2:
	.long	51                              # 0x33
	.long	4294967236                      # 0xffffffc4
	.long	69                              # 0x45
	.long	4294967218                      # 0xffffffb2
.LCPI1_3:
	.long	22                              # 0x16
	.long	4294967268                      # 0xffffffe4
	.long	34                              # 0x22
	.long	4294967256                      # 0xffffffd8
.LCPI1_4:
	.long	145                             # 0x91
	.long	4294967136                      # 0xffffff60
	.long	175                             # 0xaf
	.long	4294967106                      # 0xffffff42
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
	je	.LBB1_15
# %bb.5:
	xorl	%ebp, %ebp
	movl	$0, %ecx
	cmpl	$4, %eax
	jb	.LBB1_13
# %bb.6:
	movl	%eax, %ecx
	andl	$-4, %ecx
	leal	-4(%rcx), %edx
	roll	$30, %edx
	cmpl	$3, %edx
	ja	.LBB1_8
# %bb.7:
	movdqa	.LCPI1_0(%rip), %xmm0           # xmm0 = [5,4294967288,11,4294967282]
	jmpq	*.LJTI1_0(,%rdx,8)
.LBB1_9:
	movdqa	.LCPI1_3(%rip), %xmm0           # xmm0 = [22,4294967268,34,4294967256]
	jmp	.LBB1_12
.LBB1_1:
	movq	stderr(%rip), %rcx
	movl	$.L.str.1, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$1, %ebx
	jmp	.LBB1_16
.LBB1_3:
	movq	stderr(%rip), %rcx
	movl	$.L.str.2, %edi
	movl	$21, %esi
	movl	$1, %edx
	callq	fwrite@PLT
	movl	$2, %ebx
	jmp	.LBB1_16
.LBB1_8:
	movdqa	.LCPI1_4(%rip), %xmm0           # xmm0 = [145,4294967136,175,4294967106]
	jmp	.LBB1_12
.LBB1_10:
	movdqa	.LCPI1_2(%rip), %xmm0           # xmm0 = [51,4294967236,69,4294967218]
	jmp	.LBB1_12
.LBB1_11:
	movdqa	.LCPI1_1(%rip), %xmm0           # xmm0 = [92,4294967192,116,4294967168]
.LBB1_12:
	pshufd	$238, %xmm0, %xmm1              # xmm1 = xmm0[2,3,2,3]
	paddd	%xmm0, %xmm1
	pshufd	$85, %xmm1, %xmm0               # xmm0 = xmm1[1,1,1,1]
	paddd	%xmm1, %xmm0
	movd	%xmm0, %ebp
	cmpl	%ecx, %eax
	je	.LBB1_15
.LBB1_13:
	leal	(%rcx,%rcx,2), %esi
	movl	$-5, %edx
	subl	%esi, %edx
	leal	(%rcx,%rcx,2), %esi
	addl	$5, %esi
	.p2align	4, 0x90
.LBB1_14:                               # =>This Inner Loop Header: Depth=1
	testb	$1, %cl
	movl	%edx, %edi
	cmovel	%esi, %edi
	addl	%edi, %ebp
	addl	$1, %ecx
	addl	$-3, %edx
	addl	$3, %esi
	cmpl	%ecx, %eax
	jne	.LBB1_14
.LBB1_15:
	movl	%ebp, %edi
	callq	add_bonus
	movl	4(%rsp), %esi
	movl	$.L.str.3, %edi
	movl	%ebp, %edx
	movl	%eax, %ecx
	xorl	%eax, %eax
	callq	printf
.LBB1_16:
	movl	%ebx, %eax
	addq	$8, %rsp
	.cfi_def_cfa_offset 24
	popq	%rbx
	.cfi_def_cfa_offset 16
	popq	%rbp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
	.section	.rodata,"a",@progbits
	.p2align	3
.LJTI1_0:
	.quad	.LBB1_12
	.quad	.LBB1_9
	.quad	.LBB1_10
	.quad	.LBB1_11
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
