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

message("Running CMakeLists.txt in /src/ifcutil")

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

find_package(Eigen3 REQUIRED)

file(GLOB HELPER_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB HELPER_H_FILES   ${CMAKE_CURRENT_SOURCE_DIR}/*.h)

add_library(helpers STATIC ${HELPER_CPP_FILES} ${HELPER_H_FILES})

set_target_properties(helpers PROPERTIES
    VERSION   "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

# PUBLIC: callers (IfcViewer, test_federation, future tools) get
# `#include "Unit.h"` etc. via this directory automatically, no
# `#include "../helpers/Unit.h"` ugliness at call sites.
target_include_directories(helpers PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(helpers PUBLIC
    IfcParse
    Eigen3::Eigen
)

install(TARGETS helpers EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${HELPER_H_FILES}
    DESTINATION ${INCLUDEDIR}/helpers
)
