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
define dso_local i32 @alternating_sum(i32 noundef %0) local_unnamed_addr #0 !dbg !6 {
  %2 = icmp sgt i32 %0, 0, !dbg !10
  br i1 %2, label %3, label %36, !dbg !11

3:                                                ; preds = %1
  %4 = icmp ult i32 %0, 8, !dbg !11
  br i1 %4, label %33, label %5, !dbg !11

5:                                                ; preds = %3
  %6 = and i32 %0, -8, !dbg !11
  br label %7, !dbg !11

7:                                                ; preds = %7, %5
  %8 = phi i32 [ 0, %5 ], [ %26, %7 ], !dbg !12
  %9 = phi <4 x i32> [ zeroinitializer, %5 ], [ %24, %7 ]
  %10 = phi <4 x i32> [ zeroinitializer, %5 ], [ %25, %7 ]
  %11 = phi <4 x i32> [ <i32 0, i32 1, i32 2, i32 3>, %5 ], [ %27, %7 ]
  %12 = mul nsw <4 x i32> %11, <i32 3, i32 3, i32 3, i32 3>, !dbg !13
  %13 = mul <4 x i32> %11, <i32 3, i32 3, i32 3, i32 3>, !dbg !13
  %14 = add nuw nsw <4 x i32> %12, <i32 5, i32 5, i32 5, i32 5>, !dbg !16
  %15 = add <4 x i32> %13, <i32 17, i32 17, i32 17, i32 17>, !dbg !16
  %16 = and <4 x i32> %11, <i32 1, i32 1, i32 1, i32 1>, !dbg !17
  %17 = and <4 x i32> %11, <i32 1, i32 1, i32 1, i32 1>, !dbg !17
  %18 = icmp eq <4 x i32> %16, zeroinitializer, !dbg !18
  %19 = icmp eq <4 x i32> %17, zeroinitializer, !dbg !18
  %20 = sub nuw <4 x i32> <i32 -5, i32 -5, i32 -5, i32 -5>, %12, !dbg !19
  %21 = sub <4 x i32> <i32 -17, i32 -17, i32 -17, i32 -17>, %13, !dbg !19
  %22 = select <4 x i1> %18, <4 x i32> %14, <4 x i32> %20, !dbg !19
  %23 = select <4 x i1> %19, <4 x i32> %15, <4 x i32> %21, !dbg !19
  %24 = add <4 x i32> %22, %9, !dbg !19
  %25 = add <4 x i32> %23, %10, !dbg !19
  %26 = add nuw i32 %8, 8, !dbg !12
  %27 = add <4 x i32> %11, <i32 8, i32 8, i32 8, i32 8>
  %28 = icmp eq i32 %26, %6, !dbg !12
  br i1 %28, label %29, label %7, !dbg !12, !llvm.loop !20

29:                                               ; preds = %7
  %30 = add <4 x i32> %25, %24, !dbg !11
  %31 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %30), !dbg !11
  %32 = icmp eq i32 %6, %0, !dbg !11
  br i1 %32, label %36, label %33, !dbg !11

33:                                               ; preds = %3, %29
  %34 = phi i32 [ 0, %3 ], [ %31, %29 ]
  %35 = phi i32 [ 0, %3 ], [ %6, %29 ]
  br label %38, !dbg !11

36:                                               ; preds = %38, %29, %1
  %37 = phi i32 [ 0, %1 ], [ %31, %29 ], [ %47, %38 ], !dbg !24
  ret i32 %37, !dbg !25

38:                                               ; preds = %33, %38
  %39 = phi i32 [ %47, %38 ], [ %34, %33 ]
  %40 = phi i32 [ %48, %38 ], [ %35, %33 ]
  %41 = mul nsw i32 %40, 3, !dbg !13
  %42 = add nuw nsw i32 %41, 5, !dbg !16
  %43 = and i32 %40, 1, !dbg !17
  %44 = icmp eq i32 %43, 0, !dbg !18
  %45 = sub nuw i32 -5, %41, !dbg !19
  %46 = select i1 %44, i32 %42, i32 %45, !dbg !19
  %47 = add i32 %46, %39, !dbg !19
  %48 = add nuw nsw i32 %40, 1, !dbg !12
  %49 = icmp eq i32 %48, %0, !dbg !10
  br i1 %49, label %36, label %38, !dbg !11, !llvm.loop !26
}

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: argmemonly mustprogress nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #1

; Function Attrs: nounwind uwtable
define dso_local i32 @main() local_unnamed_addr #2 !dbg !28 {
  %1 = alloca i32, align 4
  %2 = bitcast i32* %1 to i8*, !dbg !29
  call void @llvm.lifetime.start.p0i8(i64 4, i8* nonnull %2) #7, !dbg !29
  %3 = call i32 (i8*, ...) @__isoc99_scanf(i8* noundef getelementptr inbounds ([3 x i8], [3 x i8]* @.str, i64 0, i64 0), i32* noundef nonnull %1), !dbg !30
  %4 = icmp eq i32 %3, 1, !dbg !31
  br i1 %4, label %8, label %5, !dbg !30

