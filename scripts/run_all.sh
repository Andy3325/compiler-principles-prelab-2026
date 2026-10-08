#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
bash scripts/collect_environment.sh
bash scripts/toolchain_run.sh
bash scripts/sysy_build_test.sh
python3 scripts/mlir_prepare_wheel.py
python3 scripts/mlir_probe.py
python3 scripts/mlir_run_ascend.py
python3 scripts/mlir_verify.py
python3 scripts/summarize_validation.py
