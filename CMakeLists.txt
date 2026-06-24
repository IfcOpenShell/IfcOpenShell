# Root-level CMakeLists.txt for building IfcOpenShell for UE 5.8 on Windows x64.
# Place this file in the root of a cloned IfcOpenShell repository, next to /cmake and /src.
#
# IMPORTANT CHANGE vs. the previous revision:
#   IfcOpenShell is now built as STATIC libraries (BUILD_SHARED_LIBS OFF).
#
#   Building IfcOpenShell *itself* as DLLs on MSVC does not work without patching
#   upstream sources, because several symbols that cross the DLL boundary are not
#   decorated for export:
#     * data symbols  -> taxonomy::item::counter_ (static std::atomic),
#                        IFCOPENSHELL_VERSION (global const char*)
#     * inline funcs  -> matrix4 / eigen_base / style helpers get both exported
#                        and locally emitted -> LNK2005 "already defined".
#   __declspec(dllexport) is simply absent on these, and CMake's
#   WINDOWS_EXPORT_ALL_SYMBOLS deliberately skips DATA symbols, so it cannot fix
#   counter_ / IFCOPENSHELL_VERSION. Static linkage makes IFC_PARSE_API expand to
#   nothing (see ifc_parse_api.h) and every symbol resolves at the final UE link.
#
#   This does NOT affect OCCT: OCCT remains a dynamic (DLL) dependency found via
#   its imported targets. "Static IfcOpenShell + dynamic OCCT" is the intended
#   layout for a UE ThirdParty module.
#
#   For UE: point your module's PublicAdditionalLibraries at the .lib files in
#   <build>/lib/<Config>/, add the IfcParse/IfcGeom/serializer include dirs, and
#   stage OCCT + Boost + libxml2 DLLs as RuntimeDependencies.

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
    # UE Windows builds use the DLL CRT. Build the static libs the same way so the
    # CRT/ABI matches UE and the dynamic OCCT build (both expected to be /MD).
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
        # BOOST_ALL_NO_LIB is critical: it disables MSVC auto-link #pragmas so the
        # build never tries to pull in boost_*.lib by guessed name. We control
        # exactly which Boost libs are linked via the FindBoost shim below.
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
    # Static .lib archives land here -> this is what UE links against.
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${_cfg_upper} "${CMAKE_BINARY_DIR}/lib/${_cfg}" CACHE PATH "" FORCE)
endforeach()

# -----------------------------------------------------------------------------
# User paths  (these are the four knobs you asked to "point": occt, boost,
#              eigen, nlohmann_json -- plus libxml2 for IFCXML)
# -----------------------------------------------------------------------------
set(IFCOPENSHELL_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "IfcOpenShell repository root")

# --- Boost (UE-shipped) ------------------------------------------------------
set(UE_BOOST_INCLUDE_DIR
    "D:/Editors/Epic/Binaries/UE_5.8/Engine/Source/ThirdParty/Boost/Deploy/boost-1.88.0/include"
    CACHE PATH "UE 5.8 Boost include directory")

set(UE_BOOST_LIBRARY_DIR
    "D:/Editors/Epic/Binaries/UE_5.8/Engine/Source/ThirdParty/Boost/Deploy/boost-1.88.0/VS2015/x64/lib"
    CACHE PATH "UE 5.8 Boost import library / DLL directory")

# Optional: a compiled boost_program_options .lib. ONLY needed if you flip
# IFCOS_BUILD_IFCCONVERT_EXE ON (UE's Boost does not ship program_options).
set(BOOST_PROGRAM_OPTIONS_LIBRARY "" CACHE FILEPATH
    "Path to a compiled boost_program_options .lib (only required to build IfcConvert.exe)")

# --- OCCT (dynamic) ----------------------------------------------------------
set(OCCT_ROOT "C:/Program Files/OCCT" CACHE PATH "Open CASCADE installation root")
set(OpenCASCADE_DIR "" CACHE PATH "Directory containing OpenCASCADEConfig.cmake, if available")
set(OCC_INCLUDE_DIR "" CACHE PATH "Manual OCCT include dir, e.g. C:/Program Files/OCCT/inc")
set(OCC_LIBRARY_DIR "" CACHE PATH "Manual OCCT import-library dir, e.g. C:/Program Files/OCCT/win64/vc14/lib")
set(OCCT_BIN_DIR "" CACHE PATH "OCCT DLL directory to stage during install")

