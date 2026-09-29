#!/usr/bin/env bash
# Minimal runner for ifcparse_fuzzer. See README.md for build instructions
# and an explanation of the ASan/UBSan options set below.
#
# Usage: run.sh [libFuzzer args...]
#   FUZZER_BIN=./build-fuzz/ifcfuzz/ifcparse_fuzzer ./run.sh corpus/
#
# Env overrides:
#   FUZZER_BIN   path to the built harness (default: ./build-fuzz/ifcfuzz/ifcparse_fuzzer)
#   SYMBOLIZER   path to llvm-symbolizer, if not already on PATH

set -euo pipefail

BIN="${FUZZER_BIN:-./build-fuzz/ifcfuzz/ifcparse_fuzzer}"

if [ ! -x "$BIN" ]; then
    echo "error: fuzzer binary not found or not executable: $BIN" >&2
    echo "build it first - see README.md in this directory" >&2
    exit 1
fi

SYM_OPT=""
if [ -n "${SYMBOLIZER:-}" ] && [ -x "$SYMBOLIZER" ]; then
    SYM_OPT=":external_symbolizer_path=$SYMBOLIZER"
fi

# detect_leaks defaults OFF: entity attribute parsing can still leak when
# malformed entity data follows a syntactically valid header (a narrower
# case than the old header-parse leak, which has been fixed). libFuzzer
# treats a leak like a crash and halts the whole session on the first one,
# so leak detection needs to run as a separate, deliberate, short pass
# instead of the default campaign mode.
export ASAN_OPTIONS="${ASAN_OPTIONS:-abort_on_error=1:symbolize=1:detect_leaks=0$SYM_OPT}"
export UBSAN_OPTIONS="${UBSAN_OPTIONS:-abort_on_error=1:print_stacktrace=1:symbolize=1$SYM_OPT}"

exec "$BIN" "$@"
