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
if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()
if(CMAKE_CXX_STANDARD LESS 17)
    message(FATAL_ERROR "C++17 or newer is required.")
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON) # not necessary, but encouraged
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# The VERSION file in the repository root is the single source of truth for the
# release version. Read it unconditionally so a plain source build reports the
# real version through buildinfo.cpp instead of the stale hardcoded 0.8.0
# fallback (see #8164). VERSION_OVERRIDE still controls the branch name used
# when ADD_COMMIT_SHA embeds a commit sha.
file(READ "../VERSION" "RELEASE_VERSION_")
string(STRIP "${RELEASE_VERSION_}" RELEASE_VERSION)
message(STATUS "Detected version '${RELEASE_VERSION}'")

add_definitions(-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)

if(POLICY CMP0141) # 3.25+
    # Has to be set before `project` to take effect.
    cmake_policy(SET CMP0141 NEW) # Support for `CMAKE_MSVC_DEBUG_INFORMATION_FORMAT`.
endif()
if(POLICY CMP0144) # 3.27
    cmake_policy(SET CMP0144 NEW) # find_package() uses upper-case <PACKAGENAME>_ROOT variables.
endif()
if(POLICY CMP0167) # 3.30
    cmake_policy(SET CMP0167 OLD)
endif()

project(IfcOpenShell VERSION ${RELEASE_VERSION})

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

option(
    ENABLE_BUILD_OPTIMIZATIONS
    "Enable certain compiler and linker optimizations on RelWithDebInfo and Release builds."
    OFF
)
option(BUILD_SHARED_LIBS "Build IfcParse and IfcGeom as shared libs (SO/DLL)." OFF)
option(MSVC_PARALLEL_BUILD "Multi-threaded compilation in Microsoft Visual Studio (/MP)" OFF)
option(USE_VLD "Use Visual Leak Detector for debugging memory leaks, MSVC-only." OFF)
option(USE_MMAP "Adds a command line options to parse IFC files from memory mapped files using Boost.Iostreams" OFF)
option(NO_WARN "Disable all warnings" OFF)

option(BUILD_IFCGEOM "Build IfcGeom." ON)
option(BUILD_IFCPYTHON "Build IfcPython." ON)
option(BUILD_CONVERT "Build IfcConvert executable." ON)
option(BUILD_DOCUMENTATION "Build IfcOpenShell Documentation." OFF)
option(BUILD_EXAMPLES "Build example applications." OFF)
option(BUILD_GEOMSERVER "Build IfcGeomServer executable (Open CASCADE is required)." ON)
option(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
option(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer" OFF) # QtViewer requires Qt6
option(BUILD_PACKAGE "" OFF)
# Most users probably need just common schemas,
# but we're keeping it `OFF` by default to avoid disruption
# (e.g. all Python distribution would need to adapt this option to be set).
option(
    BUILD_ONLY_COMMON_SCHEMAS
    "Build only common IFC schemas (2x3, 4, 4x3_add2). By default all schemas will be built."
    OFF
)
option(SCHEMA_VERSIONS "Explicitly specify schemas to build." "")

option(WITH_OPENCASCADE "Enable geometry interpretation using Open CASCADE" ON)
option(WITH_CGAL "Enable geometry interpretation using CGAL" ON)
option(COLLADA_SUPPORT "Build IfcConvert with COLLADA support (requires OpenCOLLADA)." ON)
option(GLTF_SUPPORT "Build IfcConvert with glTF support (requires json.hpp)." OFF)
option(HDF5_SUPPORT "Enable HDF5 support (requires HDF5, zlib)" ON)
option(WITH_PROJ "Enable output of Earth-Centered Earth-Fixed glTF output using the PROJ library" OFF)
option(IFCXML_SUPPORT "Build IfcParse with ifcXML support (requires libxml2)." ON)
option(USD_SUPPORT "Build IfcConvert with USD support (requires pixar's USD library)." OFF)
option(WITH_RELATIONSHIP_VALIDATION "Build IfcConvert with option to validate geometrical relationships." OFF)
option(WITH_ROCKSDB "Support a RocksDB key-value store as a file backend in IfcOpenShell" OFF)
option(WITH_ZSTD "Use Zstd compression in RocksDB writes" OFF)

option(USERSPACE_PYTHON_PREFIX "Installs IfcPython for the current user only instead of system-wide." OFF)
option(USE_DEBUG_PYTHON "Use debug binaries when building Debug IfcPython on Windows." OFF)
option(ADD_COMMIT_SHA "Add commit sha and branch in version number, requires git" OFF)
option(
    VERSION_OVERRIDE
    "Override the version defined in buildinfo.cpp with the file VERSION in the repository root"
    OFF
)
option(USE_CCACHE "Enable use of ccache if it's available from PATH." ON)

set(PYTHON_MODULE_INSTALL_DIR
    ""
    CACHE PATH
    "Directory to install IfcPython package to. By default package is installed in found Python's site-packages."
)

# Make sure CMake modules in this project are found first
list(PREPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})

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

if((BUILD_CONVERT OR BUILD_GEOMSERVER OR BUILD_IFCPYTHON) AND (NOT BUILD_IFCGEOM))
    message(STATUS "'IfcGeom' is required with current outputs")
    set(BUILD_IFCGEOM ON)
endif()

find_program(CCACHE_FOUND ccache)
if(USE_CCACHE AND CCACHE_FOUND)
    message(STATUS "`ccache` is found, using it as a compiler launcher.")
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CCACHE_FOUND}")
    if(MSVC)
        # By default Visual Studio generators will use /Zi which is not compatible
        # with ccache, so tell Visual Studio to use /Z7 instead.
        set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<$<CONFIG:Debug,RelWithDebInfo>:Embedded>")
        # Not needed for Ninja.
        if(CMAKE_GENERATOR MATCHES "Visual Studio")
            file(COPY_FILE ${CCACHE_FOUND} ${CMAKE_BINARY_DIR}/cl.exe ONLY_IF_DIFFERENT)
            set(CMAKE_VS_GLOBALS "CLToolExe=cl.exe" "CLToolPath=${CMAKE_BINARY_DIR}" "UseMultiToolTask=true")
        endif()
    endif()
