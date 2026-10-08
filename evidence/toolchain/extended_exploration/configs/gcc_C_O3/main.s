	.file	"main.c"
	.text
	.p2align 4
	.globl	alternating_sum
	.type	alternating_sum, @function
alternating_sum:
.LFB13:
	.cfi_startproc
	endbr64
	testl	%edi, %edi
	jle	.L6
	movl	$5, %ecx
	xorl	%edx, %edx
	xorl	%eax, %eax
	.p2align 4,,10
	.p2align 3
.L5:
	leal	(%rax,%rcx), %esi
	subl	%ecx, %eax
	testb	$1, %dl
	cmove	%esi, %eax
	addl	$1, %edx
	addl	$3, %ecx
	cmpl	%edx, %edi
	jne	.L5
	ret
	.p2align 4,,10
	.p2align 3
.L6:
	xorl	%eax, %eax
	ret
	.cfi_endproc
.LFE13:
	.size	alternating_sum, .-alternating_sum
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC0:
	.string	"%d"
.LC1:
	.string	"expected one integer\n"
.LC2:
	.string	"n must be in [0, 20]\n"
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align 8
.LC3:
	.string	"n=%d alternating=%d adjusted=%d\n"
	.section	.text.startup,"ax",@progbits
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB14:
	.cfi_startproc
	endbr64
	pushq	%r12
	.cfi_def_cfa_offset 16
	.cfi_offset 12, -16
	movl	$.LC0, %edi
	subq	$16, %rsp
	.cfi_def_cfa_offset 32
	movq	%fs:40, %rax
	movq	%rax, 8(%rsp)
	xorl	%eax, %eax
	leaq	4(%rsp), %rsi
	call	__isoc99_scanf
	cmpl	$1, %eax
	jne	.L21
	movl	4(%rsp), %esi
	cmpl	$20, %esi
	ja	.L12
	xorl	%r12d, %r12d
	testl	%esi, %esi
	je	.L14
	movl	$5, %edx
	xorl	%r12d, %r12d
	xorl	%eax, %eax
	.p2align 4,,10
	.p2align 3
.L13:
	leal	(%r12,%rdx), %ecx
	subl	%edx, %r12d
	testb	$1, %al
	cmove	%ecx, %r12d
	addl	$1, %eax
	addl	$3, %edx
	cmpl	%eax, %esi
	jne	.L13
.L14:
	movl	%r12d, %edi
	call	add_bonus
	movl	4(%rsp), %edx
	movl	%r12d, %ecx
	movl	$.LC3, %esi
	movl	%eax, %r8d
	movl	$1, %edi
	xorl	%eax, %eax
	call	__printf_chk
	xorl	%eax, %eax
.L9:
	movq	8(%rsp), %rdx
	subq	%fs:40, %rdx
	jne	.L22
	addq	$16, %rsp
	.cfi_remember_state
	.cfi_def_cfa_offset 16
	popq	%r12
	.cfi_def_cfa_offset 8
	ret
.L21:
	.cfi_restore_state
	movl	$21, %edx
	movl	$1, %esi
	movl	$.LC1, %edi
	movq	stderr(%rip), %rcx
	call	fwrite
	movl	$1, %eax
	jmp	.L9
.L12:
	movl	$21, %edx
	movl	$1, %esi
	movl	$.LC2, %edi
	movq	stderr(%rip), %rcx
	call	fwrite
	movl	$2, %eax
	jmp	.L9
.L22:
	call	__stack_chk_fail
	.cfi_endproc
.LFE14:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
