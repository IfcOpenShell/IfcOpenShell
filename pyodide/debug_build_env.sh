#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: $0 <pyodide_root>"
  exit 1
fi
export PYODIDE_ROOT=$(readlink -f "$1")
export PATH="$PYODIDE_ROOT/emsdk/emsdk:$PYODIDE_ROOT/emsdk/emsdk/node/22.16.0_64bit/bin:$PYODIDE_ROOT/emsdk/emsdk/upstream/emscripten:$PATH"
# build-all.py vars.
export WASM_PYTHON_PATH="$PYODIDE_ROOT/cpython/installs/python-3.13.2"
export WASM_TOOLCHAIN_FILE="$PYODIDE_ROOT/pyodide-build/pyodide_build/tools/cmake/Modules/Platform/Emscripten.cmake"
