# Root-level CMakeLists.txt for building IfcOpenShell as DLLs for UE 5.8 on Windows x64.
# Place this file in the root of a cloned IfcOpenShell repository, next to /cmake and /src.

cmake_minimum_required(VERSION 3.21)

# Visual Studio 18 2026 requires CMake 4.2+, but the file itself stays compatible
# with IfcOpenShell's 3.21 minimum for users building through Ninja/MSBuild wrappers.
project(IfcOpenShell_UE58_Win64 LANGUAGES C CXX)

# -----------------------------------------------------------------------------
# Compiler / ABI settings for Unreal Engine integration
# -----------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 20 CACHE STRING "C++ standard" FORCE)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(MSVC)
    # UE Windows builds use the DLL CRT. Build the third-party DLLs the same way.
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL" CACHE STRING "MSVC runtime" FORCE)

    add_compile_options(
        /permissive-
        /Zc:__cplusplus
        /bigobj
        /MP
    )

    add_definitions(
        -D_CRT_SECURE_NO_WARNINGS
        -D_SCL_SECURE_NO_WARNINGS
        -DNOMINMAX
        -DWIN32_LEAN_AND_MEAN
        -DBOOST_ALL_NO_LIB
        -DBOOST_DATE_TIME_NO_LIB
    )
endif()

if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "This configuration is intended for Windows x64 only.")
endif()

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}/install" CACHE PATH "Install prefix" FORCE)
endif()

foreach(_cfg Debug Release RelWithDebInfo MinSizeRel)
    string(TOUPPER "${_cfg}" _cfg_upper)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${_cfg_upper} "${CMAKE_BINARY_DIR}/bin/${_cfg}" CACHE PATH "" FORCE)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${_cfg_upper} "${CMAKE_BINARY_DIR}/bin/${_cfg}" CACHE PATH "" FORCE)
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${_cfg_upper} "${CMAKE_BINARY_DIR}/lib/${_cfg}" CACHE PATH "" FORCE)
endforeach()

# -----------------------------------------------------------------------------
# User paths
# -----------------------------------------------------------------------------
set(IFCOPENSHELL_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "IfcOpenShell repository root")

set(UE_BOOST_INCLUDE_DIR
    "D:/Editors/Epic/Binaries/UE_5.8/Engine/Source/ThirdParty/Boost/Deploy/boost-1.88.0/include"
    CACHE PATH "UE 5.8 Boost include directory")

set(UE_BOOST_LIBRARY_DIR
    "D:/Editors/Epic/Binaries/UE_5.8/Engine/Source/ThirdParty/Boost/Deploy/boost-1.88.0/VS2015/x64/lib"
    CACHE PATH "UE 5.8 Boost import library / DLL directory")

set(OCCT_ROOT "C:/Program Files/OCCT" CACHE PATH "Open CASCADE installation root")
set(OpenCASCADE_DIR "" CACHE PATH "Directory containing OpenCASCADEConfig.cmake, if available")
set(OCC_INCLUDE_DIR "" CACHE PATH "Manual OCCT include dir, e.g. C:/Program Files/OCCT/inc")
set(OCC_LIBRARY_DIR "" CACHE PATH "Manual OCCT library dir, e.g. C:/Program Files/OCCT/win64/vc14/lib")
set(OCCT_BIN_DIR "" CACHE PATH "Optional OCCT DLL directory to copy during install")

set(EIGEN_DIR "" CACHE PATH "Eigen include directory, e.g. D:/ThirdParty/eigen-3.4.0")

set(NLOHMANN_JSON_ROOT "" CACHE PATH "Optional nlohmann/json root")
set(NLOHMANN_JSON_INCLUDE_DIR "" CACHE PATH "Directory containing nlohmann/json.hpp, e.g. D:/ThirdParty/json/single_include")
set(nlohmann_json_DIR "" CACHE PATH "Optional nlohmann_json CMake package config directory")

set(LIBXML2_ROOT "" CACHE PATH "Optional LibXml2 root")
set(LibXml2_DIR "" CACHE PATH "Optional LibXml2 CMake package config directory")
set(LIBXML2_INCLUDE_DIR "" CACHE PATH "LibXml2 include directory, usually <root>/include/libxml2")
set(LIBXML2_LIBRARY "" CACHE FILEPATH "Path to libxml2.lib")
set(LIBXML2_DLL "" CACHE FILEPATH "Optional path to libxml2.dll to copy during install")

