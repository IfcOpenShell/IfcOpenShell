#!/usr/bin/env bash
# Sync the IfcOpenShell TypeScript sources into the WSL checkout and rebuild the
# wrapper against the newest WASM artefacts.
#
# The artefacts come out of the local ifcos-docs image (docker/docs.Dockerfile),
# so a run always yields what the Docker build last produced rather than
# whatever happens to sit in the WSL build directory.
#
#   ./sync-ifopsh.sh          # extract artefacts, stage declarations, build wrapper
#   ./sync-ifopsh.sh extract  # extract artefacts only
#
# Overridable: IFOPSH_IMAGE, IFOPSH_DEST
set -euo pipefail

WIN=/mnt/c/Users/tkrij/Documents/AECgeeks/projects/ifcopenshell/sayan
WSL=/home/thomas/ifcopenshell-wasm-v0.9-source
IMAGE="${IFOPSH_IMAGE:-ifcos-docs}"
OUT="${IFOPSH_DEST:-$HOME/ifopsh}"

rsync -av --delete \
  --exclude=node_modules/ \
  --exclude=dist/ \
  --exclude=wasm/ \
  "$WIN/src/ts/" "$WSL/src/ts/"

docker rm -f ifcos-artifacts >/dev/null 2>&1 || true
docker create --name ifcos-artifacts "$IMAGE" >/dev/null
mkdir -p "$OUT"
rm -rf "$OUT/wasm" "$OUT/typescript-api" "$OUT/demo"
docker cp ifcos-artifacts:/artifacts/wasm "$OUT/"
docker cp ifcos-artifacts:/artifacts/typescript-api "$OUT/"
docker cp ifcos-artifacts:/artifacts/demo "$OUT/"
docker rm ifcos-artifacts >/dev/null

echo "artefacts: $OUT/wasm ($(du -sh "$OUT/wasm" | cut -f1))"
echo "docs     : $OUT/typescript-api/index.html"
echo "demo     : $OUT/demo/ifcopenshell-js/examples/threejs.html"

if [ "${1:-build}" = "extract" ]; then
    exit 0
fi

source /home/thomas/ifcopenshell-wasm-v0.9/env.sh
# The extracted artefacts win over the WSL build directory named by env.sh.
export IFCOPENSHELL_WASM_DIR="$OUT/wasm"

cd "$WSL"
npm run stage --prefix src/ts/ifcopenshell-wasm
npm run build --prefix src/ts/ifcopenshell-js
echo "wrapper built against: $(ls "$IFCOPENSHELL_WASM_DIR" | head -3 | tr '\n' ' ')"
