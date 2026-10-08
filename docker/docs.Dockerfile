# This file was generated with the assistance of an AI coding tool.
#
# Local companion to .github/workflows/ifcopenshell-docs.yml: produces the
# TypeScript API reference and exports the native WASM artefacts so they can be
# inspected in a browser. It reuses the BuildKit cache mount of
# docker/native-wasm.Dockerfile, so the WASM build does not run again.

FROM node:24-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY . /src

ENV IFCOPENSHELL_WASM_DIR=/__w/ifcopenshell_build/Linux/wasm/build/ifcopenshell/build/ifcwrap/wasm

RUN --mount=type=cache,target=/__w/ifcopenshell_build \
    test -d "${IFCOPENSHELL_WASM_DIR}" \
    && cd src/ts/ifcopenshell-wasm \
    && npm ci \
    && npm run stage \
    && cd ../ifcopenshell-js \
    && npm ci \
    && npm run build \
    && npm run docs \
    && mkdir -p /artifacts/demo/ifcopenshell-js \
    && cp -r docs/api /artifacts/typescript-api \
    && cp -r "${IFCOPENSHELL_WASM_DIR}" /artifacts/wasm \
    && cp -r dist examples /artifacts/demo/ifcopenshell-js/ \
    && cp -r ../ifcopenshell-wasm/. /artifacts/demo/ifcopenshell-wasm/ \
    && rm -rf /artifacts/demo/ifcopenshell-wasm/node_modules \
    && ls -la /artifacts /artifacts/typescript-api | head -40
