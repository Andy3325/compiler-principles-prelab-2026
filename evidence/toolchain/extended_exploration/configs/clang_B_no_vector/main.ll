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
  br i1 %2, label %3, label %21

3:                                                ; preds = %1
  %4 = and i32 %0, 1
  %5 = icmp eq i32 %0, 1
  br i1 %5, label %8, label %6

6:                                                ; preds = %3
  %7 = and i32 %0, -2
  br label %23

8:                                                ; preds = %23, %3
  %9 = phi i32 [ undef, %3 ], [ %33, %23 ]
  %10 = phi i32 [ 0, %3 ], [ %33, %23 ]
  %11 = phi i32 [ 0, %3 ], [ %34, %23 ]
  %12 = icmp eq i32 %4, 0
  br i1 %12, label %21, label %13

13:                                               ; preds = %8
  %14 = mul nsw i32 %11, 3
  %15 = add nuw nsw i32 %14, 5
  %16 = and i32 %11, 1
  %17 = icmp eq i32 %16, 0
  %18 = sub nuw i32 -5, %14
  %19 = select i1 %17, i32 %15, i32 %18
  %20 = add i32 %19, %10
  br label %21

21:                                               ; preds = %13, %8, %1
  %22 = phi i32 [ 0, %1 ], [ %9, %8 ], [ %20, %13 ]
  ret i32 %22

23:                                               ; preds = %23, %6
  %24 = phi i32 [ 0, %6 ], [ %33, %23 ]
  %25 = phi i32 [ 0, %6 ], [ %34, %23 ]
  %26 = phi i32 [ 0, %6 ], [ %35, %23 ]
  %27 = mul nsw i32 %25, 3
  %28 = add nuw nsw i32 %27, 5
  %29 = add i32 %28, %24
  %30 = or i32 %25, 1
  %31 = mul i32 %30, -3
  %32 = add i32 %31, -5
  %33 = add i32 %32, %29
  %34 = add nuw nsw i32 %25, 2
  %35 = add i32 %26, 2
  %36 = icmp eq i32 %35, %7
  br i1 %36, label %8, label %23, !llvm.loop !3
}

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: nounwind uwtable
define dso_local i32 @main() local_unnamed_addr #2 {
  %1 = alloca i32, align 4
  %2 = bitcast i32* %1 to i8*
  call void @llvm.lifetime.start.p0i8(i64 4, i8* nonnull %2) #6
  %3 = call i32 (i8*, ...) @__isoc99_scanf(i8* noundef getelementptr inbounds ([3 x i8], [3 x i8]* @.str, i64 0, i64 0), i32* noundef nonnull %1)
  %4 = icmp eq i32 %3, 1
  br i1 %4, label %8, label %5

5:                                                ; preds = %0
  %6 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !tbaa !5
  %7 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.1, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %6) #7
  br label %53

8:                                                ; preds = %0
  %9 = load i32, i32* %1, align 4, !tbaa !9
  %10 = icmp ugt i32 %9, 20
  br i1 %10, label %11, label %14

11:                                               ; preds = %8
  %12 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !tbaa !5
  %13 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.2, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %12) #7
  br label %53

14:                                               ; preds = %8
  %15 = icmp eq i32 %9, 0
  br i1 %15, label %48, label %16

16:                                               ; preds = %14
  %17 = and i32 %9, 1
  %18 = icmp eq i32 %9, 1
  br i1 %18, label %35, label %19

19:                                               ; preds = %16
  %20 = and i32 %9, -2
  br label %21

21:                                               ; preds = %21, %19
  %22 = phi i32 [ 0, %19 ], [ %31, %21 ]
  %23 = phi i32 [ 0, %19 ], [ %32, %21 ]
  %24 = phi i32 [ 0, %19 ], [ %33, %21 ]
  %25 = mul nuw nsw i32 %23, 3
  %26 = add nuw nsw i32 %25, 5
  %27 = add i32 %26, %22
  %28 = or i32 %23, 1
  %29 = mul i32 %28, -3
  %30 = add i32 %29, -5
  %31 = add i32 %30, %27
  %32 = add nuw nsw i32 %23, 2
  %33 = add i32 %24, 2
  %34 = icmp eq i32 %33, %20
  br i1 %34, label %35, label %21, !llvm.loop !3

35:                                               ; preds = %21, %16
  %36 = phi i32 [ undef, %16 ], [ %31, %21 ]
  %37 = phi i32 [ 0, %16 ], [ %31, %21 ]
  %38 = phi i32 [ 0, %16 ], [ %32, %21 ]
  %39 = icmp eq i32 %17, 0
  br i1 %39, label %48, label %40

40:                                               ; preds = %35
  %41 = mul nuw nsw i32 %38, 3
  %42 = add nuw nsw i32 %41, 5
  %43 = and i32 %38, 1
  %44 = icmp eq i32 %43, 0
  %45 = sub nuw nsw i32 -5, %41
  %46 = select i1 %44, i32 %42, i32 %45
  %47 = add i32 %46, %37
  br label %48

48:                                               ; preds = %40, %35, %14
  %49 = phi i32 [ 0, %14 ], [ %36, %35 ], [ %47, %40 ]
  %50 = call i32 @add_bonus(i32 noundef %49) #6
  %51 = load i32, i32* %1, align 4, !tbaa !9
  %52 = call i32 (i8*, ...) @printf(i8* noundef nonnull dereferenceable(1) getelementptr inbounds ([33 x i8], [33 x i8]* @.str.3, i64 0, i64 0), i32 noundef %51, i32 noundef %49, i32 noundef %50)
  br label %53

53:                                               ; preds = %48, %11, %5
  %54 = phi i32 [ 1, %5 ], [ 2, %11 ], [ 0, %48 ]
  call void @llvm.lifetime.end.p0i8(i64 4, i8* nonnull %2) #6
  ret i32 %54
}

; Function Attrs: nofree nounwind
declare dso_local noundef i32 @__isoc99_scanf(i8* nocapture noundef readonly, ...) local_unnamed_addr #3

declare dso_local i32 @add_bonus(i32 noundef) local_unnamed_addr #4

; Function Attrs: nofree nounwind
declare dso_local noundef i32 @printf(i8* nocapture noundef readonly, ...) local_unnamed_addr #3

; Function Attrs: nofree nounwind
declare noundef i64 @fwrite(i8* nocapture noundef, i64 noundef, i64 noundef, %struct._IO_FILE* nocapture noundef) local_unnamed_addr #5

attributes #0 = { nofree norecurse nosync nounwind readnone uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { argmemonly mustprogress nofree nosync nounwind willreturn }
attributes #2 = { nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { nofree nounwind "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nofree nounwind }
attributes #6 = { nounwind }
attributes #7 = { cold }

!llvm.module.flags = !{!0, !1}
!llvm.ident = !{!2}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"uwtable", i32 1}
!2 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!3 = distinct !{!3, !4}
!4 = !{!"llvm.loop.mustprogress"}
!5 = !{!6, !6, i64 0}
!6 = !{!"any pointer", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C/C++ TBAA"}
!9 = !{!10, !10, i64 0}
!10 = !{!"int", !7, i64 0}
