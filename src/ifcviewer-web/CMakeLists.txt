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

add_executable(IfcViewerWeb
    main_web.cpp
    WebViewportHost.cpp
    WebViewportHost.h
)
target_link_libraries(IfcViewerWeb PRIVATE IfcViewerCore)

target_link_options(IfcViewerWeb PRIVATE
    # No -sASYNCIFY. The web init path is callback-driven
    # (initWgpuAsyncWeb chains RequestAdapter → RequestDevice via
    # WGPU's AllowSpontaneous mode + the JS event loop), so we don't
    # need to await wgpu calls as if they were sync. Asyncify would
    # also instrument every function reachable from emscripten_sleep,
    # adding ~30% to wasm size for no win here.
    #
    # EXIT_RUNTIME=0 + Module.noExitRuntime=true (set in shell.html)
    # keeps wasm alive after main() returns so Dawn-web's
    # RequestAdapter/RequestDevice promise callbacks land. The
    # alternative — calling emscripten_set_main_loop_arg early in
    # main() to set noExitRuntime as a side effect — registers a RAF
    # that starves the device promise (observed: ~10s delay in Firefox).
    "-sEXIT_RUNTIME=0"
    # Expose the C entry points to JS. _raf_tick_c drives the RAF loop
    # (shell.html); _load_sidecar_from_blob_c loads a user-picked File via
    # byte-range Blob.slice reads; _load_sidecar_from_url_c streams a remote
    # sidecar via HTTP Range; _ifcv_on_range_done / _ifcv_source_ready are the
    # JS→C completion callbacks for a landed range / a resolved URL size.
    # EMSCRIPTEN_KEEPALIVE alone keeps the symbols in the binary but doesn't
    # add them to Module. ccall lets shell.html pass a JS string (the ?model
    # URL) to load_sidecar_from_url_c without manual heap marshalling.
    "-sEXPORTED_FUNCTIONS=['_main','_raf_tick_c','_load_sidecar_from_source_c','_clear_scene_c','_ifcv_on_range_done','_ifcv_chunks_resident_c','_ifcv_chunks_total_c']"
    # ccall: shell.html passes the ?model URL string to load_sidecar_from_url_c.
    # HEAPU8: lets tooling/tests read the wasm heap size (e.g. to verify a large
    # sidecar streams by range instead of loading whole). Standard, zero-cost.
    "-sEXPORTED_RUNTIME_METHODS=['ccall','HEAPU8']"
    # Streaming + chunked geometry want a heap that can grow as buffers
    # arrive. 256 MB initial, 2 GB ceiling (matches the wasm32 pointer
    # cap; --shared64 / MEMORY64 would lift this later if we need it).
    "-sALLOW_MEMORY_GROWTH=1"
    "-sINITIAL_MEMORY=268435456"        # 256 MB
    "-sMAXIMUM_MEMORY=2147483648"       # 2 GB
    # FETCH lets emscripten_fetch issue HTTP Range requests. The local
    # file path (#88) reads byte ranges via Blob.slice and does NOT need
    # this; it's retained for the remote-URL Range backend (follow-up).
    "-sFETCH=1"
    # Bundle a small sample sidecar into Emscripten's MEMFS so the page
    # renders something on first load without a user pick. The @ separator
    # mounts the file at the virtual path the wasm fopen()s. User-picked
    # files instead stream via Blob.slice byte ranges (load_sidecar_from_blob_c).
    "--embed-file=${CMAKE_CURRENT_SOURCE_DIR}/sample.ifcview@/sample.ifcview"
    # Shell template wraps the JS output in our canvas page.
    "--shell-file=${CMAKE_CURRENT_SOURCE_DIR}/shell.html"
)
set_target_properties(IfcViewerWeb PROPERTIES SUFFIX ".html")
