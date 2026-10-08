; HAND-WRITTEN LLVM 14 typed-pointer IR, not a Clang export.
target triple = "riscv64-unknown-linux-gnu"
@calls = global i32 0, align 4
@bias = global i32 7, align 4
declare i32 @getint()
declare void @putint(i32 signext)
declare void @putch(i32 signext)

define signext i32 @tick(i32 signext %x) {
entry:
  %old = load i32, i32* @calls, align 4
  %new = add i32 %old, 1
  store i32 %new, i32* @calls, align 4
  ret i32 %x
}

define signext i32 @cell([3 x i32]* %a, i32 signext %row, i32 signext %col) {
entry:
  %r64 = sext i32 %row to i64
  %c64 = sext i32 %col to i64
  %p = getelementptr inbounds [3 x i32], [3 x i32]* %a, i64 %r64, i64 %c64
  %v = load i32, i32* %p, align 4
  ret i32 %v
}

define signext i32 @fold([3 x i32]* %a, i32 signext %n, i32 signext %stop) {
entry:
  %limit = sub i32 %n, 1
  br label %loop
loop:
  %i = phi i32 [0, %entry], [%next, %step]
  %sum = phi i32 [0, %entry], [%sum.next, %step]
  %more = icmp sle i32 %i, %limit
  br i1 %more, label %body, label %exit
body:
  %row = sdiv i32 %i, 3
  %col = srem i32 %i, 3
  %v = call signext i32 @cell([3 x i32]* %a, i32 signext %row, i32 signext %col)
  %next = add i32 %i, 1
  %zero = icmp eq i32 %v, 0
  br i1 %zero, label %step, label %check.break
check.break:
  %stop.here = icmp eq i32 %v, %stop
  br i1 %stop.here, label %exit, label %accum
accum:
  %weighted = mul i32 %v, %next
  %added = add i32 %sum, %weighted
  br label %step
step:
  %sum.next = phi i32 [%sum, %body], [%added, %accum]
  br label %loop
exit:
  ret i32 %sum
}

define void @separator() {
entry:
  call void @putch(i32 signext 32)
  ret void
}

define signext i32 @main() {
entry:
  %a = alloca [2 x [3 x i32]], align 16
  store [2 x [3 x i32]] [[3 x i32] [i32 1, i32 2, i32 0], [3 x i32] [i32 -3, i32 4, i32 5]], [2 x [3 x i32]]* %a, align 16
  %n = call signext i32 @getint()
  %stop = call signext i32 @getint()
  %gate = call signext i32 @getint()
  %divisor = call signext i32 @getint()
  br label %read.loop
read.loop:
  %i = phi i32 [0, %entry], [%next, %read.body]
  %more = icmp slt i32 %i, 6
  br i1 %more, label %read.body, label %sc.and
read.body:
  %row = sdiv i32 %i, 3
  %col = srem i32 %i, 3
  %r64 = sext i32 %row to i64
  %c64 = sext i32 %col to i64
  %p = getelementptr inbounds [2 x [3 x i32]], [2 x [3 x i32]]* %a, i64 0, i64 %r64, i64 %c64
  %old = load i32, i32* %p, align 4
  %delta = call signext i32 @getint()
  %updated = add i32 %old, %delta
  store i32 %updated, i32* %p, align 4
  %next = add i32 %i, 1
  br label %read.loop
sc.and:
  %gate.nonzero = icmp ne i32 %gate, 0
  br i1 %gate.nonzero, label %sc.and.rhs, label %sc.first.merge
sc.and.rhs:
  %first.p = getelementptr inbounds [2 x [3 x i32]], [2 x [3 x i32]]* %a, i64 0, i64 0, i64 0
  %first = load i32, i32* %first.p, align 4
  %first.ticked = call signext i32 @tick(i32 signext %first)
  %positive = icmp sgt i32 %first.ticked, 0
  %first.tag = zext i1 %positive to i32
  br label %sc.first.merge
sc.first.merge:
  %tag1 = phi i32 [0, %sc.and], [%first.tag, %sc.and.rhs]
  br i1 %gate.nonzero, label %sc.or.rhs, label %sc.add.two
sc.or.rhs:
  %last.p = getelementptr inbounds [2 x [3 x i32]], [2 x [3 x i32]]* %a, i64 0, i64 1, i64 2
  %last = load i32, i32* %last.p, align 4
  %last.negative = icmp slt i32 %last, 0
  br i1 %last.negative, label %sc.nested.rhs, label %sc.second.merge
sc.nested.rhs:
  %last.ticked = call signext i32 @tick(i32 signext %last)
  %last.nonzero = icmp ne i32 %last.ticked, 0
  br i1 %last.nonzero, label %sc.add.two, label %sc.second.merge
sc.add.two:
  %tag.plus2 = add i32 %tag1, 2
  br label %sc.second.merge
sc.second.merge:
  %tag2 = phi i32 [%tag1, %sc.or.rhs], [%tag1, %sc.nested.rhs], [%tag.plus2, %sc.add.two]
  br i1 %gate.nonzero, label %sc.final, label %sc.add.four
sc.add.four:
  %tag.plus4 = add i32 %tag2, 4
  br label %sc.final
sc.final:
  %tag = phi i32 [%tag2, %sc.second.merge], [%tag.plus4, %sc.add.four]
  %base = getelementptr inbounds [2 x [3 x i32]], [2 x [3 x i32]]* %a, i64 0, i64 0
  %folded = call signext i32 @fold([3 x i32]* %base, i32 signext %n, i32 signext %stop)
  %global.bias = load i32, i32* @bias, align 4
  %with.global = add i32 %folded, %global.bias
  %result = add i32 %with.global, 3
  call void @putint(i32 signext %result)
  call void @separator()
  %count = load i32, i32* @calls, align 4
  call void @putint(i32 signext %count)
  call void @separator()
  call void @putint(i32 signext %tag)
  call void @separator()
  %q.p = getelementptr inbounds [2 x [3 x i32]], [2 x [3 x i32]]* %a, i64 0, i64 0, i64 1
  %dividend = load i32, i32* %q.p, align 4
  %q = sdiv i32 %dividend, %divisor
  %r = srem i32 %dividend, %divisor
  call void @putint(i32 signext %q)
  call void @separator()
  call void @putint(i32 signext %r)
  call void @putch(i32 signext 10)
  ret i32 0
}
