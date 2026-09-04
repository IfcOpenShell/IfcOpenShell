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

function(ifcopenshell_native_plugin_target TARGET MODULE_TARGET)
    if(WASM_BUILD)
        return()
    endif()
    set_target_properties(${TARGET} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "$<TARGET_FILE_DIR:${MODULE_TARGET}>"
        LIBRARY_OUTPUT_DIRECTORY "$<TARGET_FILE_DIR:${MODULE_TARGET}>"
    )
endfunction()

function(ifcopenshell_wasm_plugin_dependency OUT_VAR)
    if(WASM_BUILD)
        # wasm-ld fails when the static `plugin` archive is linked into both the
        # main module and SIDE_MODULE plugins. The main module owns `plugin`.
        set(${OUT_VAR} "" PARENT_SCOPE)
    else()
        set(${OUT_VAR} plugin PARENT_SCOPE)
    endif()
endfunction()

function(ifcopenshell_wasm_plugin_import_from_main TARGET)
    if(NOT WASM_BUILD)
        return()
    endif()

    cmake_parse_arguments(IMPORT "" "" "DEPENDS" ${ARGN})
    foreach(dep IN LISTS IMPORT_DEPENDS)
        if(NOT TARGET ${dep})
            continue()
        endif()
        add_dependencies(${TARGET} ${dep})
        foreach(prop INCLUDE_DIRECTORIES INTERFACE_INCLUDE_DIRECTORIES)
            get_target_property(values ${dep} ${prop})
            if(values)
                target_include_directories(${TARGET} PRIVATE ${values})
            endif()
        endforeach()
        foreach(prop INTERFACE_COMPILE_DEFINITIONS COMPILE_DEFINITIONS)
            get_target_property(values ${dep} ${prop})
            if(values)
                target_compile_definitions(${TARGET} PRIVATE ${values})
            endif()
        endforeach()
    endforeach()
endfunction()

function(ifcopenshell_wasm_define_main_import_target SOURCE_TARGET)
    if(NOT WASM_BUILD)
        return()
    endif()
    if(NOT TARGET ${SOURCE_TARGET})
        message(FATAL_ERROR "Unknown source target '${SOURCE_TARGET}'")
    endif()

    cmake_parse_arguments(IMPORT "" "NAME" "INTERFACE_LINK_LIBRARIES" ${ARGN})
    if(NOT IMPORT_NAME)
        set(IMPORT_NAME "${SOURCE_TARGET}__wasm_main_import")
    endif()
    if(TARGET ${IMPORT_NAME})
        set_property(TARGET ${SOURCE_TARGET} PROPERTY IFCOPENSHELL_WASM_MAIN_IMPORT_TARGET "${IMPORT_NAME}")
        return()
    endif()

    add_library(${IMPORT_NAME} INTERFACE)
    foreach(prop IN ITEMS INCLUDE_DIRECTORIES INTERFACE_INCLUDE_DIRECTORIES)
        get_target_property(values ${SOURCE_TARGET} ${prop})
        if(values)
            target_include_directories(${IMPORT_NAME} INTERFACE ${values})
        endif()
    endforeach()
    foreach(prop IN ITEMS INTERFACE_COMPILE_DEFINITIONS COMPILE_DEFINITIONS)
        get_target_property(values ${SOURCE_TARGET} ${prop})
        if(values)
            target_compile_definitions(${IMPORT_NAME} INTERFACE ${values})
        endif()
    endforeach()
    if(IMPORT_INTERFACE_LINK_LIBRARIES)
        target_link_libraries(${IMPORT_NAME} INTERFACE ${IMPORT_INTERFACE_LINK_LIBRARIES})
    endif()
    set_property(TARGET ${SOURCE_TARGET} PROPERTY IFCOPENSHELL_WASM_MAIN_IMPORT_TARGET "${IMPORT_NAME}")
endfunction()

function(ifcopenshell_wasm_plugin_target_link TARGET)
    cmake_parse_arguments(PLUGIN "" "" "MAIN_TARGETS;PRIVATE" ${ARGN})
    if(WASM_BUILD)
        if(PLUGIN_PRIVATE)
            target_link_libraries(${TARGET} PRIVATE ${PLUGIN_PRIVATE})
        endif()
        if(PLUGIN_MAIN_TARGETS)
            set(import_targets)
            foreach(main_target IN LISTS PLUGIN_MAIN_TARGETS)
                if(NOT TARGET ${main_target})
                    continue()
                endif()
                add_dependencies(${TARGET} ${main_target})
                get_target_property(import_target ${main_target} IFCOPENSHELL_WASM_MAIN_IMPORT_TARGET)
                if(import_target AND TARGET ${import_target})
                    list(APPEND import_targets ${import_target})
                else()
                    ifcopenshell_wasm_plugin_import_from_main(${TARGET} DEPENDS ${main_target})
                endif()
            endforeach()
            if(import_targets)
                target_link_libraries(${TARGET} PRIVATE ${import_targets})
            endif()
        endif()
    else()
        target_link_libraries(${TARGET} PRIVATE ${PLUGIN_MAIN_TARGETS} ${PLUGIN_PRIVATE})
    endif()
endfunction()

