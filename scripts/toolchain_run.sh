#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$project_root/scripts/toolchain_experiment.py" "$@"
exec python3 "$project_root/scripts/toolchain_audit.py"
