#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$ROOT/artifacts/environment"
{
  printf 'Collected at: '; TZ=Asia/Shanghai date --iso-8601=seconds
  uname -a
  cat /etc/os-release
  printf '\nTool versions\n'
  gcc --version | head -n 1
  clang-14 --version
  llvm-as-14 --version | head -n 3
  opt-14 --version | head -n 3
  llc-14 --version | head -n 3
  riscv64-linux-gnu-gcc --version | head -n 1
  riscv64-linux-gnu-as --version | head -n 3
  qemu-riscv64 --version
  mlir-opt-14 --version
  python3 --version
  printf '\nInstalled packages\n'
  dpkg-query -W gcc clang-14 llvm-14 gcc-riscv64-linux-gnu gcc-11-riscv64-linux-gnu binutils-riscv64-linux-gnu libc6-dev-riscv64-cross qemu-user mlir-14-tools
  printf '\nWSL path\n%s\n' "$ROOT"
  printf '\nResources\n'
  free -h
  df -h /
} > "$ROOT/artifacts/environment/versions.txt" 2>&1
cat "$ROOT/artifacts/environment/versions.txt"
