#!/usr/bin/bash
set -ex

# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.13
source .venv/bin/activate

# Install pyodide cross build environment.
# Instructions: https://pyodide.org/en/stable/development/building-packages.html
uv pip install pyodide-build
# `uv run` is required, so xbuildenv would skip using `pip`.
uv run pyodide xbuildenv install

# Emscripten doesn't come with xbuildenv.
git clone https://github.com/emscripten-core/emsdk
pushd emsdk
PYODIDE_EMSCRIPTEN_VERSION=$(pyodide config get emscripten_version)
./emsdk install ${PYODIDE_EMSCRIPTEN_VERSION}
./emsdk activate ${PYODIDE_EMSCRIPTEN_VERSION}
source emsdk_env.sh
which emcc
popd

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
