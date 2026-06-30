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

# Tier-1 unit tests: pure-logic modules that need neither Qt nor an OpenGL
# context. Each test binary compiles the production source(s) under test
# directly (rather than linking the IfcViewer library) so the binaries stay
# small and don't pull Qt6, OpenCASCADE, IfcGeom, etc. into the test build.

set(IFCVIEWER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/..)

function(add_ifcviewer_unit_test name)
    cmake_parse_arguments(T "" "" "SOURCES;LIBS" ${ARGN})
    add_executable(${name} ${name}.cpp ${T_SOURCES})
    target_include_directories(${name} PRIVATE ${IFCVIEWER_SRC})
    target_link_libraries(${name} PRIVATE Catch2::Catch2WithMain ${T_LIBS})
    catch_discover_tests(${name})
endfunction()

if(WITH_MESH_OPTIMIZER)
    add_ifcviewer_unit_test(test_lod_builder
        SOURCES
            ${IFCVIEWER_SRC}/LodBuilder.cpp
        LIBS meshoptimizer::meshoptimizer
    )
    # LodBuilder.cpp's body is guarded behind WITH_MESH_OPTIMIZER; without
    # the define the test compiles the no-op stub and the buildLods
    # assertions fail. The IfcViewer library propagates this define via
    # target_compile_definitions but the test compiles LodBuilder.cpp
    # standalone, so the test target has to set it explicitly.
    target_compile_definitions(test_lod_builder PRIVATE -DWITH_MESH_OPTIMIZER)
endif()

add_ifcviewer_unit_test(test_sidecar_cache
    SOURCES ${IFCVIEWER_SRC}/SidecarCache.cpp
)

# StreamingLoader: metadata-only read + range readers + the pure buffer-based
# parse / read-plan helpers shared with the web (Blob.slice) path. Needs
# SidecarCache.cpp for writeSidecar (to lay down on-disk fixtures).
add_ifcviewer_unit_test(test_streaming_loader
    SOURCES
        ${IFCVIEWER_SRC}/StreamingLoader.cpp
        ${IFCVIEWER_SRC}/SidecarCache.cpp
)

add_ifcviewer_unit_test(test_instanced_geometry)

# ChunkPlanner: Morton sort + greedy-pack — pure CPU, no Qt / no wgpu.
add_ifcviewer_unit_test(test_chunk_planner
    SOURCES ${IFCVIEWER_SRC}/ChunkPlanner.cpp
)

# SidecarLayout: bake-time reorder of geometry into the loader's chunk order
# for streaming locality. Needs ChunkPlanner (Morton sort) + SidecarCache
# (SidecarData). Pure.
add_ifcviewer_unit_test(test_sidecar_layout
    SOURCES
        ${IFCVIEWER_SRC}/SidecarLayout.cpp
        ${IFCVIEWER_SRC}/ChunkPlanner.cpp
        ${IFCVIEWER_SRC}/SidecarCache.cpp
)

# InstanceCompose: matrix composition + cross-model object_id lookup.
# Pulls in wgpu_native for the WGPUBuffer typedef via ModelGpuData.h
# (never touched at runtime). Eigen for Matrix4d.
find_package(Eigen3 REQUIRED)
add_ifcviewer_unit_test(test_instance_compose
    SOURCES ${IFCVIEWER_SRC}/InstanceCompose.cpp
    LIBS wgpu_native Eigen3::Eigen
)
if(UNIX AND NOT APPLE AND WGPU_NATIVE_LIB_DIR)
    set_target_properties(test_instance_compose PROPERTIES
        BUILD_RPATH "${WGPU_NATIVE_LIB_DIR}"
    )
endif()

# Header-only state-machine tests for the renderer subsystems (selection,
# visibility). Subjects are inline in their .h files, so no SOURCES needed.
add_ifcviewer_unit_test(test_selection)
add_ifcviewer_unit_test(test_visibility)

# BufferPool sub-allocator invariants. The pool's wgpu calls live inside
# addSubBuffer() (the growth path); tests use the addSubBufferForTesting
# seam to preseed sub-pools with fake handles, so the only wgpu touchpoint
# the linker needs is the production destructor's wgpuBufferRelease — which
# is never reached for fake handles because we don't call destroy() / let
# the pool go out of scope holding any. Linking wgpu_native satisfies the
# symbol regardless.
add_ifcviewer_unit_test(test_buffer_pool
    SOURCES ${IFCVIEWER_SRC}/BufferPool.cpp
    LIBS wgpu_native
)
if(UNIX AND NOT APPLE AND WGPU_NATIVE_LIB_DIR)
    set_target_properties(test_buffer_pool PROPERTIES
        BUILD_RPATH "${WGPU_NATIVE_LIB_DIR}"
    )
endif()

# Federation is Qt-derived (QObject + signals). It has to pull Qt6 in
# directly and enable AUTOMOC for the Q_OBJECT moc-generation.
find_package(Qt${QT_VERSION} COMPONENTS Core Gui Test REQUIRED PATHS ${QT_DIR})

find_package(Eigen3 REQUIRED)

add_executable(test_federation
    test_federation.cpp
    ${IFCVIEWER_SRC}/Federation.cpp
)
set_target_properties(test_federation PROPERTIES AUTOMOC ON)
target_include_directories(test_federation PRIVATE ${IFCVIEWER_SRC})
target_link_libraries(test_federation PRIVATE
    Catch2::Catch2WithMain
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui    # Federation::HomeView uses QVector3D from QtGui
    Qt${QT_VERSION}::Test   # QSignalSpy
    Eigen3::Eigen           # Federation.h: composed matrices use Eigen
    # IfcUtil provides Unit::convert + Geolocation helpers
    # (helmertMetersFromParameters, getWcs, getMapUnit) + Placement
    # (getAxis2Placement, called from Geolocation::getWcs). Linking the
    # static lib avoids re-compiling those .cpp files here and pulls
    # the IfcUtil include dir + IfcParse transitively.
    IfcUtil
)
catch_discover_tests(test_federation)