endif()
mark_as_advanced(CCACHE_FOUND)

# Variable to accumulate swig definitions from various submodules.
set(SWIG_DEFINES "")

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

set(IFCOPENSHELL_EXPORT_TARGETS "${PROJECT_NAME}Targets")

# On Windows Release and Debug binaries are not compatible.
# So we add a postfix to avoid issues and allow release and debug installations to coexist.
if(WIN32)
    set(CMAKE_DEBUG_POSTFIX "_d")
endif()

if(BUILD_SHARED_LIBS)
    add_definitions(-DIFC_SHARED_BUILD)
    if(MSVC)
        message(
            WARNING
            "Building DLLs against the static VC run-time. This is not recommended if the DLLs are to be redistributed."
        )
        # C4521: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
        # There will be couple hundreds of these so suppress them away, https://msdn.microsoft.com/en-us/library/esew7y1w.aspx
        add_definitions(-wd4251)
    endif()
endif()

UNIFY_ENVVARS_AND_CACHE(BOOST_ROOT)

if(NOT MINIMAL_BUILD)
    UNIFY_ENVVARS_AND_CACHE(PYTHON_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(PYTHON_LIBRARY)
    UNIFY_ENVVARS_AND_CACHE(PYTHON_EXECUTABLE)
endif()

# Get a list of all OPTION flags from the CMakeLists.txt
get_all_option_flags(option_flags)

# Loop through the list of OPTION flags and convert the corresponding environment variables
foreach(option_flag IN LISTS option_flags)
    convert_env_var_to_bool("${option_flag}")
endforeach()

if(BUILD_IFCGEOM AND WITH_OPENCASCADE)
    find_package(OpenCASCADE REQUIRED)
    add_definitions(-DIFOPSH_WITH_OPENCASCADE)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_OPENCASCADE)
    list(APPEND GEOMETRY_KERNELS opencascade)
endif()

set(GLTF_LIBRARIES "")
if(GLTF_SUPPORT)
    find_package(nlohmann_json REQUIRED)
    set(GLTF_LIBRARIES nlohmann_json::nlohmann_json)
    add_definitions(-DWITH_GLTF)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_GLTF)
endif()

# Add USD support to serializers
set(USD_LIBRARIES "")
if(USD_SUPPORT)
    find_package(USD REQUIRED)
    set(USD_LIBRARIES pxr::USD)
endif(USD_SUPPORT)

