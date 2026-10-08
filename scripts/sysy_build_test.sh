#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
mkdir -p artifacts/sysy/{bin,objects,logs,reference}
exec > >(tee artifacts/sysy/build.log) 2>&1
set -x
date -u +%FT%TZ
uname -a
clang-14 --version
llc-14 --version
riscv64-linux-gnu-gcc --version
qemu-riscv64 --version
sha256sum runtime/sylib.c runtime/sylib.h runtime/LICENSE.upstream
# Upstream header contains tentative definitions: retain it unchanged and use -fcommon.
riscv64-linux-gnu-gcc -std=c11 -O2 -fcommon -march=rv64gc -mabi=lp64d -c runtime/sylib.c -o artifacts/sysy/objects/sylib.o
riscv64-linux-gnu-ar rcs artifacts/sysy/objects/libsylib.a artifacts/sysy/objects/sylib.o
for name in control_matrix float_stats; do
  clang-14 --target=riscv64-linux-gnu --gcc-toolchain=/usr -march=rv64gc -mabi=lp64d -std=c11 -fcommon -ffp-contract=off -O0 -x c -include runtime/sylib.h -c "src/sysy/$name.sy" -o "artifacts/sysy/objects/$name.source.o"
  llvm-as-14 "src/llvm/$name.ll" -o "artifacts/sysy/objects/$name.bc"
  opt-14 -verify -disable-output "artifacts/sysy/objects/$name.bc"
  llc-14 -O0 -mtriple=riscv64-linux-gnu -mattr=+m,+a,+f,+d,+c -target-abi=lp64d -filetype=obj "artifacts/sysy/objects/$name.bc" -o "artifacts/sysy/objects/$name.llvm.o"
  riscv64-linux-gnu-gcc -march=rv64gc -mabi=lp64d -c "src/riscv/$name.S" -o "artifacts/sysy/objects/$name.asm.o"
  for kind in source llvm asm; do
    riscv64-linux-gnu-gcc -static -no-pie -march=rv64gc -mabi=lp64d "artifacts/sysy/objects/$name.$kind.o" artifacts/sysy/objects/libsylib.a -Wl,-Map,"artifacts/sysy/$name.$kind.map" -o "artifacts/sysy/bin/$name.$kind"
    riscv64-linux-gnu-readelf -h -A "artifacts/sysy/objects/$name.$kind.o" > "artifacts/sysy/$name.$kind.elf.txt"
    riscv64-linux-gnu-nm -u "artifacts/sysy/objects/$name.$kind.o" > "artifacts/sysy/$name.$kind.undefined.txt"
    riscv64-linux-gnu-objdump -dr "artifacts/sysy/objects/$name.$kind.o" > "artifacts/sysy/$name.$kind.disasm.txt"
  done
  # Compiler exports are clearly separated; they are reference material only.
  clang-14 --target=riscv64-linux-gnu --gcc-toolchain=/usr -march=rv64gc -mabi=lp64d -std=c11 -fcommon -ffp-contract=off -O0 -x c -include runtime/sylib.h -S -emit-llvm "src/sysy/$name.sy" -o "artifacts/sysy/reference/$name.clang.ll"
  clang-14 --target=riscv64-linux-gnu --gcc-toolchain=/usr -march=rv64gc -mabi=lp64d -std=c11 -fcommon -ffp-contract=off -O0 -x c -include runtime/sylib.h -S "src/sysy/$name.sy" -o "artifacts/sysy/reference/$name.clang.s"
done
python3 tests/sysy_oracle.py
python3 scripts/sysy_mutation_check.py
sha256sum src/sysy/* src/llvm/* src/riscv/* tests/sysy_oracle.py > artifacts/sysy/source-sha256.txt
