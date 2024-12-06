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
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON) # not necessary, but encouraged
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
endif()

add_definitions(-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)

cmake_policy(SET CMP0048 NEW)
cmake_policy(SET CMP0074 NEW)
cmake_policy(SET CMP0078 NEW)
cmake_policy(SET CMP0086 NEW)
if (POLICY CMP0144)
    cmake_policy(SET CMP0144 NEW) # find_package() uses upper-case <PACKAGENAME>_ROOT variables.
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# Include utility macros and functions
include(utilities.cmake)

# use extra version to make pre-release using eg semver
if(NOT DEFINED EXTRA_VERSION)
    set(EXTRA_VERSION "-alpha.3")
endif()

option(MINIMAL_BUILD "The build is to make a minimal version of IFC converter from OCCT into IFC." OFF)
option(WASM_BUILD "Build a WebAssembly binary." OFF)

option(ENABLE_BUILD_OPTIMIZATIONS "Enable certain compiler and linker optimizations on RelWithDebInfo and Release builds." OFF)
option(BUILD_SHARED_LIBS "Build IfcParse and IfcGeom as shared libs (SO/DLL)." OFF)
option(MSVC_PARALLEL_BUILD "Multi-threaded compilation in Microsoft Visual Studio (/MP)" OFF)
option(USE_VLD "Use Visual Leak Detector for debugging memory leaks, MSVC-only." OFF)
option(USE_MMAP "Adds a command line options to parse IFC files from memory mapped files using Boost.Iostreams" OFF)
option(NO_WARN "Disable all warnings" OFF)

