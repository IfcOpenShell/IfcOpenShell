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

cmake_minimum_required (VERSION 2.8.5)

project (IfcOpenShell)

OPTION(UNICODE_SUPPORT "Build IfcOpenShell with Unicode support (requires ICU)." ON)
OPTION(COLLADA_SUPPORT "Build IfcConvert with COLLADA support (requires OpenCOLLADA)." ON)
OPTION(ENABLE_BUILD_OPTIMIZATIONS "Enable certain compiler and linker optimizations on RelWithDebInfo and Release builds." OFF)
OPTION(IFCCONVERT_DOUBLE_PRECISION "IfcConvert: Use double precision floating-point numbers." ON)
OPTION(USE_IFC4 "Use IFC 4 instead of IFC 2x3 (full rebuild recommended when switching this)" OFF)
OPTION(BUILD_IFCPYTHON "Build IfcPython." ON)
OPTION(BUILD_EXAMPLES "Build example applications." ON)
OPTION(USE_VLD "Use Visual Leak Detector for debugging memory leaks, MSVC-only." OFF)
OPTION(USE_MMAP "Adds a command line options to parse IFC files from memory mapped files using Boost.Iostreams" OFF)
OPTION(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
OPTION(BUILD_SHARED_LIBS "Build IfcParse and IfcGeom as shared libs (SO/DLL)." OFF)
# TODO QtViewer is deprecated ATM as it uses the 0.4 API
# OPTION(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer (requires Qt 4 framework)." OFF)


# Specify where to install files
IF(NOT BINDIR)
    set(BINDIR bin)
ENDIF()
IF(NOT IS_ABSOLUTE ${BINDIR})
    set(BINDIR ${CMAKE_INSTALL_PREFIX}/${BINDIR})
ENDIF()
MESSAGE(STATUS "BINDIR: ${BINDIR}")

IF(NOT INCLUDEDIR)
    set(INCLUDEDIR include)
ENDIF()
IF(NOT IS_ABSOLUTE ${INCLUDEDIR})
    set(INCLUDEDIR ${CMAKE_INSTALL_PREFIX}/${INCLUDEDIR})
ENDIF()
MESSAGE(STATUS "INCLUDEDIR: ${INCLUDEDIR}")

IF(NOT LIBDIR)
    set(LIBDIR lib)
ENDIF()
IF(NOT IS_ABSOLUTE ${LIBDIR})
    set(LIBDIR ${CMAKE_INSTALL_PREFIX}/${LIBDIR})
ENDIF()
MESSAGE(STATUS "LIBDIR: ${LIBDIR}")

set(IFCOPENSHELL_LIBARY_DIR "") # for *nix rpaths

if (BUILD_SHARED_LIBS)
    add_definitions(-DIFC_SHARED_BUILD)
    if (MSVC)
        message(WARNING "Building DLLs against the static VC run-time. This is not recommended if the DLLs are to be redistributed.")
        # C4521: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
        # There will be couple hundreds of these so suppress them away, https://msdn.microsoft.com/en-us/library/esew7y1w.aspx
        add_definitions(-wd4251)
    endif()
    set(IFCOPENSHELL_LIBARY_DIR "${LIBDIR}")
endif()

# Create cache entries if absent for environment variables
MACRO(UNIFY_ENVVARS_AND_CACHE VAR)
	IF ((NOT DEFINED ${VAR}) AND (NOT "$ENV{${VAR}}" STREQUAL ""))
		SET(${VAR} "$ENV{${VAR}}" CACHE STRING "${VAR}" FORCE)
	ENDIF()
ENDMACRO()

UNIFY_ENVVARS_AND_CACHE(OCC_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OCC_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(ICU_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(ICU_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(PCRE_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(PYTHON_EXECUTABLE)
IF(WIN32)
    UNIFY_ENVVARS_AND_CACHE(THREEDS_MAX_SDK_HOME)
ENDIF()


# Set INSTALL_RPATH for target
MACRO(SET_INSTALL_RPATHS _target _paths)
    SET(${_target}_rpaths "")
    FOREACH(_path ${_paths})
        LIST(FIND CMAKE_PLATFORM_IMPLICIT_LINK_DIRECTORIES "${_path}" isSystemDir)
        IF("${isSystemDir}" STREQUAL "-1")
            LIST(APPEND ${_target}_rpaths ${_path})
        ENDIF()
    ENDFOREACH()
    MESSAGE(STATUS "Set INSTALL_RPATH for ${_target}: ${${_target}_rpaths}")
    SET_TARGET_PROPERTIES(${_target} PROPERTIES INSTALL_RPATH "${${_target}_rpaths}")
ENDMACRO()

# Find Boost
IF(WIN32)
	SET(Boost_USE_STATIC_LIBS ON)
	SET(Boost_USE_STATIC_RUNTIME ON)
	SET(Boost_USE_MULTITHREADED ON)
ENDIF()

set(BOOST_COMPONENTS system program_options regex thread date_time)
if(USE_MMAP)
    if(MSVC)
        # filesystem is necessary for the utf-16 wpath
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams filesystem)
    else()
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams)
    endif()
    add_definitions(-DUSE_MMAP)
endif()

FIND_PACKAGE(Boost REQUIRED COMPONENTS ${BOOST_COMPONENTS})
MESSAGE(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
MESSAGE(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

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
        if ("${lib}" MATCHES ".lib")
            string(REPLACE ".lib" "" lib ${lib})
            list(APPEND LIBRARIES ${lib}.lib)
        else()
            list(APPEND LIBRARIES ${lib})
        endif()

        list(APPEND LIBRARIES debug)
        if ("${lib}" MATCHES ".lib")
            string(REPLACE ".lib" "" lib ${lib})
            list(APPEND LIBRARIES ${lib}${POSTFIX}.lib)
        else()
            list(APPEND LIBRARIES ${lib}${POSTFIX})
        endif()
    endforeach()
    set(${NAME} ${LIBRARIES} PARENT_SCOPE)
endfunction()

# Find Open CASCADE
IF("${OCC_INCLUDE_DIR}" STREQUAL "")
	SET(OCC_INCLUDE_DIR "/usr/include/oce/" CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
	MESSAGE(STATUS "Use OCC_INCLUDE_DIR to specify another directory")
ELSE()
	SET(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
ENDIF()

FIND_FILE(gp_Pnt_hxx "gp_Pnt.hxx" ${OCC_INCLUDE_DIR})
IF(gp_Pnt_hxx)
	MESSAGE(STATUS "Header files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find header files, aborting")
ENDIF()

SET(OPENCASCADE_LIBRARY_NAMES
	TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
	TKFillet TKSTEP TKSTEPBase TKSTEPAttr TKXSBase TKSTEP209 TKIGES TKOffset
)

IF("${OCC_LIBRARY_DIR}" STREQUAL "")
	SET(OCC_LIBRARY_DIR "/usr/lib/" CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
	MESSAGE(STATUS "Use OCC_LIBRARY_DIR to specify another directory")
ELSE()
	SET(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
ENDIF()

FIND_LIBRARY(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} NO_DEFAULT_PATH)
IF(libTKernel)
	MESSAGE(STATUS "Library files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find library files, aborting")
ENDIF()

# Use the found libTKernel as a template for all other OCC libraries
# TODO Extract this into macro/function
foreach(lib ${OPENCASCADE_LIBRARY_NAMES})
    # Make sure we'll handle the Windows/MSVC debug postfix convetion too.
    string(REPLACE TKerneld "${lib}" lib_path "${libTKernel}")
    string(REPLACE TKernel "${lib}" lib_path "${lib_path}")
	list(APPEND OPENCASCADE_LIBRARIES "${lib_path}")
endforeach()

if(MSVC)
    add_definitions(-DHAVE_NO_DLL)
    add_debug_variants(OPENCASCADE_LIBRARIES "${OPENCASCADE_LIBRARIES}" d)
endif()
if (WIN32)
    # OCC might require linking to Winsock depending on the version and build configuration
    list(APPEND OPENCASCADE_LIBRARIES ws2_32.lib)
endif()

IF(UNICODE_SUPPORT)
	# Find ICU 
	IF("${ICU_INCLUDE_DIR}" STREQUAL "")
		MESSAGE(STATUS "No ICU include directory specified")
	ENDIF()

	IF("${ICU_LIBRARY_DIR}" STREQUAL "")
		MESSAGE(STATUS "No ICU library directory specified")
		FIND_LIBRARY(icu NAMES icuuc icuucd PATHS ${ICU_LIBRARY_DIR})
	ELSE()
		FIND_LIBRARY(icu NAMES icuuc icuucd PATHS ${ICU_LIBRARY_DIR} NO_DEFAULT_PATH)
	ENDIF()

	IF(icu)
		GET_FILENAME_COMPONENT(ICU_LIBRARY_DIR ${icu} PATH)

		ADD_DEFINITIONS(-DHAVE_ICU)
		MESSAGE(STATUS "ICU libraries found")
		# NOTE icudata appears to be icudt on Windows/MSVC and icudata on others
		#      dl is included to resolve dlopen and friends symbols
		IF(WIN32)
			FIND_LIBRARY(icudt NAMES icudt PATHS ${ICU_LIBRARY_DIR} NO_DEFAULT_PATH)
			SET(ICU_LIBRARIES ${icu} ${icudt})
			add_debug_variants(ICU_LIBRARIES "${ICU_LIBRARIES}" d)
			# TODO MinGW build would appear to be using dynamic ICU regardless of this definition.
			ADD_DEFINITIONS(-DU_STATIC_IMPLEMENTATION) # required for static ICU
		ELSE()
			FIND_LIBRARY(icudt NAMES icudata PATHS ${ICU_LIBRARY_DIR} NO_DEFAULT_PATH)
			FIND_LIBRARY(icui18n NAMES icui18n PATHS ${ICU_LIBRARY_DIR} NO_DEFAULT_PATH)
			FIND_LIBRARY(dl NAMES dl)
			SET(ICU_LIBRARIES ${icu} ${icudt} ${dl} ${icui18n})
		ENDIF()
	ELSE()
		MESSAGE(FATAL_ERROR "UNICODE_SUPPORT enabled, but unable to find ICU. Disable UNICODE_SUPPORT or fix ICU paths to proceed.")
	ENDIF()
ENDIF()

IF(COLLADA_SUPPORT)
	# Find OpenCOLLADA
	IF("${OPENCOLLADA_INCLUDE_DIR}" STREQUAL "")
		MESSAGE(STATUS "No OpenCOLLADA include directory specified")
		SET(OPENCOLLADA_INCLUDE_DIR "/usr/include/opencollada" CACHE FILEPATH "OpenCOLLADA header files")
	ELSE()
		SET(OPENCOLLADA_INCLUDE_DIR "${OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
	ENDIF()

	IF("${OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
		MESSAGE(STATUS "No OpenCOLLADA library directory specified")
		FIND_LIBRARY(OPENCOLLADA_FRAMEWORK_LIB NAMES OpenCOLLADAFramework
			PATHS /usr/lib64/opencollada /usr/lib/opencollada /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib)
		GET_FILENAME_COMPONENT(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_FRAMEWORK_LIB} PATH)
	ENDIF()

	FIND_LIBRARY(OpenCOLLADAFramework NAMES OpenCOLLADAFramework OpenCOLLADAFrameworkd PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)
    if (OpenCOLLADAFramework)
        message(STATUS "OpenCOLLADA library files found")
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA libraries. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()

	SET(OPENCOLLADA_LIBRARY_DIR "${OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")

	SET(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

	FIND_FILE(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})
	IF(COLLADASWStreamWriter_h)
		MESSAGE(STATUS "OpenCOLLADA header files found")
		ADD_DEFINITIONS(-DWITH_OPENCOLLADA)
		SET(OPENCOLLADA_LIBRARY_NAMES
			GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
			OpenCOLLADAStreamWriter UTF buffer ftoa
		)

		# Use the found OpenCOLLADAFramework as a template for all other OpenCOLLADA libraries
		foreach(lib ${OPENCOLLADA_LIBRARY_NAMES})
            # Make sure we'll handle the Windows/MSVC debug postfix convetion too.
            string(REPLACE OpenCOLLADAFrameworkd "${lib}" lib_path "${OpenCOLLADAFramework}")
            string(REPLACE OpenCOLLADAFramework "${lib}" lib_path "${lib_path}")
 			list(APPEND OPENCOLLADA_LIBRARIES "${lib_path}")
		endforeach()

		if("${PCRE_LIBRARY_DIR}" STREQUAL "")
            if(WIN32)
                find_library(pcre_library NAMES pcre pcred PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)
            else()
                find_library(pcre_library NAMES pcre PATHS ${OPENCOLLADA_LIBRARY_DIR})
            endif()
			GET_FILENAME_COMPONENT(PCRE_LIBRARY_DIR ${pcre_library} PATH)
		else()
			find_library(pcre_library NAMES pcre pcred PATHS ${PCRE_LIBRARY_DIR} NO_DEFAULT_PATH)
		endif()

		if (pcre_library)
			SET(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_LIBRARY_DIR} ${PCRE_LIBRARY_DIR})
            if (MSVC)
                # Add release lib regardless whether release or debug found. Debug version will be appended below.
                list(APPEND OPENCOLLADA_LIBRARIES "${PCRE_LIBRARY_DIR}/pcre.lib")
            else()
                list(APPEND OPENCOLLADA_LIBRARIES "${pcre_library}")
            endif()
        else()
            message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find PCRE. "
                "Disable COLLADA_SUPPORT or fix PCRE_LIBRARY_DIR path to proceed.")
		endif()

		IF(MSVC)
			add_debug_variants(OPENCOLLADA_LIBRARIES "${OPENCOLLADA_LIBRARIES}" d)
		ENDIF()
	ELSE()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA headers. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
	ENDIF()
ENDIF()

# Make sure cross-referenced symbols between static OCC libraries get
# resolved. Also add thread and rt libraries.
get_filename_component(libTKernelExt ${libTKernel} EXT)
if("${libTKernelExt}" STREQUAL ".a")
    find_package(Threads)
    # OPENCASCADE_LIBRARIES repeated three times below in order to fix cyclic dependencies - use --start-group ... --end-group instead?
    set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
    if (NOT APPLE AND NOT WIN32)
        set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "rt")
    endif()
    if (NOT WIN32)
        set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "dl")
    endif()
endif()

IF(NOT CMAKE_BUILD_TYPE)
	SET(CMAKE_BUILD_TYPE "Release")
ENDIF()

if(ENABLE_BUILD_OPTIMIZATIONS)
	if(MSVC)
        # NOTE: RelWithDebInfo and Release use O2 (= /Ox /Gl /Gy/ = Og /Oi /Ot /Oy /Ob2 /Gs /GF /Gy) by default,
        # with the exception with RelWithDebInfo has /Ob1 instead. /Ob2 has been observed to improve the performance
        # of IfcConvert significantly.
        # TODO Setting of /GL and /LTCG don't seem to apply for static libraries (IfcGeom, IfcParse)
		# C++
		set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Ob2 /GL")
		set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELEASE} /Zi")
		# Linker
		# /OPT:REF enables also /OPT:ICF and disables INCREMENTAL
		set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /LTCG /OPT:REF")
		# /OPT:NOICF is recommended when /DEBUG is used (http://msdn.microsoft.com/en-us/library/xe4t6fc1.aspx)
		set(CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG /OPT:NOICF")
		set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG /OPT:REF")
		set(CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /DEBUG /OPT:NOICF")
	else()
        # GCC-like: Release should use O3 but RelWithDebInfo 02 so enforce 03. Anything other useful that could be added here?
        set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")
        set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELEASE} -O3")
	endif()
endif()

IF(MSVC)
    # Enable solution folders (free VS versions prior to 2012 don't support solution folders)
    if (MSVC_VERSION GREATER 1600)
        set_property(GLOBAL PROPERTY USE_FOLDERS ON)
    endif()

	IF(USE_VLD)
		ADD_DEFINITIONS(-DUSE_VLD)
	ENDIF()
	# Enforce Unicode for CRT and Win32 API calls
	ADD_DEFINITIONS(-D_UNICODE -DUNICODE)
	# Disable warnings about unsafe C functions; we could use the safe C99 & C11 versions if we have no need for supporting old compilers.
	ADD_DEFINITIONS(-D_SCL_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_WARNINGS)
	ADD_DEFINITIONS(-bigobj) # required for building the big ifcXXX.objs, https://msdn.microsoft.com/en-us/library/ms173499.aspx
	# Bump up the warning level from the default 3 to 4.
	ADD_DEFINITIONS(-W4)
	IF(MSVC_VERSION GREATER 1800) # > 2013
		# Disable overeager and false positives causing C4458 ("declaration of 'indentifier' hides class member"), at least for now.
		ADD_DEFINITIONS(-wd4458)
	ENDIF()
	# Link against the static VC runtime
    # TODO Make this configurable
	FOREACH(flag CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE CMAKE_CXX_FLAGS_MINSIZEREL
			CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
			CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
		IF(${flag} MATCHES "/MD")
			STRING(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")
		ENDIF()
		IF(${flag} MATCHES "/MDd")
			STRING(REGEX REPLACE "/MDd" "/MTd" ${flag} "${${flag}}")
		ENDIF()
	ENDFOREACH()
ElSE()
    add_definitions(-Wall -Wextra)
    if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        add_definitions(-Wno-tautological-constant-out-of-range-compare)
    endif()
    # -fPIC is not relevant on Windows and creates pointless warnings
    if (UNIX)
        add_definitions(-fPIC)
    endif()
ENDIF()

INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS}
	${ICU_INCLUDE_DIR} ${Boost_INCLUDE_DIRS}
)

function(files_for_ifc_version IFC_VERSION RESULT_NAME)
    set(IFC_PARSE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/ifcparse)
    set(${RESULT_NAME} 
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.h 
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}enum.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}-latebound.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.cpp
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}-latebound.cpp
        PARENT_SCOPE
    )
endfunction()

if(COMPILE_SCHEMA)
    find_package(PythonInterp)
    
    IF(NOT PYTHONINTERP_FOUND)
        MESSAGE(FATAL_ERROR "A Python interpreter is necessary when COMPILE_SCHEMA is enabled. Disable COMPILE_SCHEMA or fix Python paths to proceed.")
    ENDIF()
    
    set(IFC_RELEASE_NOT_USED "2x3" "4")
    
    # Install pyparsing if necessary
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)
    if ("${PYTHON_PACKAGE_LIST}" STREQUAL "")
        execute_process(COMMAND pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)
        if ("${PYTHON_PACKAGE_LIST}" STREQUAL "")
            message(WARNING "Failed to find pip. Pip is required to automatically install pyparsing")
        endif()
    endif()
    string(FIND "${PYTHON_PACKAGE_LIST}" pyparsing PYPARSING_FOUND)
    if ("${PYPARSING_FOUND}" STREQUAL "-1")
        message(STATUS "Installing pyparsing")
        execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)
        if (NOT "${SUCCESS}" STREQUAL "0")
            execute_process(COMMAND pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)
            if (NOT "${SUCCESS}" STREQUAL "0")
                message(WARNING "Failed to automatically install pyparsing. Please install manually")
            endif()
        endif()
    else()
        message(STATUS "Python interpreter with pyparsing found")
    endif()
    
    # Bootstrap the parser
    message(STATUS "Compiling schema, this will take a while...")
    execute_process(COMMAND ${PYTHON_EXECUTABLE} bootstrap.py express.bnf 
        WORKING_DIRECTORY ../src/ifcexpressparser 
        OUTPUT_FILE express_parser.py
        RESULT_VARIABLE SUCCESS)

    if (NOT "${SUCCESS}" STREQUAL "0")
        MESSAGE(FATAL_ERROR "Failed to bootstrap parser. Make sure pyparsing is installed")
    endif()
        
    # Generate code
    execute_process(COMMAND ${PYTHON_EXECUTABLE} ../ifcexpressparser/express_parser.py ../../${COMPILE_SCHEMA}
        WORKING_DIRECTORY ../src/ifcparse
        OUTPUT_VARIABLE COMPILED_SCHEMA_NAME)
    
    # Prevent the schema that had just been compiled from being excluded
    if("${COMPILED_SCHEMA_NAME}" STREQUAL "IFC2X3")
        list(REMOVE_ITEM IFC_RELEASE_NOT_USED "2x3")
        add_definitions(-DUSE_IFC2x3)
    elseif("${COMPILED_SCHEMA_NAME}" STREQUAL "IFC4")
        list(REMOVE_ITEM IFC_RELEASE_NOT_USED "4")
        add_definitions(-DUSE_IFC4)
    endif()
