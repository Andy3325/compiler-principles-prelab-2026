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
