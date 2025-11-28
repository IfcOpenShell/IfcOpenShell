#
# Input variables:
# - `HDF5_INCLUDE_DIR`
# - `HDF5_LIBRARY_DIR`
# - `HDF5_LIBRARIES`
# If input variables are not specified, try to find HDF5 config.
# Input variables could also be provided as environment variables.
#
# Output variables:
# - `HDF5_INCLUDE_DIR`
# - `HDF5_LIBRARY_DIR`
# - `HDF5_LIBRARIES`
#

UNIFY_ENVVARS_AND_CACHE(HDF5_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(HDF5_LIBRARIES)

# To avoid cyclic calls to this file
list(REMOVE_ITEM CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})

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

if(NOT HDF5_INCLUDE_DIR OR NOT HDF5_LIBRARY_DIR)
    # First try to find it as a config.
    find_package(HDF5 CONFIG)
    if(HDF5_DIR)
        message(STATUS "HDF5: found config at '${HDF5_DIR}'.")
        set(HDF5_LIBRARIES hdf5_cpp-static)
    else()
        # If it failed, still try to find as a module.
        # E.g. on Ubuntu `libhdf5-dev` doesn't provie hdf5-config.cmake.
        # Will automatically fill HDF5_LIBRARIES and HDF5_INCLUDE_DIR.
        find_package(HDF5 COMPONENTS CXX)
        if(NOT HDF5_INCLUDE_DIR)
            message(
                FATAL_ERROR
                "HDF5_INCLUDE_DIR is not provided (current value: '${HDF5_INCLUDE_DIR}'). "
                "HDF5_LIBRARY_DIR is not provided (current value: '${HDF5_LIBRARY_DIR}'). "
                "Also could not find HDF5 package (neither module or config)."
            )
        endif()
    endif()
endif()

# Restore module path.
list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})
