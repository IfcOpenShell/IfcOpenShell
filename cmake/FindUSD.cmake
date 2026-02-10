#
# Input variables:
# - `USD_INCLUDE_DIR`
# - `USD_LIBRARY_DIR`
# - `TBB_INCLUDE_DIR`
# - `TBB_LIBRARY_DIR`
# Input variables could also be provided as environment variables.
# If `USD_INCLUDE_DIR` and `USD_LIBRARY_DIR` are not provided,
# try to find USD by locating its config file.
#
# Output targets:
# - `pxr::USD`

UNIFY_ENVVARS_AND_CACHE(USD_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(USD_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(TBB_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(TBB_LIBRARY_DIR)

if(NOT USD_LIBRARY_DIR AND NOT USD_INCLUDE_DIR)
    find_package(pxr CONFIG)
    if(pxr_FOUND)
        add_library(pxr::USD INTERFACE IMPORTED)
        target_link_libraries(pxr::USD INTERFACE ${PXR_LIBRARIES})
        include(FindPackageHandleStandardArgs)
        find_package_handle_standard_args(USD REQUIRED_VARS pxr_DIR)
        return()
    endif()
endif()

if(NOT USD_INCLUDE_DIR)
    find_path(USD_INCLUDE_DIR pxr.h PATHS /usr/include/pxr /usr/local/include/pxr REQUIRED)
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
    usd_kind
    usd_pcp
    usd_arch
    usd_ar
    usd_plug
    usd_js
    usd_sdr
    usd_work
    usd_trace
    usd_ndr
    usd_ts
)

find_library(USD_LIBRARY NAMES ${USD_LIBRARIES} PATHS ${USD_LIBRARY_DIR})
if(USD_LIBRARY)
    message(STATUS "USD libraries ${USD_LIBRARIES} found in: ${USD_LIBRARY_DIR}")
    link_directories(${USD_LIBRARY_DIR})
else()
    message(FATAL_ERROR "Unable to find USD libraries in: ${USD_LIBRARY_DIR}")
endif()

add_library(pxr::USD INTERFACE IMPORTED)
target_link_directories(pxr::USD INTERFACE ${USD_LIBRARY_DIR} ${TBB_LIBRARY_DIR})
target_include_directories(pxr::USD INTERFACE ${USD_INCLUDE_DIR} ${TBB_INCLUDE_DIR})

# We don't link TBB libraries - on Windows they're provided using `pragma(lib)`.
# On Unix there's no `pragma(lib)`, so in theory it will break.
target_link_libraries(pxr::USD INTERFACE ${USD_LIBRARIES})

if(MSVC)
    target_link_libraries(pxr::USD INTERFACE debug DbgHelp.lib)
endif()

target_compile_definitions(pxr::USD INTERFACE PXR_STATIC WITH_USD)

set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_USD)
