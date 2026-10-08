; ModuleID = '<PROJECT>/src/toolchain/main.c'
source_filename = "<PROJECT>/src/toolchain/main.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct._IO_FILE = type { i32, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, i8*, %struct._IO_marker*, %struct._IO_FILE*, i32, i32, i64, i16, i8, [1 x i8], i8*, i64, %struct._IO_codecvt*, %struct._IO_wide_data*, %struct._IO_FILE*, i8*, i64, i32, [20 x i8] }
%struct._IO_marker = type opaque
%struct._IO_codecvt = type opaque
%struct._IO_wide_data = type opaque

@.str = private unnamed_addr constant [3 x i8] c"%d\00", align 1
@.str.1 = private unnamed_addr constant [22 x i8] c"expected one integer\0A\00", align 1
@stderr = external dso_local local_unnamed_addr global %struct._IO_FILE*, align 8
@.str.2 = private unnamed_addr constant [22 x i8] c"n must be in [0, 20]\0A\00", align 1
@.str.3 = private unnamed_addr constant [33 x i8] c"n=%d alternating=%d adjusted=%d\0A\00", align 1

; Function Attrs: nofree norecurse nosync nounwind readnone uwtable
define dso_local i32 @alternating_sum(i32 noundef %0) local_unnamed_addr #0 {
  %2 = icmp sgt i32 %0, 0
  br i1 %2, label %3, label %36

3:                                                ; preds = %1
  %4 = icmp ult i32 %0, 8
  br i1 %4, label %33, label %5

5:                                                ; preds = %3
  %6 = and i32 %0, -8
  br label %7

7:                                                ; preds = %7, %5
  %8 = phi i32 [ 0, %5 ], [ %26, %7 ]
  %9 = phi <4 x i32> [ zeroinitializer, %5 ], [ %24, %7 ]
  %10 = phi <4 x i32> [ zeroinitializer, %5 ], [ %25, %7 ]
  %11 = phi <4 x i32> [ <i32 0, i32 1, i32 2, i32 3>, %5 ], [ %27, %7 ]
  %12 = mul nsw <4 x i32> %11, <i32 3, i32 3, i32 3, i32 3>
  %13 = mul <4 x i32> %11, <i32 3, i32 3, i32 3, i32 3>
  %14 = add nuw nsw <4 x i32> %12, <i32 5, i32 5, i32 5, i32 5>
  %15 = add <4 x i32> %13, <i32 17, i32 17, i32 17, i32 17>
  %16 = and <4 x i32> %11, <i32 1, i32 1, i32 1, i32 1>
  %17 = and <4 x i32> %11, <i32 1, i32 1, i32 1, i32 1>
  %18 = icmp eq <4 x i32> %16, zeroinitializer
  %19 = icmp eq <4 x i32> %17, zeroinitializer
  %20 = sub nuw <4 x i32> <i32 -5, i32 -5, i32 -5, i32 -5>, %12
  %21 = sub <4 x i32> <i32 -17, i32 -17, i32 -17, i32 -17>, %13
  %22 = select <4 x i1> %18, <4 x i32> %14, <4 x i32> %20
  %23 = select <4 x i1> %19, <4 x i32> %15, <4 x i32> %21
  %24 = add <4 x i32> %22, %9
  %25 = add <4 x i32> %23, %10
  %26 = add nuw i32 %8, 8
  %27 = add <4 x i32> %11, <i32 8, i32 8, i32 8, i32 8>
  %28 = icmp eq i32 %26, %6
  br i1 %28, label %29, label %7, !llvm.loop !3

29:                                               ; preds = %7
  %30 = add <4 x i32> %25, %24
  %31 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %30)
  %32 = icmp eq i32 %6, %0
  br i1 %32, label %36, label %33

33:                                               ; preds = %3, %29
  %34 = phi i32 [ 0, %3 ], [ %31, %29 ]
  %35 = phi i32 [ 0, %3 ], [ %6, %29 ]
  br label %38

36:                                               ; preds = %38, %29, %1
  %37 = phi i32 [ 0, %1 ], [ %31, %29 ], [ %47, %38 ]
  ret i32 %37

38:                                               ; preds = %33, %38
  %39 = phi i32 [ %47, %38 ], [ %34, %33 ]
  %40 = phi i32 [ %48, %38 ], [ %35, %33 ]
  %41 = mul nsw i32 %40, 3
  %42 = add nuw nsw i32 %41, 5
  %43 = and i32 %40, 1
  %44 = icmp eq i32 %43, 0
  %45 = sub nuw i32 -5, %41
  %46 = select i1 %44, i32 %42, i32 %45
  %47 = add i32 %46, %39
  %48 = add nuw nsw i32 %40, 1
  %49 = icmp eq i32 %48, %0
  br i1 %49, label %36, label %38, !llvm.loop !6
}

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: nounwind uwtable
define dso_local i32 @main() local_unnamed_addr #2 {
  %1 = alloca i32, align 4
  %2 = bitcast i32* %1 to i8*
  call void @llvm.lifetime.start.p0i8(i64 4, i8* nonnull %2) #7
  %3 = call i32 (i8*, ...) @__isoc99_scanf(i8* noundef getelementptr inbounds ([3 x i8], [3 x i8]* @.str, i64 0, i64 0), i32* noundef nonnull %1)
  %4 = icmp eq i32 %3, 1
  br i1 %4, label %8, label %5

