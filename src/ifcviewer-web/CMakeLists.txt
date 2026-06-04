################################################################################
#                                                                              #
# This file is part of IfcOpenShell.                                           #
#                                                                              #
# IfcOpenShell is free software: you can redistribute it and/or modify         #
# it under the terms of the Lesser GNU General Public License as published by  #
# the Free Software Foundation, either version 3.0 of the License, or          #
# (at your option) any later version.                                          #
#                                                                              #
# IfcOpenShell is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 #
# Lesser GNU General Public License for more details.                          #
#                                                                              #
# You should have received a copy of the Lesser GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.         #
#                                                                              #
################################################################################

# Web (Emscripten + WebGPU) build root.
#
# This is a SEPARATE root from cmake/CMakeLists.txt — the desktop CMake
# pulls in Qt, OpenCASCADE, IfcGeom, CGAL, Boost, none of which exist or
# make sense for wasm. The web build only needs IfcViewerCore (the
# Qt-free, OpenCASCADE-free static lib carved out of src/ifcviewer)
# plus this main_web.cpp scaffold.
#
# Usage:
#   source /path/to/emsdk_env.sh
#   emcmake cmake -S src/ifcviewer-web -B build-web
#   ninja -C build-web
#   python3 -m http.server --directory build-web 8080
#   # open http://localhost:8080/IfcViewerWeb.html
#
# Why a separate root and not a sub-add under cmake/CMakeLists.txt:
# making every find_package() conditional on (NOT EMSCRIPTEN) would
# pollute the desktop build with web-only branches it never exercises.
# Better to keep the web path's machinery local to this directory.

cmake_minimum_required(VERSION 3.21)
project(IfcViewerWeb LANGUAGES CXX)

if(NOT EMSCRIPTEN)
    message(FATAL_ERROR
        "src/ifcviewer-web requires the Emscripten toolchain. "
        "Re-run via `emcmake cmake ...`.")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Allow find_package to look at the host system for header-only deps
# (Eigen3 is the only one we need). Emscripten's CMake toolchain
# defaults this to ONLY, which restricts searches to the emcc sysroot
# and blocks the system Eigen3Config.cmake. Eigen is pure-header so
# pulling its include path from the host is completely safe.
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)

# --- IfcViewerCore: portable runtime subset ----------------------------------
#
# Build IfcViewerCore by adding src/ifcviewer as a subdir. The Qt /
# IfcGeom / OpenCASCADE-coupled IfcViewer target inside that CMakeLists
# will fail under emcc (find_package(Qt6) etc. won't resolve), so the
# subdir's full build can't be reached here. We add it with EXCLUDE_FROM_ALL
# so only the targets we explicitly reference (IfcViewerCore) are built.
# Eigen and wgpu_native (the latter becomes a no-op interface under
# EMSCRIPTEN — see ifcviewer/CMakeLists.txt) get pulled in transitively.
#
# TODO(web): when src/ifcviewer/CMakeLists.txt is taught to skip the
# Qt-using IfcViewer target under EMSCRIPTEN, we can drop EXCLUDE_FROM_ALL.
set(IFCVIEWER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../ifcviewer")
add_subdirectory(${IFCVIEWER_DIR} ifcviewer EXCLUDE_FROM_ALL)

# --- The web executable ------------------------------------------------------

add_executable(IfcViewerWeb main_web.cpp)
target_link_libraries(IfcViewerWeb PRIVATE IfcViewerCore)
target_link_options(IfcViewerWeb PRIVATE
    # Asyncify lets us await wgpu's RequestAdapter/RequestDevice/MapAsync
    # as if they were synchronous. Adds ~30-50% wasm size and a small
    # per-await runtime cost; acceptable for the spike, revisit when
    # we ship.
    "-sASYNCIFY"
    # Streaming + chunked geometry want a heap that can grow as buffers
    # arrive. 256 MB initial, 2 GB ceiling (matches the wasm32 pointer
    # cap; --shared64 / MEMORY64 would lift this later if we need it).
    "-sALLOW_MEMORY_GROWTH=1"
    "-sINITIAL_MEMORY=268435456"        # 256 MB
    "-sMAXIMUM_MEMORY=2147483648"       # 2 GB
    # FETCH lets emscripten_fetch issue HTTP Range requests for the
    # sidecar byte-range loader. Not used yet by the scaffold but
    # needed by the upcoming #27 web streaming I/O backend.
    "-sFETCH=1"
    # Shell template wraps the JS output in our canvas page.
    "--shell-file=${CMAKE_CURRENT_SOURCE_DIR}/shell.html"
)
set_target_properties(IfcViewerWeb PROPERTIES SUFFIX ".html")