option(BUILD_IFCGEOM "Build IfcGeom." ON)
option(BUILD_IFCPYTHON "Build IfcPython." ON)
option(BUILD_CONVERT "Build IfcConvert executable." ON)
option(BUILD_DOCUMENTATION "Build IfcOpenShell Documentation." OFF)
option(BUILD_EXAMPLES "Build example applications." ON)
option(BUILD_GEOMSERVER "Build IfcGeomServer executable." ON)
option(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
option(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer" OFF) # QtViewer requires Qt6
option(BUILD_PACKAGE "" OFF)

option(WITH_OPENCASCADE "Enable geometry interpretation using Open CASCADE" ON)
option(WITH_CGAL "Enable geometry interpretation using CGAL" ON)
option(COLLADA_SUPPORT "Build IfcConvert with COLLADA support (requires OpenCOLLADA)." ON)
option(GLTF_SUPPORT "Build IfcConvert with glTF support (requires json.hpp)." OFF)
option(HDF5_SUPPORT "Enable HDF5 support (requires HDF5, zlib)" ON)
option(WITH_PROJ "Enable output of Earth-Centered Earth-Fixed glTF output using the PROJ library" OFF)
option(IFCXML_SUPPORT "Build IfcParse with ifcXML support (requires libxml2)." ON)
option(USD_SUPPORT "Build IfcConvert with USD support (requires pixar's USD library)." OFF)
option(CITYJSON_SUPPORT "Build IfcConvert with CityJSON support (requires CityJSON library)." ON)
option(WITH_RELATIONSHIP_VALIDATION "Build IfcConvert with option to validate geometrical relationships." OFF)

option(USERSPACE_PYTHON_PREFIX "Installs IfcPython for the current user only instead of system-wide." OFF)
option(ADD_COMMIT_SHA "Add commit sha and branch in version number, warning results in many rebuilds, requires git" OFF)
option(VERSION_OVERRIDE "Override the version defined in IfcParse.h with the file VERSION in the repository root" OFF)

if (VERSION_OVERRIDE)
    file(READ "../VERSION" "RELEASE_VERSION_")
    string(STRIP "${RELEASE_VERSION_}" RELEASE_VERSION)
    message(STATUS "Detected version '${RELEASE_VERSION}'")
else()
    set(RELEASE_VERSION "0.8.0")
endif()

project(IfcOpenShell VERSION ${RELEASE_VERSION})

if(MINIMAL_BUILD)
    message(STATUS "Setting options for minimal build")
    set(BUILD_GEOMSERVER OFF)
    set(BUILD_IFCPYTHON OFF)
    set(WITH_CGAL OFF)
    set(COLLADA_SUPPORT OFF)
    set(GLTF_SUPPORT OFF)
    set(HDF5_SUPPORT OFF)
    set(IFCXML_SUPPORT OFF)
    set(USD_SUPPORT OFF)
endif()

if((BUILD_CONVERT OR BUILD_GEOMSERVER OR BUILD_IFCPYTHON) AND(NOT BUILD_IFCGEOM))
    message(STATUS "'IfcGeom' is required with current outputs")
    set(BUILD_IFCGEOM ON)
endif()

if(MSVC AND MSVC_PARALLEL_BUILD)
    add_definitions("/MP")
endif()

if(NO_WARN)
    if(MSVC)
        add_compile_options("/w")
    else()
        add_compile_options("-w")
    endif()
endif()

include(GNUInstallDirs)

# Specify paths to install files
if(NOT BINDIR)
    set(BINDIR bin)
endif()
if(NOT IS_ABSOLUTE ${BINDIR})
    set(BINDIR ${CMAKE_INSTALL_BINDIR})
endif()
message(STATUS "BINDIR: ${BINDIR}")

if(NOT IS_ABSOLUTE ${INCLUDEDIR})
    set(INCLUDEDIR ${CMAKE_INSTALL_INCLUDEDIR}/ifcopenshell)
endif()
message(STATUS "INCLUDEDIR: ${INCLUDEDIR}")

if(NOT LIBDIR)
    set(LIBDIR lib)
endif()
if(NOT IS_ABSOLUTE ${LIBDIR})
    set(LIBDIR ${CMAKE_INSTALL_LIBDIR})
endif()
message(STATUS "LIBDIR: ${LIBDIR}")

set(IFCOPENSHELL_LIBRARY_DIR "") # for *nix rpaths

if(BUILD_SHARED_LIBS)
    add_definitions(-DIFC_SHARED_BUILD)
    if(MSVC)
        message(WARNING "Building DLLs against the static VC run-time. This is not recommended if the DLLs are to be redistributed.")
        # C4521: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
        # There will be couple hundreds of these so suppress them away, https://msdn.microsoft.com/en-us/library/esew7y1w.aspx
        add_definitions(-wd4251)
    endif()

    set(IFCOPENSHELL_LIBRARY_DIR "${LIBDIR}")
endif()

UNIFY_ENVVARS_AND_CACHE(OCC_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OCC_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(BOOST_ROOT)
UNIFY_ENVVARS_AND_CACHE(BOOST_LIBRARYDIR)
UNIFY_ENVVARS_AND_CACHE(EIGEN_DIR)

if(NOT MINIMAL_BUILD)
    UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_LIBRARY_DIR)
    UNIFY_ENVVARS_AND_CACHE(LIBXML2_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(LIBXML2_LIBRARIES)
    UNIFY_ENVVARS_AND_CACHE(PCRE_LIBRARY_DIR)
    UNIFY_ENVVARS_AND_CACHE(PYTHON_EXECUTABLE)
    UNIFY_ENVVARS_AND_CACHE(HDF5_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARY_DIR)
    UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARIES)
    UNIFY_ENVVARS_AND_CACHE(CGAL_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(CGAL_LIBRARY_DIR)
    UNIFY_ENVVARS_AND_CACHE(GMP_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(GMP_LIBRARY_DIR)
    UNIFY_ENVVARS_AND_CACHE(MPFR_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(MPFR_LIBRARY_DIR)
endif()

# Get a list of all OPTION flags from the CMakeLists.txt
get_all_option_flags(option_flags)

# Loop through the list of OPTION flags and convert the corresponding environment variables
foreach(option_flag IN LISTS option_flags)
    convert_env_var_to_bool("${option_flag}")
endforeach()

if(WASM_BUILD)
    # when using the nix/build-all.py build script we should not
    # look into the sysroot for most of the dependencies but rather
    # in the designated build/ folder created by the script.
    set(CMAKE_FIND_ROOT_PATH_BACKUP "${CMAKE_FIND_ROOT_PATH}")
    set(CMAKE_FIND_ROOT_PATH "")
endif()

if(WITH_CGAL)
    add_definitions(-DIFOPSH_WITH_CGAL)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_CGAL)

    if(CITYJSON_SUPPORT)
		add_definitions(-DIFOPSH_WITH_CITYJSON)
    endif()

    list(APPEND GEOMETRY_KERNELS cgal)
endif()

if(WITH_OPENCASCADE)
    add_definitions(-DIFOPSH_WITH_OPENCASCADE)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_OPENCASCADE)
    list(APPEND GEOMETRY_KERNELS opencascade)
endif()

if(GLTF_SUPPORT OR CITYJSON_SUPPORT)
    UNIFY_ENVVARS_AND_CACHE(JSON_INCLUDE_DIR)
    find_path(json_header_path "nlohmann/json.hpp" HINTS ${JSON_INCLUDE_DIR})
    set(JSON_INCLUDE_DIR ${json_header_path})

    if(json_header_path)
        message(STATUS "JSON for Modern C++ header file found in ${JSON_INCLUDE_DIR}")
    else()
        message(FATAL_ERROR "Unable to find JSON for Modern C++ header file, aborting")
    endif()

    add_definitions(-DWITH_GLTF)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_GLTF)
endif()

# Add USD support to serializers 
if(USD_SUPPORT)
    UNIFY_ENVVARS_AND_CACHE(USD_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(USD_LIBRARY_DIR)

    if("${USD_INCLUDE_DIR}" STREQUAL "")
        find_path(USD_INCLUDE_DIR pxr.h
            PATHS
                /usr/include/pxr
                /usr/local/include/pxr
            REQUIRED
        )
        if(USD_INCLUDE_DIR)
            message(STATUS "Found USD include files in: ${USD_INCLUDE_DIR}")
        else()
            message(FATAL_ERROR "Unable to find USD include directory, specify USD_INCLUDE_DIR manually.")
        endif()
    else()
        set(USD_INCLUDE_DIR ${USD_INCLUDE_DIR} CACHE FILEPATH "USD header files")
        message(STATUS "Looking for USD include files in: ${USD_INCLUDE_DIR}")
    endif()

    set(USD_LIBRARIES
            usd_usd 
            usd_usdGeom
            usd_usdShade 
            usd_usdLux 
            usd_vt 
            usd_sdf 
            usd_tf 
            usd_gf
        )

    find_library(USD_LIBRARY
        NAMES ${USD_LIBRARIES}
        PATHS ${USD_LIBRARY_DIR})
    if(USD_LIBRARY)
        message(STATUS "USD libraries ${USD_LIBRARIES} found in: ${USD_LIBRARY_DIR}")
        link_directories(${USD_LIBRARY_DIR})
    else()
        message(FATAL_ERROR "Unable to find USD libraries in: ${USD_LIBRARY_DIR}")
    endif()

    add_definitions(-DWITH_USD)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_USD)
endif(USD_SUPPORT)

# Find Boost: On win32 the (hardcoded) default is to use static libraries and
# runtime, when doing running conda-build we pick what conda prepared for us.
if(WIN32 AND("$ENV{CONDA_BUILD}" STREQUAL ""))
    set(Boost_USE_STATIC_LIBS ON)
    set(Boost_USE_STATIC_RUNTIME OFF)
    set(Boost_USE_MULTITHREADED ON)

    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and wrong libraries would be asked for when code is
    # compiled with a toolset different from default.
    if(MSVC)
        add_definitions(-DBOOST_ALL_NO_LIB)

        # Necessary for boost version >= 1.67
        set(BCRYPT_LIBRARIES "bcrypt.lib")
    endif()
else()
    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and it's going to conflict if there are multiple, as is
    # the case in conda-forge's libboost feedstock.
    add_definitions(-DBOOST_ALL_NO_LIB)

    if(WIN32)
        # Necessary for boost version >= 1.67
        set(BCRYPT_LIBRARIES "bcrypt.lib")
    endif()
endif()

if(WASM_BUILD)
    set(BOOST_COMPONENTS)
else()
    # @todo review this, shouldn't this be all possible header-only now?
    # ... or rewritten using C++17 features?
    set(BOOST_COMPONENTS system program_options regex thread date_time)
endif()

if(USE_MMAP)
    if(MSVC)
        # filesystem is necessary for the utf-16 wpath
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams filesystem)
    else()
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams)
    endif()

    add_definitions(-DUSE_MMAP)
