// -----// IR Dump After GraphSyncSolver (hivm-graph-sync-solver) ('func.func' operation: @add) //----- //
module attributes {dlti.target_system_spec = #dlti.target_system_spec<"NPU" : #hacc.target_device_spec<#dlti.dl_entry<"AI_CORE_COUNT", 24 : i32>, #dlti.dl_entry<"CUBE_CORE_COUNT", 24 : i32>, #dlti.dl_entry<"VECTOR_CORE_COUNT", 48 : i32>, #dlti.dl_entry<"UB_SIZE", 1572864 : i32>, #dlti.dl_entry<"L1_SIZE", 4194304 : i32>, #dlti.dl_entry<"L0A_SIZE", 524288 : i32>, #dlti.dl_entry<"L0B_SIZE", 524288 : i32>, #dlti.dl_entry<"L0C_SIZE", 1048576 : i32>, #dlti.dl_entry<"UB_ALIGN_SIZE", 256 : i32>, #dlti.dl_entry<"L1_ALIGN_SIZE", 256 : i32>, #dlti.dl_entry<"L0C_ALIGN_SIZE", 4096 : i32>>>, hacc.hivmc_compatible_print = false, hacc.hivmc_version = #hacc.hivmc_version<"0.0.0">, hivm.module_core_type = #hivm.module_core_type<AIV>} {
  func.func @add(%arg0: memref<16xi16, #hivm.address_space<gm>>, %arg1: memref<16xi16, #hivm.address_space<gm>>, %arg2: memref<16xi16, #hivm.address_space<gm>>) attributes {hacc.entry, hacc.function_kind = #hacc.function_kind<DEVICE>, hivm.func_core_type = #hivm.func_core_type<AIV>, hivm.storage_aligned} {
    %c32_i64 = arith.constant 32 : i64
    %c0_i64 = arith.constant 0 : i64
    hivm.hir.set_mask_norm
    %0 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
    hivm.hir.load ins(%arg0 : memref<16xi16, #hivm.address_space<gm>>) outs(%0 : memref<16xi16, #hivm.address_space<ub>>)
    %1 = hivm.hir.pointer_cast(%c32_i64) : memref<16xi16, #hivm.address_space<ub>>
    hivm.hir.load ins(%arg1 : memref<16xi16, #hivm.address_space<gm>>) outs(%1 : memref<16xi16, #hivm.address_space<ub>>)
    hivm.hir.set_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
    %2 = hivm.hir.pointer_cast(%c0_i64) : memref<16xi16, #hivm.address_space<ub>>
    hivm.hir.wait_flag[<PIPE_MTE2>, <PIPE_V>, <EVENT_ID0>]
    hivm.hir.vadd ins(%0, %1 : memref<16xi16, #hivm.address_space<ub>>, memref<16xi16, #hivm.address_space<ub>>) outs(%2 : memref<16xi16, #hivm.address_space<ub>>)
    hivm.hir.set_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
    hivm.hir.wait_flag[<PIPE_V>, <PIPE_MTE3>, <EVENT_ID0>]
    hivm.hir.store ins(%2 : memref<16xi16, #hivm.address_space<ub>>) outs(%arg2 : memref<16xi16, #hivm.address_space<gm>>)
    hivm.hir.pipe_barrier[<PIPE_ALL>]
    return
  }
}
