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

# Thils file can also be build standalone, outside of the IfcOpenShell build tree,
# to demonstrate the usage IfcOpenShell as a cmake package.
if(NOT BUILD_EXAMPLES)
    set(STANDALONE_PROJECT ON)
endif()

if(STANDALONE_PROJECT)
    cmake_minimum_required(VERSION 3.21)
    project(IfcOpenShellExamples)

    set(CMAKE_CXX_STANDARD 17)
    find_package(IfcOpenShell CONFIG REQUIRED)
    set(SCHEMA_VERSIONS ${IFCOPENSHELL_SCHEMA_VERSIONS})
    set(WITH_OPENCASCADE ${IFCOPENSHELL_WITH_OPENCASCADE})
else()
    include_directories("${CMAKE_SOURCE_DIR}/../src")
endif()

macro(build_example exe_name)
    set(additional_targets ${ARGN})
    add_executable(${exe_name} ${exe_name}.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(
            ${exe_name}
            IfcOpenShell::IfcParse
            $<$<BOOL:${additional_targets}>:IfcOpenShell::${additional_targets}>
        )
    else()
        target_include_directories(${exe_name} PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(${exe_name} IfcParse ${additional_targets})
        set_target_properties(${exe_name} PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS ${exe_name})
endmacro()

macro(build_schema_example exe_name schema)
    build_example(${exe_name} ${ARGN})
    if(NOT STANDALONE_PROJECT)
        target_link_libraries(${exe_name} parse_schema_ifc${schema})
    endif()
endmacro()

if("4" IN_LIST SCHEMA_VERSIONS)
    build_schema_example(arbitrary_open_profile_def 4)
    build_schema_example(triangulated_faceset 4)
endif()

if("2x3" IN_LIST SCHEMA_VERSIONS)
    build_schema_example(composite_profile_def 2x3)
    build_schema_example(csg_primitive 2x3)
    build_schema_example(ellipse_pies 2x3)
    build_schema_example(faces 2x3)
    build_schema_example(ifc_curve_rebar 2x3)
    build_schema_example(profiles 2x3)
    build_schema_example(IfcParseExamples 2x3)

    if(WITH_OPENCASCADE)
        build_schema_example(IfcOpenHouse 2x3 geometry_serializer)
        build_schema_example(IfcAdvancedHouse 2x3 geometry_serializer)
    endif()
endif()

if("4x3_add2" IN_LIST SCHEMA_VERSIONS)
    build_schema_example(IfcAlignment 4x3_add2)
    build_schema_example(IfcSimplifiedAlignment 4x3_add2)
endif()
