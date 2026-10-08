# AscendNPU IR sources and provenance

`official/` is a read-only downloaded subset from Ascend/AscendNPU-IR commit
`37c6ebc33d1789500014e6a7b2b62164b3cb566b` (master observed 2026-10-03).
`official-tool-1.1.0/` is a read-only downloaded subset from commit
`428ab8fdab46a879c7349caba4cde705bc8c9bb6` (`v1.1.0-post2`), matching the
actual `bishengir-opt --version` and `bishengir-compile --version` output.

The experiment executes the latter version's unmodified `add.mlir`. Both copies
have identical bytes, SHA-256:
`bf6be387f569d6178346e4beabf9dcc156ea8cdc862a8e5c5f5ce8e9119b1750`.

These are upstream files, not student-authored compiler implementations. The
original `LICENSE` and `NOTICE` are retained in each subset. Apache-2.0 notices
in source files are unchanged. Exact URLs and file hashes are recorded in
`artifacts/mlir/sources/source-manifest.json` and
`artifacts/mlir/sources/tool-source-manifest.json`.

The official 1.1.0 wheel is cached outside the submission tree under the WSL
user's `~/.cache/compiler-coursework/ascendnpu-ir-1.1.0/`; it is verified by the
fixed SHA-256 in `scripts/mlir_prepare_wheel.py`. No system Python or LLVM
installation is changed by this unpacking operation.

Locally authored experiment scripts are `scripts/mlir_*.py`; their output
MLIR and logs live under `artifacts/mlir/`. The device compile is explicitly
marked blocked despite process exit 0 because `hivmc` is unavailable and no
kernel object exists. No device execution output is supplied or claimed.
