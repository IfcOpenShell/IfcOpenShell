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

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    project(IfcOpenShellPython LANGUAGES CXX)
    set(IFCOPENSHELL_IFCWRAP_STANDALONE ON)
else()
    set(IFCOPENSHELL_IFCWRAP_STANDALONE OFF)
endif()

if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()
if(CMAKE_CXX_STANDARD LESS 17)
    message(FATAL_ERROR "C++17 or newer is required.")
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(POLICY CMP0148) # 3.27
    cmake_policy(SET CMP0148 OLD)
endif()
if(POLICY CMP0177) # 3.31
    cmake_policy(SET CMP0177 OLD)
endif()

set(_ifcwrap_feature_definitions "")
if(IFCOPENSHELL_IFCWRAP_STANDALONE)
    get_filename_component(_ifcwrap_repo_root "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
    list(PREPEND CMAKE_MODULE_PATH "${_ifcwrap_repo_root}/cmake")

    find_package(IfcOpenShell REQUIRED)

    set(WITH_OPENCASCADE "${IFCOPENSHELL_WITH_OPENCASCADE}")
    set(WITH_CGAL "${IFCOPENSHELL_WITH_CGAL}")
    set(SWIG_DEFINES "")

    if(IFCOPENSHELL_WITH_OPENCASCADE)
        list(APPEND SWIG_DEFINES -DIFOPSH_WITH_OPENCASCADE)
        list(APPEND _ifcwrap_feature_definitions IFOPSH_WITH_OPENCASCADE)
    endif()
    if(IFCOPENSHELL_WITH_CGAL)
        list(APPEND SWIG_DEFINES -DIFOPSH_WITH_CGAL)
        list(APPEND _ifcwrap_feature_definitions IFOPSH_WITH_CGAL)
    endif()
    if(IFCOPENSHELL_IFCXML)
        list(APPEND SWIG_DEFINES -DWITH_IFCXML)
        list(APPEND _ifcwrap_feature_definitions WITH_IFCXML)
    endif()
    if(IFCOPENSHELL_WITH_ROCKSDB)
        list(APPEND SWIG_DEFINES -DIFOPSH_WITH_ROCKSDB)
        list(APPEND _ifcwrap_feature_definitions IFOPSH_WITH_ROCKSDB)
    endif()
endif()

include(GNUInstallDirs)

if(BUILD_IFCAPI)
    if(WASM_BUILD AND NOT IFCAPI_REGENERATE_BINDINGS)
        set(IFCAPI_REGENERATE_BINDINGS ON CACHE BOOL "Regenerate the low-level bindings during the build." FORCE)
    endif()

    if(WASM_BUILD)
        set(IFCOPENSHELL_BINDINGS_GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
    else()
        set(IFCOPENSHELL_BINDINGS_GENERATED_DIR "${CMAKE_CURRENT_SOURCE_DIR}/binding_generator/generated")
    endif()
    set(IFCOPENSHELL_BINDING_SPEC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/binding_generator/specs")
    set(IFCOPENSHELL_BINDING_SPEC_MACROS "${IFCOPENSHELL_BINDING_SPEC_DIR}/cpp/spec_macros.h")
    set(UNIFIED_CAPI_HEADER "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}/ifcopenshell_api.h")
    set(UNIFIED_CAPI_CPP "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}/ifcopenshell_api.cpp")
    set(UNIFIED_CAPI_INTERNAL_HEADER "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}/ifcopenshell_api_internal.hpp")
    set(IFCOPENSHELL_BINDING_BYPRODUCTS
        "${UNIFIED_CAPI_HEADER}"
        "${UNIFIED_CAPI_CPP}"
        "${UNIFIED_CAPI_INTERNAL_HEADER}"
    )
    set(IFCOPENSHELL_BINDING_TARGET_ARGS)
    if(WASM_BUILD)
        set(IFCOPENSHELL_WASM_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/wasm")
        set(IFCOPENSHELL_WASM_API_MJS "${IFCOPENSHELL_WASM_OUTPUT_DIR}/ifcopenshell_api.mjs")
        set(IFCOPENSHELL_WASM_EXPORTS "${IFCOPENSHELL_WASM_OUTPUT_DIR}/ifcopenshell_exports.txt")
        set(IFCOPENSHELL_WASM_D_TS "${IFCOPENSHELL_WASM_OUTPUT_DIR}/ifcopenshell_api.d.ts")
        list(APPEND IFCOPENSHELL_BINDING_BYPRODUCTS
            "${IFCOPENSHELL_WASM_API_MJS}"
            "${IFCOPENSHELL_WASM_EXPORTS}"
            "${IFCOPENSHELL_WASM_D_TS}"
        )
        list(APPEND IFCOPENSHELL_BINDING_TARGET_ARGS
            --wasm-output-dir "${IFCOPENSHELL_WASM_OUTPUT_DIR}"
        )
    endif()
    set(IFCOPENSHELL_BINDING_SPEC_DEPENDS
        "${IFCOPENSHELL_BINDING_SPEC_DIR}/ifcparse.yml"
        "${IFCOPENSHELL_BINDING_SPEC_DIR}/ifcgeom.yml"
        "${IFCOPENSHELL_BINDING_SPEC_DIR}/cpp/ifcparse.hpp"
        "${IFCOPENSHELL_BINDING_SPEC_DIR}/cpp/ifcgeom.hpp"
        "${IFCOPENSHELL_BINDING_SPEC_MACROS}"
    )

    if(IFCAPI_REGENERATE_BINDINGS)
        if(DEFINED PYTHON_EXECUTABLE AND NOT "${PYTHON_EXECUTABLE}" STREQUAL "")
            set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
        endif()
        find_package(Python COMPONENTS Interpreter REQUIRED)
        message(STATUS "Using Python interpreter for binding generation: ${Python_EXECUTABLE}")

        execute_process(
            COMMAND ${Python_EXECUTABLE} -c "import clang.cindex; import yaml"
            RESULT_VARIABLE IFCOPENSHELL_BINDGEN_PYTHON_DEPS_STATUS
            OUTPUT_QUIET
            ERROR_QUIET
        )
        if(NOT IFCOPENSHELL_BINDGEN_PYTHON_DEPS_STATUS EQUAL 0)
            message(
                FATAL_ERROR
                "IFCAPI_REGENERATE_BINDINGS enabled, but the selected Python interpreter does not provide "
                "the Clang Python bindings and PyYAML. Install the generator dependencies or disable "
                "IFCAPI_REGENERATE_BINDINGS."
            )
        endif()

        set(IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS)
        foreach(include_dir IN ITEMS
            "${CMAKE_CURRENT_SOURCE_DIR}/.."
            "${CMAKE_CURRENT_SOURCE_DIR}/../plugin"
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcparse"
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcparse/schemas"
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom"
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom/mapping"
            "${CMAKE_CURRENT_SOURCE_DIR}/../serializers"
            "${CMAKE_CURRENT_SOURCE_DIR}/../svgfill/src"
        )
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS --discovery-include-dir "${include_dir}")
        endforeach()
        if(WITH_OPENCASCADE)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
                --discovery-include-dir "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom/kernels/opencascade"
            )
        endif()
        if(WITH_CGAL)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
                --discovery-include-dir "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom/kernels/cgal"
            )
        endif()
        if(WITH_MANIFOLD)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
                --discovery-include-dir "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom/kernels/manifold"
            )
        endif()
        list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
            --discovery-include-dir "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom/kernels/passthrough"
        )
        foreach(include_dir IN LISTS
            Boost_INCLUDE_DIRS
            CGAL_INCLUDE_DIR
            GMP_INCLUDE_DIR
            MPFR_INCLUDE_DIR
            OCC_INCLUDE_DIR
            OpenCASCADE_INCLUDE_DIR
            OpenCASCADE_INCLUDE_DIRS
            EIGEN3_INCLUDE_DIR
            Eigen3_INCLUDE_DIR
            Eigen3_INCLUDE_DIRS
        )
            if(NOT "${include_dir}" STREQUAL "")
                list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS --discovery-include-dir "${include_dir}")
            endif()
        endforeach()
        if(OpenCASCADE_DIR)
            get_filename_component(IFCOPENSHELL_BINDINGS_OPENCASCADE_PREFIX "${OpenCASCADE_DIR}/../../.." ABSOLUTE)
            if(EXISTS "${IFCOPENSHELL_BINDINGS_OPENCASCADE_PREFIX}/include/opencascade")
                list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
                    --discovery-include-dir "${IFCOPENSHELL_BINDINGS_OPENCASCADE_PREFIX}/include/opencascade"
                )
            endif()
        endif()
        if(Eigen3_DIR)
            get_filename_component(IFCOPENSHELL_BINDINGS_EIGEN_PREFIX "${Eigen3_DIR}/../../.." ABSOLUTE)
            if(EXISTS "${IFCOPENSHELL_BINDINGS_EIGEN_PREFIX}/include/eigen3")
                list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS
                    --discovery-include-dir "${IFCOPENSHELL_BINDINGS_EIGEN_PREFIX}/include/eigen3"
                )
            endif()
        endif()

        set(IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS)
        foreach(define IN LISTS SCHEMA_DEFINITIONS)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define "${define}")
        endforeach()
        if(USE_MMAP)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define USE_MMAP)
        endif()
        if(WITH_CGAL)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define IFOPSH_WITH_CGAL)
        endif()
        if(WITH_OPENCASCADE)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define IFOPSH_WITH_OPENCASCADE)
        endif()
        if(WITH_MANIFOLD)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define IFOPSH_WITH_MANIFOLD)
        endif()
        if(WITH_ROCKSDB)
            list(APPEND IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS --discovery-define IFOPSH_WITH_ROCKSDB)
        endif()

        file(
            GLOB_RECURSE IFCOPENSHELL_BINDGEN_SOURCES
            CONFIGURE_DEPENDS
            "${CMAKE_CURRENT_SOURCE_DIR}/binding_generator/*.py"
        )
        list(FILTER IFCOPENSHELL_BINDGEN_SOURCES EXCLUDE REGEX "/generated/")
        list(FILTER IFCOPENSHELL_BINDGEN_SOURCES EXCLUDE REGEX "/wrappergen/")

        set(IFCOPENSHELL_BINDINGS_CODEGEN_STAMP "${CMAKE_CURRENT_BINARY_DIR}/ifcopenshell_bindings_codegen.stamp")
        add_custom_command(
            OUTPUT "${IFCOPENSHELL_BINDINGS_CODEGEN_STAMP}"
            BYPRODUCTS ${IFCOPENSHELL_BINDING_BYPRODUCTS}
            COMMAND
                ${Python_EXECUTABLE} -m src.ifcwrap.binding_generator.generate
                --spec-dir "${IFCOPENSHELL_BINDING_SPEC_DIR}"
                --c-output-dir "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}"
                ${IFCOPENSHELL_BINDING_TARGET_ARGS}
                ${IFCOPENSHELL_BINDINGS_DISCOVERY_INCLUDE_ARGS}
                ${IFCOPENSHELL_BINDINGS_DISCOVERY_DEFINE_ARGS}
            COMMAND ${CMAKE_COMMAND} -E touch "${IFCOPENSHELL_BINDINGS_CODEGEN_STAMP}"
            DEPENDS
                ${IFCOPENSHELL_BINDING_SPEC_DEPENDS}
                ${IFCOPENSHELL_BINDGEN_SOURCES}
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../.."
            VERBATIM
        )
        add_custom_target(
            ifcopenshell_bindings_codegen
            DEPENDS "${IFCOPENSHELL_BINDINGS_CODEGEN_STAMP}"
        )
    endif()

    if((EXISTS "${UNIFIED_CAPI_HEADER}" AND EXISTS "${UNIFIED_CAPI_CPP}") OR IFCAPI_REGENERATE_BINDINGS)
        if(WASM_BUILD)
            add_library(ifcopenshell_capi STATIC "${UNIFIED_CAPI_HEADER}" "${UNIFIED_CAPI_CPP}")
        else()
            add_library(ifcopenshell_capi SHARED "${UNIFIED_CAPI_HEADER}" "${UNIFIED_CAPI_CPP}")
        endif()
        if(TARGET ifcopenshell_bindings_codegen)
            add_dependencies(ifcopenshell_capi ifcopenshell_bindings_codegen)
        endif()
        if((schema_libraries OR kernel_libraries OR mapping_libraries) AND NOT WASM_BUILD)
            add_dependencies(ifcopenshell_capi ${schema_libraries} ${kernel_libraries} ${mapping_libraries})
        endif()
        target_link_libraries(ifcopenshell_capi PRIVATE IfcParse)
        if(GLTF_SUPPORT)
            target_compile_definitions(ifcopenshell_capi PRIVATE WITH_GLTF)
            target_link_libraries(ifcopenshell_capi PRIVATE nlohmann_json::nlohmann_json)
        endif()
        if(TARGET IfcGeom)
            target_link_libraries(ifcopenshell_capi PRIVATE IfcGeom)
            if(NOT WASM_BUILD)
                target_link_libraries(ifcopenshell_capi PRIVATE ${OpenCASCADE_LIBRARIES})
            endif()
        endif()
        if(TARGET Serializers AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE Serializers)
        endif()
        if(TARGET geometry_serializer AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE geometry_serializer)
        endif()
        if(geometry_serializer_libraries AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE ${geometry_serializer_libraries})
        endif()
        if(document_serializer_libraries AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE ${document_serializer_libraries})
        endif()
        if(TARGET svgfill AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE svgfill)
        endif()
        if(TARGET IFCOPENSHELL_CGAL AND NOT WASM_BUILD)
            target_link_libraries(ifcopenshell_capi PRIVATE IFCOPENSHELL_CGAL)
        endif()
        target_include_directories(
            ifcopenshell_capi
            PUBLIC "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}"
            PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/.."
            PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../ifcparse"
            PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../plugin"
            PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../serializers"
            PRIVATE "${OCC_INCLUDE_DIR}"
        )
        if(BUILD_IFCGEOM)
            target_include_directories(ifcopenshell_capi PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../ifcgeom")
        endif()
        set_target_properties(ifcopenshell_capi PROPERTIES
            POSITION_INDEPENDENT_CODE ON
        )

        # Smoke tests - separate executables for each test scope
        if(BUILD_IFCGEOM AND NOT WASM_BUILD)
            add_executable(ifcopenshell_capi_smoke "${CMAKE_CURRENT_SOURCE_DIR}/tests/ifcgeom_c_api_smoke.c")
            target_link_libraries(ifcopenshell_capi_smoke PRIVATE ifcopenshell_capi)
            if(TARGET geometry_serializer)
                target_link_libraries(ifcopenshell_capi_smoke PRIVATE geometry_serializer)
            endif()
            target_include_directories(ifcopenshell_capi_smoke PRIVATE "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}")
            if(tree_libraries)
                add_dependencies(ifcopenshell_capi_smoke ${tree_libraries})
            endif()
        endif()

        if(NOT WASM_BUILD)
            add_executable(ifcparse_capi_smoke "${CMAKE_CURRENT_SOURCE_DIR}/tests/ifcparse_c_api_smoke.c")
            target_link_libraries(ifcparse_capi_smoke PRIVATE ifcopenshell_capi)
            if(TARGET geometry_serializer)
                target_link_libraries(ifcparse_capi_smoke PRIVATE geometry_serializer)
            endif()
            target_include_directories(ifcparse_capi_smoke PRIVATE "${IFCOPENSHELL_BINDINGS_GENERATED_DIR}")
            target_compile_definitions(ifcparse_capi_smoke PRIVATE $<$<BOOL:${WITH_ROCKSDB}>:IFOPSH_WITH_ROCKSDB>)
        endif()

        if(WASM_BUILD)
            include(wasm.cmake)
        endif()
    else()
        message(FATAL_ERROR
            "BUILD_IFCAPI requires generated bindings at ${UNIFIED_CAPI_HEADER}; "
            "enable IFCAPI_REGENERATE_BINDINGS or generate the committed outputs first")
    endif()

    if(BUILD_TESTING)
        if(TARGET ifcopenshell_capi_smoke)
            add_test(NAME ifcopenshell_capi_smoke COMMAND ifcopenshell_capi_smoke)
        endif()
        if(TARGET ifcparse_capi_smoke)
            add_test(NAME ifcparse_capi_smoke COMMAND ifcparse_capi_smoke)
        endif()
    endif()
endif()

if(BUILD_IFCPYTHON)
find_package(SWIG 4.1)
if(NOT SWIG_FOUND)
    message(
        FATAL_ERROR
        "BUILD_IFCPYTHON requires SWIG 4.1 or newer. Disable BUILD_IFCPYTHON or fix SWIG paths to proceed. "
        "Found version '${SWIG_VERSION}' at '${SWIG_EXECUTABLE}'."
    )
endif()
include(${SWIG_USE_FILE})

IF(NOT "${PYTHON_INCLUDE_DIR}" STREQUAL "")
    # Hint for FindPython where to find Python_INCLUDE_DIRS.
    set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
    MESSAGE(STATUS "Looking for Python header files in: ${Python_INCLUDE_DIR}")
ENDIF()
IF(NOT "${PYTHON_LIBRARY}" STREQUAL "")
    # Hint for FindPython where to find Python_LIBRARIES.
    set(Python_LIBRARY "${PYTHON_LIBRARY}")
    MESSAGE(STATUS "Looking for Python library file in: ${Python_LIBRARY}")
ENDIF()

# Development.Module = headers on Unix, headers+libraries on Windows.
# Required variables:
# - Windows - Python_INCLUDE_DIR, Python_LIBRARY (MSVC doesn't allow undefined symbols at link time)
# - Unix - Python_INCLUDE_DIR
# Unfortunately all paths must be always provided explicitly, not by prefixing PATH.
# Otherwise FindPython will break on newer Python versions (list of supported versions is hardcoded).
find_package(Python COMPONENTS Development.Module)
IF(NOT Python_Development.Module_FOUND)
	MESSAGE(FATAL_ERROR "BUILD_IFCPYTHON enabled, but unable to find Python lib or header. Disable BUILD_IFCPYTHON or fix Python paths to proceed.")
ENDIF()

# Ensure version is saved here, from wasm libraries,
# not from Python interpreter that might be unrelated to pyodide Python version.
set(_python_libs_version "${Python_VERSION_MAJOR}${Python_VERSION_MINOR}")
INCLUDE_DIRECTORIES(BEFORE ${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS ${SWIG_DEFINES})

if(WITH_CGAL)
    if(IFCOPENSHELL_IFCWRAP_STANDALONE)
        if(TARGET IfcOpenShell::svgfill)
            set(LIBSVGFILL IfcOpenShell::svgfill)
        else()
            message(FATAL_ERROR "IfcOpenShell was built with CGAL, but the exported svgfill target was not found.")
        endif()
    else()
        set(LIBSVGFILL svgfill)
    endif()
endif()

set_source_files_properties(IfcPython.i PROPERTIES CPLUSPLUS ON)
# Rebuild on changes in other .i files.
SET_PROPERTY(
	SOURCE IfcPython.i
	PROPERTY DEPENDS
		IfcGeomWrapper.i
		IfcParseWrapper.i
		utils/type_conversion.i
		utils/typemaps_in.i
		utils/typemaps_out.i
)

# On Windows there is '_d' prefix for debug builds - e.g. `_d.cp311-win_amd64.pyd`.
# In 4.2+ it's done automatically when discovering `Development.Module`.
if(WIN32 AND CMAKE_VERSION VERSION_LESS "4.2")
    set(Python_DEBUG_POSTFIX "_d")
endif()
# Workaround for most likely missing debug Python libraries on Windows.
# Even if user has them, it's unlikely that they want to use them for building IfcPython
# since it makes extension incompatiblew with standard Python
# and requires all other extensions to be built in debug mode as well.
# But debug mode is still might be needed - e.g. Blender's Python is using it, if you're running debug build.
if(NOT USE_DEBUG_PYTHON)
    set(Python_DEBUG_POSTFIX "")
	add_compile_definitions(SWIG_PYTHON_INTERPRETER_NO_DEBUG)
    if(Python_LIBRARY_DEBUG)
        # If debug libraries were found, then override them with release ones.
        get_target_property(IMPORTED_IMPLIB Python::Module IMPORTED_IMPLIB_RELEASE)
        get_target_property(IMPORTED_LOCATION Python::Module IMPORTED_LOCATION_RELEASE)
        set_target_properties(
            Python::Module
            PROPERTIES
            IMPORTED_IMPLIB_DEBUG "${IMPORTED_IMPLIB}"
            IMPORTED_LOCATION_DEBUG "${IMPORTED_LOCATION}"
        )
    endif()
endif()
if (CMAKE_VERSION VERSION_GREATER_EQUAL "4.2")
    # `DEBUG_POSTFIX` argument was added in 4.2.
    swig_add_library(ifcopenshell_wrapper LANGUAGE python SOURCES IfcPython.i DEBUG_POSTFIX "${Python_DEBUG_POSTFIX}")
else()
    # If we won't override -interface name,
    # swig py wrapper will try to import `_ifcopenshell_wrapper_d` module and would fail.
    set(SWIG_MODULE_ifcopenshell_wrapper_EXTRA_FLAGS "-interface" "_ifcopenshell_wrapper")
    swig_add_library(ifcopenshell_wrapper LANGUAGE python SOURCES IfcPython.i)
    set_target_properties(
        ifcopenshell_wrapper PROPERTIES
        DEBUG_POSTFIX "${Python_DEBUG_POSTFIX}"
    )
endif()

target_link_libraries(ifcopenshell_wrapper PRIVATE Python::Module)
if(WITH_CGAL)
    target_sources(ifcopenshell_wrapper PRIVATE ../svgfill/src/linework_processing_facade.cpp)
endif()
if(WITH_ROCKSDB)
    target_link_libraries(ifcopenshell_wrapper PRIVATE document_serializer_rdb)
endif()

if(_ifcwrap_feature_definitions)
    target_compile_definitions(ifcopenshell_wrapper PRIVATE ${_ifcwrap_feature_definitions})
endif()
if(IFCOPENSHELL_IFCWRAP_STANDALONE)
    set(_ifcwrap_ifcopenshell_libraries ${IFCOPENSHELL_LIBRARIES})
    set(_ifcwrap_geometry_libraries ${IFCOPENSHELL_GEOMETRY_LIBRARIES})
    set(_ifcwrap_cgal_libraries "")
    set(_ifcwrap_swig_depends "")
else()
    set(_ifcwrap_ifcopenshell_libraries ${IFCOPENSHELL_LIBRARIES})
    set(_ifcwrap_geometry_libraries IfcGeom)
    set(_ifcwrap_cgal_libraries ${CGAL_LIBRARIES})
    set(_ifcwrap_swig_depends ${IFCOPENSHELL_LIBRARIES})
endif()
set_property(TARGET ifcopenshell_wrapper PROPERTY SWIG_DEPENDS ${_ifcwrap_swig_depends})
if(WASM_BUILD)
    # SIDE_MODULE=1 - add to .so all symbols from linked archives (default used by pyodide).
    # Since currently libIfcGeom.a seems to be linked twice it results in duplicated symbols and compilation errors.
    # Possibly in the future we can clean up linked libs and try `=1`.
    # SIDE_MODULE=2 - add to .so only explicitly exported functions (`-s EXPORTED_FUNCTIONS).
    # Have to provide it here to override possible `=1` coming from pyodide.
    if(CMAKE_GENERATOR MATCHES "Makefile" AND CMAKE_VERSION VERSION_LESS "4.2")
        # Accomodate bug in cmake makefile generator (fixed in 4.2+).
        # https://gitlab.kitware.com/cmake/cmake/-/issues/27326
        string(
            REPLACE "SIDE_MODULE=1" "SIDE_MODULE=2"
            CMAKE_MODULE_LINKER_FLAGS
            "${CMAKE_MODULE_LINKER_FLAGS}"
        )
    endif()
    target_link_options(
        ifcopenshell_wrapper
        PRIVATE "SHELL:-s EXPORTED_FUNCTIONS=_PyInit__ifcopenshell_wrapper -s SIDE_MODULE=2" -O1
    )
endif()
target_link_libraries(ifcopenshell_wrapper PRIVATE
    ${_ifcwrap_geometry_libraries}
    ${_ifcwrap_ifcopenshell_libraries}
    ${Boost_LIBRARIES}
)
if(schema_libraries OR kernel_libraries OR tree_libraries OR mapping_libraries OR geometry_serializer_libraries OR document_serializer_libraries OR linework_processing_libraries)
    add_dependencies(ifcopenshell_wrapper ${schema_libraries} ${kernel_libraries} ${tree_libraries} ${mapping_libraries} ${geometry_serializer_libraries} ${document_serializer_libraries} ${linework_processing_libraries})
endif()
if((NOT WIN32) AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_RPATHS)
    if(IFCOPENSHELL_IFCWRAP_STANDALONE)
        set(_ifcwrap_ifcopenshell_library_dir "${IFCOPENSHELL_LIBRARY_DIR}")
    else()
        set(_ifcwrap_ifcopenshell_library_dir "${CMAKE_INSTALL_FULL_LIBDIR}")
    endif()
    # The Python package and IfcOpenShell libraries can have unrelated install
    # prefixes. This is notably the case for standalone ifcwrap builds against
    # an installed CMake package and GitHub Actions' hosted Python.
    SET_INSTALL_RPATHS(ifcopenshell_wrapper "${_ifcwrap_ifcopenshell_library_dir};${IFCDIRS};${OCC_LIBRARY_DIR}")
elseif((NOT WIN32) AND BUILD_SHARED_LIBS AND COMMAND SET_INSTALL_RPATHS)
    SET_INSTALL_RPATHS(ifcopenshell_wrapper "${IFCDIRS};${OCC_LIBRARY_DIR}")
endif()

# Try to find the Python interpreter to get the site-packages
# directory in which the wrapper can be installed.
if(NOT ${PYTHON_EXECUTABLE} STREQUAL "")
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
    MESSAGE(STATUS "Looking for Python interpreter in: ${PYTHON_EXECUTABLE}")
endif()
FIND_PACKAGE(Python COMPONENTS Interpreter)
IF(Python_Interpreter_FOUND OR PYTHON_MODULE_INSTALL_DIR)
    # Python_SOABI example value is 'cp311-win_amd64'.
    if(WASM_BUILD)
        # For WASM we usually don't provide interpreter,
        # so `find_package` couldn't find `Python_SOABI`.
        # So we just hardcode it.
        # .cpython-313-wasm32-emscripten.so
        set(PYTHON_EXTENSION_SUFFIX ".cpython-${_python_libs_version}-wasm32-emscripten.so")
    elseif(WIN32)
        set(PYTHON_EXTENSION_SUFFIX ".${Python_SOABI}.pyd")
    else()
        set(PYTHON_EXTENSION_SUFFIX ".${Python_SOABI}.so")
    endif()
    set_target_properties(
        ifcopenshell_wrapper PROPERTIES
        SUFFIX ${PYTHON_EXTENSION_SUFFIX}
    )
    if (PYTHON_MODULE_INSTALL_DIR)
	set(python_package_dir "${PYTHON_MODULE_INSTALL_DIR}")
    else()
        IF (USERSPACE_PYTHON_PREFIX)
            EXECUTE_PROCESS(
                COMMAND ${PYTHON_EXECUTABLE} -c "import sys; import site; sys.stdout.write(site.USER_SITE)"
                OUTPUT_VARIABLE python_package_dir
            )
        ELSE ()
            set(python_package_dir "${Python_SITEARCH}")
        ENDIF()
        if (BUILD_PACKAGE)
            set(python_package_dir ${CMAKE_INSTALL_LIBDIR}/python${PYTHON_VERSION_MAJOR}/dist-packages/)
        endif()
    endif()
    IF("${python_package_dir}" STREQUAL "")
        MESSAGE(WARNING "Unable to locate Python site-package directory, unable to install the Python wrapper")
    ELSE()
        message(STATUS "Python wrapper will be installed to '${python_package_dir}'.")
        file(GLOB_RECURSE sourcefiles "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/*")
        # Exclude compiled extensions - they're part of dev environment and shouldn't leak into installation.
        list(FILTER sourcefiles EXCLUDE REGEX "\\.(so|pyd|dylib)$")
        foreach(file ${sourcefiles})
            file(RELATIVE_PATH relative "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/" "${file}")
            get_filename_component(dir "${relative}" DIRECTORY)
            if(NOT IS_DIRECTORY "${file}")
                install(FILES "${file}" DESTINATION "${python_package_dir}/ifcopenshell/${dir}")
            endif()
        endforeach()
        install(
            FILES "${CMAKE_CURRENT_BINARY_DIR}/ifcopenshell_wrapper.py"
            DESTINATION "${python_package_dir}/ifcopenshell"
        )
        INSTALL(TARGETS ifcopenshell_wrapper
                DESTINATION "${python_package_dir}/ifcopenshell")

        if (CREATE_BUNDLE)
            set(_ifcopenshell_python_runtime_targets
                IfcGeom
                IfcParse
                ${schema_libraries}
                ${kernel_libraries}
                ${tree_libraries}
                ${mapping_libraries}
                geometry_serializer
                ${geometry_serializer_libraries}
                ${document_serializer_libraries}
                ${linework_processing_libraries}
                plugin
            )

            list(REMOVE_DUPLICATES _ifcopenshell_python_runtime_targets)

            if(_ifcopenshell_python_runtime_targets)
                INSTALL(TARGETS ${_ifcopenshell_python_runtime_targets}
                        LIBRARY DESTINATION "${python_package_dir}/ifcopenshell"
                        RUNTIME DESTINATION "${python_package_dir}/ifcopenshell")
            endif()

            if(NOT WIN32 AND NOT WASM_BUILD)
                # On Linux $ORIGIN expands to the directory of the loaded
                # object (= site-packages/ifcopenshell/). macOS dyld doesn't
                # expand $ORIGIN; the equivalent placeholder is
                # @loader_path. Setting $ORIGIN on macOS bakes a literal
                # "$ORIGIN" into LC_RPATH which resolves to nothing at
                # runtime — the wrapper's `@rpath/ifcopenshell_document_rdb
                # .dylib` LC_LOAD_DYLIB then fails to find the plug-in even
                # though INSTALL(TARGETS … LIBRARY DESTINATION …/ifcopenshell)
                # above has dropped it right next to the wrapper.
                if(APPLE)
                    set_target_properties(ifcopenshell_wrapper PROPERTIES
                        INSTALL_RPATH "@loader_path"
                    )
                else()
                    set_target_properties(ifcopenshell_wrapper PROPERTIES
                        INSTALL_RPATH "$ORIGIN"
                    )
                endif()
            endif()
        endif()
	if (MSVC)
	    INSTALL(FILES $<TARGET_PDB_FILE:ifcopenshell_wrapper> DESTINATION bin OPTIONAL)
	endif()
    ENDIF()
ELSE()
    MESSAGE(WARNING "No Python interpreter found, unable to install the Python wrapper")
ENDIF()
endif()
