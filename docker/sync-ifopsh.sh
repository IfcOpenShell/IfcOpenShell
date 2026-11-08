#!/usr/bin/env bash
# Sync the locally built IfcOpenShell artefacts (native WASM build + TypeScript
# API reference) out of the ifcos-docs image so they can be browsed and debugged.
#
#   ./sync-ifopsh.sh           # extract, then serve on http://localhost:8000
#   ./sync-ifopsh.sh extract   # extract only
#
# Overridable: IFOPSH_IMAGE, IFOPSH_DEST, IFOPSH_PORT
set -euo pipefail

IMAGE="${IFOPSH_IMAGE:-ifcos-docs}"
DEST="${IFOPSH_DEST:-$HOME/ifopsh}"
PORT="${IFOPSH_PORT:-8000}"

mkdir -p "$DEST"
docker rm -f ifcos-artifacts >/dev/null 2>&1 || true
docker create --name ifcos-artifacts "$IMAGE" >/dev/null
docker cp ifcos-artifacts:/artifacts/. "$DEST"
docker rm ifcos-artifacts >/dev/null

echo "synced into $DEST:"
ls -1 "$DEST"

if [ "${1:-serve}" = "extract" ]; then
    exit 0
fi

echo
echo "TypeScript API : http://localhost:${PORT}/typescript-api/index.html"
echo "WASM module    : http://localhost:${PORT}/wasm/ifcopenshell_wasm.mjs"
echo "Three.js demo  : http://localhost:${PORT}/demo/ifcopenshell-js/examples/threejs.html"
echo "scratch page   : http://localhost:${PORT}/inspect.html"
echo

cd "$DEST"
exec python -m http.server "$PORT"
