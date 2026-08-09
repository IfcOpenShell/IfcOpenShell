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

# Create a cache entry if absent for environment variables
macro(UNIFY_ENVVARS_AND_CACHE VAR)
    if(NOT DEFINED ${VAR} AND DEFINED ENV{${VAR}} AND NOT ENV{${VAR}} STREQUAL "")
        set(${VAR} "$ENV{${VAR}}" CACHE STRING "${VAR}" FORCE)
        mark_as_advanced(${VAR})
    endif()
endmacro()

# Set INSTALL_RPATH for target with given paths
macro(SET_INSTALL_RPATHS _target _paths)
    set(${_target}_rpaths "")

    foreach(_path ${_paths})
        list(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${_path}" isSystemDir)

        if("${isSystemDir}" STREQUAL "-1")
            list(APPEND ${_target}_rpaths ${_path})
        endif()
    endforeach()

    message(STATUS "Set INSTALL_RPATH for ${_target}: ${${_target}_rpaths}")
    set_target_properties(${_target} PROPERTIES INSTALL_RPATH "${${_target}_rpaths}")
endmacro()

macro(SET_INSTALL_SELF_RPATH _target)
    if(IS_ABSOLUTE "${CMAKE_INSTALL_LIBDIR}")
        SET_INSTALL_RPATHS(${_target} "${CMAKE_INSTALL_LIBDIR}")
    elseif(APPLE)
        SET_INSTALL_RPATHS(${_target} "@loader_path")
    else()
        SET_INSTALL_RPATHS(${_target} "$ORIGIN")
    endif()
endmacro()

function(ifcopenshell_plugin_target TARGET)
    # Plug-ins are loaded by exact filename and should not receive a platform library prefix.
    set_target_properties(${TARGET} PROPERTIES PREFIX "")
    if((NOT WIN32) AND BUILD_SHARED_LIBS AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
        SET_INSTALL_SELF_RPATH(${TARGET})
    endif()
endfunction()

function(ifcopenshell_wasm_plugin_link_options TARGET REGISTRATION_SYMBOL)
    ifcopenshell_plugin_target(${TARGET})

    if(NOT WASM_BUILD)
        return()
    endif()

    cmake_parse_arguments(PLUGIN "" "OPTIMIZATION" "" ${ARGN})
    if(NOT PLUGIN_OPTIMIZATION)
        set(PLUGIN_OPTIMIZATION -O1)
    endif()

    set(plugin_symbols
        ifcopenshell_plugin_abi_v1
        ifcopenshell_plugin_metadata_v1
        ${REGISTRATION_SYMBOL}
    )

    target_link_options(${TARGET} PRIVATE "SHELL:-s SIDE_MODULE=2" ${PLUGIN_OPTIMIZATION})
    foreach(symbol IN LISTS plugin_symbols)
        target_link_options(${TARGET} PRIVATE "LINKER:--export=${symbol}")
    endforeach()
endfunction()

function(ifcopenshell_deploy_qt_runtime TARGET)
    if(NOT IFCOPENSHELL_DEPLOY_QT_RUNTIME)
        return()
    endif()

    if(NOT TARGET ${TARGET})
        message(FATAL_ERROR "Cannot deploy Qt runtime for unknown target '${TARGET}'.")
    endif()

    get_target_property(target_type ${TARGET} TYPE)
    if(NOT target_type STREQUAL "EXECUTABLE")
        message(FATAL_ERROR "Qt runtime deployment target '${TARGET}' is not an executable.")
    endif()

    if(NOT DEFINED QT_DEFAULT_MAJOR_VERSION)
        if(DEFINED QT_VERSION)
            set(QT_DEFAULT_MAJOR_VERSION ${QT_VERSION})
        else()
            set(QT_DEFAULT_MAJOR_VERSION 6)
        endif()
    endif()

    if(NOT TARGET Qt${QT_DEFAULT_MAJOR_VERSION}::Core)
        set(qt_find_args Qt${QT_DEFAULT_MAJOR_VERSION} COMPONENTS Core REQUIRED)
        if(DEFINED QT_DIR AND NOT QT_DIR STREQUAL "")
            list(APPEND qt_find_args PATHS ${QT_DIR})
        endif()
        find_package(${qt_find_args})
    endif()

    if(COMMAND _qt_internal_setup_deploy_support)
        if(NOT DEFINED QT_CMAKE_EXPORT_NAMESPACE AND TARGET Qt${QT_DEFAULT_MAJOR_VERSION}::Core)
            set(QT_CMAKE_EXPORT_NAMESPACE Qt${QT_DEFAULT_MAJOR_VERSION})
        endif()

        if(QT_DEFAULT_MAJOR_VERSION EQUAL 6 AND TARGET Qt6::Core)
            get_target_property(qt_core_type Qt6::Core TYPE)
            if(qt_core_type STREQUAL "SHARED_LIBRARY")
                set(QT6_IS_SHARED_LIBS_BUILD ON)
            else()
                set(QT6_IS_SHARED_LIBS_BUILD OFF)
            endif()
        endif()

        _qt_internal_setup_deploy_support()
    endif()

    set(deploy_args
        TARGET ${TARGET}
        OUTPUT_SCRIPT deploy_script
        NO_UNSUPPORTED_PLATFORM_ERROR
    )

    if(NOT IFCOPENSHELL_DEPLOY_QT_TRANSLATIONS)
        list(APPEND deploy_args NO_TRANSLATIONS)
    endif()

    list(APPEND deploy_args ${ARGN})

    if(COMMAND qt_generate_deploy_app_script)
        qt_generate_deploy_app_script(${deploy_args})
    elseif(COMMAND qt6_generate_deploy_app_script)
        qt6_generate_deploy_app_script(${deploy_args})
    else()
        message(WARNING
            "Qt runtime deployment requested for '${TARGET}', but this Qt version "
            "does not provide qt_generate_deploy_app_script()."
        )
        return()
    endif()

    install(SCRIPT ${deploy_script})
endfunction()

# Get a list of all OPTION flags from the CMakeLists.txt and store in an output LIST
function(get_all_option_flags output_list)
    # Read the contents of the CMakeLists.txt
    file(READ "${CMAKE_SOURCE_DIR}/CMakeLists.txt" cmake_contents)

    # Find all OPTION flags using a regular expression
    string(REGEX MATCHALL "[oO][pP][tT][iI][oO][nN]\\s*\\(\\s*([A-Za-z0-9_]+)" matches "${cmake_contents}")

    # Extract the variable names from the matches
    set(option_flags)
    foreach(match IN LISTS matches)
        string(REGEX REPLACE "[oO][pP][tT][iI][oO][nN]\\s*\\(\\s*([A-Za-z0-9_]+)" "\\1" option_flag "${match}")
        list(APPEND option_flags "${option_flag}")
    endforeach()

    # Return the list of OPTION flags
    set(${output_list} "${option_flags}" PARENT_SCOPE)
endfunction()

# Loop through a LIST of OPTION flags and convert to corresponding environment variables
function(convert_env_var_to_bool var_name)
    if(DEFINED ENV{${var_name}})
        string(TOUPPER "$ENV{${var_name}}" bool_value)
        if(bool_value STREQUAL "ON" OR bool_value STREQUAL "TRUE" OR bool_value STREQUAL "1")
            set(${var_name} ON CACHE BOOL "${var_name} as boolean" FORCE)
        elseif(bool_value STREQUAL "OFF" OR bool_value STREQUAL "FALSE" OR bool_value STREQUAL "0")
            set(${var_name} OFF CACHE BOOL "${var_name} as boolean" FORCE)
        else()
            # Not a bool, leave it as a string
        endif()
    else()
        # Not defined, leave it as a string
    endif()
endfunction()

# Usage:
# set(SOME_LIRARIES foo bar)
# add_debug_variants(SOME_LIRARIES "${SOME_LIRARIES}" d)
# "foo bar" -> "optimized foo debug food optimized bar debug bard"
# or
# set(SOME_LIRARIES path/foo.lib)
# add_debug_variants(SOME_LIRARIES "${SOME_LIRARIES}" "d")
# "path/foo.lib" -> "optimized path/foo.lib debug path/food.lib"
# TODO Could be refined: take the library file extension as a parameter and
# make sure the lib variable ends with not just contains it.
function(add_debug_variants NAME LIBRARIES POSTFIX)
    set(LIBRARIES_STR "${LIBRARIES}")
    set(LIBRARIES "")

    # the result, "optimized <lib> debug <lib>", needs to be a list instead of a string
    foreach(lib ${LIBRARIES_STR})
        list(APPEND LIBRARIES optimized)

        if("${lib}" MATCHES ".lib")
            string(REPLACE ".lib" "" lib ${lib})
            list(APPEND LIBRARIES ${lib}.lib)
        else()
            list(APPEND LIBRARIES ${lib})
        endif()

        list(APPEND LIBRARIES debug)

        if("${lib}" MATCHES ".lib")
            string(REPLACE ".lib" "" lib ${lib})
            list(APPEND LIBRARIES ${lib}${POSTFIX}.lib)
        else()
            list(APPEND LIBRARIES ${lib}${POSTFIX})
        endif()
    endforeach()

    set(${NAME} ${LIBRARIES} PARENT_SCOPE)
endfunction()

# E.g.
# - `get_release_variant(MYLIB "mylibd.lib" "d")` -> `MYLIB = "mylib.lib"`
# - `get_release_variant(MYLIB "mylib.lib" "d")`  -> `MYLIB = "mylib.lib"`
function(get_release_variant NAME LIBRARY POSTFIX)
    set(RELEASE_SUFFIX ".lib")
    set(DEBUG_SUFFIX "${POSTFIX}${RELEASE_SUFFIX}")
    if("${LIBRARY}" MATCHES "${DEBUG_SUFFIX}$")
        string(REPLACE "${DEBUG_SUFFIX}" "${RELEASE_SUFFIX}" LIBRARY ${LIBRARY})
    endif()
    set(${NAME} "${LIBRARY}" PARENT_SCOPE)
endfunction()

# E.g.
# - `get_debug_variant(MYLIB "mylib.lib" "d")`  -> `MYLIB = "mylibd.lib"`
# - `get_debug_variant(MYLIB "mylibd.lib" "d")` -> `MYLIB = "mylibd.lib"`
function(get_debug_variant NAME LIBRARY POSTFIX)
    set(RELEASE_SUFFIX ".lib")
    set(DEBUG_SUFFIX "${POSTFIX}${RELEASE_SUFFIX}")
    if(NOT "${LIBRARY}" MATCHES "${DEBUG_SUFFIX}$" AND "${LIBRARY}" MATCHES "${RELEASE_SUFFIX}$")
        string(REPLACE "${RELEASE_SUFFIX}" "${DEBUG_SUFFIX}" LIBRARY ${LIBRARY})
    endif()
    set(${NAME} "${LIBRARY}" PARENT_SCOPE)
endfunction()

function(files_for_ifc_version IFC_VERSION RESULT_NAME)
    set(IFC_PARSE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/ifcparse)
    set(${RESULT_NAME}
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}enum.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.cpp
        PARENT_SCOPE
    )
endfunction()