endif()

find_package(Boost REQUIRED COMPONENTS ${BOOST_COMPONENTS})
message(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
message(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

if(NOT MINIMAL_BUILD)
    # libxml2 is required for IFCXML (optional) and SVGFILL (mandatory)
    find_package(LibXml2 REQUIRED)
endif()

if(IFCXML_SUPPORT)
    add_definitions(-DWITH_IFCXML)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_IFCXML)
endif()

if(BUILD_IFCGEOM)
    if(MSVC)
        add_debug_variants(LIBXML2_LIBRARIES "${LIBXML2_LIBRARIES}" d)
    endif()

    # Open CASCADE
    if(WITH_OPENCASCADE)
    if("${OCC_INCLUDE_DIR}" STREQUAL "")
        find_path(OCC_INCLUDE_DIR Standard_Version.hxx
            PATHS
                /usr/include/occt
                /usr/include/oce
                /usr/include/opencascade
            REQUIRED
        )

        if(OCC_INCLUDE_DIR)
            message(STATUS "Found Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
        else()
            message(FATAL_ERROR "Unable to find Open CASCADE include directory, specify OCC_INCLUDE_DIR manually.")
        endif()
    else()
        set(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
        message(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
    endif()

    if(OCC_INCLUDE_DIR)
        file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAJOR
            REGEX "#define OCC_VERSION_MAJOR.*"
        )
        string(REGEX MATCH "[0-9]+" OCC_MAJOR ${OCC_MAJOR})
        file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MINOR
          REGEX "#define OCC_VERSION_MINOR.*"
        )
        string(REGEX MATCH "[0-9]+" OCC_MINOR ${OCC_MINOR})
        file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAINT
          REGEX "#define OCC_VERSION_MAINTENANCE.*"
        )
        string(REGEX MATCH "[0-9]+" OCC_MAINT ${OCC_MAINT})
        set(OCC_VERSION_STRING "${OCC_MAJOR}.${OCC_MINOR}.${OCC_MAINT}")
    endif(OCC_INCLUDE_DIR)

    set(OPENCASCADE_LIBRARY_NAMES
        TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
        TKFillet TKXSBase TKOffset TKHLR

        # @todo investigate the exact conditions when this is necessary
        TKBin
    )

    if(OCC_VERSION_STRING VERSION_LESS 7.8.0)
        list(APPEND OPENCASCADE_LIBRARY_NAMES  TKIGES TKSTEPBase TKSTEPAttr TKSTEP209 TKSTEP)
    else(OCC_VERSION_STRING VERSION_LESS 7.8.0)
        list(APPEND OPENCASCADE_LIBRARY_NAMES TKDESTEP TKDEIGES)
    endif(OCC_VERSION_STRING VERSION_LESS 7.8.0)

    if("${OCC_LIBRARY_DIR}" STREQUAL "")
        find_library(OCC_LIBRARY TKernel
            PATHS
                /usr/lib
            REQUIRED
        )

        if(OCC_LIBRARY)
            GET_FILENAME_COMPONENT(OCC_LIBRARY_DIR ${OCC_LIBRARY} PATH)
            message(STATUS "Found Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
        else()
            message(FATAL_ERROR "Unable find Open CASCADE library directory, specify OCC_LIBRARY_DIR manually.")
        endif()
    else()
        set(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
        message(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
    endif()

    find_library(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} NO_DEFAULT_PATH)

    if(libTKernel)
        message(STATUS "Required Open Cascade Library files found")
    else()
        message(FATAL_ERROR "Unable to find Open Cascade library files, aborting")
    endif()

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

    if(WIN32)
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
        
        if(WASM_BUILD)
            set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
        else()
            # OPENCASCADE_LIBRARIES repeated N times below in order to fix cyclic dependencies
            # tfk: --start-group ... --end-group didn't work on the apple linker when last tested
            if(APPLE)
                set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
            else()
                set(OPENCASCADE_LIBRARIES -Wl,--start-group ${OPENCASCADE_LIBRARIES} -Wl,--end-group ${CMAKE_THREAD_LIBS_INIT})
            endif()
        endif()
        
        if(NOT APPLE AND NOT WIN32)
            set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "rt")
        endif()
        if(NOT WIN32)
            set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "dl")
        endif()
    endif()
    endif(WITH_OPENCASCADE)
endif(BUILD_IFCGEOM)

if(COLLADA_SUPPORT)
    # Find OpenCOLLADA
    if("${OPENCOLLADA_INCLUDE_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA include directory specified")
        set(OPENCOLLADA_INCLUDE_DIR "/usr/include/opencollada" CACHE FILEPATH "OpenCOLLADA header files")
    else()
        set(OPENCOLLADA_INCLUDE_DIR "${OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
    endif()

    if("${OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA library directory specified")
        find_library(OPENCOLLADA_FRAMEWORK_LIB NAMES OpenCOLLADAFramework
            PATHS /usr/lib64/opencollada /usr/lib/opencollada /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib)
        get_filename_component(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_FRAMEWORK_LIB} PATH)
    endif()

    find_library(OpenCOLLADAFramework NAMES OpenCOLLADAFramework OpenCOLLADAFrameworkd PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)

    if(OpenCOLLADAFramework)
        message(STATUS "OpenCOLLADA library files found")
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA libraries. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()

    set(OPENCOLLADA_LIBRARY_DIR "${OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")

    set(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

    find_file(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})

    if(COLLADASWStreamWriter_h)
        message(STATUS "OpenCOLLADA header files found")
        add_definitions(-DWITH_OPENCOLLADA)
        set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_OPENCOLLADA)

        set(OPENCOLLADA_LIBRARY_NAMES
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

            get_filename_component(PCRE_LIBRARY_DIR ${pcre_library} PATH)
        else()
            find_library(pcre_library NAMES pcre pcred PATHS ${PCRE_LIBRARY_DIR} NO_DEFAULT_PATH)
        endif()

        if(pcre_library)
            set(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_LIBRARY_DIR} ${PCRE_LIBRARY_DIR})

            if(MSVC)
                # Add release lib regardless whether release or debug found. Debug version will be appended below.
                list(APPEND OPENCOLLADA_LIBRARIES "${PCRE_LIBRARY_DIR}/pcre.lib")
            else()
                list(APPEND OPENCOLLADA_LIBRARIES "${pcre_library}")
            endif()
        else()
            message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find PCRE. "
                "Disable COLLADA_SUPPORT or fix PCRE_LIBRARY_DIR path to proceed.")
        endif()

        if(MSVC)
            add_debug_variants(OPENCOLLADA_LIBRARIES "${OPENCOLLADA_LIBRARIES}" d)
        endif()
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA headers. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()
endif(COLLADA_SUPPORT)

