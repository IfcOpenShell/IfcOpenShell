#
# Input variables:
# - `USD_INCLUDE_DIR`
# - `USD_LIBRARY_DIR`
# Input variables could also be provided as environment variables.
# TODO: Try to find USD config if varibales are not provided.
# TODO: does usd have a config file?
#
# Output variables:
# - `USD_LIBRARIES`

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
