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

cmake_minimum_required(VERSION 3.1.3)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)  # not necessary, but encouraged

project (IfcOpenShell VERSION 0.7.0)

cmake_policy(SET CMP0048 NEW)
cmake_policy(SET CMP0074 NEW)
cmake_policy(SET CMP0078 OLD)
cmake_policy(SET CMP0086 NEW)

# use extra version to make pre-release using eg semver
set( EXTRA_VERSION "-alpha.3")

foreach(max_year RANGE 2014 2030)
set(max_sdk "$ENV{ADSK_3DSMAX_SDK_${max_year}}")
if (NOT "${max_sdk}" STREQUAL "")
MESSAGE(STATUS "Autodesk 3ds Max SDK found at ${max_sdk}")
set(HAS_MAX TRUE)
endif()
endforeach()

OPTION(COLLADA_SUPPORT "Build IfcConvert with COLLADA support (requires OpenCOLLADA)." ON)
OPTION(IFCXML_SUPPORT "Build IfcParse with ifcXML support (requires libxml2)." ON)
OPTION(ENABLE_BUILD_OPTIMIZATIONS "Enable certain compiler and linker optimizations on RelWithDebInfo and Release builds." OFF)
OPTION(BUILD_PACKAGE "" OFF)
OPTION(BUILD_IFCGEOM "Build IfcGeom." ON)
OPTION(BUILD_DOCUMENTATION "Build IfcOpenShell Documentation." OFF)
OPTION(BUILD_IFCPYTHON "Build IfcPython." ON)
OPTION(BUILD_EXAMPLES "Build example applications." ON)
OPTION(BUILD_GEOMSERVER "Build IfcGeomServer executable." ON)
OPTION(BUILD_CONVERT "Build IfcConvert executable." ON)
OPTION(HDF5_SUPPORT "Enable HDF5 support (requires HDF5, zlib)" ON)
OPTION(USE_VLD "Use Visual Leak Detector for debugging memory leaks, MSVC-only." OFF)
OPTION(USE_MMAP "Adds a command line options to parse IFC files from memory mapped files using Boost.Iostreams" OFF)
OPTION(BUILD_SHARED_LIBS "Build IfcParse and IfcGeom as shared libs (SO/DLL)." OFF)
if (${HAS_MAX})
OPTION(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
endif()
if (${BUILD_CONVERT})
OPTION(GLTF_SUPPORT "Build IfcConvert with glTF support (requires json.hpp)." OFF)
endif()
OPTION(USERSPACE_PYTHON_PREFIX "Installs IfcPython for the current user only instead of system-wide." OFF)
OPTION(ADD_COMMIT_SHA "Add commit sha and branch in version number, warning results in many rebuilds, requires git" OFF)

IF(NOT CMAKE_BUILD_TYPE)
	SET(CMAKE_BUILD_TYPE "Release")
ENDIF()

# TODO QtViewer is deprecated ATM as it uses the 0.4 API
# OPTION(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer (requires Qt 4 framework)." OFF)
include(GNUInstallDirs)
if((BUILD_CONVERT OR BUILD_GEOMSERVER OR BUILD_IFCPYTHON) AND (NOT BUILD_IFCGEOM))
    message(STATUS "'IfcGeom' is required with current outputs")
    set(BUILD_IFCGEOM ON)
endif()

# Specify where to install files
IF(NOT BINDIR)
    set(BINDIR bin)
ENDIF()
IF(NOT IS_ABSOLUTE ${BINDIR})
    set(BINDIR ${CMAKE_INSTALL_BINDIR})
ENDIF()
MESSAGE(STATUS "BINDIR: ${BINDIR}")

IF(NOT INCLUDEDIR)
    set(INCLUDEDIR include)
ENDIF()
IF(NOT IS_ABSOLUTE ${INCLUDEDIR})
    set(INCLUDEDIR ${CMAKE_INSTALL_INCLUDEDIR})
ENDIF()
MESSAGE(STATUS "INCLUDEDIR: ${INCLUDEDIR}")

IF(NOT LIBDIR)
    set(LIBDIR lib)
ENDIF()
IF(NOT IS_ABSOLUTE ${LIBDIR})
    set(LIBDIR ${CMAKE_INSTALL_LIBDIR})
ENDIF()
MESSAGE(STATUS "LIBDIR: ${LIBDIR}")

set(IFCOPENSHELL_LIBRARY_DIR "") # for *nix rpaths

if (BUILD_SHARED_LIBS)
    add_definitions(-DIFC_SHARED_BUILD)
    if (MSVC)
        message(WARNING "Building DLLs against the static VC run-time. This is not recommended if the DLLs are to be redistributed.")
        # C4521: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
        # There will be couple hundreds of these so suppress them away, https://msdn.microsoft.com/en-us/library/esew7y1w.aspx
        add_definitions(-wd4251)
    endif()
    set(IFCOPENSHELL_LIBRARY_DIR "${LIBDIR}")
endif()

# Create cache entries if absent for environment variables
MACRO(UNIFY_ENVVARS_AND_CACHE VAR)
	IF ((NOT DEFINED ${VAR}) AND (NOT "$ENV{${VAR}}" STREQUAL ""))
		SET(${VAR} "$ENV{${VAR}}" CACHE STRING "${VAR}" FORCE)
	ENDIF()
ENDMACRO()

UNIFY_ENVVARS_AND_CACHE(OCC_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OCC_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(LIBXML2_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(LIBXML2_LIBRARIES)
UNIFY_ENVVARS_AND_CACHE(PCRE_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(PYTHON_EXECUTABLE)
UNIFY_ENVVARS_AND_CACHE(HDF5_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARIES)
UNIFY_ENVVARS_AND_CACHE(BOOST_ROOT)
UNIFY_ENVVARS_AND_CACHE(BOOST_LIBRARYDIR)

UNIFY_ENVVARS_AND_CACHE(CGAL_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(CGAL_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_LIBRARY_DIR)

if (GLTF_SUPPORT AND BUILD_CONVERT)
UNIFY_ENVVARS_AND_CACHE(JSON_INCLUDE_DIR)
FIND_FILE(json_hpp "json.hpp" ${JSON_INCLUDE_DIR}/nlohmann)
IF(json_hpp)
	MESSAGE(STATUS "JSON for Modern C++ header file found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find JSON for Modern C++ header file, aborting")
ENDIF()
add_definitions(-DWITH_GLTF)
set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_GLTF)
endif()

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

# Find Boost: On win32 the (hardcoded) default is to use static libraries and
# runtime, when doing running conda-build we pick what conda prepared for us.
IF(WIN32 AND ("$ENV{CONDA_BUILD}" STREQUAL ""))
	SET(Boost_USE_STATIC_LIBS ON)
	SET(Boost_USE_STATIC_RUNTIME OFF)
	SET(Boost_USE_MULTITHREADED ON)
    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and wrong libraries would be asked for when code is
    # compiled with a toolset different from default.
    if(MSVC)
        ADD_DEFINITIONS(-DBOOST_ALL_NO_LIB)
        # Necessary for boost version >= 1.67
        SET(BCRYPT_LIBRARIES "bcrypt.lib")
    ENDIF()
ELSE()
    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and it's going to conflict if there are multiple, as is
    # the case in conda-forge's libboost feedstock.
    ADD_DEFINITIONS(-DBOOST_ALL_NO_LIB)
    IF(WIN32)
        # Necessary for boost version >= 1.67
        SET(BCRYPT_LIBRARIES "bcrypt.lib")
    ENDIF()
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

# libxml2 is required for IFCXML (optional) and SVGFILL (mandatory)
find_package(LibXml2 REQUIRED)

if (IFCXML_SUPPORT)
    add_definitions(-DWITH_IFCXML)
	set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_IFCXML)
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

if(BUILD_IFCGEOM)

IF(MSVC)
    add_debug_variants(LIBXML2_LIBRARIES "${LIBXML2_LIBRARIES}" d)
ENDIF()

# Open CASCADE
IF("${OCC_INCLUDE_DIR}" STREQUAL "")
    FIND_PATH(OCC_INCLUDE_DIR Standard_Version.hxx
        [PATHS
            /usr/include/occt
            /usr/include/oce
            /usr/include/opencascade
        ]
        REQUIRED
    )
    IF(OCC_INCLUDE_DIR)
        MESSAGE(STATUS "Found Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
    ELSE()
        MESSAGE(FATAL_ERROR "Unable to find Open CASCADE include directory, specify OCC_INCLUDE_DIR manually.")
    ENDIF()
ELSE()
    SET(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
    MESSAGE(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
ENDIF()

SET(OPENCASCADE_LIBRARY_NAMES
    TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
    TKFillet TKSTEP TKSTEPBase TKSTEPAttr TKXSBase TKSTEP209 TKIGES TKOffset TKHLR
    
    # @todo investigate the exact conditions when this is necessary
    TKBin
)

IF("${OCC_LIBRARY_DIR}" STREQUAL "")
    find_library(OCC_LIBRARY TKernel
        [PATHS
            /usr/lib
        ]
        REQUIRED
    )
    IF(OCC_LIBRARY)
	GET_FILENAME_COMPONENT(OCC_LIBRARY_DIR ${OCC_LIBRARY} PATH)
        MESSAGE(STATUS "Found Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
    ELSE()
        MESSAGE(FATAL_ERROR "Unable find Open CASCADE library directory, specify OCC_LIBRARY_DIR manually.")
    ENDIF()
ELSE()
    SET(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
    MESSAGE(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
ENDIF()

FIND_LIBRARY(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} NO_DEFAULT_PATH)
IF(libTKernel)
    MESSAGE(STATUS "Required Open Cascade Library files found")
ELSE()
    MESSAGE(FATAL_ERROR "Unable to find Open Cascade library files, aborting")
ENDIF()

# Use the found libTKernel as a template for all other OCC libraries
# TODO Extract this into macro/function
foreach(lib ${OPENCASCADE_LIBRARY_NAMES})
    # Make sure we'll handle the Windows/MSVC debug postfix convention too.
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

# Make sure cross-referenced symbols between static OCC libraries get
# resolved. Also add thread and rt libraries.
get_filename_component(libTKernelExt ${libTKernel} EXT)
if("${libTKernelExt}" STREQUAL ".a")
    set(OCCT_STATIC ON)
endif()

if(OCCT_STATIC)
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

endif(BUILD_IFCGEOM)

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
		set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_OPENCOLLADA)

		SET(OPENCOLLADA_LIBRARY_NAMES
			GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
			OpenCOLLADAStreamWriter UTF buffer ftoa
		)

		# Use the found OpenCOLLADAFramework as a template for all other OpenCOLLADA libraries
		foreach(lib ${OPENCOLLADA_LIBRARY_NAMES})
            # Make sure we'll handle the Windows/MSVC debug postfix convention too.
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

if(HDF5_SUPPORT)
    IF("${HDF5_INCLUDE_DIR}" STREQUAL "")
		MESSAGE(STATUS "No HDF5 include directory specified")
	ElSE()
		SET(HDF5_INCLUDE_DIR "${HDF5_INCLUDE_DIR}" CACHE FILEPATH "HDF5 header files")
	ENDIF()
	
    IF("${HDF5_LIBRARY_DIR}" STREQUAL "")
		MESSAGE(STATUS "No HDF5 library directory specified")
	ElSE()
		SET(HDF5_LIBRARY_DIR "${HDF5_LIBRARY_DIR}" CACHE FILEPATH "HDF5 library files")
	ENDIF()

    if (HDF5_LIBRARY_DIR)
    	# result of the HDF5 ctest package
    	
        if (WIN32)
        	set(zlib_post lib)
        	set(lib_ext lib)
        else()
        	set(lib_ext a)
        endif()

	if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
		set(debug_postfix "_debug")
	endif() 
        
        SET(HDF5_LIBRARIES 
            "${HDF5_LIBRARY_DIR}/libhdf5_cpp${debug_postfix}.${lib_ext}"
            "${HDF5_LIBRARY_DIR}/libhdf5${debug_postfix}.${lib_ext}"
            "${HDF5_LIBRARY_DIR}/libz${zlib_post}${debug_postfix}.${lib_ext}"
            "${HDF5_LIBRARY_DIR}/libsz${debug_postfix}.${lib_ext}"
            "${HDF5_LIBRARY_DIR}/libaec${debug_postfix}.${lib_ext}"
        )
    endif()
    
    if (NOT HDF5_LIBRARIES)
    	# debian default
    	
        SET(HDF5_LIBRARIES
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_cpp.so
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5.so
            /usr/lib/x86_64-linux-gnu/libsz.so
            /usr/lib/x86_64-linux-gnu/libaec.so
            z dl
        )
    endif()
    
    add_definitions(-DWITH_HDF5)
	set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_HDF5)
endif()

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
	# warning due to virtual inheritance
	ADD_DEFINITIONS(-wd4250)
	# warning due to select definitions in the schema being redundant
	ADD_DEFINITIONS(-wd4584)
	
	# didn't work well on ifcopenbot, @todo make configurable
	# add_definitions(/MP)

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
    # Enforce standards-conformance on VS > 2015, older Boost versions fail to compile with this
    if (MSVC_VERSION GREATER 1900 AND (Boost_MAJOR_VERSION GREATER 1 OR Boost_MINOR_VERSION GREATER 66))
        add_definitions(-permissive-)
    endif()
	# Link against the static VC runtime
    # TODO Make this configurable
	# IF("$ENV{CONDA_BUILD}" STREQUAL "")
	# FOREACH(flag CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE CMAKE_CXX_FLAGS_MINSIZEREL
			# CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
			# CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
		# IF(${flag} MATCHES "/MD")
			# STRING(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")
		# ENDIF()
		# IF(${flag} MATCHES "/MDd")
			# STRING(REGEX REPLACE "/MDd" "/MTd" ${flag} "${${flag}}")
		# ENDIF()
	# ENDFOREACH()
	# ENDIF()
ElSE()
    add_definitions(-Wall -Wextra)
    if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        add_definitions(-Wno-tautological-constant-out-of-range-compare)
    else()
        add_definitions(-Wno-maybe-uninitialized)
    endif()
    if (CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND (CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 9.0 OR CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL 9.0))
        # OpenCascade spews a lot of deprecated-copy warnings
        add_definitions(-Wno-deprecated-copy)
    endif()
    # -fPIC is not relevant on Windows and creates pointless warnings
    if (UNIX)
        add_definitions(-fPIC)
    endif()
ENDIF()

INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS}
	${Boost_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR} ${JSON_INCLUDE_DIR} ${HDF5_INCLUDE_DIR}
)

function(files_for_ifc_version IFC_VERSION RESULT_NAME)
    set(IFC_PARSE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src/ifcparse)
    set(${RESULT_NAME}
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}enum.h
        ${IFC_PARSE_DIR}/Ifc${IFC_VERSION}.cpp
		PARENT_SCOPE
    )
endfunction()

if(NOT SCHEMA_VERSIONS)
    set(SCHEMA_VERSIONS "2x3" "4" "4x1" "4x2" "4x3_rc1" "4x3_rc2" "4x3_rc3" "4x3_rc4")
endif()

foreach(s ${SCHEMA_VERSIONS})
	add_definitions(-DHAS_SCHEMA_${s})
endforeach()

if(COMPILE_SCHEMA)
	# @todo, this appears to be untested at the moment

    find_package(PythonInterp)

    IF(NOT PYTHONINTERP_FOUND)
        MESSAGE(FATAL_ERROR "A Python interpreter is necessary when COMPILE_SCHEMA is enabled. Disable COMPILE_SCHEMA or fix Python paths to proceed.")
    ENDIF()

    set(IFC_RELEASE_NOT_USED ${SCHEMA_VERSIONS})

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
	foreach(s ${SCHEMA_VERSIONS})
		if("${COMPILED_SCHEMA_NAME}" STREQUAL "${s}")
			list(REMOVE_ITEM IFC_RELEASE_NOT_USED "${s}")
		endif()
	endforeach()
endif()

# Boost >= 1.58 requires BOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE to build on some Linux distros.
if(NOT Boost_VERSION LESS 105800)
    add_definitions(-DBOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE)
endif()

set(IFCOPENSHELL_LIBRARIES IfcParse)
if (BUILD_IFCGEOM)
	foreach(s ${SCHEMA_VERSIONS})
		set(IFCGEOM_SCHEMA_LIBRARIES ${IFCGEOM_SCHEMA_LIBRARIES} IfcGeom_ifc${s})
	endforeach()
	set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES})
endif()
if (BUILD_CONVERT)
	foreach(s ${SCHEMA_VERSIONS})
		set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} Serializers_ifc${s})
	endforeach()
	set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} Serializers ${SERIALIZER_SCHEMA_LIBRARIES})
