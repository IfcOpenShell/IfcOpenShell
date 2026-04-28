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

add_ifcviewer_unit_test(test_bvh_accel
    SOURCES ${IFCVIEWER_SRC}/BvhAccel.cpp
)

add_ifcviewer_unit_test(test_lod_builder
    SOURCES
        ${IFCVIEWER_SRC}/LodBuilder.cpp
    LIBS meshoptimizer::meshoptimizer
)

add_ifcviewer_unit_test(test_sidecar_cache
    SOURCES ${IFCVIEWER_SRC}/SidecarCache.cpp
)

add_ifcviewer_unit_test(test_instanced_geometry)
