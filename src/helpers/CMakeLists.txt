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

message("Running CMakeLists.txt in /src/helpers")

# Schema-agnostic IFC helpers ported from ifcopenshell.util.*. Pure
# IfcParse + Eigen, no Qt, no IfcGeom, no viewer/renderer deps — so unit
# tests and standalone IFC tools can pull them in without dragging
# OpenCASCADE or Qt6 into the link.
#
# Currently:
#   * Unit        — unit conversions (ifcopenshell.util.unit)
#   * Geolocation — IfcMapConversion / WCS / helmert helpers
#                   (ifcopenshell.util.geolocation)
#   * Placement   — IfcLocalPlacement / IfcAxis2Placement reduction
#                   (ifcopenshell.util.placement)
#   * Pset        — property and quantity retrieval
#                   (ifcopenshell.util.element)
#   * Element     — get_predefined_type (ifcopenshell.util.element)

find_package(Eigen3 REQUIRED)

# helpers_math: the schema-free subset — unit conversion tables and Helmert
# matrix math over plain numbers. No IfcParse, no Qt, no schema dispatch, so it
# builds under Emscripten where the rest of this directory cannot.
#
# It exists as its own target rather than being compiled into both `helpers` and
# IfcViewerCore so the objects are built exactly once and both libraries agree
# on them. IfcViewerCore links it directly (see src/ifcviewer/CMakeLists.txt);
# `helpers` re-exports it PUBLIC below so existing consumers keep working
# through the unchanged unit.h / geolocation.h includes.
set(HELPER_MATH_CPP_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/unit_convert.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/geolocation_transform.cpp
)
add_library(helpers_math STATIC ${HELPER_MATH_CPP_FILES})
target_include_directories(helpers_math PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(helpers_math PUBLIC Eigen3::Eigen)
set_target_properties(helpers_math PROPERTIES POSITION_INDEPENDENT_CODE ON)
install(TARGETS helpers_math EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

# The rest of this directory needs IfcParse and the generated schema bindings,
# so it is desktop-only.
if(EMSCRIPTEN)
    return()
endif()

file(GLOB HELPER_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB HELPER_H_FILES   ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
list(REMOVE_ITEM HELPER_CPP_FILES ${HELPER_MATH_CPP_FILES})

add_library(helpers STATIC ${HELPER_CPP_FILES} ${HELPER_H_FILES})

# The installed headers stay schema-agnostic. Implementations are compiled
# against only the schema plugins selected for this build and dispatch from an
# untyped entry point to generated, compiler-checked entity accessors.
foreach(schema ${SCHEMA_VERSIONS})
    target_compile_definitions(helpers PRIVATE
        IFCOPENSHELL_HELPER_SCHEMA_${schema}
    )
    list(APPEND HELPER_SCHEMA_LIBRARIES parse_schema_ifc${schema})
endforeach()

set_target_properties(helpers PROPERTIES
    VERSION   "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

# PUBLIC: callers (IfcViewer, test_federation, future tools) get
# `#include "unit.h"` etc. via this directory automatically, no
# `#include "../helpers/unit.h"` ugliness at call sites.
target_include_directories(helpers PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(helpers PUBLIC
    IfcParse
    Eigen3::Eigen
    helpers_math
    PRIVATE
    ${HELPER_SCHEMA_LIBRARIES}
)

install(TARGETS helpers EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${HELPER_H_FILES}
    DESTINATION ${INCLUDEDIR}/helpers
)
