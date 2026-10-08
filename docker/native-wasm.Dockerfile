# syntax=docker/dockerfile:1

# Local mirror of .github/workflows/build-ifcopenshell-native-wasm.yml.
#
# `docker build` runs the workflow's steps in the same order, so a build that
# succeeds means the workflow's build and verification steps pass. The steps
# that only make sense on CI are deliberately not reproduced: the ccache
# action, uploading the artifacts, and committing the refreshed dependency
# cache back to IfcOpenShell/build-outputs.
#
# The dependency cache and the IfcOpenShell build tree live in a BuildKit cache
# mount, so a failed build can be retried without redoing the emsdk bootstrap
# and the dependency builds.

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# The workflow inherits most of this toolchain from the ubuntu-22.04 runner
# image, the plain base image needs it installed explicitly.
RUN apt-get update && apt-get install -y --no-install-recommends \
        autoconf automake bison byacc build-essential bzip2 ca-certificates ccache \
        cmake curl git gnupg libtool m4 ninja-build patch pkg-config python3 \
        python3-venv rsync software-properties-common tar unzip wget xz-utils \
    && rm -rf /var/lib/apt/lists/*

# "Install Clang" step. The binding generator's `clang` bindings are pinned in
# pyproject.toml and need a matching libclang, which is newer than the
# distribution Clang, so the LLVM repository's Clang is registered as the
# default one. `software-properties-common` above stands in for the runner
# image's `add-apt-repository`.
RUN wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | tee /etc/apt/trusted.gpg.d/apt.llvm.org.asc > /dev/null \
    && add-apt-repository -y "deb http://apt.llvm.org/jammy/ llvm-toolchain-jammy-21 main" \
    && apt-get update \
    && apt-get install -y --no-install-recommends clang-21 libclang-21-dev \
    && update-alternatives --install /usr/bin/clang++ clang++ /usr/lib/llvm-21/bin/clang++ 200 \
    && rm -rf /var/lib/apt/lists/*

# "Set up Node" step. Taken from the official image because the distribution's
# Node is too old for the test runner.
COPY --from=node:24 /usr/local/bin/node /usr/local/bin/node
COPY --from=node:24 /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# "Set up uv" step.
COPY --from=ghcr.io/astral-sh/uv:0.11.27 /uv /uvx /usr/local/bin/

# "Install Python" step. Installs the latest Python version so it is preferred
# by uv over the distribution's older one, which the repository's scripts need.
RUN uv python install

WORKDIR /__w
COPY . /__w/IfcOpenShell

# The workflow's "Checkout Repository" step uses `submodules: recursive`; the
# build needs `src/svgfill/3rdparty/svgpp` for the SVG serializer.
RUN git -C /__w/IfcOpenShell submodule update --init --recursive

# "Checkout Build Repository" step. The repository is public, so the workflow's
# BUILD_REPO_TOKEN is not required here.
# "Unpack Dependencies" and "Build" steps.
#
# The workflow inherits `cpu_count + 1` build jobs from its runner; that is more
# parallel emscripten/OCCT compilation than this container's memory allows, so
# the job count is bounded explicitly.
ENV BUILD_DIR=/__w/ifcopenshell_build
ENV IFCOS_NUM_BUILD_PROCS=6

ARG IFCOS_CMAKE_ARGS=""

RUN --mount=type=cache,target=/__w/ifcopenshell_build \
    set -eux; \
    if [ ! -d /__w/ifcopenshell_build/.git ]; then \
        git clone --depth 1 --branch wasm-native \
            https://github.com/IfcOpenShell/build-outputs.git /__w/ifcopenshell_build; \
    fi; \
    cd /__w/ifcopenshell_build; \
    uv run ../IfcOpenShell/nix/cache_dependencies.py unpack; \
    cd /__w/IfcOpenShell; \
    IFCOS_CMAKE_ARGS="${IFCOS_CMAKE_ARGS}" uv run --with clang==21.1.7 ./nix/build-all.py -v --native-wasm --build-cfg Release

# "Verify artifacts" step.
RUN --mount=type=cache,target=/__w/ifcopenshell_build \
    cd /__w/IfcOpenShell \
    && python3 .github/scripts/verify-wasm-artifacts.py \
        /__w/ifcopenshell_build/Linux/wasm/build/ifcopenshell/build/ifcwrap/wasm

# "Run the basic I/O tests" step. `tests/io.test.ts` is the port of
# `test/tests.py` and drives the artifacts built above through the TypeScript API.
ENV IFCOPENSHELL_WASM_DIR=/__w/ifcopenshell_build/Linux/wasm/build/ifcopenshell/build/ifcwrap/wasm

RUN --mount=type=cache,target=/__w/ifcopenshell_build \
    cd /__w/IfcOpenShell/src/ts/ifcopenshell-wasm \
    && npm ci \
    && npm run stage \
    && cd ../ifcopenshell-js \
    && npm ci \
    && npm run build \
    && npm test -- tests/io.test.ts
