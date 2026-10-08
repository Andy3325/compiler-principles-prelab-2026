module attributes {hivm.module_core_type = #hivm.module_core_type<AIV>} {
  func.func private @load_gm_to_ubuf_1d_int16_t(memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, i32, i16, index) attributes {hacc.always_inline, hivm.func_core_type = #hivm.func_core_type<AIV>, llvm.emit_c_interface}
  func.func private @vadd_1d_int16_t(memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>) attributes {hacc.always_inline, hivm.func_core_type = #hivm.func_core_type<AIV>, llvm.emit_c_interface}
  func.func private @store_ubuf_to_gm_1d_int16_t(memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>, i32) attributes {hacc.always_inline, hivm.func_core_type = #hivm.func_core_type<AIV>, llvm.emit_c_interface}
  func.func @add(%arg0: memref<16xi16, #hivm.address_space<gm>>, %arg1: memref<16xi16, #hivm.address_space<gm>>, %arg2: memref<16xi16, #hivm.address_space<gm>>) attributes {hacc.entry, hacc.function_kind = #hacc.function_kind<DEVICE>, hivm.func_core_type = #hivm.func_core_type<AIV>} {
    %c0 = arith.constant 0 : index
    %c0_i16 = arith.constant 0 : i16
    %c0_i32 = arith.constant 0 : i32
    %c32_i64 = arith.constant 32 : i64
    %c0_i64 = arith.constant 0 : i64
    %0 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
    %cast = memref.cast %arg0 : memref<16xi16, #hivm.address_space<gm>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>
    %cast_0 = memref.cast %0 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    call @load_gm_to_ubuf_1d_int16_t(%cast, %cast_0, %c0_i32, %c0_i16, %c0) : (memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, i32, i16, index) -> ()
    %1 = hivm.hir.pointer_cast(%c32_i64) : memref<16xi16, #hivm.address_space<ub>>
    %cast_1 = memref.cast %arg1 : memref<16xi16, #hivm.address_space<gm>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>
    %cast_2 = memref.cast %1 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    call @load_gm_to_ubuf_1d_int16_t(%cast_1, %cast_2, %c0_i32, %c0_i16, %c0) : (memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, i32, i16, index) -> ()
    hivm.hir.set_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
    %2 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
    hivm.hir.wait_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
    %3 = hivm.hir.pointer_cast(%c0_i64) : memref<0xi16, #hivm.address_space<ub>>
    %cast_3 = memref.cast %0 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    %cast_4 = memref.cast %1 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    %cast_5 = memref.cast %2 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    %cast_6 = memref.cast %3 : memref<0xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    call @vadd_1d_int16_t(%cast_3, %cast_4, %cast_5, %cast_6) : (memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>) -> ()
    hivm.hir.set_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
    hivm.hir.wait_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
    %cast_7 = memref.cast %2 : memref<16xi16, #hivm.address_space<ub>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>
    %cast_8 = memref.cast %arg2 : memref<16xi16, #hivm.address_space<gm>> to memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>
    call @store_ubuf_to_gm_1d_int16_t(%cast_7, %cast_8, %c0_i32) : (memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<ub>>, memref<?xi16, strided<[?], offset: ?>, #hivm.address_space<gm>>, i32) -> ()
    hivm.hir.pipe_barrier[<PIPE_ALL>]
    return
  }
}

