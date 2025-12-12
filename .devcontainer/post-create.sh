#!/usr/bin/env bash
# .devcontainer/post-create.sh
# Runs once after the container is created.

set -euo pipefail

WORKSPACE="/workspaces/IfcOpenShell"
BUILD_DIR="$WORKSPACE/build"

echo "==> Setting up IfcOpenShell build environment..."

# ── 1. Create build directory ─────────────────────────────────────────────────
mkdir -p "$BUILD_DIR"

# ── 2. Run CMake configuration ────────────────────────────────────────────────
# Adjust flags here if your layout or dependencies differ.
cmake -S "$WORKSPACE/cmake" -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DOCC_INCLUDE_DIR=/usr/include/opencascade \
    -DOCC_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu \
    -DLIBXML2_INCLUDE_DIR=/usr/include/libxml2 \
    -DLIBXML2_LIBRARIES=/usr/lib/x86_64-linux-gnu/libxml2.so \
    -DUSERSPACE_PYTHON_PREFIX=ON \
    -DCOLLADA_SUPPORT=OFF \
    -DBUILD_IFCPYTHON=ON \
    -G Ninja \
    || echo "[WARN] CMake configuration failed — check dependency paths and re-run manually."

echo ""
echo "==> Build environment ready!"
echo "    To compile:   cmake --build build -j\$(nproc)"
echo "    To run tests: cd build && ctest --output-on-failure"