5:                                                ; preds = %0
  %6 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !dbg !32, !tbaa !33
  %7 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.1, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %6) #8, !dbg !37
  br label %52, !dbg !38

8:                                                ; preds = %0
  %9 = load i32, i32* %1, align 4, !dbg !39, !tbaa !40
  %10 = icmp ugt i32 %9, 20, !dbg !42
  br i1 %10, label %11, label %14, !dbg !42

11:                                               ; preds = %8
  %12 = load %struct._IO_FILE*, %struct._IO_FILE** @stderr, align 8, !dbg !43, !tbaa !33
  %13 = call i64 @fwrite(i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str.2, i64 0, i64 0), i64 21, i64 1, %struct._IO_FILE* %12) #8, !dbg !44
  br label %52, !dbg !45

14:                                               ; preds = %8
  %15 = icmp eq i32 %9, 0, !dbg !46
  br i1 %15, label %47, label %16, !dbg !48

16:                                               ; preds = %14
  %17 = icmp ult i32 %9, 4, !dbg !48
  br i1 %17, label %32, label %18, !dbg !48

18:                                               ; preds = %16
  %19 = and i32 %9, -4, !dbg !48
  %20 = sub i32 %19, 4, !dbg !49
  %21 = lshr i32 %20, 2, !dbg !49
  %22 = shl i32 %20, 30, !dbg !49
  %23 = or i32 %21, %22, !dbg !49
  switch i32 %23, label %24 [
    i32 0, label %28
    i32 1, label %25
    i32 2, label %26
    i32 3, label %27
  ], !dbg !49

24:                                               ; preds = %18
  br label %28

25:                                               ; preds = %18
  br label %28, !dbg !48

26:                                               ; preds = %18
  br label %28, !dbg !48

27:                                               ; preds = %18
  br label %28, !dbg !48

28:                                               ; preds = %18, %27, %26, %25, %24
  %29 = phi <4 x i32> [ <i32 5, i32 -8, i32 11, i32 -14>, %18 ], [ <i32 145, i32 -160, i32 175, i32 -190>, %24 ], [ <i32 22, i32 -28, i32 34, i32 -40>, %25 ], [ <i32 51, i32 -60, i32 69, i32 -78>, %26 ], [ <i32 92, i32 -104, i32 116, i32 -128>, %27 ], !dbg !50
  %30 = call i32 @llvm.vector.reduce.add.v4i32(<4 x i32> %29), !dbg !48
  %31 = icmp eq i32 %9, %19, !dbg !48
  br i1 %31, label %47, label %32, !dbg !48

32:                                               ; preds = %16, %28
  %33 = phi i32 [ 0, %16 ], [ %30, %28 ]
  %34 = phi i32 [ 0, %16 ], [ %19, %28 ]
  br label %35, !dbg !48

35:                                               ; preds = %32, %35
  %36 = phi i32 [ %44, %35 ], [ %33, %32 ]
  %37 = phi i32 [ %45, %35 ], [ %34, %32 ]
  %38 = mul nuw nsw i32 %37, 3, !dbg !51
  %39 = add nuw nsw i32 %38, 5, !dbg !53
  %40 = and i32 %37, 1, !dbg !54
  %41 = icmp eq i32 %40, 0, !dbg !55
  %42 = sub nuw nsw i32 -5, %38, !dbg !50
  %43 = select i1 %41, i32 %39, i32 %42, !dbg !50
  %44 = add i32 %43, %36, !dbg !50
  %45 = add nuw nsw i32 %37, 1, !dbg !49
  %46 = icmp eq i32 %45, %9, !dbg !46
  br i1 %46, label %47, label %35, !dbg !48, !llvm.loop !56

47:                                               ; preds = %35, %28, %14
  %48 = phi i32 [ 0, %14 ], [ %30, %28 ], [ %44, %35 ], !dbg !58
  %49 = call i32 @add_bonus(i32 noundef %48) #7, !dbg !59
  %50 = load i32, i32* %1, align 4, !dbg !60, !tbaa !40
  %51 = call i32 (i8*, ...) @printf(i8* noundef nonnull dereferenceable(1) getelementptr inbounds ([33 x i8], [33 x i8]* @.str.3, i64 0, i64 0), i32 noundef %50, i32 noundef %48, i32 noundef %49), !dbg !61
  br label %52

52:                                               ; preds = %47, %11, %5
  %53 = phi i32 [ 1, %5 ], [ 2, %11 ], [ 0, %47 ], !dbg !62
  call void @llvm.lifetime.end.p0i8(i64 4, i8* nonnull %2) #7, !dbg !63
  ret i32 %53, !dbg !63
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

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4}
!llvm.ident = !{!5}

