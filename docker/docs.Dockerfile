# syntax=docker/dockerfile:1
# This file was generated with the assistance of an AI coding tool.
#
# Build the unified Sphinx site (C++, Python, and TypeScript), reusing the
# WASM cache populated by docker/native-wasm.Dockerfile.

FROM node:24-trixie-slim AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv git doxygen graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY docs/requirements.txt /tmp/docs-requirements.txt
RUN python3 -m venv /opt/docs-venv \
    && /opt/docs-venv/bin/pip install --no-cache-dir -r /tmp/docs-requirements.txt
ENV PATH="/opt/docs-venv/bin:${PATH}"

COPY . /src

ENV IFCOPENSHELL_WASM_DIR=/__w/ifcopenshell_build/Linux/wasm/build/ifcopenshell/build/ifcwrap/wasm

RUN --mount=type=cache,target=/__w/ifcopenshell_build,sharing=locked \
    test -d "${IFCOPENSHELL_WASM_DIR}" \
    && cd src/ts/ifcopenshell-wasm \
    && npm ci \
    && npm run stage \
    && cd ../ifcopenshell-js \
    && npm ci \
    && npm run build \
    && npm run docs \
    && npm run docs:sphinx \
    && mkdir -p /artifacts/demo/ifcopenshell-js \
    && cp -r docs/api /artifacts/typescript-api \
    && cp -r "${IFCOPENSHELL_WASM_DIR}" /artifacts/wasm \
    && cp -r dist examples /artifacts/demo/ifcopenshell-js/ \
    && cp -r ../ifcopenshell-wasm/. /artifacts/demo/ifcopenshell-wasm/ \
    && rm -rf /artifacts/demo/ifcopenshell-wasm/node_modules

WORKDIR /src/docs
ARG SKIP_PYTHON_API=0
RUN SKIP_PYTHON_API="${SKIP_PYTHON_API}" PROJECT_NUMBER="$(git rev-parse --short HEAD)" sphinx-build -j 2 -b html . /artifacts/html \
    && test -s /artifacts/html/cpp-api.html \
    && test -s /artifacts/html/output/api/library_root.html \
    && { [ "${SKIP_PYTHON_API}" = "1" ] || test -s /artifacts/html/autoapi/ifcopenshell/index.html; } \
    && test -s /artifacts/html/output/typescript-api/index.html

FROM python:3.13-slim AS serve
COPY --from=build /artifacts /artifacts
WORKDIR /artifacts/html
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