endif()

# IfcParse
file(GLOB IFCPARSE_H_FILES_ALL ../src/ifcparse/*.h)
file(GLOB IFCPARSE_CPP_FILES_ALL ../src/ifcparse/*.cpp)

foreach(s ${IFCPARSE_H_FILES_ALL})
get_filename_component(p "${s}" NAME)
if (NOT "${p}" MATCHES "[0-9]")
list(APPEND IFCPARSE_H_FILES "${s}")
endif()
endforeach()

foreach(s ${IFCPARSE_CPP_FILES_ALL})
get_filename_component(p "${s}" NAME)
if (NOT "${p}" MATCHES "[0-9]")
list(APPEND IFCPARSE_CPP_FILES "${s}")
endif()
endforeach()

foreach(s ${SCHEMA_VERSIONS})
	list(APPEND IFCPARSE_H_FILES
		../src/ifcparse/Ifc${s}.h
		../src/ifcparse/Ifc${s}-definitions.h
	)
	list(APPEND IFCPARSE_CPP_FILES
		../src/ifcparse/Ifc${s}.cpp
		../src/ifcparse/Ifc${s}-schema.cpp
	)
endforeach()


set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
set_target_properties(IfcParse PROPERTIES COMPILE_FLAGS -DIFC_PARSE_EXPORTS VERSION "0.6.0" SOVERSION "0.6")

TARGET_LINK_LIBRARIES(IfcParse ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES} ${LIBXML2_LIBRARIES})

if (BUILD_IFCGEOM)

# IfcGeom
file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/*.h ../src/ifcgeom/*.i)
file(GLOB IFCGEOM_CPP_FILES ../src/ifcgeom/*.cpp)
set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

foreach(s ${SCHEMA_VERSIONS})
	add_library(IfcGeom_ifc${s} STATIC ${IFCGEOM_FILES})
	set_target_properties(IfcGeom_ifc${s} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${s}")
	TARGET_LINK_LIBRARIES(IfcGeom_ifc${s} IfcParse ${OPENCASCADE_LIBRARIES})
endforeach()

# IfcGeom (schema agnostic)
file(GLOB SCHEMA_AGNOSTIC_H_FILES ../src/ifcgeom_schema_agnostic/*.h)
file(GLOB SCHEMA_AGNOSTIC_CPP_FILES ../src/ifcgeom_schema_agnostic/*.cpp)
set(SCHEMA_AGNOSTIC_FILES ${SCHEMA_AGNOSTIC_H_FILES} ${SCHEMA_AGNOSTIC_CPP_FILES})

add_library(IfcGeom ${SCHEMA_AGNOSTIC_FILES})
set_target_properties(IfcGeom PROPERTIES COMPILE_FLAGS -DIFC_GEOM_EXPORTS VERSION "0.6.0" SOVERSION "0.6")

if (UNIX)
find_package(Threads)
endif()

TARGET_LINK_LIBRARIES(IfcGeom IfcParse ${IFCGEOM_SCHEMA_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})

endif(BUILD_IFCGEOM)

if (BUILD_CONVERT)

# Serializers
file(GLOB SERIALIZERS_H_FILES ../src/serializers/*.h)
file(GLOB SERIALIZERS_CPP_FILES ../src/serializers/*.cpp)
set(SERIALIZERS_FILES ${SERIALIZERS_H_FILES} ${SERIALIZERS_CPP_FILES})
file(GLOB SERIALIZERS_S_H_FILES ../src/serializers/schema_dependent/*.h)
file(GLOB SERIALIZERS_S_CPP_FILES ../src/serializers/schema_dependent/*.cpp)
set(SERIALIZERS_S_FILES ${SERIALIZERS_S_H_FILES} ${SERIALIZERS_S_CPP_FILES})

foreach(s ${SCHEMA_VERSIONS})
	add_library(Serializers_ifc${s} STATIC ${SERIALIZERS_S_FILES})
	set_target_properties(Serializers_ifc${s} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${s} ${CONVERT_PRECISION}")
	TARGET_LINK_LIBRARIES(Serializers_ifc${s} IfcGeom ${OPENCASCADE_LIBRARIES} ${HDF5_LIBRARIES})
endforeach()

add_library(Serializers ${SERIALIZERS_FILES})
set_target_properties(Serializers PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS ${CONVERT_PRECISION}" VERSION "0.6.0" SOVERSION "0.6")

TARGET_LINK_LIBRARIES(Serializers ${SERIALIZER_SCHEMA_LIBRARIES} ${OPENCOLLADA_LIBRARIES})

# IfcConvert
file(GLOB IFCCONVERT_CPP_FILES ../src/ifcconvert/*.cpp)
file(GLOB IFCCONVERT_H_FILES ../src/ifcconvert/*.h)
set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
ADD_EXECUTABLE(IfcConvert ${IFCCONVERT_FILES})
set_target_properties(IfcConvert PROPERTIES COMPILE_FLAGS "${CONVERT_PRECISION}")

TARGET_LINK_LIBRARIES(IfcConvert ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES})

if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    # Only set RPATHs when building shared libraries (i.e. IfcParse and
    # IfcGeom are dynamically linked). Not necessarily a perfect solution
    # but probably a good indication of whether RPATHs are necessary.
    SET_INSTALL_RPATHS(IfcConvert "${IFCOPENSHELL_LIBRARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS};${OPENCOLLADA_LIBRARY_DIR}")
endif()

INSTALL(TARGETS IfcConvert
    ARCHIVE DESTINATION ${LIBDIR}
    LIBRARY DESTINATION ${LIBDIR}
    RUNTIME DESTINATION ${BINDIR}
)

endif(BUILD_CONVERT)

# IfcGeomServer
if(BUILD_GEOMSERVER)

file(GLOB CPP_FILES ../src/ifcgeomserver/*.cpp)
file(GLOB H_FILES ../src/ifcgeomserver/*.h)
set(SOURCE_FILES ${CPP_FILES} ${H_FILES})
ADD_EXECUTABLE(IfcGeomServer ${SOURCE_FILES})
TARGET_LINK_LIBRARIES(IfcGeomServer ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES})

if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    SET_INSTALL_RPATHS(IfcGeomServer "${IFCOPENSHELL_LIBRARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS}")
endif()

INSTALL(TARGETS IfcGeomServer
    ARCHIVE DESTINATION ${LIBDIR}
    LIBRARY DESTINATION ${LIBDIR}
    RUNTIME DESTINATION ${BINDIR}
)

endif()

if (ADD_COMMIT_SHA)
find_package (Git)
if (GIT_FOUND)
	message("git found: ${GIT_EXECUTABLE} with version ${GIT_VERSION_STRING}")
	execute_process(
		COMMAND ${GIT_EXECUTABLE} branch --contains HEAD
		OUTPUT_VARIABLE git_branches
		OUTPUT_STRIP_TRAILING_WHITESPACE
	)
	string(REPLACE "\n" ";" git_branch_list "${git_branches}")
	foreach(git_branch_candidate IN ITEMS ${git_branch_list})
		string(STRIP "${git_branch_candidate}" git_branch_candidate_2)
		if (NOT git_branch_candidate_2 MATCHES "^HEAD$")
			set(git_branch ${git_branch_candidate_2})
		endif()
	endforeach()
	execute_process(
		COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
		OUTPUT_VARIABLE git_sha
		OUTPUT_STRIP_TRAILING_WHITESPACE
	)
	message(STATUS "IfcOpenShell branch: \"${git_branch}\"")
	message(STATUS "IfcOpenShell commit: \"${git_sha}\"")
	add_definitions(-DIFCOPENSHELL_BRANCH=${git_branch})
	add_definitions(-DIFCOPENSHELL_COMMIT=${git_sha})
endif()
endif()

# Documentation
IF(BUILD_DOCUMENTATION)
	set(CMAKE_MODULE_PATH "../docs/cmake")
	ADD_SUBDIRECTORY(../docs docs)
ENDIF()

IF(BUILD_IFCPYTHON)
	ADD_SUBDIRECTORY(../src/ifcwrap ifcwrap)
ENDIF()

IF(BUILD_EXAMPLES)
	ADD_SUBDIRECTORY(../src/examples examples)
ENDIF()

IF(BUILD_IFCMAX)
	ADD_SUBDIRECTORY(../src/ifcmax ifcmax)
ENDIF()

ADD_SUBDIRECTORY(../src/svgfill svgfill)

# CMake installation targets
INSTALL(FILES ${IFCPARSE_H_FILES}
	DESTINATION ${INCLUDEDIR}/ifcparse
)

INSTALL(TARGETS IfcParse
	ARCHIVE DESTINATION ${LIBDIR}
	LIBRARY DESTINATION ${LIBDIR}
	RUNTIME DESTINATION ${BINDIR}
)

if(BUILD_IFCGEOM)
INSTALL(FILES ${IFCGEOM_H_FILES}
	DESTINATION ${INCLUDEDIR}/ifcgeom
)

INSTALL(FILES  ${SCHEMA_AGNOSTIC_H_FILES}
	DESTINATION ${INCLUDEDIR}/ifcgeom_schema_agnostic
)

INSTALL(TARGETS ${IFCGEOM_SCHEMA_LIBRARIES} IfcGeom
	ARCHIVE DESTINATION ${LIBDIR}
	LIBRARY DESTINATION ${LIBDIR}
	RUNTIME DESTINATION ${BINDIR}
)
endif()

if(BUILD_CONVERT)
INSTALL(TARGETS Serializers ${SERIALIZER_SCHEMA_LIBRARIES}
	ARCHIVE DESTINATION ${LIBDIR}
	LIBRARY DESTINATION ${LIBDIR}
	RUNTIME DESTINATION ${BINDIR}
)

INSTALL(FILES  ${SERIALIZERS_FILES}
	DESTINATION ${INCLUDEDIR}/serializers/
)

INSTALL(FILES  ${SERIALIZERS_S_FILES}
	DESTINATION ${INCLUDEDIR}/serializers/schema_dependent
)
endif()


list(APPEND CPACK_SOURCE_IGNORE_FILES
  .git
  .gitignore
  )

set(CPACK_PACKAGE_NAME "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}${EXTRA_VERSION}")
SET(CPACK_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}-${CMAKE_SYSTEM_NAME}")
set(CPACK_PACKAGE_DIRECTORY "${PROJECT_BINARY_DIR}/assets")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "IfcOpenShell")
set(CPACK_PACKAGE_DESCRIPTION "IfcOpenShell.")
set(CPACK_PACKAGE_VENDOR "Cemosis")
set(CPACK_PACKAGE_CONTACT "Christophe Prud'homme <christophe.prudhomme@cemosis.fr>")
set(CPACK_PACKAGE_VERSION_MAJOR "${PROJECT_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${PROJECT_VERSION_MINOR}")
set(CPACK_PACKAGE_VERSION_PATCH "${PROJECT_VERSION_PATCH}")


set(CPACK_GENERATOR "TGZ;DEB")
set(CPACK_SOURCE_GENERATOR "TGZ")

FOREACH(COMPONENT IN ITEMS ${BOOST_COMPONENTS})
    string(REPLACE "_" "-" COMP ${COMPONENT})
    set(BOOST_DEPS "${BOOST_DEPS}, libboost-${COMP}1.67.0")
endforeach(COMPONENT)

set(CPACK_DEBIAN_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3, libxml2, liboce-foundation11, liboce-modeling11, liboce-ocaf11, liboce-visualization11, liboce-ocaf-lite11, libpython3.8 ${BOOST_DEPS}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "${CPACK_PACKAGE_DESCRIPTION_SUMMARY}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION "${CPACK_PACKAGE_DESCRIPTION}")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_SECTION "science")
set(CPACK_DEBIAN_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}${EXTRA_VERSION}")
set(CPACK_DEBIAN_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
#set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_SOURCE_DIR}/cmake/debian/postinst")

include(CPack)