!0 = distinct !DICompileUnit(language: DW_LANG_C99, file: !1, producer: "Ubuntu clang version 14.0.0-1ubuntu1.1", isOptimized: true, runtimeVersion: 0, emissionKind: LineTablesOnly, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "<PROJECT>/src/toolchain/main.c", directory: "<PROJECT>")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 1, !"wchar_size", i32 4}
!4 = !{i32 7, !"uwtable", i32 1}
!5 = !{!"Ubuntu clang version 14.0.0-1ubuntu1.1"}
!6 = distinct !DISubprogram(name: "alternating_sum", scope: !7, file: !7, line: 10, type: !8, scopeLine: 11, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !9)
!7 = !DIFile(filename: "src/toolchain/main.c", directory: "<PROJECT>")
!8 = !DISubroutineType(types: !9)
!9 = !{}
!10 = !DILocation(line: 13, column: 23, scope: !6)
!11 = !DILocation(line: 13, column: 5, scope: !6)
!12 = !DILocation(line: 13, column: 28, scope: !6)
!13 = !DILocation(line: 7, column: 18, scope: !14, inlinedAt: !15)
!14 = distinct !DISubprogram(name: "scale_and_bias", scope: !7, file: !7, line: 5, type: !8, scopeLine: 6, flags: DIFlagPrototyped, spFlags: DISPFlagLocalToUnit | DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !9)
!15 = distinct !DILocation(line: 14, column: 20, scope: !6)
!16 = !DILocation(line: 7, column: 22, scope: !14, inlinedAt: !15)
!17 = !DILocation(line: 15, column: 15, scope: !6)
!18 = !DILocation(line: 15, column: 19, scope: !6)
!19 = !DILocation(line: 15, column: 13, scope: !6)
!20 = distinct !{!20, !11, !21, !22, !23}
!21 = !DILocation(line: 20, column: 5, scope: !6)
!22 = !{!"llvm.loop.mustprogress"}
!23 = !{!"llvm.loop.isvectorized", i32 1}
!24 = !DILocation(line: 0, scope: !6)
!25 = !DILocation(line: 21, column: 5, scope: !6)
!26 = distinct !{!26, !11, !21, !22, !27, !23}
!27 = !{!"llvm.loop.unroll.runtime.disable"}
!28 = distinct !DISubprogram(name: "main", scope: !7, file: !7, line: 24, type: !8, scopeLine: 25, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition | DISPFlagOptimized, unit: !0, retainedNodes: !9)
!29 = !DILocation(line: 26, column: 5, scope: !28)
!30 = !DILocation(line: 27, column: 9, scope: !28)
!31 = !DILocation(line: 27, column: 25, scope: !28)
!32 = !DILocation(line: 28, column: 41, scope: !28)
!33 = !{!34, !34, i64 0}
!34 = !{!"any pointer", !35, i64 0}
!35 = !{!"omnipotent char", !36, i64 0}
!36 = !{!"Simple C/C++ TBAA"}
!37 = !DILocation(line: 28, column: 9, scope: !28)
!38 = !DILocation(line: 29, column: 9, scope: !28)
!39 = !DILocation(line: 31, column: 9, scope: !28)
!40 = !{!41, !41, i64 0}
!41 = !{!"int", !35, i64 0}
!42 = !DILocation(line: 31, column: 15, scope: !28)
!43 = !DILocation(line: 32, column: 41, scope: !28)
!44 = !DILocation(line: 32, column: 9, scope: !28)
!45 = !DILocation(line: 33, column: 9, scope: !28)
!46 = !DILocation(line: 13, column: 23, scope: !6, inlinedAt: !47)
!47 = distinct !DILocation(line: 35, column: 15, scope: !28)
!48 = !DILocation(line: 13, column: 5, scope: !6, inlinedAt: !47)
!49 = !DILocation(line: 13, column: 28, scope: !6, inlinedAt: !47)
!50 = !DILocation(line: 15, column: 13, scope: !6, inlinedAt: !47)
!51 = !DILocation(line: 7, column: 18, scope: !14, inlinedAt: !52)
!52 = distinct !DILocation(line: 14, column: 20, scope: !6, inlinedAt: !47)
!53 = !DILocation(line: 7, column: 22, scope: !14, inlinedAt: !52)
!54 = !DILocation(line: 15, column: 15, scope: !6, inlinedAt: !47)
!55 = !DILocation(line: 15, column: 19, scope: !6, inlinedAt: !47)
!56 = distinct !{!56, !48, !57, !22, !27, !23}
!57 = !DILocation(line: 20, column: 5, scope: !6, inlinedAt: !47)
!58 = !DILocation(line: 0, scope: !6, inlinedAt: !47)
!59 = !DILocation(line: 36, column: 20, scope: !28)
!60 = !DILocation(line: 37, column: 49, scope: !28)
!61 = !DILocation(line: 37, column: 5, scope: !28)
!62 = !DILocation(line: 0, scope: !28)
!63 = !DILocation(line: 39, column: 1, scope: !28)