set(ROCKSDB_LIBRARIES "")
if(WITH_ROCKSDB)
    # Temporaily mess with CMAKE_FIND_PACKAGE_PREFER_CONFIG to help RocksDB
    # find it's zstd dependency on Windows.
    # Only do it on Windows, otherwise it might create problems as
    # findzstd and zstd-config target names do not match.
    # https://github.com/facebook/rocksdb/pull/13975
    if(WIN32)
        set(TEMP CMAKE_FIND_PACKAGE_PREFER_CONFIG)
        set(CMAKE_FIND_PACKAGE_PREFER_CONFIG TRUE)
    endif()
    find_package(RocksDB CONFIG REQUIRED)
    mark_as_advanced(RocksDB_DIR)
    if(WIN32)
        set(CMAKE_FIND_PACKAGE_PREFER_CONFIG ${TEMP})
    endif()

    message(STATUS "RocksDB: found at '${RocksDB_DIR}'.")
    add_library(IFCOPENSHELL_RocksDB INTERFACE)
    set(ROCKSDB_LIBRARIES "IFCOPENSHELL_RocksDB")
    target_compile_definitions(IFCOPENSHELL_RocksDB INTERFACE IFOPSH_WITH_ROCKSDB)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_ROCKSDB)
    # See https://github.com/facebook/rocksdb/issues/981.
    if(TARGET RocksDB::rocksdb)
        target_link_libraries(IFCOPENSHELL_RocksDB INTERFACE RocksDB::rocksdb)
    elseif(TARGET RocksDB::rocksdb-shared)
        target_link_libraries(IFCOPENSHELL_RocksDB INTERFACE RocksDB::rocksdb-shared)
    else()
        message(FATAL_ERROR "RocksDB found but neither RocksDB::rocksdb nor RocksDB::rocksdb-shared target exists")
    endif()

    if(WITH_ZSTD)
        # @todo do we actually need the zstd include dir or rather just pass
        # the libzstd.a along with the rocksdb library when needed and feature
        # detect based on rocksdb API?
        find_package(zstd CONFIG REQUIRED)
        mark_as_advanced(zstd_DIR)
        message(STATUS "zstd: found at '${zstd_DIR}'.")
        target_link_libraries(IFCOPENSHELL_RocksDB INTERFACE zstd::libzstd_static)
    endif()

    install(TARGETS IFCOPENSHELL_RocksDB EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endif()

# Find Boost: On win32 the (hardcoded) default is to use static libraries and
# runtime, when doing running conda-build we pick what conda prepared for us.
if(WIN32 AND NOT DEFINED ENV{CONDA_BUILD})
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
    # Boost.System has been header-only since 1.69 and its compiled stub library
    # was dropped in newer Boost, so requesting it as a component makes
    # find_package fail on Boost 1.70 and up (for example Boost 1.90). It is
    # still pulled in transitively by thread / iostreams where needed, so do not
    # request it explicitly.
    set(BOOST_COMPONENTS
        program_options
        regex
        thread
        date_time
        iostreams
    )
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

# Handle CGAL after Boost settings are set, since CGAL will use them too.
# Do `find_package(Boost)` only after this, to make sure `FindBoost` finds correct components.
# Otherwise it will find components needed for CGAL and we might some libraries.
if(WITH_CGAL)
    find_package(CGAL REQUIRED)
    set(CGAL_LIBRARIES IFCOPENSHELL_CGAL)
    list(APPEND GEOMETRY_KERNELS cgal)
endif()

find_package(Boost REQUIRED COMPONENTS ${BOOST_COMPONENTS})
message(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
message(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

if(COLLADA_SUPPORT)
    find_package(OpenCOLLADA REQUIRED)
    add_definitions(-DWITH_OPENCOLLADA)
endif()

if(HDF5_SUPPORT)
    find_package(HDF5 REQUIRED COMPONENTS C CXX)
    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} hdf5::hdf5_cpp)

    add_definitions(-DWITH_HDF5)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_HDF5)