if(HDF5_SUPPORT)
    if("${HDF5_INCLUDE_DIR}" STREQUAL "")
        message(STATUS "No HDF5 include directory specified")
    else()
        set(HDF5_INCLUDE_DIR "${HDF5_INCLUDE_DIR}" CACHE FILEPATH "HDF5 header files")
    endif()

    if("${HDF5_LIBRARY_DIR}" STREQUAL "")
        message(STATUS "No HDF5 library directory specified")
    else()
        set(HDF5_LIBRARY_DIR "${HDF5_LIBRARY_DIR}" CACHE FILEPATH "HDF5 library files")
    endif()

    if(HDF5_LIBRARY_DIR)
        # result of the HDF5 ctest package
        # Find zlib using cmake find_library. How should this be implemented?
        # FIND_LIBRARY(NAMES z libz libz_debug PATHS ... NO_DEFAULT_PATH)
        if("$ENV{CONDA_BUILD}" STREQUAL "")
            # result of the HDF5 ctest package
            if(WIN32)
                set(zlib_post lib)
                set(lib_ext lib)
            else()
                set(lib_ext a)
            endif()

            if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
                set(debug_postfix "_debug")
            endif()

            set(HDF5_LIBRARIES
                "${HDF5_LIBRARY_DIR}/libhdf5_cpp${debug_postfix}.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libhdf5${debug_postfix}.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libz${zlib_post}${debug_postfix}.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libsz${debug_postfix}.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libaec${debug_postfix}.${lib_ext}"
            )

        else()
            message(STATUS "Packaging hdf5 and zlib for conda distribution")

            if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
                # macOS
                set(zlib_post libz)
                set(lib_ext dylib)
                set(HDF5_LIBRARIES
                "${HDF5_LIBRARY_DIR}/libhdf5_cpp.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libhdf5.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/${zlib_post}.${lib_ext}"
            )
            else()
                # linux and windows
                # Find HDF5 package
                find_package(HDF5 REQUIRED COMPONENTS C CXX)
                # Find ZLIB package
                find_package(ZLIB REQUIRED)
                # Include directories
                include_directories(${HDF5_INCLUDE_DIRS} ${ZLIB_INCLUDE_DIRS})
                # Link libraries
                set(HDF5_LIBRARIES ${HDF5_LIBRARIES} ${ZLIB_LIBRARIES})
                message(STATUS "HDF5 libraries: ${HDF5_LIBRARIES}")
            endif()
        endif()
    endif()

    if(NOT HDF5_LIBRARIES)
        # debian default
        set(HDF5_LIBRARIES
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_cpp.so
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5.so
            /usr/lib/x86_64-linux-gnu/libsz.so
            /usr/lib/x86_64-linux-gnu/libaec.so
            z dl
        )
    endif()

    add_definitions(-DWITH_HDF5)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_HDF5)
endif(HDF5_SUPPORT)

if(WASM_BUILD)
    # reset to use sysroot
    set(CMAKE_FIND_ROOT_PATH "${CMAKE_FIND_ROOT_PATH_BACKUP}")
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
else()
    # @tfk I commented this out as this kind of defeats the purpose of RelWithDebInfo. For the
    # best debugging experience simply use Debug. Note that in MSVC you can selectively toggle
    # optimization on a specific file if you're investigating a specific issue.
    # if(MSVC)
    #     set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} /Od")
    # endif()
endif(ENABLE_BUILD_OPTIMIZATIONS)

