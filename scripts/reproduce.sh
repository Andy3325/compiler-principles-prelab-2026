#!/usr/bin/env bash
# Portable entry point for the published experiment sources.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bash scripts/reproduce.sh [--extended]

Run the recorded baseline toolchain, SysY and Ascend host-side experiments.
--extended also runs optimization diagnostics, nine controlled compiler
configurations, and twelve GDB boundary-path checks, in that order.

Requires the Ubuntu/WSL dependencies listed in README.md. It rebuilds generated
artifacts but does not compile the report, regenerate figures, or run a device
kernel. The Ascend backend blockage is recorded separately from host success.
EOF
}

extended=false
case "${1:-}" in
  "") ;;
  --extended) extended=true ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac
if (( $# > 1 )); then usage >&2; exit 2; fi

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
# Empty generated directories are not retained by Git.
mkdir -p artifacts/mlir/sources
bash scripts/run_all.sh
if [[ "$extended" == true ]]; then
  python3 scripts/toolchain_mechanism.py
  python3 scripts/toolchain_extended_experiment.py
  python3 scripts/toolchain_extended_boundary.py
fi
