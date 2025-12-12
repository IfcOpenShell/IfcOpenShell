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
    set(Boost_USE_STATIC_LIBS ON)
    set(Boost_USE_STATIC_RUNTIME OFF)
    set(Boost_USE_MULTITHREADED ON)
    set(Boost_COMPONENTS system program_options regex thread date_time iostreams)
    find_package(Boost CONFIG REQUIRED COMPONENTS ${Boost_COMPONENTS})
    find_package(zstd CONFIG REQUIRED)
    find_package(RocksDB CONFIG REQUIRED)
    find_package(LibXml2 CONFIG REQUIRED)
    find_package(IfcOpenShell CONFIG REQUIRED)
endif()

if(STANDALONE_PROJECT OR SCHEMA_VERSIONS MATCHES "2x3")
    add_executable(IfcParseExamples IfcParseExamples.cpp)

    if(STANDALONE_PROJECT)
        target_include_directories(IfcParseExamples PRIVATE "${IfcOpenShell_DIR}/../../../include")
        target_include_directories(IfcParseExamples PRIVATE ${Boost_INCLUDE_DIRS})
        target_link_libraries(IfcParseExamples ${Boost_LIBRARIES})
        target_link_libraries(IfcParseExamples IfcOpenShell::IfcParse)
        target_compile_features(IfcParseExamples PRIVATE cxx_std_17)
        target_compile_definitions(IfcParseExamples PRIVATE "SCHEMA_SEQ=(2x3)" HAS_SCHEMA_2x3 IFOPSH_WITH_ROCKSDB)
    else()
        target_include_directories(IfcParseExamples PRIVATE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(IfcParseExamples IfcParse)
        set_target_properties(IfcParseExamples PROPERTIES FOLDER Examples)
        target_compile_features(IfcParseExamples PRIVATE cxx_std_17)
    endif()
    install(TARGETS IfcParseExamples)

    if(STANDALONE_PROJECT OR WITH_OPENCASCADE)
        add_executable(IfcOpenHouse IfcOpenHouse.cpp)
        add_executable(IfcAdvancedHouse IfcAdvancedHouse.cpp)
        add_library(IfcHouseInterface INTERFACE)

        if (STANDALONE_PROJECT)
            find_package(Eigen3 CONFIG REQUIRED)
            find_package(CGAL CONFIG REQUIRED)
            find_package(OpenCASCADE CONFIG REQUIRED)
            add_library(CGAL::CGAL_INTERFACE INTERFACE IMPORTED)
            target_link_libraries(CGAL::CGAL_INTERFACE INTERFACE CGAL::CGAL)

            target_include_directories(IfcHouseInterface INTERFACE "${IfcOpenShell_DIR}/../../../include")
            target_include_directories(IfcHouseInterface INTERFACE ${Boost_INCLUDE_DIRS})
            target_link_libraries(IfcHouseInterface
                INTERFACE ${OpenCASCADE_LIBRARIES} RocksDB::rocksdb
                IfcOpenShell::IfcParse IfcOpenShell::geometry_serializer
            )
            target_compile_definitions(IfcHouseInterface INTERFACE "SCHEMA_SEQ=(2x3)" HAS_SCHEMA_2x3 IFOPSH_WITH_ROCKSDB)
        else()
            target_include_directories(IfcHouseInterface INTERFACE "${CMAKE_SOURCE_DIR}/../src")
            target_link_libraries(IfcHouseInterface INTERFACE ${IFCOPENSHELL_LIBRARIES} ${OpenCASCADE_LIBRARIES})
            set_target_properties(IfcOpenHouse PROPERTIES FOLDER Examples)
            set_target_properties(IfcAdvancedHouse PROPERTIES FOLDER Examples)
        endif()
        target_link_libraries(IfcOpenHouse PRIVATE IfcHouseInterface)
        target_link_libraries(IfcAdvancedHouse PRIVATE IfcHouseInterface)
        install(TARGETS IfcOpenHouse IfcAdvancedHouse)
    endif()
endif()

if(STANDALONE_PROJECT OR SCHEMA_VERSIONS MATCHES "4x3_add2")
    add_executable(IfcAlignment IfcAlignment.cpp)
    add_executable(IfcSimplifiedAlignment IfcSimplifiedAlignment.cpp)
    add_library(IfcAlignmentInterface INTERFACE)

    if(STANDALONE_PROJECT)
        target_include_directories(IfcAlignmentInterface INTERFACE "${IfcOpenShell_DIR}/../../../include")
        target_include_directories(IfcAlignmentInterface INTERFACE ${Boost_INCLUDE_DIRS})
        target_compile_definitions(IfcAlignmentInterface INTERFACE HAS_SCHEMA_4x3_add2 IFOPSH_WITH_ROCKSDB)
        target_link_libraries(IfcAlignment PRIVATE IfcOpenShell::IfcParse)
        target_link_libraries(IfcSimplifiedAlignment PRIVATE IfcOpenShell::IfcParse)
    else()
        target_include_directories(IfcAlignmentInterface INTERFACE "${CMAKE_SOURCE_DIR}/../src")
        target_link_libraries(IfcAlignmentInterface INTERFACE ${IFCOPENSHELL_LIBRARIES})
        set_target_properties(IfcAlignment PROPERTIES FOLDER Examples)
        set_target_properties(IfcSimplifiedAlignment PROPERTIES FOLDER Examples)
    endif()

    target_link_libraries(IfcAlignment PRIVATE IfcAlignmentInterface)
    target_link_libraries(IfcSimplifiedAlignment PRIVATE IfcAlignmentInterface)

    install(TARGETS IfcAlignment IfcSimplifiedAlignment)
endif()
