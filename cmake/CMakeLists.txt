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
OPTION(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
# TODO QtViewer is deprecated ATM as it uses the 0.4 API
# OPTION(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer (requires Qt 4 framework)." OFF)


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

# Find Boost
IF(MSVC)
	SET(Boost_USE_STATIC_LIBS ON)
	SET(Boost_USE_STATIC_RUNTIME ON)
	SET(Boost_USE_MULTITHREADED ON)
ENDIF()
FIND_PACKAGE(Boost REQUIRED COMPONENTS system program_options regex thread date_time)
MESSAGE(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
MESSAGE(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

# Usage:
# SET(SOME_LIRARIES foo bar)
# ADD_DEBUG_VARIANTS(SOME_LIRARIES "${SOME_LIRARIES}" "d")
# "foo bar" -> "optimized foo debug food optimized bar debug bard"
FUNCTION(ADD_DEBUG_VARIANTS NAME LIBRARIES POSTFIX)
	SET(LIBRARIES_STR "${LIBRARIES}")
	SET(LIBRARIES "")
	FOREACH(lib ${LIBRARIES_STR})
		SET(LIBRARIES "${LIBRARIES} optimized ${lib}")
		SET(LIBRARIES "${LIBRARIES} debug ${lib}${POSTFIX}")
	ENDFOREACH()
	STRING(STRIP ${LIBRARIES} LIBRARIES) # leading and trailing whitespace cause confusion
	SEPARATE_ARGUMENTS(LIBRARIES) # "optimized <lib> debug <lib>" needs to be a list instead of a string
	SET(${NAME} ${LIBRARIES} PARENT_SCOPE)
ENDFUNCTION()

# Find Open CASCADE
IF("${OCC_INCLUDE_DIR}" STREQUAL "")
	SET(OCC_INCLUDE_DIR "/usr/include/oce/" CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for opencascade include files in: ${OCC_INCLUDE_DIR}")
	MESSAGE(STATUS "Use OCC_INCLUDE_DIR to specify another directory")
ELSE()
	SET(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for opencascade include files in: ${OCC_INCLUDE_DIR}")
ENDIF()

FIND_FILE(gp_Pnt_hxx "gp_Pnt.hxx" ${OCC_INCLUDE_DIR} /usr/inc /usr/local/inc /usr/local/include/oce)
IF(gp_Pnt_hxx)
	MESSAGE(STATUS "Header files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find header files, aborting")
ENDIF()

SET(OPENCASCADE_LIBRARIES
	TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
	TKFillet TKSTEP TKSTEPBase TKSTEPAttr TKXSBase TKSTEP209 TKIGES TKOffset
)

IF(MSVC)
	ADD_DEBUG_VARIANTS(OPENCASCADE_LIBRARIES "${OPENCASCADE_LIBRARIES}" "d")
ENDIF()

IF("${OCC_LIBRARY_DIR}" STREQUAL "")
	SET(OCC_LIBRARY_DIR "/usr/lib/" CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for opencascade library files in: ${OCC_LIBRARY_DIR}")
	MESSAGE(STATUS "Use OCC_LIBRARY_DIR to specify another directory")
ELSE()
	SET(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for opencascade library files in: ${OCC_LIBRARY_DIR}")
ENDIF()

FIND_LIBRARY(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64)
IF(libTKernel)
	MESSAGE(STATUS "Library files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find library files, aborting")
ENDIF()

IF(UNICODE_SUPPORT)
	# Find ICU 
	IF("${ICU_INCLUDE_DIR}" STREQUAL "")
		MESSAGE(STATUS "No ICU include directory specified")
	ElSE()
		SET(ICU_INCLUDE_DIR "${ICU_INCLUDE_DIR}" CACHE FILEPATH "ICU header files")
	ENDIF()

	IF("${ICU_LIBRARY_DIR}" STREQUAL "")
		MESSAGE(STATUS "No ICU library directory specified")
	ElSE()
		SET(ICU_LIBRARY_DIR "${ICU_LIBRARY_DIR}" CACHE FILEPATH "ICU library files")
	ENDIF()

	FIND_LIBRARY(icu NAMES icuuc icuucd PATHS /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64 ${ICU_LIBRARY_DIR})

	IF(icu)
		ADD_DEFINITIONS(-DHAVE_ICU)
		MESSAGE(STATUS "ICU libraries found")
		# NOTE icudata appears to be icudt on Windows/MSVC and icudata on others
		#      dl is included to resolve dlopen and friends symbols
		IF(MSVC)
			SET(ICU_LIBRARIES icuuc icudt)
			ADD_DEBUG_VARIANTS(ICU_LIBRARIES "${ICU_LIBRARIES}" "d")
			ADD_DEFINITIONS(-DU_STATIC_IMPLEMENTATION) # required for static ICU
		ELSE()
			SET(ICU_LIBRARIES icuuc icudata dl)
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
	ElSE()
		SET(OPENCOLLADA_INCLUDE_DIR "${OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
	ENDIF()

	IF("${OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
		MESSAGE(STATUS "No OpenCOLLADA library directory specified")
		SET(OPENCOLLADA_LIBRARY_DIR "/usr/lib/opencollada" CACHE FILEPATH "OpenCOLLADA library files")
	ElSE()
		SET(OPENCOLLADA_LIBRARY_DIR "${OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")
	ENDIF()

	SET(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

	FIND_FILE(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})
	IF(COLLADASWStreamWriter_h)
		MESSAGE(STATUS "OpenCOLLADA header files found")
		ADD_DEFINITIONS(-DWITH_OPENCOLLADA)
		SET(OPENCOLLADA_LIBRARIES
			GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
			OpenCOLLADAStreamWriter UTF buffer ftoa pcre
		)
		IF(NOT "${PCRE_LIBRARY_DIR}" STREQUAL "")
			SET(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_LIBRARY_DIR} ${PCRE_LIBRARY_DIR})
		ENDIF()
		IF(MSVC)
			ADD_DEBUG_VARIANTS(OPENCOLLADA_LIBRARIES "${OPENCOLLADA_LIBRARIES}" "d")
		ENDIF()
	ELSE()
		MESSAGE(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA. Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
	ENDIF()
ENDIF()

 # TODO Are these needed on other platforms still or can these be removed for good?
IF (NOT WIN32)
	INCLUDE(CheckIncludeFileCXX)

	MACRO(CHECK_ADD_OCE_OCC_DEF INCLUDE)
		STRING(REPLACE . _ STR ${INCLUDE})
		STRING(TOUPPER ${STR} STR)
		CHECK_INCLUDE_FILE_CXX("${INCLUDE}" FOUND_${STR})
		IF(FOUND_${STR})
			ADD_DEFINITIONS(-DOCE_HAVE_${STR})
			ADD_DEFINITIONS(-DHAVE_${STR})
		ENDIF(FOUND_${STR})
	ENDMACRO()

	CHECK_ADD_OCE_OCC_DEF(limits)
	CHECK_ADD_OCE_OCC_DEF(climits)
	CHECK_ADD_OCE_OCC_DEF(limits.h)
	CHECK_ADD_OCE_OCC_DEF(fstream)
	CHECK_ADD_OCE_OCC_DEF(fstream.h)
	CHECK_ADD_OCE_OCC_DEF(iomanip)
	CHECK_ADD_OCE_OCC_DEF(iomanip.h)
	CHECK_ADD_OCE_OCC_DEF(iostream)
	CHECK_ADD_OCE_OCC_DEF(iostream.h)
ENDIF()

IF(NOT CMAKE_BUILD_TYPE)
	SET(CMAKE_BUILD_TYPE "Release")
ENDIF()

# NOTE: RelWithDebInfo and Release use O2 (= /Ox /Gl /Gy/ = Og /Oi /Ot /Oy /Ob2 /Gs /GF /Gy) by default,
# with the exception with RelWithDebInfo has /Ob1 instead. /Ob2 has been observed to improve the performance
# of IfcConvert significantly.
# TODO Setting of /GL and /LTCG don't seem to apply for static libraries (IfcGeom, IfcParse)
if(ENABLE_BUILD_OPTIMIZATIONS)
	if(MSVC)
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
		#TODO GCC (& Clang?) optimizations
		message(STATUS "ENABLE_BUILD_OPTIMIZATIONS not implemented for GCC/non-MSVC compilers.)")
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
	ADD_DEFINITIONS(-fPIC -Wno-non-virtual-dtor)
ENDIF()

INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS}
	${ICU_INCLUDE_DIR} ${Boost_INCLUDE_DIRS}
)
if(NOT WIN32)
	INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} /usr/inc /usr/local/inc /usr/local/include/oce)
endif()

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

LINK_DIRECTORIES(${LINK_DIRECTORIES} ${IfcOpenShell_BINARY_DIR} ${OCC_LIBRARY_DIR} ${OPENCOLLADA_LIBRARY_DIR}
	${ICU_LIBRARY_DIR} ${Boost_LIBRARY_DIRS}
)
if(NOT WIN32)
	LINK_DIRECTORIES(${LINK_DIRECTORIES} /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64)
endif()

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

ADD_LIBRARY(IfcParse STATIC ${IFCPARSE_FILES})

IF(UNICODE_SUPPORT)
	TARGET_LINK_LIBRARIES(IfcParse ${ICU_LIBRARIES} ${Boost_LIBRARIES})
ENDIF()

# IfcGeom
file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/*.h)
file(GLOB IFCGEOM_CPP_FILES ../src/ifcgeom/*.cpp)

set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})
ADD_LIBRARY(IfcGeom STATIC ${IFCGEOM_FILES})

TARGET_LINK_LIBRARIES(IfcGeom IfcParse)

# IfcConvert
if (IFCCONVERT_DOUBLE_PRECISION)
    add_definitions(-DIFCCONVERT_DOUBLE_PRECISION)
endif()
file(GLOB IFCCONVERT_CPP_FILES ../src/ifcconvert/*.cpp)
file(GLOB IFCCONVERT_H_FILES ../src/ifcconvert/*.h)
set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
ADD_EXECUTABLE(IfcConvert ${IFCCONVERT_FILES})

# Make sure cross-referenced symbols between static OCC libraries get
# resolved. Also add thread and rt libraries.
get_filename_component(libTKernelExt ${libTKernel} EXT)
if("${libTKernelExt}" STREQUAL ".a")
    find_package(Threads)
    if (NOT APPLE)
        set(LIB_RT "rt")
    endif()
    set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} ${LIB_RT} dl)
endif()

TARGET_LINK_LIBRARIES(IfcConvert IfcParse IfcGeom ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${OPENCOLLADA_LIBRARIES} ${ICU_LIBRARIES})

# IfcGeomServer
file(GLOB CPP_FILES ../src/ifcgeomserver/*.cpp)
file(GLOB H_FILES ../src/ifcgeomserver/*.h)
set(SOURCE_FILES ${CPP_FILES} ${H_FILES})
ADD_EXECUTABLE(IfcGeomServer ${SOURCE_FILES})

TARGET_LINK_LIBRARIES(IfcGeomServer IfcParse IfcGeom ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${ICU_LIBRARIES})

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
INSTALL(FILES ${IFCPARSE_H_FILES} DESTINATION include/ifcparse)
INSTALL(FILES ${IFCGEOM_H_FILES} DESTINATION include/ifcgeom)
INSTALL(TARGETS IfcConvert IfcGeomServer DESTINATION bin)
INSTALL(TARGETS IfcParse IfcGeom DESTINATION lib)
