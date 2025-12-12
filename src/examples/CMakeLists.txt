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

cmake_minimum_required(VERSION 3.21)
project(IfcOpenShellExamples)

set(CMAKE_CXX_STANDARD 17)
find_package(IfcOpenShell CONFIG REQUIRED)

macro(build_example exe_name)
    set(additional_targets ${ARGN})
    add_executable(${exe_name} ${exe_name}.cpp)
    target_link_libraries(${exe_name} IfcOpenShell::IfcParse $<$<BOOL:${additional_targets}>:IfcOpenShell::${additional_targets}>)
    install(TARGETS ${exe_name})
endmacro()

message(STATUS "Building examples for IFC schema versions: ${SCHEMA_VERSIONS}")
message(STATUS "SCHEMA_SEQ: ${SCHEMA_SEQ}")
# if("4" IN_LIST SCHEMA_VERSIONS)
    build_example(arbitrary_open_profile_def)
    build_example(triangulated_faceset)
# endif()

# if("2x3" IN_LIST SCHEMA_VERSIONS)
    build_example(composite_profile_def)
    build_example(csg_primitive)
    build_example(ellipse_pies)
    build_example(faces)
    build_example(ifc_curve_rebar)
    build_example(profiles)
    build_example(IfcParseExamples)

    # if(WITH_OPENCASCADE)
        build_example(IfcOpenHouse geometry_serializer)
        build_example(IfcAdvancedHouse geometry_serializer)
    # endif()
# endif()

# if("4x3_add2" IN_LIST SCHEMA_VERSIONS)
    build_example(IfcAlignment)
    build_example(IfcSimplifiedAlignment)
# endif()
