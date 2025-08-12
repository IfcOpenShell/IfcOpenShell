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
    if((NOT DEFINED ${VAR}) AND(NOT "$ENV{${VAR}}" STREQUAL ""))
        set(${VAR} "$ENV{${VAR}}" CACHE STRING "${VAR}" FORCE)
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

function(files_for_ifc_version IFC_VERSION RESULT_NAME)
    set(IFC_PARSE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/ifcparse)
    set(${RESULT_NAME}
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}enum.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.cpp
        PARENT_SCOPE
    )
endfunction()
