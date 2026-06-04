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

message("Running CMakeLists.txt in /src/ifcviewer")

set(QT_VERSION 6 CACHE STRING "Qt version")
find_package(Qt${QT_VERSION} COMPONENTS Core Gui REQUIRED PATHS ${QT_DIR})

# Eigen3 — used by Federation matrices, ViewportWindow's instance compose,
# the per-model coordinate-operation matrices stored on ModelGpuData, and
# everywhere a 4x4 transform shows up.
find_package(Eigen3 REQUIRED)

# wgpu-native — fetched as a pre-built binary release from upstream.
# Pin the version with WGPU_NATIVE_VERSION; bump to pull a newer release.
set(WGPU_NATIVE_VERSION "v29.0.0.0" CACHE STRING "wgpu-native release tag")

# Pick the right release archive for the host platform.
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "ARM64|aarch64")
        set(_wgpu_archive "wgpu-windows-aarch64-msvc-release.zip")
    else()
        set(_wgpu_archive "wgpu-windows-x86_64-msvc-release.zip")
    endif()
    set(_wgpu_lib     "wgpu_native.dll.lib")
    set(_wgpu_runtime "wgpu_native.dll")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
        set(_wgpu_archive "wgpu-macos-aarch64-release.zip")
    else()
        set(_wgpu_archive "wgpu-macos-x86_64-release.zip")
    endif()
    set(_wgpu_lib "libwgpu_native.dylib")
else() # Linux + BSDs
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
        set(_wgpu_archive "wgpu-linux-aarch64-release.zip")
    else()
        set(_wgpu_archive "wgpu-linux-x86_64-release.zip")
    endif()
    set(_wgpu_lib "libwgpu_native.so")
endif()

include(FetchContent)
FetchContent_Declare(
    wgpu_native
    URL https://github.com/gfx-rs/wgpu-native/releases/download/${WGPU_NATIVE_VERSION}/${_wgpu_archive}
    DOWNLOAD_NO_PROGRESS FALSE
)
FetchContent_MakeAvailable(wgpu_native)

# Release archive layout: include/webgpu/*.h and lib/<libname>.
#
# The Linux .so shipped in the v29 release has no DT_SONAME, which causes
# CMake to bake the relative IMPORTED_LOCATION path into DT_NEEDED. We patch
# the SONAME in once at configure time so dependents get a clean
# libwgpu_native.so reference, and pin the executable's rpath to the lib dir.
if(UNIX AND NOT APPLE)
    find_program(PATCHELF_EXECUTABLE patchelf)
    if(PATCHELF_EXECUTABLE)
        execute_process(
            COMMAND ${PATCHELF_EXECUTABLE} --set-soname "${_wgpu_lib}"
                    "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}"
            RESULT_VARIABLE _patchelf_rc
        )
        if(NOT _patchelf_rc EQUAL 0)
            message(WARNING "patchelf --set-soname failed on libwgpu_native.so")
        endif()
    else()
        message(WARNING
            "patchelf not found; libwgpu_native.so will be linked with a "
            "relative DT_NEEDED. Install patchelf to fix.")
    endif()
endif()

add_library(wgpu_native SHARED IMPORTED GLOBAL)
set_target_properties(wgpu_native PROPERTIES
    IMPORTED_LOCATION             "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}"
    INTERFACE_INCLUDE_DIRECTORIES "${wgpu_native_SOURCE_DIR}/include"
)
if(WIN32)
    # On Windows the .lib is the import library; the .dll is the runtime.
    set_target_properties(wgpu_native PROPERTIES
        IMPORTED_IMPLIB   "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}"
        IMPORTED_LOCATION "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_runtime}"
    )
endif()

# Expose the lib dir so dependents can put it on their rpath.
set(WGPU_NATIVE_LIB_DIR "${wgpu_native_SOURCE_DIR}/lib" CACHE INTERNAL
    "Directory containing the wgpu-native shared library")

file(GLOB IFCVIEWER_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB IFCVIEWER_H_FILES   ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
set(IFCVIEWER_FILES ${IFCVIEWER_CPP_FILES} ${IFCVIEWER_H_FILES})

# Cocoa bridge for the CAMetalLayer surface attach — Objective-C++.
# Only compiled into the target on Apple platforms; CMake handles `.mm`
# natively once OBJCXX is enabled.
if(APPLE)
    enable_language(OBJCXX)
    list(APPEND IFCVIEWER_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/MetalSurface_mac.mm
    )
endif()

add_library(IfcViewer STATIC ${IFCVIEWER_FILES})

set_target_properties(IfcViewer PROPERTIES
    AUTOMOC ON
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

if (WITH_MESH_OPTIMIZER)
    find_package(meshoptimizer REQUIRED)
    set(MESH_OPTIMIZER_LIB meshoptimizer::meshoptimizer)
    target_compile_definitions(IfcViewer PUBLIC -DWITH_MESH_OPTIMIZER)
endif()

# Consumers include headers as `#include "ViewportWindow.h"`, so expose this
# directory on the public interface.
target_include_directories(IfcViewer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_dependencies(IfcViewer ${kernel_libraries} ${mapping_libraries})

target_link_libraries(IfcViewer PUBLIC
    IfcUtil
    IfcGeom
    IfcParse
    ${OpenCASCADE_LIBRARIES}
    ${Boost_LIBRARIES}
    ${CGAL_LIBRARIES}
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui
    Eigen3::Eigen
    wgpu_native
    ${MESH_OPTIMIZER_LIB}
)

# Qt platform-handle access (QNativeInterface::QX11Application etc.) is in
# the public Gui headers in Qt 6.2+, no PRIVATE_INCLUDE_DIRS needed.

if(UNIX AND NOT APPLE)
    find_package(Threads REQUIRED)
    target_link_libraries(IfcViewer PUBLIC Threads::Threads)
endif()

# Cocoa + QuartzCore for MetalSurface_mac.mm (NSView, CAMetalLayer).
if(APPLE)
    target_link_libraries(IfcViewer PUBLIC
        "-framework Cocoa"
        "-framework QuartzCore"
    )
endif()

install(TARGETS IfcViewer EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${IFCVIEWER_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcviewer
)

# Install the wgpu_native shared library so the deployed runtime can find it.
# At build/run-from-build-tree time CMake adds wgpu_native_SOURCE_DIR to the
# binary's rpath automatically (IMPORTED_LOCATION dirname).
#
# macOS: drop libwgpu_native.dylib straight into BonsaiViewer.app's
# Frameworks/. The exe has `LC_LOAD_DYLIB @rpath/libwgpu_native.dylib`
# (baked from the dylib's install_name), and BonsaiViewer's
# INSTALL_RPATH is set to @executable_path/../Frameworks — together
# they resolve at launch without depending on macdeployqt to follow
# non-Qt @rpath references.
if(WIN32)
    install(FILES "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_runtime}" DESTINATION bin)
elseif(APPLE AND BUILD_BONSAIVIEWER)
    install(FILES "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}"
            DESTINATION "BonsaiViewer.app/Contents/Frameworks")
else()
    install(FILES "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}" DESTINATION lib)
endif()

if(BUILD_BONSAIVIEWER_TESTS)
    add_subdirectory(tests)
endif()