5:                                                ; preds = %0
  %6 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !tbaa !8
  %7 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.1, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %6) #8
  br label %52

8:                                                ; preds = %0
  %9 = load i32, i32* %1, align 4, !tbaa !12
  %10 = icmp ugt i32 %9, 20
  br i1 %10, label %11, label %14

11:                                               ; preds = %8
  %12 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !tbaa !8
  %13 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.2, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %12) #8
  br label %52

14:                                               ; preds = %8
  %15 = icmp eq i32 %9, 0
  br i1 %15, label %47, label %16

16:                                               ; preds = %14
  %17 = icmp ult i32 %9, 4
  br i1 %17, label %32, label %18

18:                                               ; preds = %16
  %19 = and i32 %9, -4
  %20 = sub i32 %19, 4
  %21 = lshr i32 %20, 2
  %22 = shl i32 %20, 30
  %23 = or i32 %21, %22
  switch i32 %23, label %24 [
    i32 0, label %28
    i32 1, label %25
    i32 2, label %26
    i32 3, label %27
  ]

24:                                               ; preds = %18
  br label %28

25:                                               ; preds = %18
  br label %28

26:                                               ; preds = %18
  br label %28

27:                                               ; preds = %18
  br label %28

28:                                               ; preds = %18, %27, %26, %25, %24
  %29 = phi <4 x i32> [ <i32 5, i32 -8, i32 11, i32 -14>, %18 ], [ <i32 145, i32 -160, i32 175, i32 -190>, %24 ], [ <i32 22, i32 -28, i32 34, i32 -40>, %25 ], [ <i32 51, i32 -60, i32 69, i32 -78>, %26 ], [ <i32 92, i32 -104, i32 116, i32 -128>, %27 ]
  %30 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %29)
  %31 = icmp eq i32 %9, %19
  br i1 %31, label %47, label %32

32:                                               ; preds = %16, %28
  %33 = phi i32 [ 0, %16 ], [ %30, %28 ]
  %34 = phi i32 [ 0, %16 ], [ %19, %28 ]
  br label %35

35:                                               ; preds = %32, %35
  %36 = phi i32 [ %44, %35 ], [ %33, %32 ]
  %37 = phi i32 [ %45, %35 ], [ %34, %32 ]
  %38 = mul nuw nsw i32 %37, 3
  %39 = add nuw nsw i32 %38, 5
  %40 = and i32 %37, 1
  %41 = icmp eq i32 %40, 0
  %42 = sub nuw nsw i32 -5, %38
  %43 = select i1 %41, i32 %39, i32 %42
  %44 = add i32 %43, %36
  %45 = add nuw nsw i32 %37, 1
  %46 = icmp eq i32 %45, %9
  br i1 %46, label %47, label %35, !llvm.loop !14

47:                                               ; preds = %35, %28, %14
  %48 = phi i32 [ 0, %14 ], [ %30, %28 ], [ %44, %35 ]
  %49 = call i32 @add_bonus(i32 noundef %48) #7
  %50 = load i32, i32* %1, align 4, !tbaa !12
  %51 = call i32 (i8*, ...) @printf(i8* noundef nonnull dereferenceable(1) getelementptr inbounds ([33 x i8], [33 x i8]* @.str.3, i64 0, i64 0), i32 noundef %50, i32 noundef %48, i32 noundef %49)
  br label %52

52:                                               ; preds = %47, %11, %5
  %53 = phi i32 [ 1, %5 ], [ 2, %11 ], [ 0, %47 ]
  call void @llvm.lifetime.end.p0i8(i64 4, i8* nonnull %2) #7
  ret i32 %53
}

; Function Attrs: nofree nounwind
declare dso_local noundef i32 @__isoc99_scanf(i8* nocapture noundef readonly, ...) local_unnamed_addr #3

declare dso_local i32 @add_bonus(i32 noundef) local_unnamed_addr #4

; Function Attrs: nofree nounwind
declare dso_local noundef i32 @printf(i8* nocapture noundef readonly, ...) local_unnamed_addr #3

; Function Attrs: nofree nounwind
declare noundef i64 @fwrite(i8* nocapture noundef, i64 noundef, i64 noundef, %struct._IO_FILE* nocapture noundef) local_unnamed_addr #5

; Function Attrs: nofree nosync nounwind readnone willreturn
declare i32 @llvm.vector.reduce.add.v4i32(<4 x i32>) #6

attributes #0 = { nofree norecurse nosync nounwind readnone uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { argmemonly mustprogress nofree nosync nounwind willreturn }
attributes #2 = { nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nofree nounwind "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nofree nounwind }
attributes #6 = { nofree nosync nounwind readnone willreturn }
attributes #7 = { nounwind }
attributes #8 = { cold }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"uwtable", i32 1}
!2 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!3 = distinct !{!3, !4, !5}
!4 = !{!"llvm.loop.mustprogress"}
!5 = !{!"llvm.loop.isvectorized", i32 1}
!6 = distinct !{!6, !4, !7, !5}
!7 = !{!"llvm.loop.unroll.runtime.disable"}
!8 = !{!9, !9, i64 0}
!9 = !{!"any pointer", !10, i64 0}
!10 = !{!"omnipotent char", !11, i64 0}
!11 = !{!"Simple C/C++ TBAA"}
!12 = !{!13, !13, i64 0}
!13 = !{!"int", !10, i64 0}
!14 = distinct !{!14, !4, !7, !5}
