#!/usr/bin/bash
set -ex

PYODIDE_VERSION=0.29.3
PYODIDE_BUILD_VERSION=0.33.0
PYODIDE_XBUILDENV_ROOT="${HOME}/.cache/.pyodide-xbuildenv-${PYODIDE_BUILD_VERSION}"
PYODIDE_XBUILDENV="${PYODIDE_XBUILDENV_ROOT}/${PYODIDE_VERSION}"

# Script is assuming that it will be possible to execute it multiple times
# therefore we're clearing venv each time and ignoring existing 'emsdk' folder.

# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.13 --clear
source .venv/bin/activate

# Install pyodide cross build environment.
# Instructions: https://pyodide.org/en/stable/development/building-packages.html
uv pip install "pyodide-build==${PYODIDE_BUILD_VERSION}"
# `uv run` is required, so xbuildenv would skip using `pip`.
uv run pyodide xbuildenv install "${PYODIDE_VERSION}"
uv run pyodide xbuildenv install-emscripten

EMSDK_ROOT="${PYODIDE_XBUILDENV}/emsdk"
source "${EMSDK_ROOT}/emsdk_env.sh"
which emcc
emcc --version

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
