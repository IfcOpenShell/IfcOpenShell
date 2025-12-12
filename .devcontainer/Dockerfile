FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# Install base tools
RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    wget \
    git \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install build tools and compilers
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    gcc \
    g++ \
    clang \
    clang-format \
    clangd \
    gdb \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install IfcOpenShell core dependencies
RUN apt-get update && apt-get install -y \
    libboost-all-dev \
    libicu-dev \
    libeigen3-dev \
    libhdf5-dev \
    libxml2-dev \
    libpcre3-dev \
    zlib1g-dev \
    libtbb-dev \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCASCADE (OCCT) — the geometry kernel
RUN apt-get update && apt-get install -y \
    libocct-foundation-dev \
    libocct-modeling-algorithms-dev \
    libocct-modeling-data-dev \
    libocct-ocaf-dev \
    libocct-visualization-dev \
    libocct-data-exchange-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python and SWIG for Python bindings
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Install useful Python packages for IFC development
RUN pip3 install --no-cache-dir \
    pytest \
    black \
    pylint \
    lark \
    numpy \
    requests

# Install optional: CGAL for advanced geometry operations
RUN apt-get update && apt-get install -y \
    libcgal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install optional: OpenGL / visualization support
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libftgl-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root vscode user (standard devcontainer pattern)
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd

USER vscode
WORKDIR /workspaces/IfcOpenShell