# --- Eigen -------------------------------------------------------------------
set(EIGEN_DIR "" CACHE PATH "Eigen include root, e.g. D:/ThirdParty/eigen-3.4.0 (contains Eigen/Dense)")
set(Eigen3_DIR "" CACHE PATH "Optional Eigen3 CMake package config directory (Eigen3Config.cmake)")

# --- nlohmann/json -----------------------------------------------------------
set(NLOHMANN_JSON_ROOT "" CACHE PATH "Optional nlohmann/json root")
set(NLOHMANN_JSON_INCLUDE_DIR "" CACHE PATH "Directory containing nlohmann/json.hpp, e.g. D:/ThirdParty/json/single_include")
set(nlohmann_json_DIR "" CACHE PATH "Optional nlohmann_json CMake package config directory")

# --- LibXml2 (for IFCXML) ----------------------------------------------------
set(LIBXML2_ROOT "" CACHE PATH "Optional LibXml2 root")
set(LibXml2_DIR "" CACHE PATH "Optional LibXml2 CMake package config directory")
set(LIBXML2_INCLUDE_DIR "" CACHE PATH "LibXml2 include directory, usually <root>/include/libxml2")
set(LIBXML2_LIBRARY "" CACHE FILEPATH "Path to libxml2.lib")
set(LIBXML2_DLL "" CACHE FILEPATH "Optional path to libxml2.dll to stage during install")

# --- Build-shape options -----------------------------------------------------
# Escape hatch only. Leaving this OFF is what fixes the LNK2001/LNK2005/LNK1120
# errors. Turning it ON re-introduces them unless you patch upstream export macros.
option(IFCOS_BUILD_SHARED "Build IfcOpenShell as DLLs (requires source patches; NOT recommended)" OFF)

# IfcConvert.exe needs boost::program_options, which UE's Boost does not ship.
# The Serializers library is built regardless (it does NOT need program_options);
# only the CLI executable does, so it is excluded from the default build by default.
option(IFCOS_BUILD_IFCCONVERT_EXE "Also build the IfcConvert.exe CLI (needs BOOST_PROGRAM_OPTIONS_LIBRARY)" OFF)

# Upstream's ifcconvert/CMakeLists.txt does:
#     install(TARGETS IfcConvert EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})   # no OPTIONAL
# When the exe is excluded from the build (above), the INSTALL target still tries to
# copy a non-existent IfcConvert.exe and fails (MSB3073 / "file INSTALL cannot find").
# This adds OPTIONAL to that one rule so INSTALL skips the missing exe. Idempotent;
# only touches the file when the exe is excluded and OPTIONAL is not already present.
option(IFCOS_PATCH_IFCCONVERT_INSTALL "Add OPTIONAL to the IfcConvert install rule when the exe is excluded" ON)

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

# Eigen: if only EIGEN_DIR is given, try to locate the include root that holds Eigen/Dense.
if(EIGEN_DIR STREQUAL "" AND NOT Eigen3_DIR STREQUAL "")
    # A config dir was provided; leave EIGEN_DIR empty and let CONFIG mode handle it.
elseif(NOT EIGEN_DIR STREQUAL "" AND NOT EXISTS "${EIGEN_DIR}/Eigen/Dense")
    _ifcos_first_existing_dir(_detected_eigen_inc
        "${EIGEN_DIR}/include/eigen3"
        "${EIGEN_DIR}/include"
        "${EIGEN_DIR}/eigen3"
    )
    if(NOT _detected_eigen_inc STREQUAL "" AND EXISTS "${_detected_eigen_inc}/Eigen/Dense")
        set(EIGEN_DIR "${_detected_eigen_inc}" CACHE PATH "Eigen include root" FORCE)
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
# IfcOpenShell calls find_package(Boost REQUIRED COMPONENTS system program_options
# regex thread date_time iostreams) and find_package(Eigen3 REQUIRED). UE's Boost
# uses simplified file names, ships date_time header-only, and does NOT ship a
# compiled program_options. These shims bridge that so configuration succeeds.
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
set(_IFCOS_BOOST_PROGRAM_OPTIONS_LIB "@BOOST_PROGRAM_OPTIONS_LIBRARY@")

if(NOT EXISTS "${Boost_INCLUDE_DIR}/boost/version.hpp")
    set(Boost_INCLUDE_DIR "Boost_INCLUDE_DIR-NOTFOUND")
    set(Boost_INCLUDE_DIRS "")
    set(Boost_NOT_FOUND_MESSAGE "Boost headers were not found at '@UE_BOOST_INCLUDE_DIR@'.")