endif(HDF5_SUPPORT)

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
        set(LINKER_FLAGS_RELEASE "/LTCG /OPT:REF")
        # /OPT:NOICF is recommended when /DEBUG is used (http://msdn.microsoft.com/en-us/library/xe4t6fc1.aspx)
        set(LINKER_FLAGS_RELWITHDEBINFO "/DEBUG /OPT:NOICF")

        set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELEASE}")
        set(CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO
            "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELWITHDEBINFO}"
        )
        set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELEASE}")
        set(CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO "${CMAKE_EXE_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELWITHDEBINFO}")
        set(CMAKE_MODULE_LINKER_FLAGS_RELEASE "${CMAKE_MODULE_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELEASE}")
        set(CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO
            "${CMAKE_MODULE_LINKER_FLAGS_RELEASE} ${LINKER_FLAGS_RELWITHDEBINFO}"
        )
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
    if(MSVC_VERSION GREATER 1900 AND (Boost_MAJOR_VERSION GREATER 1 OR Boost_MINOR_VERSION GREATER 66))
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

    if(
        CMAKE_CXX_COMPILER_ID MATCHES "GNU"
        AND (CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 9.0 OR CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL 9.0)
    )
        # OpenCascade spews a lot of deprecated-copy warnings
        add_definitions(-Wno-deprecated-copy)
    endif()

    # -fPIC is not relevant on Windows and creates pointless warnings
    if(UNIX)
        add_definitions(-fPIC)
    endif()
endif(MSVC)

include_directories(${OPENCOLLADA_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS} ${HDF5_INCLUDE_DIR})

if(NOT SCHEMA_VERSIONS)
    # `WASM_BUILD` - super arbitrarily try to keep size down at least a little bit
    if(BUILD_ONLY_COMMON_SCHEMAS OR WASM_BUILD)
        set(SCHEMA_VERSIONS "2x3" "4" "4x3_add2")
    else()
        set(SCHEMA_VERSIONS
            "2x3"
            "4"
            "4x1"
            "4x2"
            "4x3"
            "4x3_tc1"
            "4x3_add1"
            "4x3_add2"
        )
    endif()
endif()

message(STATUS "IFC SCHEMA_VERSIONS that will be used for the build: ${SCHEMA_VERSIONS}.")

set(SCHEMA_DEFINITIONS "")
foreach(schema ${SCHEMA_VERSIONS})
    list(APPEND SCHEMA_DEFINITIONS "-DHAS_SCHEMA_${schema}")
endforeach()

string(REPLACE ";" ")(" schema_version_seq "(${SCHEMA_VERSIONS})")
list(APPEND SCHEMA_DEFINITIONS "-DSCHEMA_SEQ=${schema_version_seq}")

if(COMPILE_SCHEMA)
    # @todo, this appears to be untested at the moment
    find_package(PythonInterp)

    if(NOT PYTHONINTERP_FOUND)
        message(
            FATAL_ERROR
            "A Python interpreter is necessary when COMPILE_SCHEMA is enabled. Disable COMPILE_SCHEMA or fix Python paths to proceed."
        )
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
        execute_process(
            COMMAND ${PYTHON_EXECUTABLE} -m pip "install" --user pyparsing
            RESULT_VARIABLE SUCCESS
        )

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
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} bootstrap.py
        WORKING_DIRECTORY ../src/ifcopenshell-python/ifcopenshell/express
        OUTPUT_FILE express_parser.py
        RESULT_VARIABLE SUCCESS
    )

    if(NOT "${SUCCESS}" STREQUAL "0")
        message(FATAL_ERROR "Failed to bootstrap parser. Make sure pyparsing is installed")
    endif()

    # Generate code
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} ../ifcopenshell-python/ifcopenshell/express/express_parser.py ../../${COMPILE_SCHEMA}
        WORKING_DIRECTORY ../src/ifcparse
        OUTPUT_VARIABLE COMPILED_SCHEMA_NAME
    )

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

add_subdirectory(../src/ifcparse ifcparse)
set(IFCOPENSHELL_LIBRARIES IfcParse)

if(BUILD_IFCGEOM)
    add_subdirectory(../src/ifcgeom ifcgeom)
endif(BUILD_IFCGEOM)

if(BUILD_CONVERT OR BUILD_IFCPYTHON)
    add_subdirectory(../src/serializers serializers)
    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} ${SERIALIZER_SCHEMA_LIBRARIES})
endif(BUILD_CONVERT OR BUILD_IFCPYTHON)

if(BUILD_CONVERT)
    add_subdirectory(../src/ifcconvert ifcconvert)
endif(BUILD_CONVERT)

