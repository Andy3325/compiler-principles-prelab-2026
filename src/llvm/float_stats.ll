; HAND-WRITTEN: strict binary32 operations; no fast/contract flags.
target triple = "riscv64-unknown-linux-gnu"
declare i32 @getint()
declare float @getfloat()
declare void @putint(i32 signext)
declare void @putfloat(float)
declare void @putch(i32 signext)

define float @affine(float %x, float %scale, i32 signext %offset) {
entry:
  %product = fmul float %x, %scale
  %off.float = sitofp i32 %offset to float
  %result = fadd float %product, %off.float
  ret float %result
}

define float @sum_positive(float* %a, i32 signext %n, float %scale) {
entry:
  br label %loop
loop:
  %i = phi i32 [0, %entry], [%next, %step]
  %sum = phi float [0.0, %entry], [%sum.next, %step]
  %bound = add i32 %i, 1
  %more = icmp sge i32 %n, %bound
  br i1 %more, label %body, label %exit
body:
  %i64 = sext i32 %i to i64
  %p = getelementptr inbounds float, float* %a, i64 %i64
  %x = load float, float* %p, align 4
  %v = call float @affine(float %x, float %scale, i32 signext %i)
  %positive = fcmp ogt float %v, 0.0
  br i1 %positive, label %accum, label %step
accum:
  %added = fadd float %sum, %v
  br label %step
step:
  %sum.next = phi float [%sum, %body], [%added, %accum]
  %next = add i32 %i, 1
  br label %loop
exit:
  ret float %sum
}

define signext i32 @main() {
entry:
  %a = alloca [4 x float], align 16
  store [4 x float] [float 1.0, float -2.0, float 0.5, float 0.0], [4 x float]* %a, align 16
  %n = call signext i32 @getint()
  %scale = call float @getfloat()
  br label %read.loop
read.loop:
  %i = phi i32 [0, %entry], [%next, %read.body]
  %more = icmp slt i32 %i, %n
  br i1 %more, label %read.body, label %compute
read.body:
  %x = call float @getfloat()
  %i64 = sext i32 %i to i64
  %p = getelementptr inbounds [4 x float], [4 x float]* %a, i64 0, i64 %i64
  store float %x, float* %p, align 4
  %next = add i32 %i, 1
  br label %read.loop
compute:
  %base = getelementptr inbounds [4 x float], [4 x float]* %a, i64 0, i64 0
  %sum = call float @sum_positive(float* %base, i32 signext %n, float %scale)
  %result = fadd float %sum, 0.25
  %truncated = fptosi float %result to i32
  %denom.int = add i32 %n, 1
  %denom = sitofp i32 %denom.int to float
  %normalized = fdiv float %result, %denom
  call void @putfloat(float %result)
  call void @putch(i32 signext 32)
  call void @putint(i32 signext %truncated)
  call void @putch(i32 signext 32)
  call void @putfloat(float %normalized)
  call void @putch(i32 signext 10)
  ret i32 0
}