# -----------------------------------------------------------------------------
# Path auto-detection helpers
# -----------------------------------------------------------------------------
function(_ifcos_first_existing_dir out_var)
    foreach(_candidate IN LISTS ARGN)
        if(EXISTS "${_candidate}")
            set(${out_var} "${_candidate}" PARENT_SCOPE)
            return()
        endif()
    endforeach()
    set(${out_var} "" PARENT_SCOPE)
endfunction()

# OCCT: prefer OpenCASCADEConfig.cmake if installed. Otherwise fill OCC_* hints.
list(PREPEND CMAKE_PREFIX_PATH
    "${OCCT_ROOT}"
    "${OCCT_ROOT}/cmake"
    "${OCCT_ROOT}/lib/cmake/opencascade"
    "${OCCT_ROOT}/lib/cmake/OpenCASCADE"
)

if(OpenCASCADE_DIR STREQUAL "")
    _ifcos_first_existing_dir(_detected_occt_config_dir
        "${OCCT_ROOT}/cmake"
        "${OCCT_ROOT}/lib/cmake/opencascade"
        "${OCCT_ROOT}/lib/cmake/OpenCASCADE"
    )
    if(NOT _detected_occt_config_dir STREQUAL "")
        set(OpenCASCADE_DIR "${_detected_occt_config_dir}" CACHE PATH "Directory containing OpenCASCADEConfig.cmake" FORCE)
    endif()
endif()

if(OpenCASCADE_DIR STREQUAL "")
    if(OCC_INCLUDE_DIR STREQUAL "")
        _ifcos_first_existing_dir(_detected_occ_include
            "${OCCT_ROOT}/inc"
            "${OCCT_ROOT}/include/opencascade"
            "${OCCT_ROOT}/include"
        )
        if(NOT _detected_occ_include STREQUAL "")
            set(OCC_INCLUDE_DIR "${_detected_occ_include}" CACHE PATH "Manual OCCT include dir" FORCE)
        endif()
    endif()

    if(OCC_LIBRARY_DIR STREQUAL "")
        _ifcos_first_existing_dir(_detected_occ_lib
            "${OCCT_ROOT}/win64/vc145/lib"
            "${OCCT_ROOT}/win64/vc143/lib"
            "${OCCT_ROOT}/win64/vc14/lib"
            "${OCCT_ROOT}/lib"
            "${OCCT_ROOT}/lib64"
        )
        if(NOT _detected_occ_lib STREQUAL "")
            set(OCC_LIBRARY_DIR "${_detected_occ_lib}" CACHE PATH "Manual OCCT library dir" FORCE)
        endif()
    endif()
endif()

if(OCCT_BIN_DIR STREQUAL "")
    _ifcos_first_existing_dir(_detected_occ_bin
        "${OCCT_ROOT}/win64/vc145/bin"
        "${OCCT_ROOT}/win64/vc143/bin"
        "${OCCT_ROOT}/win64/vc14/bin"
        "${OCCT_ROOT}/bin"
    )
    if(NOT _detected_occ_bin STREQUAL "")
        set(OCCT_BIN_DIR "${_detected_occ_bin}" CACHE PATH "Optional OCCT DLL directory" FORCE)
    endif()
endif()

# nlohmann/json: support either a package config or a plain include folder.
if(NOT NLOHMANN_JSON_ROOT STREQUAL "")
    list(PREPEND CMAKE_PREFIX_PATH "${NLOHMANN_JSON_ROOT}")
    if(NLOHMANN_JSON_INCLUDE_DIR STREQUAL "")
        _ifcos_first_existing_dir(_detected_nlohmann_include
            "${NLOHMANN_JSON_ROOT}/single_include"
            "${NLOHMANN_JSON_ROOT}/include"
            "${NLOHMANN_JSON_ROOT}"
        )
        if(NOT _detected_nlohmann_include STREQUAL "")
            set(NLOHMANN_JSON_INCLUDE_DIR "${_detected_nlohmann_include}" CACHE PATH "Directory containing nlohmann/json.hpp" FORCE)
        endif()
    endif()
endif()

