#!/usr/bin/env bash
#
# Build an IfcOpenShell RPM package on Fedora (and compatible RHEL/Rocky/Alma
# with EPEL enabled) using the system C++ toolchain and distribution packages.
#
# This mirrors the Debian-oriented `make package` flow used in CI
# (.github/workflows/ci-ifcopenshell-docker.yml) but resolves Fedora-specific
# library/include locations and produces an `.rpm` via CPack's RPM generator
# (see cmake/CMakeLists.txt). The resulting artifacts are written to
# <build-dir>/assets/.
#
# Usage:
#   fedora/build-rpm.sh [build-dir]
#
# Environment overrides:
#   BUILD_TYPE   CMake build type            (default: Release)
#   JOBS         Parallel build jobs         (default: nproc)
#   INSTALL_DEPS Install build deps via dnf  (default: 1; set 0 to skip)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${1:-${REPO_ROOT}/build-fedora}"
BUILD_TYPE="${BUILD_TYPE:-Release}"
JOBS="${JOBS:-$(nproc)}"
INSTALL_DEPS="${INSTALL_DEPS:-1}"

# Fedora/RHEL runtime + build dependencies. opencascade and hdf5 come from
# EPEL on RHEL-family distros.
DEPS=(
    gcc gcc-c++ make cmake git rpm-build
    boost-devel
    opencascade-devel
    hdf5-devel
    zlib-devel
    libxml2-devel
    cgal-devel
    gmp-devel
    mpfr-devel
    eigen3-devel
    json-devel
    swig
    pcre-devel
    python3-devel
    python3-pip
)

if [ "${INSTALL_DEPS}" = "1" ]; then
    echo "==> Installing build dependencies via dnf"
    SUDO=""
    if [ "$(id -u)" != "0" ]; then SUDO="sudo"; fi
    ${SUDO} dnf install -y "${DEPS[@]}"
fi

# Resolve Fedora-specific locations rather than hard-coding them, so the script
# keeps working across Fedora releases, Python versions and architectures.
LIBDIR="$(rpm --eval '%{_libdir}')"                       # e.g. /usr/lib64
LIB="$(rpm --eval '%{_lib}')"                             # e.g. lib64
PY="$(command -v python3)"
PY_INCLUDE="$(${PY} -c 'import sysconfig; print(sysconfig.get_path("include"))')"
PY_LIBDIR="$(${PY} -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
PY_LDLIBRARY="$(${PY} -c 'import sysconfig; print(sysconfig.get_config_var("LDLIBRARY"))')"
PY_LIBRARY="${PY_LIBDIR}/${PY_LDLIBRARY}"
PY_XY="$(${PY} -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
# Install the Python module to Fedora's system site-packages (kept relative to
# the /usr package prefix) so `import ifcopenshell` works without PYTHONPATH.
# Overrides the Debian-style "dist-packages" default in src/ifcwrap/CMakeLists.txt.
PY_MODULE_SUBDIR="${LIB}/python${PY_XY}/site-packages"    # e.g. lib64/python3.14/site-packages

echo "==> Configuring (build dir: ${BUILD_DIR}, type: ${BUILD_TYPE})"
echo "    libdir=${LIBDIR} python=${PY}"

mkdir -p "${BUILD_DIR}"
cmake -S "${REPO_ROOT}/cmake" -B "${BUILD_DIR}" \
    -DCMAKE_INSTALL_PREFIX="${BUILD_DIR}/install" \
    -DCMAKE_BUILD_TYPE="${BUILD_TYPE}" \
    -DCMAKE_PREFIX_PATH=/usr \
    -DCMAKE_SYSTEM_PREFIX_PATH=/usr \
    -DBUILD_PACKAGE=On \
    -DOCC_INCLUDE_DIR=/usr/include/opencascade \
    -DOCC_LIBRARY_DIR="${LIBDIR}" \
    -DPYTHON_EXECUTABLE:FILEPATH="${PY}" \
    -DPYTHON_INCLUDE_DIR:PATH="${PY_INCLUDE}" \
    -DPYTHON_LIBRARY:FILEPATH="${PY_LIBRARY}" \
    -DPACKAGE_PYTHON_SUBDIR="${PY_MODULE_SUBDIR}" \
    -DCOLLADA_SUPPORT=Off \
    -DLIBXML2_INCLUDE_DIR=/usr/include/libxml2 \
    -DLIBXML2_LIBRARIES="${LIBDIR}/libxml2.so" \
    -DCGAL_INCLUDE_DIR=/usr/include \
    -DGMP_INCLUDE_DIR=/usr/include \
    -DMPFR_INCLUDE_DIR=/usr/include \
    -DGMP_LIBRARY_DIR="${LIBDIR}" \
    -DMPFR_LIBRARY_DIR="${LIBDIR}" \
    -DHDF5_INCLUDE_DIR=/usr/include \
    -DGLTF_SUPPORT=On \
    -DJSON_INCLUDE_DIR=/usr/include \
    -DEIGEN_DIR=/usr/include/eigen3

echo "==> Building with ${JOBS} jobs"
cmake --build "${BUILD_DIR}" -j "${JOBS}"

echo "==> Installing"
cmake --build "${BUILD_DIR}" --target install

echo "==> Packaging (RPM + TGZ)"
cmake --build "${BUILD_DIR}" --target package

echo "==> Done. Artifacts:"
ls -1 "${BUILD_DIR}/assets/" 2>/dev/null || true