if(MSVC)
    # warning due to virtual inheritance
    add_definitions(-wd4250)
    # warning due to select definitions in the schema being redundant
    add_definitions(-wd4584)

    # didn't work well on ifcopenbot, @todo make configurable
    # add_definitions(/MP)

    # Enable solution folders (free VS versions prior to 2012 don't support solution folders)
    if(MSVC_VERSION GREATER 1600)
        set_property(GLOBAL PROPERTY USE_FOLDERS ON)
    endif()

    if(USE_VLD)
        add_definitions(-DUSE_VLD)
    endif()

    # Enforce Unicode for CRT and Win32 API calls
    add_definitions(-D_UNICODE -DUNICODE)

    # Disable warnings about unsafe C functions; we could use the safe C99 & C11 versions if we have no need for supporting old compilers.
    add_definitions(-D_SCL_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-bigobj) # required for building the big ifcXXX.objs, https://msdn.microsoft.com/en-us/library/ms173499.aspx

    # Bump up the warning level from the default 3 to 4.
    add_definitions(-W4)

    if(MSVC_VERSION GREATER 1800) # > 2013
        # Disable overeager and false positives causing C4458 ("declaration of 'indentifier' hides class member"), at least for now.
        add_definitions(-wd4458)
    endif()

    # Enforce standards-conformance on VS > 2015, older Boost versions fail to compile with this
    if(MSVC_VERSION GREATER 1900 AND(Boost_MAJOR_VERSION GREATER 1 OR Boost_MINOR_VERSION GREATER 66))
        add_definitions(-permissive-)
    endif()

    # Link against the static VC runtime
    # TODO Make this configurable
    # if("$ENV{CONDA_BUILD}" STREQUAL "")
    #     foreach(flag CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE CMAKE_CXX_FLAGS_MINSIZEREL
    #     CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
    #     CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
    #         if(${flag} MATCHES "/MD")
    #             STRING(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")
    #         endif()
    #         if(${flag} MATCHES "/MDd")
    #             STRING(REGEX REPLACE "/MDd" "/MTd" ${flag} "${${flag}}")
    #         endif()
    #     endforeach()
    # endif()

	add_definitions(-D_ENABLE_EXTENDED_ALIGNED_STORAGE)
	# See #5158.
	if(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 19.40)
		add_definitions(-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)
	endif()
else()
    add_definitions(-Wall -Wextra)

    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        add_definitions(-Wno-tautological-constant-out-of-range-compare)
    else()
        add_definitions(-Wno-maybe-uninitialized)
    endif()

    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 9.0 OR CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL 9.0))
        # OpenCascade spews a lot of deprecated-copy warnings
        add_definitions(-Wno-deprecated-copy)
    endif()

    # -fPIC is not relevant on Windows and creates pointless warnings
    if(UNIX)
        add_definitions(-fPIC)
    endif()
endif(MSVC)

include_directories(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS}
	${Boost_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR} ${JSON_INCLUDE_DIR} ${HDF5_INCLUDE_DIR}
    ${EIGEN_DIR} ${CGAL_INCLUDE_DIR} ${GMP_INCLUDE_DIR} ${MPFR_INCLUDE_DIR} ${USD_INCLUDE_DIR}
    ${TBB_INCLUDE_DIR}
)

if(NOT SCHEMA_VERSIONS)
    if(WASM_BUILD)
        # super arbitrarily try to keep size down at least a little bit
        set(SCHEMA_VERSIONS "2x3" "4")
    else()
        set(SCHEMA_VERSIONS "2x3" "4" "4x1" "4x2" "4x3" "4x3_tc1" "4x3_add1" "4x3_add2")
    endif()
endif()

message(STATUS "IFC SCHEMA_VERSIONS that will be used for the build: ${SCHEMA_VERSIONS}.")

foreach(schema ${SCHEMA_VERSIONS})
    add_definitions(-DHAS_SCHEMA_${schema})
endforeach()

string(REPLACE ";" ")(" schema_version_seq "(${SCHEMA_VERSIONS})")
add_definitions(-DSCHEMA_SEQ=${schema_version_seq})

if(COMPILE_SCHEMA)
    # @todo, this appears to be untested at the moment
    find_package(PythonInterp)

    if(NOT PYTHONINTERP_FOUND)
        message(FATAL_ERROR "A Python interpreter is necessary when COMPILE_SCHEMA is enabled. Disable COMPILE_SCHEMA or fix Python paths to proceed.")
    endif()

    set(IFC_RELEASE_NOT_USED ${SCHEMA_VERSIONS})

    # Install pyparsing if necessary
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)

    if("${PYTHON_PACKAGE_LIST}" STREQUAL "")
        execute_process(COMMAND pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)

        if("${PYTHON_PACKAGE_LIST}" STREQUAL "")
            message(WARNING "Failed to find pip. Pip is required to automatically install pyparsing")
        endif()
    endif()

    string(FIND "${PYTHON_PACKAGE_LIST}" pyparsing PYPARSING_FOUND)

    if("${PYPARSING_FOUND}" STREQUAL "-1")
        message(STATUS "Installing pyparsing")
        execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)

        if(NOT "${SUCCESS}" STREQUAL "0")
            execute_process(COMMAND pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)

            if(NOT "${SUCCESS}" STREQUAL "0")
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

    if(NOT "${SUCCESS}" STREQUAL "0")
        message(FATAL_ERROR "Failed to bootstrap parser. Make sure pyparsing is installed")
    endif()

    # Generate code
    execute_process(COMMAND ${PYTHON_EXECUTABLE} ../ifcexpressparser/express_parser.py ../../${COMPILE_SCHEMA}
        WORKING_DIRECTORY ../src/ifcparse
        OUTPUT_VARIABLE COMPILED_SCHEMA_NAME)

    # Prevent the schema that had just been compiled from being excluded
    foreach(schema ${SCHEMA_VERSIONS})
        if("${COMPILED_SCHEMA_NAME}" STREQUAL "${schema}")
            list(REMOVE_ITEM IFC_RELEASE_NOT_USED "${schema}")
        endif()
    endforeach()
endif(COMPILE_SCHEMA)

# Boost >= 1.58 requires BOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE to build on some Linux distros.
if(NOT Boost_VERSION LESS 105800)
    add_definitions(-DBOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE)
endif()

set(IFCOPENSHELL_LIBRARIES IfcParse)

if(BUILD_IFCGEOM)
	foreach(schema ${SCHEMA_VERSIONS})
		set(IFCGEOM_SCHEMA_LIBRARIES ${IFCGEOM_SCHEMA_LIBRARIES} geometry_mapping_ifc${schema})
	endforeach()
	if(WASM_BUILD)
	    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES})
	else()
	    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES})	
	endif()
endif()