# LibXml2: support either a CMake package or manual include/lib paths.
if(NOT LIBXML2_ROOT STREQUAL "")
    list(PREPEND CMAKE_PREFIX_PATH
        "${LIBXML2_ROOT}"
        "${LIBXML2_ROOT}/lib/cmake/libxml2"
        "${LIBXML2_ROOT}/share/libxml2"
    )
    if(LIBXML2_INCLUDE_DIR STREQUAL "")
        _ifcos_first_existing_dir(_detected_libxml2_include
            "${LIBXML2_ROOT}/include/libxml2"
            "${LIBXML2_ROOT}/include"
        )
        if(NOT _detected_libxml2_include STREQUAL "")
            set(LIBXML2_INCLUDE_DIR "${_detected_libxml2_include}" CACHE PATH "LibXml2 include directory" FORCE)
        endif()
    endif()
    if(LIBXML2_LIBRARY STREQUAL "")
        find_library(_detected_libxml2_library
            NAMES libxml2 xml2
            PATHS "${LIBXML2_ROOT}/lib" "${LIBXML2_ROOT}/lib64"
            NO_DEFAULT_PATH)
        if(_detected_libxml2_library)
            set(LIBXML2_LIBRARY "${_detected_libxml2_library}" CACHE FILEPATH "Path to libxml2.lib" FORCE)
        endif()
    endif()
endif()

# -----------------------------------------------------------------------------
# CMake find shims
# -----------------------------------------------------------------------------
# IfcOpenShell uses find_package(Boost COMPONENTS system program_options regex
# thread date_time iostreams). UE's Boost package uses simplified file names and
# usually does not ship boost_date_time-mt-x64.lib. DateTime is header-only in
# modern Boost, so this shim marks date_time as found without adding a library.
set(_IFCOS_SHIM_DIR "${CMAKE_BINARY_DIR}/ifcos_find_shims")
file(MAKE_DIRECTORY "${_IFCOS_SHIM_DIR}")

set(_IFCOS_FIND_BOOST_CMAKE [==[
include(FindPackageHandleStandardArgs)

set(Boost_VERSION "1.88.0")
set(Boost_VERSION_STRING "1.88.0")
set(Boost_VERSION_MACRO "108800")
set(Boost_MAJOR_VERSION "1")
set(Boost_MINOR_VERSION "88")
set(Boost_SUBMINOR_VERSION "0")
set(Boost_LIB_VERSION "1_88")

set(Boost_INCLUDE_DIR "@UE_BOOST_INCLUDE_DIR@")
set(Boost_INCLUDE_DIRS "${Boost_INCLUDE_DIR}")
set(Boost_LIBRARY_DIR_RELEASE "@UE_BOOST_LIBRARY_DIR@")
set(Boost_LIBRARY_DIRS "${Boost_LIBRARY_DIR_RELEASE}")
set(Boost_LIBRARIES "")

if(NOT EXISTS "${Boost_INCLUDE_DIR}/boost/version.hpp")
    set(Boost_INCLUDE_DIR "Boost_INCLUDE_DIR-NOTFOUND")
    set(Boost_INCLUDE_DIRS "")
    set(Boost_NOT_FOUND_MESSAGE "Boost headers were not found at '@UE_BOOST_INCLUDE_DIR@'.")
endif()

foreach(_boost_component IN LISTS Boost_FIND_COMPONENTS)
    string(TOUPPER "${_boost_component}" _BOOST_COMPONENT_UPPER)

    if(_boost_component STREQUAL "date_time")
        set(Boost_${_boost_component}_FOUND TRUE)
        set(Boost_${_BOOST_COMPONENT_UPPER}_FOUND TRUE)
        set(Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY "")
        if(NOT TARGET Boost::date_time)
            add_library(Boost::date_time INTERFACE IMPORTED)
            target_include_directories(Boost::date_time INTERFACE "${Boost_INCLUDE_DIR}")
        endif()
        continue()
    endif()

    find_library(_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE
        NAMES
            boost_${_boost_component}-mt-x64
            boost_${_boost_component}
        PATHS "${Boost_LIBRARY_DIR_RELEASE}"
        NO_DEFAULT_PATH)

    if(_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE)
        set(Boost_${_boost_component}_FOUND TRUE)
        set(Boost_${_BOOST_COMPONENT_UPPER}_FOUND TRUE)
        set(Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY "${_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE}")
        set(Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE "${_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE}")
        list(APPEND Boost_LIBRARIES "${_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE}")

        if(NOT TARGET Boost::${_boost_component})
            add_library(Boost::${_boost_component} UNKNOWN IMPORTED)
            set_target_properties(Boost::${_boost_component} PROPERTIES
                IMPORTED_LOCATION "${_Boost_${_BOOST_COMPONENT_UPPER}_LIBRARY_RELEASE}"
                INTERFACE_INCLUDE_DIRECTORIES "${Boost_INCLUDE_DIR}")
        endif()
    else()
        set(Boost_${_boost_component}_FOUND FALSE)
        set(Boost_${_BOOST_COMPONENT_UPPER}_FOUND FALSE)
    endif()
endforeach()

if(NOT TARGET Boost::headers)
    add_library(Boost::headers INTERFACE IMPORTED)
    target_include_directories(Boost::headers INTERFACE "${Boost_INCLUDE_DIR}")
endif()

if(NOT TARGET Boost::boost)
    add_library(Boost::boost INTERFACE IMPORTED)
    target_include_directories(Boost::boost INTERFACE "${Boost_INCLUDE_DIR}")
endif()

find_package_handle_standard_args(Boost
    REQUIRED_VARS Boost_INCLUDE_DIR
    VERSION_VAR Boost_VERSION_STRING
    HANDLE_COMPONENTS)
]==])
file(CONFIGURE OUTPUT "${_IFCOS_SHIM_DIR}/FindBoost.cmake" CONTENT "${_IFCOS_FIND_BOOST_CMAKE}" @ONLY)

