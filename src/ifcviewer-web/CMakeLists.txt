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
project(IfcViewerWeb LANGUAGES C CXX)  # C for the vendored zstd decoder

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
    WebFederation.cpp
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
    # EXIT_RUNTIME=0 + Module.noExitRuntime=true (set in the host page (web/ifcviewer.js))
    # keeps wasm alive after main() returns so Dawn-web's
    # RequestAdapter/RequestDevice promise callbacks land. The
    # alternative — calling emscripten_set_main_loop_arg early in
    # main() to set noExitRuntime as a side effect — registers a RAF
    # that starves the device promise (observed: ~10s delay in Firefox).
    "-sEXIT_RUNTIME=0"
    # Emit a reusable module factory (IfcViewerWeb.js) instead of a baked page,
    # so multiple static example pages can load the same wasm. Each page does
    #   createIfcViewer({ canvas, ... }).then(Module => …)
    # (see web/ifcviewer.js, which wraps this into a small integration API).
    "-sMODULARIZE=1"
    "-sEXPORT_NAME=createIfcViewer"
    # Expose the C entry points to JS. _raf_tick_c drives the RAF loop
    # (the host page (web/ifcviewer.js)); _load_sidecar_from_blob_c loads a user-picked File via
    # byte-range Blob.slice reads; _load_sidecar_from_url_c streams a remote
    # sidecar via HTTP Range; _ifcv_on_range_done / _ifcv_source_ready are the
    # JS→C completion callbacks for a landed range / a resolved URL size.
    # The _ifcv_{get,set,apply}_* family is the scripting API (camera, selection,
    # visibility, colour override, object enumeration, mouse nav preset) that
    # web/ifcviewer.js wraps; _malloc/_free let it marshal id arrays into the
    # wasm heap.
    # EMSCRIPTEN_KEEPALIVE alone keeps the symbols in the binary but doesn't
    # add them to Module. ccall lets the host page (web/ifcviewer.js) pass a JS string (the ?model
    # URL) to load_sidecar_from_url_c without manual heap marshalling.
    "-sEXPORTED_FUNCTIONS=['_main','_malloc','_free','_raf_tick_c','_load_sidecar_from_source_c','_clear_scene_c','_ifcv_on_range_done','_ifcv_chunks_resident_c','_ifcv_chunks_total_c','_ifcv_model_count_c','_ifcv_model_resident_c','_ifcv_model_total_c','_ifcv_bytes_total_c','_ifcv_bytes_needed_c','_ifcv_bytes_loaded_c','_view_all_c','_frame_selection_c','_toggle_projection_c','_projection_is_ortho_c','_standard_view_c','_toggle_fly_c','_fly_is_active_c','_hide_selected_c','_isolate_selected_c','_show_all_c','_hide_all_c','_toggle_xray_c','_xray_is_active_c','_toggle_section_c','_clear_section_c','_section_is_active_c','_ifcv_get_camera_c','_ifcv_set_camera_c','_ifcv_set_ortho_c','_ifcv_set_nav_preset_c','_ifcv_set_background_c','_ifcv_get_selection_c','_ifcv_get_active_object_c','_ifcv_apply_selection_c','_ifcv_set_visible_c','_ifcv_get_hidden_c','_ifcv_set_color_c','_ifcv_clear_colors_c','_ifcv_request_objects_c','_ifcv_set_selection_outline_c','_ifcv_selection_outline_is_on_c','_ifcv_set_federation_unit_c','_ifcv_set_false_origin_c','_ifcv_get_false_origin_c','_ifcv_set_model_transform_c','_ifcv_clear_model_transform_c','_ifcv_set_model_name_c','_ifcv_get_model_georef_c','_ifcv_get_frame_stats_c','_ifcv_unload_model_c','_ifcv_load_model_c','_ifcv_model_unloaded_c','_ifcv_model_vram_bytes_c']"
    # ccall: the host page (web/ifcviewer.js) passes the ?model URL string to load_sidecar_from_url_c,
    # and the nav-preset name to ifcv_set_nav_preset_c.
    # HEAPU8: lets tooling/tests read the wasm heap size (e.g. to verify a large
    # sidecar streams by range instead of loading whole). HEAPU32/HEAPF32: the
    # scripting API marshals object-id arrays and the camera state through them.
    "-sEXPORTED_RUNTIME_METHODS=['ccall','HEAPU8','HEAPU32','HEAPF32','HEAPF64','UTF8ToString']"
    # Streaming + chunked geometry want a heap that can grow as buffers
    # arrive. 256 MB initial, 2 GB ceiling (matches the wasm32 pointer
    # cap; --shared64 / MEMORY64 would lift this later if we need it).
    "-sALLOW_MEMORY_GROWTH=1"
    "-sINITIAL_MEMORY=268435456"        # 256 MB
    "-sMAXIMUM_MEMORY=4294967296"       # 4 GB (wasm32 max) — big federations need the headroom
    # FETCH lets emscripten_fetch issue HTTP Range requests. The local
    # file path (#88) reads byte ranges via Blob.slice and does NOT need
    # this; it's retained for the remote-URL Range backend (follow-up).
    "-sFETCH=1"
    # Bundle a small sample sidecar into Emscripten's MEMFS so the page
    # renders something on first load without a user pick. The @ separator
    # mounts the file at the virtual path the wasm fopen()s. User-picked
    # files instead stream via Blob.slice byte ranges (load_sidecar_from_blob_c).
    "--embed-file=${CMAKE_CURRENT_SOURCE_DIR}/sample.ifcview@/sample.ifcview"
)
# MODULARIZE emits IfcViewerWeb.js (the createIfcViewer factory) + .wasm.
set_target_properties(IfcViewerWeb PROPERTIES SUFFIX ".js")