endif()

# Helper: create a header-only INTERFACE imported target for a component that
# UE ships header-only (or that we intentionally do not link).
function(_ifcos_boost_header_only_component _component)
    string(TOUPPER "${_component}" _COMPONENT_UPPER)
    set(Boost_${_component}_FOUND TRUE PARENT_SCOPE)
    set(Boost_${_COMPONENT_UPPER}_FOUND TRUE PARENT_SCOPE)
    set(Boost_${_COMPONENT_UPPER}_LIBRARY "" PARENT_SCOPE)
    if(NOT TARGET Boost::${_component})
        add_library(Boost::${_component} INTERFACE IMPORTED)
        target_include_directories(Boost::${_component} INTERFACE "${Boost_INCLUDE_DIR}")
    endif()
endfunction()

foreach(_boost_component IN LISTS Boost_FIND_COMPONENTS)
    string(TOUPPER "${_boost_component}" _BOOST_COMPONENT_UPPER)

    # date_time is header-only in modern Boost; UE does not ship the .lib.
    if(_boost_component STREQUAL "date_time")
        _ifcos_boost_header_only_component("date_time")
        continue()
    endif()

    # program_options: prefer a real compiled lib if the user supplied one,
    # otherwise fall back to a header-only interface so configure passes. The
    # only consumer of its *compiled* symbols is IfcConvert.exe, which is
    # excluded from the default build (see IFCOS_BUILD_IFCCONVERT_EXE).
    if(_boost_component STREQUAL "program_options")
        set(_po_lib "")
        if(NOT _IFCOS_BOOST_PROGRAM_OPTIONS_LIB STREQUAL "" AND EXISTS "${_IFCOS_BOOST_PROGRAM_OPTIONS_LIB}")
            set(_po_lib "${_IFCOS_BOOST_PROGRAM_OPTIONS_LIB}")
        else()
            find_library(_Boost_PROGRAM_OPTIONS_LIBRARY_RELEASE
                NAMES boost_program_options-mt-x64 boost_program_options
                PATHS "${Boost_LIBRARY_DIR_RELEASE}" NO_DEFAULT_PATH)
            if(_Boost_PROGRAM_OPTIONS_LIBRARY_RELEASE)
                set(_po_lib "${_Boost_PROGRAM_OPTIONS_LIBRARY_RELEASE}")
            endif()
        endif()

        if(NOT _po_lib STREQUAL "")
            set(Boost_program_options_FOUND TRUE)
            set(Boost_PROGRAM_OPTIONS_FOUND TRUE)
            set(Boost_PROGRAM_OPTIONS_LIBRARY "${_po_lib}")
            list(APPEND Boost_LIBRARIES "${_po_lib}")
            if(NOT TARGET Boost::program_options)
                add_library(Boost::program_options UNKNOWN IMPORTED)
                set_target_properties(Boost::program_options PROPERTIES
                    IMPORTED_LOCATION "${_po_lib}"
                    INTERFACE_INCLUDE_DIRECTORIES "${Boost_INCLUDE_DIR}")
            endif()
        else()
            # No compiled lib -> header-only stand-in. Safe because we don't link the exe.
            _ifcos_boost_header_only_component("program_options")
        endif()
        continue()
    endif()

    # All remaining components (system, regex, thread, iostreams, filesystem...)
    # must resolve to a real compiled lib.
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

