#!/usr/bin/bash
set -ex

PYODIDE_VERSION=0.29.3
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Script is assuming that it will be possible to execute it multiple times
# therefore we're clearing venv each time and ignoring existing 'emsdk' folder.

# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.13 --clear
source .venv/bin/activate

# Install pyodide cross build environment.
# Instructions: https://pyodide.org/en/stable/development/building-packages.html
uv pip install -r "${SCRIPT_DIR}/requirements.txt"
# `uv run` is required, so xbuildenv would skip using `pip`.
uv run pyodide xbuildenv install "${PYODIDE_VERSION}"
uv run pyodide xbuildenv install-emscripten

# Cache path includes a hash segment that varies by pyodide-build version,
# so query it instead of constructing it manually.
EMSDK_ROOT=$(uv run pyodide config get emsdk_dir)
[ -f "${EMSDK_ROOT}/emsdk_env.sh" ] && source "${EMSDK_ROOT}/emsdk_env.sh"
[ -f "${EMSDK_ROOT}/../../emsdk_env.sh" ] && source "${EMSDK_ROOT}/../../emsdk_env.sh"
which emcc
emcc --version

mkdir -p packages/ifcopenshell
VERSION=`cat IfcOpenShell/VERSION`
# Normalize to the canonical PEP 440 form (e.g. 0.9.0alpha0 -> 0.9.0a0).
VERSION=`python3 -c "from packaging.version import Version; print(Version('$VERSION'))"`
cp IfcOpenShell/pyodide/meta.yaml packages/ifcopenshell
sed -i s/9.9.9/$VERSION/g packages/ifcopenshell/meta.yaml

# Use custom build ifcopenshell directory in build-all to make caching simpler
# Otherwise pyodide build path typically includes package version, so cached cmake configs might break.
export BUILD_DIR=`readlink -f ifcopenshell_build`

# Sat, 25 Apr 2026 12:11:39 GMT 2026-04-25 12:11:39,173 - DEBUG - running
# command `make -j5 ifcopenshell_wrapper VERBOSE=1` in directory
# '/home/runner/work/IfcOpenShell/IfcOpenShell/ifcopenshell_build/Linux/wasm/build/ifcopenshell/build'
# Sat, 25 Apr 2026 12:18:01 GMT Error: Process completed with exit code 143.
export IFCOS_NUM_BUILD_PROCS=1

# Use build-recipes-no-deps first, so logs would be printed to stdout.
pyodide build-recipes-no-deps ifcopenshell
pyodide build-recipes ifcopenshell --install