# --embed-file above is a link-time input, but it lives inside a link OPTION, so
# CMake cannot see it as a dependency: regenerating sample.ifcview (make_sample.py)
# would otherwise leave the previous model baked into the wasm with ninja
# reporting "no work to do". Name it explicitly so a changed sample relinks.
set_property(TARGET IfcViewerWeb APPEND
    PROPERTY LINK_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/sample.ifcview")

# Copy the static example pages + the JS integration helper next to the wasm so
# a plain `python3 -m http.server --directory build-web` serves the whole demo:
#   /IfcViewerWeb.html  fullscreen example
#   /embedded.html      embedded viewer + DOM model list / selection (JS API)
#   /scripting.html     the full scripting API — camera, selection, visibility, colour
#   /index.html         links to all three
set(IFCVIEWERWEB_STATIC
    "${CMAKE_CURRENT_SOURCE_DIR}/web/ifcviewer.js"
    "${CMAKE_CURRENT_SOURCE_DIR}/web/IfcViewerWeb.html"
    "${CMAKE_CURRENT_SOURCE_DIR}/web/embedded.html"
    "${CMAKE_CURRENT_SOURCE_DIR}/web/scripting.html"
    "${CMAKE_CURRENT_SOURCE_DIR}/web/index.html"
)
# One copy rule per page, each DEPENDing on its own source, so editing a page or
# ifcviewer.js re-copies it. The previous POST_BUILD command on IfcViewerWeb only
# fired when the wasm itself relinked, which left a stale copy in the build dir —
# the served demo (and the Playwright tests, which run against it) kept the old
# file with ninja reporting "no work to do".
#
# The copies go next to the wasm, i.e. the executable's output directory. Pin
# that to the build root rather than reading it back through
# $<TARGET_FILE_DIR:IfcViewerWeb>: a generator expression in a custom command's
# OUTPUT may not reference a target.
set_target_properties(IfcViewerWeb PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")

set(IFCVIEWERWEB_STATIC_OUT)
foreach(static_src IN LISTS IFCVIEWERWEB_STATIC)
    get_filename_component(static_name "${static_src}" NAME)
    set(static_dst "${CMAKE_CURRENT_BINARY_DIR}/${static_name}")
    add_custom_command(
        OUTPUT  "${static_dst}"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "${static_src}" "${static_dst}"
        DEPENDS "${static_src}"
        COMMENT "Copying ${static_name} next to IfcViewerWeb.js"
        VERBATIM)
    list(APPEND IFCVIEWERWEB_STATIC_OUT "${static_dst}")
endforeach()
add_custom_target(IfcViewerWebStatic ALL DEPENDS ${IFCVIEWERWEB_STATIC_OUT})