function(ifcopenshell_wasm_main_module_link TARGET)
    if(NOT WASM_BUILD)
        return()
    endif()

    set(wrapper "${CMAKE_SOURCE_DIR}/cmake/emscripten-main-module-link.sh")
    if(EXISTS "${wrapper}")
        set_property(TARGET ${TARGET} PROPERTY RULE_LAUNCH_LINK "${wrapper}")
    endif()
endfunction()

function(ifcopenshell_wasm_plugins_dir OUT_VAR)
    set(${OUT_VAR} "${CMAKE_BINARY_DIR}/ifcwrap/wasm/plugins" PARENT_SCOPE)
endfunction()

function(ifcopenshell_wasm_set_plugin_info TARGET KIND ID)
    if(NOT WASM_BUILD)
        return()
    endif()
    set_target_properties(${TARGET} PROPERTIES
        IFCOPENSHELL_PLUGIN_KIND "${KIND}"
        IFCOPENSHELL_PLUGIN_ID "${ID}"
    )
endfunction()

function(ifcopenshell_wasm_configure_plugin_target TARGET)
    if(NOT WASM_BUILD)
        return()
    endif()

    cmake_parse_arguments(PLUGIN "" "KIND;ID;SYMBOL_ID;EXPORT_SYMBOL" "DEPENDS" ${ARGN})
    foreach(required IN ITEMS KIND ID SYMBOL_ID EXPORT_SYMBOL)
        if(NOT PLUGIN_${required})
            message(FATAL_ERROR "ifcopenshell_wasm_configure_plugin_target(${TARGET}) requires ${required}")
        endif()
    endforeach()

    ifcopenshell_wasm_plugins_dir(plugin_runtime_dir)
    set_target_properties(${TARGET} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${plugin_runtime_dir}"
        IFCOPENSHELL_PLUGIN_DEPENDS "${PLUGIN_DEPENDS}"
    )
    target_compile_definitions(${TARGET} PRIVATE IFCOPENSHELL_WASM_PLUGIN_ID=${PLUGIN_SYMBOL_ID})
    target_link_options(${TARGET} PRIVATE "LINKER:--export=${PLUGIN_EXPORT_SYMBOL}")
    ifcopenshell_wasm_set_plugin_info(${TARGET} "${PLUGIN_KIND}" "${PLUGIN_ID}")
endfunction()

function(ifcopenshell_wasm_plugin_manifest_entry TARGET OUT_ENTRY)
    if(NOT TARGET ${TARGET})
        set(${OUT_ENTRY} "" PARENT_SCOPE)
        return()
    endif()

    get_target_property(kind ${TARGET} IFCOPENSHELL_PLUGIN_KIND)
    get_target_property(plugin_id ${TARGET} IFCOPENSHELL_PLUGIN_ID)
    if(NOT kind OR NOT plugin_id)
        set(${OUT_ENTRY} "" PARENT_SCOPE)
        return()
    endif()

    get_target_property(output_name ${TARGET} OUTPUT_NAME)
    if(NOT output_name)
        set(output_name ${TARGET})
    endif()

    get_target_property(depends ${TARGET} IFCOPENSHELL_PLUGIN_DEPENDS)
    if(NOT depends OR depends STREQUAL "depends-NOTFOUND")
        set(depends "")
    endif()
    string(REPLACE ";" "," depends_csv "${depends}")
    set(${OUT_ENTRY} "${kind}|${plugin_id}|${output_name}|${depends_csv}" PARENT_SCOPE)
endfunction()

function(ifcopenshell_wasm_plugin_link_options TARGET REGISTRATION_SYMBOL)
    ifcopenshell_plugin_target(${TARGET})

    if(NOT WASM_BUILD)
        return()
    endif()

    cmake_parse_arguments(PLUGIN "EXPORT_DYNAMIC" "OPTIMIZATION;SIDE_MODULE" "" ${ARGN})
    if(NOT PLUGIN_OPTIMIZATION)
        # WASM plugins optimize for size by default (side modules download on demand).
        set(PLUGIN_OPTIMIZATION -Oz)
    endif()
    if(NOT PLUGIN_SIDE_MODULE)
        set(PLUGIN_SIDE_MODULE 2)
    endif()

    set(plugin_symbols
        ifcopenshell_plugin_abi_v1
        ifcopenshell_plugin_metadata_v1
        ${REGISTRATION_SYMBOL}
    )

    target_compile_options(${TARGET} PRIVATE -fwasm-exceptions)
    target_link_options(${TARGET} PRIVATE "SHELL:-fwasm-exceptions" "SHELL:-s SIDE_MODULE=${PLUGIN_SIDE_MODULE}" "SHELL:-s ALLOW_TABLE_GROWTH=1" "SHELL:-s ERROR_ON_UNDEFINED_SYMBOLS=0" "SHELL:-sSUPPORT_LONGJMP=wasm" ${PLUGIN_OPTIMIZATION})
    if(PLUGIN_EXPORT_DYNAMIC)
        # Export all symbols defined in this module so dependent side modules
        # (tree/serializer plugins) can resolve them at runtime via
        # allowUndefinedSymbols. Without this, wasm-ld dead-code-eliminates
        # symbols that are only referenced by external side modules, not from
        # within the module itself (e.g. OpenCascadeShape::shape()).
        target_link_options(${TARGET} PRIVATE "LINKER:--export-dynamic")
    endif()
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
