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

message("Running CMakeLists.txt in /src/ifcviewer-wgpu")

set(QT_VERSION 6 CACHE STRING "Qt version")
find_package(Qt${QT_VERSION} COMPONENTS Core Gui REQUIRED PATHS ${QT_DIR})

# wgpu-native — fetched as a pre-built binary release from upstream.
# Pin the version with WGPU_NATIVE_VERSION; bump to pull a newer release.
set(WGPU_NATIVE_VERSION "v29.0.0.0" CACHE STRING "wgpu-native release tag")

# Pick the right release archive for the host platform.
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(_wgpu_archive "wgpu-windows-x86_64-msvc-release.zip")
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

file(GLOB IFCVIEWER_WGPU_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB IFCVIEWER_WGPU_H_FILES   ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
set(IFCVIEWER_WGPU_FILES ${IFCVIEWER_WGPU_CPP_FILES} ${IFCVIEWER_WGPU_H_FILES})

# Intentional source-level borrowing from the GL backend until ifcviewer-core
# is extracted (task #12). SidecarCache + InstancedGeometry have zero Qt /
# OCCT / IFC-parse deps, so compiling them directly into IfcViewerWgpu is
# cheaper than dragging in the IfcViewer static lib (which would pull all
# of IfcGeom + IfcParse + OCCT + Qt OpenGL).
set(IFCVIEWER_SHARED_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../ifcviewer)
list(APPEND IFCVIEWER_WGPU_FILES
    ${IFCVIEWER_SHARED_DIR}/SidecarCache.cpp
)

add_library(IfcViewerWgpu STATIC ${IFCVIEWER_WGPU_FILES})

set_target_properties(IfcViewerWgpu PROPERTIES
    AUTOMOC ON
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

target_include_directories(IfcViewerWgpu
    PUBLIC  ${CMAKE_CURRENT_SOURCE_DIR}
    PUBLIC  ${IFCVIEWER_SHARED_DIR}  # SidecarCache.h is reachable via WgpuViewportWindow.h
)

target_link_libraries(IfcViewerWgpu PUBLIC
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui
    wgpu_native
)

# Qt platform-handle access (QNativeInterface::QX11Application etc.) is in
# the public Gui headers in Qt 6.2+, no PRIVATE_INCLUDE_DIRS needed.

if(UNIX AND NOT APPLE)
    find_package(Threads REQUIRED)
    target_link_libraries(IfcViewerWgpu PUBLIC Threads::Threads)
endif()

install(TARGETS IfcViewerWgpu EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${IFCVIEWER_WGPU_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcviewer-wgpu
)

# Install the wgpu_native shared library so the deployed runtime can find it.
# At build/run-from-build-tree time CMake adds wgpu_native_SOURCE_DIR to the
# binary's rpath automatically (IMPORTED_LOCATION dirname).
if(NOT WIN32)
    install(FILES "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_lib}" DESTINATION lib)
else()
    install(FILES "${wgpu_native_SOURCE_DIR}/lib/${_wgpu_runtime}" DESTINATION bin)
endif()