# Eigen3 shim: upstream calls find_package(Eigen3 REQUIRED) and links Eigen3::Eigen.
# This lets you "point Eigen" with a plain header dir (EIGEN_DIR). A real
# Eigen3Config.cmake (via Eigen3_DIR) is preferred when available.
set(_IFCOS_FIND_EIGEN3_CMAKE [==[
include(FindPackageHandleStandardArgs)

# Prefer a real config package if one was provided.
if(DEFINED Eigen3_DIR AND NOT Eigen3_DIR STREQUAL "")
    find_package(Eigen3 CONFIG QUIET)
    if(TARGET Eigen3::Eigen)
        set(Eigen3_FOUND TRUE)
        return()
    endif()
endif()

set(_eigen_hint "@EIGEN_DIR@")
set(EIGEN3_INCLUDE_DIR "")

if(EXISTS "${_eigen_hint}/Eigen/Dense")
    set(EIGEN3_INCLUDE_DIR "${_eigen_hint}")
elseif(EXISTS "${_eigen_hint}/include/eigen3/Eigen/Dense")
    set(EIGEN3_INCLUDE_DIR "${_eigen_hint}/include/eigen3")
endif()

if(NOT EIGEN3_INCLUDE_DIR STREQUAL "")
    set(EIGEN3_INCLUDE_DIRS "${EIGEN3_INCLUDE_DIR}")
    set(EIGEN3_VERSION_STRING "3.4.0")
    if(NOT TARGET Eigen3::Eigen)
        add_library(Eigen3::Eigen INTERFACE IMPORTED)
        set_target_properties(Eigen3::Eigen PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${EIGEN3_INCLUDE_DIR}")
    endif()
endif()

find_package_handle_standard_args(Eigen3
    REQUIRED_VARS EIGEN3_INCLUDE_DIR
    VERSION_VAR EIGEN3_VERSION_STRING)
]==])
file(CONFIGURE OUTPUT "${_IFCOS_SHIM_DIR}/FindEigen3.cmake" CONTENT "${_IFCOS_FIND_EIGEN3_CMAKE}" @ONLY)

list(PREPEND CMAKE_MODULE_PATH "${_IFCOS_SHIM_DIR}")

# Safety net: also put Eigen on the global include path so any TU that includes
# Eigen headers directly (without going through the target) still compiles.
if(NOT EIGEN_DIR STREQUAL "" AND EXISTS "${EIGEN_DIR}/Eigen/Dense")
    include_directories(SYSTEM "${EIGEN_DIR}")
endif()

# -----------------------------------------------------------------------------
# IfcOpenShell build options
# -----------------------------------------------------------------------------
# Static libs are the fix for the LNK2001/LNK2005/LNK1120 errors (see header).
set(BUILD_SHARED_LIBS ${IFCOS_BUILD_SHARED} CACHE BOOL "Build IfcOpenShell libraries as DLLs" FORCE)
if(IFCOS_BUILD_SHARED)
    message(WARNING
        "IFCOS_BUILD_SHARED=ON: IfcOpenShell will be built as DLLs. Upstream does not "
        "export several data symbols (taxonomy::item::counter_, IFCOPENSHELL_VERSION) "
        "nor consistently decorate inline taxonomy helpers, so expect LNK2001/LNK2005 "
        "unless you patch the sources. OFF (static) is recommended for UE.")
endif()

set(BUILD_IFCGEOM ON CACHE BOOL "Build IfcGeom" FORCE)
set(WITH_OPENCASCADE ON CACHE BOOL "Use Open CASCADE geometry kernel" FORCE)
set(WITH_CGAL OFF CACHE BOOL "Disable CGAL for smaller UE-oriented build" FORCE)

# Upstream only adds /src/serializers when BUILD_CONVERT or BUILD_IFCPYTHON is on.
# Keep BUILD_CONVERT ON for GLB/glTF serializer support; the IfcConvert.exe target
# it also pulls in is excluded from the default build below.
set(BUILD_CONVERT ON CACHE BOOL "Build serializers (and, unless excluded, IfcConvert)" FORCE)
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

# Make the IfcConvert install rule OPTIONAL when we are not building the exe, so the
# INSTALL target does not fail trying to copy a binary that was never produced. This
# edits your fork's source once, before add_subdirectory reads it, and is a no-op if
# OPTIONAL is already present or if you opted to build the exe.
if(IFCOS_PATCH_IFCCONVERT_INSTALL AND NOT IFCOS_BUILD_IFCCONVERT_EXE)
    set(_ifcconvert_cml "${IFCOPENSHELL_REPO_ROOT}/src/ifcconvert/CMakeLists.txt")
    if(EXISTS "${_ifcconvert_cml}")
        file(READ "${_ifcconvert_cml}" _ifcconvert_src)
        # \$ keeps ${IFCOPENSHELL_EXPORT_TARGETS} literal (it is not defined in this scope).
        string(FIND "${_ifcconvert_src}"
            "install(TARGETS IfcConvert EXPORT \${IFCOPENSHELL_EXPORT_TARGETS} OPTIONAL)"
            _ifcconvert_already_optional)
        if(_ifcconvert_already_optional EQUAL -1)
            string(REPLACE
                "install(TARGETS IfcConvert EXPORT \${IFCOPENSHELL_EXPORT_TARGETS})"
                "install(TARGETS IfcConvert EXPORT \${IFCOPENSHELL_EXPORT_TARGETS} OPTIONAL)"
                _ifcconvert_patched "${_ifcconvert_src}")
            if(NOT _ifcconvert_patched STREQUAL _ifcconvert_src)
                file(WRITE "${_ifcconvert_cml}" "${_ifcconvert_patched}")
                message(STATUS "Patched ifcconvert/CMakeLists.txt: IfcConvert install rule is now OPTIONAL.")
            else()
                message(WARNING
                    "Could not auto-patch the IfcConvert install rule (line not found as expected). "
                    "If INSTALL fails on a missing IfcConvert.exe, add OPTIONAL to the "
                    "install(TARGETS IfcConvert ...) line in src/ifcconvert/CMakeLists.txt manually.")
            endif()
        endif()
    endif()
endif()

add_subdirectory("${IFCOPENSHELL_REPO_ROOT}/cmake" "${CMAKE_BINARY_DIR}/ifcopenshell")

# -----------------------------------------------------------------------------
# Exclude / wire the IfcConvert.exe target
# -----------------------------------------------------------------------------
# The serializers library is built (BUILD_CONVERT pulled it in) and does NOT need
# boost::program_options. The IfcConvert.exe target does, and UE's Boost lacks it,
# which is the source of the program_options LNK2019s. By default we keep the
# library and drop the exe.
if(TARGET IfcConvert)
    if(NOT IFCOS_BUILD_IFCCONVERT_EXE)
        set_target_properties(IfcConvert PROPERTIES
            EXCLUDE_FROM_ALL ON
            EXCLUDE_FROM_DEFAULT_BUILD ON)
        message(STATUS "IfcConvert.exe excluded from build (serializers library still built).")
        message(STATUS "  -> Set IFCOS_BUILD_IFCCONVERT_EXE=ON and BOOST_PROGRAM_OPTIONS_LIBRARY to build the CLI.")
    else()
        if(BOOST_PROGRAM_OPTIONS_LIBRARY STREQUAL "" OR NOT EXISTS "${BOOST_PROGRAM_OPTIONS_LIBRARY}")
            message(WARNING
                "IFCOS_BUILD_IFCCONVERT_EXE=ON but BOOST_PROGRAM_OPTIONS_LIBRARY is unset/invalid. "
                "IfcConvert.exe will fail to link (unresolved boost::program_options symbols) "
                "because UE's Boost does not ship a compiled program_options library.")
        else()
            target_link_libraries(IfcConvert PRIVATE "${BOOST_PROGRAM_OPTIONS_LIBRARY}")
        endif()
    endif()
endif()

# -----------------------------------------------------------------------------
# Stage runtime DLLs useful for UE ThirdParty packaging
# -----------------------------------------------------------------------------
# IfcOpenShell is now static, so there are no IfcOpenShell DLLs to ship. You still
# need the dynamic dependencies (OCCT, Boost, libxml2) at runtime next to UE.
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
message(STATUS "  Repository          : ${IFCOPENSHELL_REPO_ROOT}")
message(STATUS "  Link mode           : (IfcOpenShell) ${BUILD_SHARED_LIBS} shared  |  OCCT dynamic")
message(STATUS "  Static .libs output : ${CMAKE_BINARY_DIR}/lib/<Config>")
message(STATUS "  Boost include       : ${UE_BOOST_INCLUDE_DIR}")
message(STATUS "  Boost libraries     : ${UE_BOOST_LIBRARY_DIR}")
message(STATUS "  program_options lib : ${BOOST_PROGRAM_OPTIONS_LIBRARY}")
message(STATUS "  Build IfcConvert.exe: ${IFCOS_BUILD_IFCCONVERT_EXE}")
message(STATUS "  OCCT root           : ${OCCT_ROOT}")
message(STATUS "  OpenCASCADE_DIR     : ${OpenCASCADE_DIR}")
message(STATUS "  OCC_INCLUDE_DIR     : ${OCC_INCLUDE_DIR}")
message(STATUS "  OCC_LIBRARY_DIR     : ${OCC_LIBRARY_DIR}")
message(STATUS "  Eigen dir           : ${EIGEN_DIR}")
message(STATUS "  nlohmann include    : ${NLOHMANN_JSON_INCLUDE_DIR}")
message(STATUS "  LibXml2 include     : ${LIBXML2_INCLUDE_DIR}")
message(STATUS "  LibXml2 library     : ${LIBXML2_LIBRARY}")
message(STATUS "  Install prefix      : ${CMAKE_INSTALL_PREFIX}")