set(_IFCOS_FIND_NLOHMANN_JSON_CMAKE [==[
include(FindPackageHandleStandardArgs)

# Prefer a real package config if the user supplied one.
if(DEFINED nlohmann_json_DIR AND NOT nlohmann_json_DIR STREQUAL "")
    find_package(nlohmann_json CONFIG QUIET)
    if(TARGET nlohmann_json::nlohmann_json)
        set(nlohmann_json_FOUND TRUE)
        return()
    endif()
endif()

set(NLOHMANN_JSON_INCLUDE_DIR "@NLOHMANN_JSON_INCLUDE_DIR@")
set(_nlohmann_json_include "")

if(EXISTS "${NLOHMANN_JSON_INCLUDE_DIR}/nlohmann/json.hpp")
    set(_nlohmann_json_include "${NLOHMANN_JSON_INCLUDE_DIR}")
elseif(EXISTS "${NLOHMANN_JSON_INCLUDE_DIR}/json.hpp")
    get_filename_component(_nlohmann_json_include "${NLOHMANN_JSON_INCLUDE_DIR}" DIRECTORY)
endif()

if(NOT _nlohmann_json_include STREQUAL "")
    if(NOT TARGET nlohmann_json::nlohmann_json)
        add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED)
        target_include_directories(nlohmann_json::nlohmann_json INTERFACE "${_nlohmann_json_include}")
    endif()
endif()

find_package_handle_standard_args(nlohmann_json REQUIRED_VARS _nlohmann_json_include)
]==])
file(CONFIGURE OUTPUT "${_IFCOS_SHIM_DIR}/Findnlohmann_json.cmake" CONTENT "${_IFCOS_FIND_NLOHMANN_JSON_CMAKE}" @ONLY)

list(PREPEND CMAKE_MODULE_PATH "${_IFCOS_SHIM_DIR}")

# -----------------------------------------------------------------------------
# IfcOpenShell build options
# -----------------------------------------------------------------------------
set(BUILD_SHARED_LIBS ON CACHE BOOL "Build IfcOpenShell libraries as DLLs" FORCE)
set(BUILD_IFCGEOM ON CACHE BOOL "Build IfcGeom" FORCE)
set(WITH_OPENCASCADE ON CACHE BOOL "Use Open CASCADE geometry kernel" FORCE)
set(WITH_CGAL OFF CACHE BOOL "Disable CGAL for smaller UE-oriented build" FORCE)

# Needed because upstream only adds /src/serializers when BUILD_CONVERT or
# BUILD_IFCPYTHON is enabled. Keep this ON for GLB/glTF serializer support.
set(BUILD_CONVERT ON CACHE BOOL "Build IfcConvert so serializers are included" FORCE)
set(GLTF_SUPPORT ON CACHE BOOL "Enable glTF/GLB serializer support" FORCE)
set(IFCXML_SUPPORT ON CACHE BOOL "Enable IFCXML support through LibXml2" FORCE)

