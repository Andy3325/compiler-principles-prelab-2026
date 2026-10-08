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
  br i1 %2, label %3, label %27

3:                                                ; preds = %1
  %4 = icmp ult i32 %0, 4
  br i1 %4, label %24, label %5

5:                                                ; preds = %3
  %6 = and i32 %0, -4
  br label %7

7:                                                ; preds = %7, %5
  %8 = phi i32 [ 0, %5 ], [ %18, %7 ]
  %9 = phi <4 x i32> [ zeroinitializer, %5 ], [ %17, %7 ]
  %10 = phi <4 x i32> [ <i32 0, i32 1, i32 2, i32 3>, %5 ], [ %19, %7 ]
  %11 = mul nsw <4 x i32> %10, <i32 3, i32 3, i32 3, i32 3>
  %12 = add nuw nsw <4 x i32> %11, <i32 5, i32 5, i32 5, i32 5>
  %13 = and <4 x i32> %10, <i32 1, i32 1, i32 1, i32 1>
  %14 = icmp eq <4 x i32> %13, zeroinitializer
  %15 = sub nuw <4 x i32> <i32 -5, i32 -5, i32 -5, i32 -5>, %11
  %16 = select <4 x i1> %14, <4 x i32> %12, <4 x i32> %15
  %17 = add <4 x i32> %16, %9
  %18 = add nuw i32 %8, 4
  %19 = add <4 x i32> %10, <i32 4, i32 4, i32 4, i32 4>
  %20 = icmp eq i32 %18, %6
  br i1 %20, label %21, label %7, !llvm.loop !3

21:                                               ; preds = %7
  %22 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %17)
  %23 = icmp eq i32 %6, %0
  br i1 %23, label %27, label %24

24:                                               ; preds = %3, %21
  %25 = phi i32 [ 0, %3 ], [ %22, %21 ]
  %26 = phi i32 [ 0, %3 ], [ %6, %21 ]
  br label %29

27:                                               ; preds = %29, %21, %1
  %28 = phi i32 [ 0, %1 ], [ %22, %21 ], [ %38, %29 ]
  ret i32 %28

29:                                               ; preds = %24, %29
  %30 = phi i32 [ %38, %29 ], [ %25, %24 ]
  %31 = phi i32 [ %39, %29 ], [ %26, %24 ]
  %32 = mul nsw i32 %31, 3
  %33 = add nuw nsw i32 %32, 5
  %34 = and i32 %31, 1
  %35 = icmp eq i32 %34, 0
  %36 = sub nuw i32 -5, %32
  %37 = select i1 %35, i32 %33, i32 %36
  %38 = add i32 %37, %30
  %39 = add nuw nsw i32 %31, 1
  %40 = icmp eq i32 %39, %0
  br i1 %40, label %27, label %29, !llvm.loop !7
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
  br label %57

8:                                                ; preds = %0
  %9 = load i32, i32* %1, align 4, !tbaa !12
  %10 = icmp ugt i32 %9, 20
  br i1 %10, label %11, label %14

11:                                               ; preds = %8
  %12 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !tbaa !8
  %13 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.2, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %12) #8
  br label %57

14:                                               ; preds = %8
  %15 = icmp eq i32 %9, 0
  br i1 %15, label %52, label %16

16:                                               ; preds = %14
  %17 = icmp ult i32 %9, 4
  br i1 %17, label %37, label %18

18:                                               ; preds = %16
  %19 = and i32 %9, -4
  br label %20

20:                                               ; preds = %20, %18
  %21 = phi i32 [ 0, %18 ], [ %31, %20 ]
  %22 = phi <4 x i32> [ zeroinitializer, %18 ], [ %30, %20 ]
  %23 = phi <4 x i32> [ <i32 0, i32 1, i32 2, i32 3>, %18 ], [ %32, %20 ]
  %24 = mul nuw nsw <4 x i32> %23, <i32 3, i32 3, i32 3, i32 3>
  %25 = add nuw nsw <4 x i32> %24, <i32 5, i32 5, i32 5, i32 5>
  %26 = and <4 x i32> %23, <i32 1, i32 1, i32 1, i32 1>
  %27 = icmp eq <4 x i32> %26, zeroinitializer
  %28 = sub nuw nsw <4 x i32> <i32 -5, i32 -5, i32 -5, i32 -5>, %24
  %29 = select <4 x i1> %27, <4 x i32> %25, <4 x i32> %28
  %30 = add <4 x i32> %29, %22
  %31 = add nuw i32 %21, 4
  %32 = add <4 x i32> %23, <i32 4, i32 4, i32 4, i32 4>
  %33 = icmp eq i32 %31, %19
  br i1 %33, label %34, label %20, !llvm.loop !14

34:                                               ; preds = %20
  %35 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %30)
  %36 = icmp eq i32 %9, %19
  br i1 %36, label %52, label %37

37:                                               ; preds = %16, %34
  %38 = phi i32 [ 0, %16 ], [ %35, %34 ]
  %39 = phi i32 [ 0, %16 ], [ %19, %34 ]
  br label %40

40:                                               ; preds = %37, %40
  %41 = phi i32 [ %49, %40 ], [ %38, %37 ]
  %42 = phi i32 [ %50, %40 ], [ %39, %37 ]
  %43 = mul nuw nsw i32 %42, 3
  %44 = add nuw nsw i32 %43, 5
  %45 = and i32 %42, 1
  %46 = icmp eq i32 %45, 0
  %47 = sub nuw nsw i32 -5, %43
  %48 = select i1 %46, i32 %44, i32 %47
  %49 = add i32 %48, %41
  %50 = add nuw nsw i32 %42, 1
  %51 = icmp eq i32 %50, %9
  br i1 %51, label %52, label %40, !llvm.loop !15

52:                                               ; preds = %40, %34, %14
  %53 = phi i32 [ 0, %14 ], [ %35, %34 ], [ %49, %40 ]
  %54 = call i32 @add_bonus(i32 noundef %53) #7
  %55 = load i32, i32* %1, align 4, !tbaa !12
  %56 = call i32 (i8*, ...) @printf(i8* noundef nonnull dereferenceable(1) getelementptr inbounds ([33 x i8], [33 x i8]* @.str.3, i64 0, i64 0), i32 noundef %55, i32 noundef %53, i32 noundef %54)
  br label %57

57:                                               ; preds = %52, %11, %5
  %58 = phi i32 [ 1, %5 ], [ 2, %11 ], [ 0, %52 ]
  call void @llvm.lifetime.end.p0i8(i64 4, i8* nonnull %2) #7
  ret i32 %58
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
!3 = distinct !{!3, !4, !5, !6}
!4 = !{!"llvm.loop.mustprogress"}
!5 = !{!"llvm.loop.unroll.disable"}
!6 = !{!"llvm.loop.isvectorized", i32 1}
!7 = distinct !{!7, !4, !5, !6}
!8 = !{!9, !9, i64 0}
!9 = !{!"any pointer", !10, i64 0}
!10 = !{!"omnipotent char", !11, i64 0}
!11 = !{!"Simple C/C++ TBAA"}
!12 = !{!13, !13, i64 0}
!13 = !{!"int", !10, i64 0}
!14 = distinct !{!14, !4, !5, !6}
!15 = distinct !{!15, !4, !5, !6}