# IfcGeomServer
if(BUILD_GEOMSERVER)
    add_subdirectory(../src/ifcgeomserver ifcgeomserver)
endif(BUILD_GEOMSERVER)

if(ADD_COMMIT_SHA)
    find_package(Git)

    if(NOT GIT_FOUND)
        message(FATAL_ERROR "Failed to find Git for ADD_COMMIT_SHA option.")
    endif()

    if(GIT_FOUND)
        if(VERSION_OVERRIDE)
            set(git_branch ${RELEASE_VERSION})
        else()
            message("git found: ${GIT_EXECUTABLE} with version ${GIT_VERSION_STRING}")
            execute_process(
                COMMAND ${GIT_EXECUTABLE} branch -a --contains HEAD
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
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
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE git_sha
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )

        message(STATUS "IfcOpenShell branch: \"${git_branch}\"")
        message(STATUS "IfcOpenShell commit: \"${git_sha}\"")

        if("${git_branch}" STREQUAL "" OR "${git_sha}" STREQUAL "")
            message(FATAL_ERROR "Unable to determine commit sha and/or branch")
        endif()

        target_compile_definitions(
            IfcParse
            PRIVATE -DIFCOPENSHELL_BRANCH=${git_branch} -DIFCOPENSHELL_COMMIT=${git_sha}
        )
    endif()
endif(ADD_COMMIT_SHA)

# Always expose the release version (from the VERSION file) to buildinfo.cpp so
# that a build without commit-sha info reports the correct version instead of a
# stale hardcoded fallback. See #8164.
target_compile_definitions(IfcParse PRIVATE IFCOPENSHELL_VERSION_STRING=${RELEASE_VERSION})

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

if(BUILD_IFCPYTHON AND WITH_CGAL)
    add_subdirectory(../src/svgfill svgfill)
endif()

if(BUILD_QTVIEWER)
    add_subdirectory(../src/qtviewer qtviewer)
endif()

# Cmake uninstall target
if(NOT TARGET uninstall)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
        IMMEDIATE
        @ONLY
    )

    add_custom_target(uninstall COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)
endif()

# Packaging
list(APPEND CPACK_SOURCE_IGNORE_FILES "/\\\\.git" "/build/" "/.pytest_cache/" "/__pycache__/")
set(CPACK_SOURCE_INSTALLED_DIRECTORIES "${CMAKE_SOURCE_DIR}/..;/")
set(CPACK_PACKAGE_NAME
    "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}"
)
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${PROJECT_NAME}-${PROJECT_VERSION}${EXTRA_VERSION}")
set(CPACK_PACKAGE_FILE_NAME
    "${PROJECT_NAME}-${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}${EXTRA_VERSION}-${CMAKE_SYSTEM_NAME}"
)
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

set(BOOST_DEPS "")
foreach(COMPONENT IN ITEMS ${BOOST_COMPONENTS})
    string(REPLACE "_" "-" COMP ${COMPONENT})
    set(BOOST_DEPS "${BOOST_DEPS}, libboost-${COMP}-dev")
endforeach(COMPONENT)

set(CPACK_DEBIAN_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "${CPACK_PACKAGE_CONTACT}")
set(CPACK_DEBIAN_PACKAGE_DEPENDS
    "python3, libxml2, libocct-foundation-dev, libocct-modeling-algorithms-dev, libocct-modeling-data-dev, libocct-ocaf-dev, libocct-visualization-dev, libocct-data-exchange-dev, libhdf5-serial-dev, libpython3-dev, python3-pytest ${BOOST_DEPS}"
)
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION_SUMMARY "${CPACK_PACKAGE_DESCRIPTION_SUMMARY}")
set(CPACK_DEBIAN_PACKAGE_DESCRIPTION "${CPACK_PACKAGE_DESCRIPTION}")
set(CPACK_DEBIAN_PACKAGE_PRIORITY "optional")
set(CPACK_DEBIAN_PACKAGE_SECTION "science")
set(CPACK_DEBIAN_PACKAGE_VERSION
    "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}${EXTRA_VERSION}"
)
set(CPACK_DEBIAN_ARCHITECTURE "${CMAKE_SYSTEM_PROCESSOR}")
# set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_SOURCE_DIR}/cmake/debian/postinst")

include(CPack)

include(package_export.cmake)
