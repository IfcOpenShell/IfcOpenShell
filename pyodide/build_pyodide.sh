#!/usr/bin/bash
set -ex

# Script is assuming that it will be possible to execute it multiple times
# therefore we're clearing venv each time and ignoring existing 'emsdk' folder.

# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.13 --clear
source .venv/bin/activate

# Install pyodide cross build environment.
# Instructions: https://pyodide.org/en/stable/development/building-packages.html
uv pip install pyodide-build
# `uv run` is required, so xbuildenv would skip using `pip`.
uv run pyodide xbuildenv install
uv run pyodide xbuildenv install-emscripten

EMSDK_ROOT=$(pyodide config get emscripten_dir)
[ -f ${EMSDK_ROOT}/emsdk_env.sh ] && source ${EMSDK_ROOT}/emsdk_env.sh
[ -f ${EMSDK_ROOT}/../../emsdk_env.sh ] && source ${EMSDK_ROOT}/../../emsdk_env.sh
which emcc

mkdir -p packages/ifcopenshell
VERSION=`cat IfcOpenShell/VERSION`
cp IfcOpenShell/pyodide/meta.yaml packages/ifcopenshell
sed -i s/0.8.0/$VERSION/g packages/ifcopenshell/meta.yaml

# Use custom build ifcopenshell directory in build-all to make caching simpler
# Otherwise pyodide build path typically includes package version, so cached cmake configs might break.
export BUILD_DIR=`readlink -f ifcopenshell_build`

# Use build-recipes-no-deps first, so logs would be printed to stdout.
pyodide build-recipes-no-deps ifcopenshell
pyodide build-recipes ifcopenshell --install
