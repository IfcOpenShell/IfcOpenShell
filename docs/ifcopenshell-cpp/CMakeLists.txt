# This file was generated with the assistance of an AI coding tool.
################################################################################
#
# Builds the standalone C++ sources that are included in the IfcOpenShell C++
# documentation pages, and runs every one of them:
#
#   hello_world.rst
#   code_examples.rst
#   geometry_processing.rst
#
# This is a standalone project: it consumes an installed IfcOpenShell cmake
# package through find_package(IfcOpenShell CONFIG), exactly like any other
# third party consumer would.
#
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=/path/to/ifcopenshell
#   cmake --build build --config RelWithDebInfo
#   ctest --test-dir build -C RelWithDebInfo --output-on-failure
#
# Building and running every example in a single command:
#
#   cmake --build build --config RelWithDebInfo --target run_examples
#
################################################################################

cmake_minimum_required(VERSION 3.21)

project(IfcOpenShellCppExamples LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# The cmake package config that find_package(IfcOpenShell CONFIG) is resolved
# against. Set IfcOpenShell_DIR or CMAKE_PREFIX_PATH when configuring if the
# package is not in a default location.
find_package(IfcOpenShell CONFIG REQUIRED)

if(NOT TARGET IfcOpenShell::parse_schema_ifc4)
    message(FATAL_ERROR "The IfcOpenShell package was found, but it does not provide the IfcOpenShell::parse_schema_ifc4 target.")
endif()

# The models the examples are run against. hello_world.ifc is a small IFC4 model
# which contains a project, a site, a building, a storey, and a single named wall
# with a property set. AC20-FZK-Haus.ifc is a small building with real geometry,
# which the code examples and the geometry examples both need.
set(
    HELLO_WORLD_MODEL
    "${CMAKE_CURRENT_SOURCE_DIR}/hello_world/hello_world.ifc"
    CACHE FILEPATH "IFC model that the Hello, world! programs are run against."
)
set(
    FZK_HAUS_MODEL
    "${CMAKE_CURRENT_SOURCE_DIR}/models/AC20-FZK-Haus.ifc"
    CACHE FILEPATH "IFC model that the code example and geometry processing programs are run against."
)
foreach(model_variable IN ITEMS HELLO_WORLD_MODEL FZK_HAUS_MODEL)
    if(NOT EXISTS "${${model_variable}}")
        message(FATAL_ERROR "${model_variable} '${${model_variable}}' does not exist.")
    endif()
endforeach()

# The IfcOpenShell libraries are imported targets, so the loader has to be able
# to find them next to the examples as well.
enable_testing()

# Where the examples that write files write them to.
set(EXAMPLES_RUN_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/run")
file(MAKE_DIRECTORY "${EXAMPLES_RUN_DIRECTORY}")

# Every .cpp in the given subdirectory is an example, and is built as its own
# program. register_examples(<subdirectory> <folder> <model> <libraries>...)
function(register_examples subdirectory folder model)
    file(GLOB example_sources CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/${subdirectory}/*.cpp")
    list(SORT example_sources)

    set(example_targets "")
    foreach(example_source IN LISTS example_sources)
        get_filename_component(example_name "${example_source}" NAME_WE)

        add_executable("${example_name}" "${example_source}")
        # Boost headers auto link against boost::filesystem, which is not part of
        # the IfcOpenShell link interface and is not otherwise needed here.
        target_compile_definitions("${example_name}" PRIVATE BOOST_ALL_NO_LIB)
        target_link_libraries("${example_name}" PRIVATE ${ARGN})

        if(MSVC OR CMAKE_CONFIGURATION_TYPES)
            set_target_properties("${example_name}" PROPERTIES FOLDER "${folder}")
        endif()

        add_test(NAME "${example_name}" COMMAND "$<TARGET_FILE:${example_name}>" "${model}")
        set_tests_properties(
            "${example_name}"
            PROPERTIES
                WORKING_DIRECTORY "${EXAMPLES_RUN_DIRECTORY}"
                ENVIRONMENT_MODIFICATION
                "PATH=path_list_prepend:$<TARGET_FILE_DIR:IfcOpenShell::IfcParse>"
        )

        list(APPEND example_targets "${example_name}")
    endforeach()

    set(EXAMPLES ${EXAMPLES} ${example_targets} PARENT_SCOPE)
endfunction()

register_examples(
    hello_world "Hello, world!" "${HELLO_WORLD_MODEL}"
    IfcOpenShell::IfcParse IfcOpenShell::parse_schema_ifc4
)
register_examples(
    code_examples "Code examples and mechanisms" "${FZK_HAUS_MODEL}"
    IfcOpenShell::IfcParse IfcOpenShell::parse_schema_ifc4
)
register_examples(
    geometry_processing "Geometry processing" "${FZK_HAUS_MODEL}"
    IfcOpenShell::IfcParse IfcOpenShell::parse_schema_ifc4
    IfcOpenShell::IfcGeom IfcOpenShell::geometry_kernel_opencascade
    IfcOpenShell::geometry_serializer
)

# A single custom command that runs all of the examples and fails if any of them
# fails.
add_custom_target(
    run_examples
    COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure -C "$<CONFIG>"
    DEPENDS ${EXAMPLES}
    USES_TERMINAL
    COMMENT "Running the IfcOpenShell C++ examples"
)
