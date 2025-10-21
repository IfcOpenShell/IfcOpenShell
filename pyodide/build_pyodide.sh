#!/usr/bin/bash
set -e
cd pyodide
make
cd ..
mkdir -p packages/ifcopenshell
cp IfcOpenShell/pyodide/meta.yaml packages/ifcopenshell
# Required, otherwise pyodide will create new temp pyodide environment.
export PYODIDE_ROOT=/src/pyodide
# Ensure emsdk tools are in PATH.
export PATH=$PYODIDE_ROOT/emsdk/emsdk:$PYODIDE_ROOT/emsdk/emsdk/node/22.16.0_64bit/bin:$PYODIDE_ROOT/emsdk/emsdk/upstream/emscripten:$PATH
# Use custom build ifcopenshell directory in build-all to make caching simpler
# Otherwise pyodide build path typically includes package version, so cached cmake configs might break.
export BUILD_DIR=/src/ifcopenshell_build
pyodide build-recipes ifcopenshell --install