if(BUILD_CONVERT OR BUILD_IFCPYTHON)
	foreach(schema ${SCHEMA_VERSIONS})
		set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} Serializers_ifc${schema})
	endforeach()
	set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} Serializers ${SERIALIZER_SCHEMA_LIBRARIES})

    if(WITH_OPENCASCADE)
        foreach(schema ${SCHEMA_VERSIONS})
            set(GEOM_SERIALIZER_SCHEMA_LIBRARIES ${GEOM_SERIALIZER_SCHEMA_LIBRARIES} GeometrySerializers_ifc${schema})

            add_library(geometry_serializer_ifc${schema} STATIC ../src/ifcgeom/Serialization/schema/Serialization.cpp)
            set_target_properties(geometry_serializer_ifc${schema} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}")
            list(APPEND geometry_serializer_libraries geometry_serializer_ifc${schema})
        endforeach()

        add_library(geometry_serializer STATIC ../src/ifcgeom/Serialization/Serialization.cpp)
        target_link_libraries(geometry_serializer ${geometry_serializer_libraries})
        set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} geometry_serializer ${geometry_serializer_libraries})
    endif()
endif()

# IfcParse
file(GLOB IFCPARSE_H_FILES_ALL ../src/ifcparse/*.h)
file(GLOB IFCPARSE_CPP_FILES_ALL ../src/ifcparse/*.cpp)

foreach(file ${IFCPARSE_H_FILES_ALL})
    get_filename_component(filename "${file}" NAME)

    if(NOT "${filename}" MATCHES "[0-9]")
        list(APPEND IFCPARSE_H_FILES "${file}")
    endif()
endforeach()

foreach(file ${IFCPARSE_CPP_FILES_ALL})
    get_filename_component(filename "${file}" NAME)

    if(NOT "${filename}" MATCHES "[0-9]")
        list(APPEND IFCPARSE_CPP_FILES "${file}")
    endif()
endforeach()

foreach(schema ${SCHEMA_VERSIONS})
    list(APPEND IFCPARSE_H_FILES
        ../src/ifcparse/Ifc${schema}.h
        ../src/ifcparse/Ifc${schema}-definitions.h
    )
    list(APPEND IFCPARSE_CPP_FILES
        ../src/ifcparse/Ifc${schema}.cpp
        ../src/ifcparse/Ifc${schema}-schema.cpp
    )
endforeach()

set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
set_target_properties(IfcParse PROPERTIES COMPILE_FLAGS -DIFC_PARSE_EXPORTS VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

if(WASM_BUILD)
    target_link_libraries(IfcParse ${BCRYPT_LIBRARIES} ${LIBXML2_LIBRARIES})
else()
    target_link_libraries(IfcParse ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES} ${LIBXML2_LIBRARIES})
endif()

if(BUILD_IFCGEOM)
    if(WITH_CGAL)
        find_library(libGMP NAMES gmp mpir PATHS ${GMP_LIBRARY_DIR} NO_DEFAULT_PATH)
        find_library(libMPFR NAMES mpfr PATHS ${MPFR_LIBRARY_DIR} NO_DEFAULT_PATH)
        if(NOT libGMP)
            message(FATAL_ERROR "Unable to find GMP library files, aborting")
        endif()
        if(NOT libMPFR)
            message(FATAL_ERROR "Unable to find MPFR library files, aborting")
        endif()

        list(APPEND CGAL_LIBRARIES "${libMPFR}")
        list(APPEND CGAL_LIBRARIES "${libGMP}")
    endif()

    foreach(kernel ${GEOMETRY_KERNELS})
        string(TOUPPER ${kernel} KERNEL_UPPER)
        file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/kernels/${kernel}/*.h)
        file(GLOB IFCGEOM_CPP_FILES ../src/ifcgeom/kernels/${kernel}/*.cpp)
        set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})
        
        add_library(geometry_kernel_${kernel} ${IFCGEOM_FILES})
        set_property(TARGET geometry_kernel_${kernel} APPEND PROPERTY COMPILE_FLAGS "-DIFC_GEOM_EXPORTS")
        # needed?
        # if(NOT WASM_BUILD)
        # endif()
        target_link_libraries(geometry_kernel_${kernel} ${${KERNEL_UPPER}_LIBRARIES})
        list(APPEND kernel_libraries geometry_kernel_${kernel})
        
        if(${kernel} STREQUAL "cgal")
            set_property(TARGET geometry_kernel_${kernel} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

            add_library(geometry_kernel_${kernel}_simple ${IFCGEOM_FILES})
            set_target_properties(geometry_kernel_${kernel}_simple PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS")
            # needed?
            # if(NOT WASM_BUILD)
            # endif()
            target_link_libraries(geometry_kernel_${kernel}_simple ${${KERNEL_UPPER}_LIBRARIES})
            list(APPEND kernel_libraries geometry_kernel_${kernel}_simple)
        endif()
    endforeach()

    # IfcGeom
    foreach(schema ${SCHEMA_VERSIONS})
        file(GLOB IFCGEOM_I_FILES ../src/ifcgeom/mapping/*.i)
        file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/mapping/*.h)
        file(GLOB IFCGEOM_CPP_FILES ../src/ifcgeom/mapping/*.cpp)
        set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})
        
        add_library(geometry_mapping_ifc${schema} STATIC ${IFCGEOM_FILES})
        set_target_properties(geometry_mapping_ifc${schema} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}")
        target_link_libraries(geometry_mapping_ifc${schema} IfcParse)
        list(APPEND mapping_libraries geometry_mapping_ifc${schema})
    endforeach()

    # IfcGeom (schema agnostic)
    file(GLOB SCHEMA_AGNOSTIC_H_FILES ../src/ifcgeom/*.h)
    file(GLOB SCHEMA_AGNOSTIC_CPP_FILES ../src/ifcgeom/*.cpp)
    set(SCHEMA_AGNOSTIC_FILES ${SCHEMA_AGNOSTIC_H_FILES} ${SCHEMA_AGNOSTIC_CPP_FILES})

    add_library(IfcGeom ${SCHEMA_AGNOSTIC_FILES})
    set_target_properties(IfcGeom PROPERTIES COMPILE_FLAGS -DIFC_GEOM_EXPORTS VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

    if(UNIX)
        find_package(Threads)
    endif()

    if(WASM_BUILD)
        target_link_libraries(IfcGeom ${kernel_libraries} ${mapping_libraries} ${CMAKE_THREAD_LIBS_INIT})
    else()
        target_link_libraries(IfcGeom IfcParse ${kernel_libraries} ${mapping_libraries} ${CMAKE_THREAD_LIBS_INIT})
    endif()

endif(BUILD_IFCGEOM)

if(BUILD_CONVERT OR BUILD_IFCPYTHON)
    # Serializers
    file(GLOB SERIALIZERS_H_FILES ../src/serializers/*.h)
    file(GLOB SERIALIZERS_CPP_FILES ../src/serializers/*.cpp)
    set(SERIALIZERS_FILES ${SERIALIZERS_H_FILES} ${SERIALIZERS_CPP_FILES})
    file(GLOB SERIALIZERS_S_H_FILES ../src/serializers/schema_dependent/*.h)
    file(GLOB SERIALIZERS_S_CPP_FILES ../src/serializers/schema_dependent/*.cpp)
    set(SERIALIZERS_S_FILES ${SERIALIZERS_S_H_FILES} ${SERIALIZERS_S_CPP_FILES})

    foreach(schema ${SCHEMA_VERSIONS})
        add_library(Serializers_ifc${schema} STATIC ${SERIALIZERS_S_FILES})
        set_target_properties(Serializers_ifc${schema} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}")
        
        if(WASM_BUILD)
            target_link_libraries(Serializers_ifc${schema} ${HDF5_LIBRARIES})
        else()
            target_link_libraries(Serializers_ifc${schema} IfcGeom ${OPENCASCADE_LIBRARIES} ${HDF5_LIBRARIES})
        endif()
    endforeach()

    add_library(Serializers ${SERIALIZERS_FILES})
    set_target_properties(Serializers PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS" VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

    if(WITH_PROJ)
        target_compile_definitions(Serializers PRIVATE "WITH_PROJ")
        if (PROJ_STATIC)
            target_compile_definitions(Serializers PRIVATE "PROJ_DLL=")
        endif()
        target_include_directories(Serializers PRIVATE ${PROJ_INCLUDE_DIR} ${SQLITE_INCLUDE_DIR})
        target_link_libraries(Serializers ${PROJ_LIBRARIES})
    endif()

    target_link_libraries(Serializers ${SERIALIZER_SCHEMA_LIBRARIES} ${OPENCOLLADA_LIBRARIES} ${USD_LIBRARIES})

endif(BUILD_CONVERT OR BUILD_IFCPYTHON)

if(BUILD_CONVERT)
    if(WITH_CGAL AND CITYJSON_SUPPORT)
        message(STATUS "Building CityJSON support")
        set(CITYJSON_CONVERT_FILES
            ../src/ifcconvert/cityjson/geobim.cpp
            ../src/ifcconvert/cityjson/global_execution_context.cpp
            ../src/ifcconvert/cityjson/opening_collector.cpp
            ../src/ifcconvert/cityjson/processing.cpp
            ../src/ifcconvert/cityjson/radius_comparison.cpp
            ../src/ifcconvert/cityjson/radius_execution_context.cpp
            ../src/ifcconvert/cityjson/settings.cpp
            ../src/ifcconvert/cityjson/writer.cpp
        )
        add_library(cityjson_converter ${CITYJSON_CONVERT_FILES})
        target_include_directories(cityjson_converter PRIVATE ../src)
        set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} cityjson_converter)

        install(TARGETS cityjson_converter
            ARCHIVE DESTINATION ${LIBDIR}
            LIBRARY DESTINATION ${LIBDIR}
        )

        add_executable(cityjson_converter_exe ${CITYJSON_CONVERT_FILES})
        set_target_properties(cityjson_converter_exe PROPERTIES COMPILE_FLAGS "-DCITYJSON_EXECUTABLE")
        target_include_directories(cityjson_converter_exe PRIVATE ../src)
        target_link_libraries(cityjson_converter_exe ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})

        install(TARGETS cityjson_converter_exe
            RUNTIME DESTINATION ${BINDIR}
        )
    endif()

    # IfcConvert
	if (WITH_RELATIONSHIP_VALIDATION)
		file(GLOB IFCCONVERT_CPP_FILES ../src/ifcconvert/*.cpp)
		file(GLOB IFCCONVERT_H_FILES ../src/ifcconvert/*.h)
	else()
		file(GLOB IFCCONVERT_CPP_FILES ../src/ifcconvert/IfcConvert.cpp)
		file(GLOB IFCCONVERT_H_FILES)
	endif()
    set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
    add_executable(IfcConvert ${IFCCONVERT_FILES})

    target_link_libraries(IfcConvert ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})
	if (WITH_RELATIONSHIP_VALIDATION)
        set_property(TARGET IfcConvert APPEND_STRING PROPERTY COMPILE_FLAGS " -DWITH_RELATIONSHIP_VALIDATION")
    endif()

    if(WITH_CGAL AND CITYJSON_SUPPORT)
        set_property(TARGET IfcConvert APPEND_STRING PROPERTY COMPILE_FLAGS " -DIFOPSH_WITH_CITYJSON")
    endif()

    if((NOT WIN32) AND BUILD_SHARED_LIBS)
        # Only set RPATHs when building shared libraries (i.e. IfcParse and
        # IfcGeom are dynamically linked). Not necessarily a perfect solution
        # but probably a good indication of whether RPATHs are necessary.
        SET_INSTALL_RPATHS(IfcConvert "${IFCOPENSHELL_LIBRARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS};${OPENCOLLADA_LIBRARY_DIR}")
    endif()

    install(TARGETS IfcConvert
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
    add_executable(IfcGeomServer ${SOURCE_FILES})
    target_link_libraries(IfcGeomServer ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES})

    if((NOT WIN32) AND BUILD_SHARED_LIBS)
        SET_INSTALL_RPATHS(IfcGeomServer "${IFCOPENSHELL_LIBRARY_DIR};${OCC_LIBRARY_DIR};${Boost_LIBRARY_DIRS}")
    endif()

    install(TARGETS IfcGeomServer
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
    )
endif(BUILD_GEOMSERVER)

if(ADD_COMMIT_SHA)
    find_package(Git)

    if(GIT_FOUND)
        if (VERSION_OVERRIDE)
            set (git_branch ${RELEASE_VERSION})
        else()
            message("git found: ${GIT_EXECUTABLE} with version ${GIT_VERSION_STRING}")
            execute_process(
                COMMAND ${GIT_EXECUTABLE} branch -a --contains HEAD
                OUTPUT_VARIABLE git_branches
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            string(REPLACE "\n" ";" git_branch_list "${git_branches}")

            foreach(git_branch_candidate IN ITEMS ${git_branch_list})
		        string(REPLACE "*" "" git_branch_candidate_temp "${git_branch_candidate}")
		        string(STRIP "${git_branch_candidate_temp}" git_branch_candidate_2)
                if(NOT git_branch_candidate_2 MATCHES "^HEAD$")
                    string(REPLACE "/" ";" git_branch_candidate_2_list "${git_branch_candidate_2}")
                    list(GET git_branch_candidate_2_list -1 git_branch)
                endif()
            endforeach()
        endif()

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
endif(ADD_COMMIT_SHA)

if(MSVC)
    # @todo still needs to be understood better, but the cgal and cgal-simple kernel cause multiply defined boost lambda placeholders _1 ... _3
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /FORCE:MULTIPLE")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /FORCE:MULTIPLE")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} /FORCE:MULTIPLE")
endif()

# Documentation
if(BUILD_DOCUMENTATION)
    set(CMAKE_MODULE_PATH "../docs/cmake")
    add_subdirectory(../docs docs)
endif()

if(BUILD_IFCPYTHON)
    add_subdirectory(../src/ifcwrap ifcwrap)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(../src/examples examples)
endif()

if(BUILD_IFCMAX)
    add_subdirectory(../src/ifcmax ifcmax)
endif()

if(WITH_CGAL)
    add_subdirectory(../src/svgfill svgfill)        
endif()

if(BUILD_QTVIEWER)
    add_subdirectory(../src/qtviewer qtviewer)
endif()

# CMake installation targets
install(FILES ${IFCPARSE_H_FILES}
	DESTINATION ${INCLUDEDIR}/ifcparse
)

install(TARGETS IfcParse
	ARCHIVE DESTINATION ${LIBDIR}
	LIBRARY DESTINATION ${LIBDIR}
	RUNTIME DESTINATION ${BINDIR}
)

if(BUILD_IFCGEOM)
    # install(FILES ${IFCGEOM_H_FILES}
    #     DESTINATION ${INCLUDEDIR}/ifcgeom
    # )

    install(FILES ${SCHEMA_AGNOSTIC_H_FILES}
        DESTINATION ${INCLUDEDIR}/ifcgeom
    )

    foreach(kernel ${GEOMETRY_KERNELS})
        file(GLOB IFCGEOM_H_FILES ../src/ifcgeom/kernels/${kernel}/*.h)
         install(FILES ${IFCGEOM_H_FILES}
            DESTINATION ${INCLUDEDIR}/ifcgeom/kernels/${kernel}
        )
    endforeach()

    install(TARGETS ${IFCGEOM_SCHEMA_LIBRARIES} ${kernel_libraries} IfcGeom
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
    )
endif(BUILD_IFCGEOM)

if(BUILD_CONVERT)
    install(TARGETS Serializers ${SERIALIZER_SCHEMA_LIBRARIES}
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
    )

    install(FILES ${SERIALIZERS_H_FILES}
        DESTINATION ${INCLUDEDIR}/serializers/
    )

    install(FILES ${SERIALIZERS_S_H_FILES}
        DESTINATION ${INCLUDEDIR}/serializers/schema_dependent
    )
endif(BUILD_CONVERT)

if(BUILD_CONVERT OR BUILD_IFCPYTHON)
    install(TARGETS geometry_serializer ${geometry_serializer_libraries}
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
    )
endif(BUILD_CONVERT OR BUILD_IFCPYTHON)

# Cmake uninstall target
if(NOT TARGET uninstall)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
        IMMEDIATE @ONLY)

    add_custom_target(uninstall
        COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)
endif()

# Packaging
list(APPEND CPACK_SOURCE_IGNORE_FILES
    "/\\\\.git"
    "/build/"
)
set(CPACK_SOURCE_INSTALLED_DIRECTORIES "${CMAKE_SOURCE_DIR}/..;/")
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

foreach(COMPONENT IN ITEMS ${BOOST_COMPONENTS})
    string(REPLACE "_" "-" COMP ${COMPONENT})
    set(BOOST_DEPS "${BOOST_DEPS}, libboost-${COMP}-dev")
endforeach(COMPONENT)

set(CPACK_DEBIAN_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3, libxml2, libocct-foundation-dev, libocct-modeling-algorithms-dev, libocct-modeling-data-dev, libocct-ocaf-dev, libocct-visualization-dev, libocct-data-exchange-dev, libhdf5-serial-dev, libpython3-dev, python3-pytest ${BOOST_DEPS}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "${CPACK_PACKAGE_DESCRIPTION_SUMMARY}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION "${CPACK_PACKAGE_DESCRIPTION}")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_SECTION "science")
set(CPACK_DEBIAN_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}${EXTRA_VERSION}")
set(CPACK_DEBIAN_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
# set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_SOURCE_DIR}/cmake/debian/postinst")

include(CPack)