set(BUILD_IFCPYTHON OFF CACHE BOOL "Do not build Python wrapper" FORCE)
set(BUILD_GEOMSERVER OFF CACHE BOOL "Do not build geometry server executable" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "Do not build examples" FORCE)
set(BUILD_DOCUMENTATION OFF CACHE BOOL "Do not build documentation" FORCE)
set(BUILD_IFCMAX OFF CACHE BOOL "Do not build 3ds Max plugin" FORCE)
set(BUILD_QTVIEWER OFF CACHE BOOL "Do not build Qt viewer" FORCE)

set(COLLADA_SUPPORT OFF CACHE BOOL "Disable OpenCOLLADA" FORCE)
set(HDF5_SUPPORT OFF CACHE BOOL "Disable HDF5" FORCE)
set(USD_SUPPORT OFF CACHE BOOL "Disable USD" FORCE)
set(WITH_PROJ OFF CACHE BOOL "Disable PROJ" FORCE)
set(WITH_ROCKSDB OFF CACHE BOOL "Disable RocksDB" FORCE)
set(WITH_ZSTD OFF CACHE BOOL "Disable Zstd" FORCE)
set(USE_MMAP OFF CACHE BOOL "Disable Boost.Iostreams mmap parser option" FORCE)
set(MSVC_PARALLEL_BUILD ON CACHE BOOL "Enable /MP in IfcOpenShell" FORCE)
set(BUILD_ONLY_COMMON_SCHEMAS ON CACHE BOOL "Build common IFC schemas only" FORCE)
set(SCHEMA_VERSIONS "2x3;4;4x3_add2" CACHE STRING "IFC schemas to build" FORCE)

# -----------------------------------------------------------------------------
# Add upstream IfcOpenShell CMake project
# -----------------------------------------------------------------------------
if(NOT EXISTS "${IFCOPENSHELL_REPO_ROOT}/cmake/CMakeLists.txt")
    message(FATAL_ERROR "IFCOPENSHELL_REPO_ROOT must point to the IfcOpenShell repository root. Missing: ${IFCOPENSHELL_REPO_ROOT}/cmake/CMakeLists.txt")
endif()

add_subdirectory("${IFCOPENSHELL_REPO_ROOT}/cmake" "${CMAKE_BINARY_DIR}/ifcopenshell")

# -----------------------------------------------------------------------------
# Install runtime dependencies useful for UE ThirdParty packaging
# -----------------------------------------------------------------------------
file(GLOB _UE_BOOST_RUNTIME_DLLS CONFIGURE_DEPENDS "${UE_BOOST_LIBRARY_DIR}/boost_*-mt-x64.dll")
if(_UE_BOOST_RUNTIME_DLLS)
    install(FILES ${_UE_BOOST_RUNTIME_DLLS} DESTINATION bin)
endif()

if(NOT OCCT_BIN_DIR STREQUAL "" AND EXISTS "${OCCT_BIN_DIR}")
    install(DIRECTORY "${OCCT_BIN_DIR}/" DESTINATION bin FILES_MATCHING PATTERN "*.dll")
endif()

if(NOT LIBXML2_DLL STREQUAL "" AND EXISTS "${LIBXML2_DLL}")
    install(FILES "${LIBXML2_DLL}" DESTINATION bin)
endif()

message(STATUS "IfcOpenShell UE build summary:")
message(STATUS "  Repository        : ${IFCOPENSHELL_REPO_ROOT}")
message(STATUS "  Boost include     : ${UE_BOOST_INCLUDE_DIR}")
message(STATUS "  Boost libraries   : ${UE_BOOST_LIBRARY_DIR}")
message(STATUS "  OCCT root         : ${OCCT_ROOT}")
message(STATUS "  OpenCASCADE_DIR   : ${OpenCASCADE_DIR}")
message(STATUS "  OCC_INCLUDE_DIR   : ${OCC_INCLUDE_DIR}")
message(STATUS "  OCC_LIBRARY_DIR   : ${OCC_LIBRARY_DIR}")
message(STATUS "  Eigen dir         : ${EIGEN_DIR}")
message(STATUS "  nlohmann include  : ${NLOHMANN_JSON_INCLUDE_DIR}")
message(STATUS "  LibXml2 include   : ${LIBXML2_INCLUDE_DIR}")
message(STATUS "  LibXml2 library   : ${LIBXML2_LIBRARY}")
message(STATUS "  Install prefix    : ${CMAKE_INSTALL_PREFIX}")