else()
    if(USE_IFC4)
        add_definitions(-DUSE_IFC4)
        set(IFC_RELEASE_NOT_USED "2x3")
    else()
        add_definitions(-DUSE_IFC2x3) # TODO Make all caps? i.e. USE_IFC2X3
        set(IFC_RELEASE_NOT_USED "4")
    endif()
endif()

# Boost >= 1.58 requires BOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE to build on some Linux distros.
if(NOT Boost_VERSION LESS 105800)
    add_definitions(-DBOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE)
endif()

# Detect OCC version on gcc/clang/mingw as
# -std=c++11 is needed for OCCT >= 7.0.0
if(NOT MSVC)
    FIND_FILE(Standard_Version "Standard_Version.hxx" ${OCC_INCLUDE_DIR})

    set(CMAKE_CONFIGURABLE_FILE_CONTENT "
        #include <Standard_Version.hxx>
        #include <iostream>
        int main(int argc, char** argv) {
            std::cout << OCC_VERSION_COMPLETE;
        }")
    configure_file(
        "${CMAKE_ROOT}/Modules/CMakeConfigurableFile.in"
        "${CMAKE_BINARY_DIR}/version.cxx" @ONLY)

    try_compile(VERSION_CHECK
        ${CMAKE_BINARY_DIR}
        "${CMAKE_BINARY_DIR}/version.cxx"
        CMAKE_FLAGS "-DINCLUDE_DIRECTORIES=${OCC_INCLUDE_DIR}"
        COPY_FILE "${CMAKE_BINARY_DIR}/version"
        OUTPUT_VARIABLE OUT
        COPY_FILE_ERROR ERR
    )

    if(${VERSION_CHECK})
        EXECUTE_PROCESS(COMMAND ${CMAKE_BINARY_DIR}/version OUTPUT_VARIABLE OCC_VERSION)
    else()
        message(FATAL_ERROR "Failed to compile OCC version test:
        ${OUT}
        ------
        ${ERR}")
    endif()

    MESSAGE(STATUS "OCC version is ${OCC_VERSION}. Detected from: ${Standard_Version}")

    if(NOT ("${OCC_VERSION}" LESS "7.0.0"))
        include(CheckCXXCompilerFlag)
        CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
        if(COMPILER_SUPPORTS_CXX11)
            add_definitions(-std=c++11)
        else()
            message(FATAL_ERROR "OCCT7 requires a compiler with C++11 support")
        endif()
    else()
        add_definitions(-std=c++03)
    endif()
endif()

set(IFCOPENSHELL_LIBRARIES IfcParse IfcGeom)

# IfcParse
file(GLOB IFCPARSE_H_FILES ../src/ifcparse/*.h)
file(GLOB IFCPARSE_CPP_FILES ../src/ifcparse/*.cpp)

foreach(IFC_RELEASE ${IFC_RELEASE_NOT_USED})
    files_for_ifc_version(${IFC_RELEASE} SOURCE_FILES_NOT_USED)
    foreach(SOURCE_FILE ${SOURCE_FILES_NOT_USED})
        list(REMOVE_ITEM IFCPARSE_CPP_FILES ${SOURCE_FILE})
        list(REMOVE_ITEM IFCPARSE_H_FILES ${SOURCE_FILE})
    endforeach()
endforeach()

set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
set_target_properties(IfcParse PROPERTIES COMPILE_FLAGS -DIFC_PARSE_EXPORTS)

IF(UNICODE_SUPPORT)
	TARGET_LINK_LIBRARIES(IfcParse ${ICU_LIBRARIES} ${Boost_LIBRARIES})
ENDIF()

# IfcGeom
file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/*.h)
file(GLOB IFCGEOM_CPP_FILES ../src/ifcgeom/*.cpp)
set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

add_library(IfcGeom ${IFCGEOM_FILES})
set_target_properties(IfcGeom PROPERTIES COMPILE_FLAGS -DIFC_GEOM_EXPORTS)

TARGET_LINK_LIBRARIES(IfcGeom IfcParse ${OPENCASCADE_LIBRARIES})

# IfcConvert
file(GLOB IFCCONVERT_CPP_FILES ../src/ifcconvert/*.cpp)
file(GLOB IFCCONVERT_H_FILES ../src/ifcconvert/*.h)
set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
ADD_EXECUTABLE(IfcConvert ${IFCCONVERT_FILES})
if (IFCCONVERT_DOUBLE_PRECISION)
    set_target_properties(IfcConvert PROPERTIES COMPILE_FLAGS -DIFCCONVERT_DOUBLE_PRECISION)
endif()

TARGET_LINK_LIBRARIES(IfcConvert ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${OPENCOLLADA_LIBRARIES} ${ICU_LIBRARIES})
if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    # Only set RPATHs when building shared libraries (i.e. IfcParse and
    # IfcGeom are dynamically linked). Not necessarily a perfect solution
    # but probably a good indication of whether RPATHs are necessary.
    SET_INSTALL_RPATHS(IfcConvert "${IFCOPENSHELL_LIBARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS};${OPENCOLLADA_LIBRARY_DIR};${ICU_LIBRARY_DIR}")
endif()

# IfcGeomServer
file(GLOB CPP_FILES ../src/ifcgeomserver/*.cpp)
file(GLOB H_FILES ../src/ifcgeomserver/*.h)
set(SOURCE_FILES ${CPP_FILES} ${H_FILES})
ADD_EXECUTABLE(IfcGeomServer ${SOURCE_FILES})
TARGET_LINK_LIBRARIES(IfcGeomServer ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${ICU_LIBRARIES})
if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    SET_INSTALL_RPATHS(IfcGeomServer "${IFCOPENSHELL_LIBARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS};${ICU_LIBRARY_DIR}")
endif()

IF(BUILD_IFCPYTHON)
	ADD_SUBDIRECTORY(../src/ifcwrap ifcwrap)
ENDIF()

IF(BUILD_EXAMPLES)
	ADD_SUBDIRECTORY(../src/examples examples)
ENDIF()

IF(BUILD_IFCMAX)
	ADD_SUBDIRECTORY(../src/ifcmax ifcmax)
ENDIF()

# CMake installation targets
INSTALL(FILES ${IFCPARSE_H_FILES} 
	DESTINATION ${INCLUDEDIR}/ifcparse
)

INSTALL(FILES ${IFCGEOM_H_FILES} 
	DESTINATION ${INCLUDEDIR}/ifcgeom
)

INSTALL(TARGETS IfcParse IfcGeom IfcConvert IfcGeomServer
	ARCHIVE DESTINATION ${LIBDIR}
	LIBRARY DESTINATION ${LIBDIR}
	RUNTIME DESTINATION ${BINDIR}
)
