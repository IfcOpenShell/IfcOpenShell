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

if(SCHEMA_VERSIONS MATCHES "4")
    # arbitrary_open_profile_def
    add_executable(arbitrary_open_profile_def arbitrary_open_profile_def.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(arbitrary_open_profile_def IfcOpenShell::IfcParse)
    else()
        target_include_directories(arbitrary_open_profile_def PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(arbitrary_open_profile_def IfcParse)
        set_target_properties(arbitrary_open_profile_def PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS arbitrary_open_profile_def)

    # triangulated_faceset
    add_executable(triangulated_faceset triangulated_faceset.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(triangulated_faceset IfcOpenShell::IfcParse)
    else()
        target_include_directories(triangulated_faceset PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(triangulated_faceset IfcParse)
        set_target_properties(triangulated_faceset PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS triangulated_faceset)

endif()

if(SCHEMA_VERSIONS MATCHES "2x3")
    # composite_profile_def.cpp
    add_executable(composite_profile_def composite_profile_def.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(composite_profile_def IfcOpenShell::IfcParse)
    else()
        target_include_directories(composite_profile_def PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(composite_profile_def IfcParse)
        set_target_properties(composite_profile_def PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS composite_profile_def)

    # csg_primitive
    add_executable(csg_primitive csg_primitive.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(csg_primitive IfcOpenShell::IfcParse)
    else()
        target_include_directories(csg_primitive PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(csg_primitive IfcParse)
        set_target_properties(csg_primitive PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS csg_primitive)

    # ellipse_pies
    add_executable(ellipse_pies ellipse_pies.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(ellipse_pies IfcOpenShell::IfcParse)
    else()
        target_include_directories(ellipse_pies PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(ellipse_pies IfcParse)
        set_target_properties(ellipse_pies PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS ellipse_pies)

    # faces
    add_executable(faces faces.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(faces IfcOpenShell::IfcParse)
    else()
        target_include_directories(faces PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(faces IfcParse)
        set_target_properties(faces PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS faces)

    # ifc_curve_rebar
    add_executable(ifc_curve_rebar ifc_curve_rebar.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(ifc_curve_rebar IfcOpenShell::IfcParse)
    else()
        target_include_directories(ifc_curve_rebar PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(ifc_curve_rebar IfcParse)
        set_target_properties(ifc_curve_rebar PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS ifc_curve_rebar)

    # profiles
    add_executable(profiles profiles.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(profiles IfcOpenShell::IfcParse)
    else()
        target_include_directories(profiles PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(profiles IfcParse)
        set_target_properties(profiles PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS profiles)

    # IfcParseExamples
    add_executable(IfcParseExamples IfcParseExamples.cpp)

    if(STANDALONE_PROJECT)
        target_link_libraries(IfcParseExamples IfcOpenShell::IfcParse)
    else()
        target_include_directories(IfcParseExamples PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(IfcParseExamples IfcParse)
        set_target_properties(IfcParseExamples PROPERTIES FOLDER Examples)
    endif()
    install(TARGETS IfcParseExamples)

    if(WITH_OPENCASCADE)
        # IfcOpenHouse and IfcAdvancedHouse
        add_executable(IfcOpenHouse IfcOpenHouse.cpp)
        add_executable(IfcAdvancedHouse IfcAdvancedHouse.cpp)
        add_library(IfcHouseInterface INTERFACE)

        if(STANDALONE_PROJECT)
            target_link_libraries(IfcHouseInterface INTERFACE IfcOpenShell::IfcParse IfcOpenShell::geometry_serializer)
        else()
            target_link_libraries(IfcHouseInterface INTERFACE IfcParse geometry_serializer)
            set_target_properties(IfcOpenHouse PROPERTIES FOLDER Examples)
            set_target_properties(IfcAdvancedHouse PROPERTIES FOLDER Examples)
        endif()
        target_link_libraries(IfcOpenHouse PRIVATE IfcHouseInterface)
        target_link_libraries(IfcAdvancedHouse PRIVATE IfcHouseInterface)
        install(TARGETS IfcOpenHouse IfcAdvancedHouse)
    endif()
endif()

if(SCHEMA_VERSIONS MATCHES "4x3_add2")
    # IfcAlignment and IfcSimplifiedAlignment
    add_executable(IfcAlignment IfcAlignment.cpp)
    add_executable(IfcSimplifiedAlignment IfcSimplifiedAlignment.cpp)
    add_library(IfcAlignmentInterface INTERFACE)

    if(STANDALONE_PROJECT)
        target_link_libraries(IfcAlignmentInterface INTERFACE IfcOpenShell::IfcParse)
    else()
        target_link_libraries(IfcAlignmentInterface INTERFACE IfcParse)
        set_target_properties(IfcAlignment PROPERTIES FOLDER Examples)
        set_target_properties(IfcSimplifiedAlignment PROPERTIES FOLDER Examples)
    endif()

    target_link_libraries(IfcAlignment PRIVATE IfcAlignmentInterface)
    target_link_libraries(IfcSimplifiedAlignment PRIVATE IfcAlignmentInterface)

    install(TARGETS IfcAlignment IfcSimplifiedAlignment)
endif()
