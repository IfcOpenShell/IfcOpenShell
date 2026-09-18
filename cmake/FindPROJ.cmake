#
# Input variables:
# - `PROJ_INCLUDE_DIR`
# - `PROJ_LIBRARY_DIR`
# If input variables are not specified, try to find PROJ config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `proj::proj`
#

# To avoid cyclic calls to this file
list(REMOVE_ITEM CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})

UNIFY_ENVVARS_AND_CACHE(PROJ_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(PROJ_LIBRARY_DIR)

if(NOT PROJ_INCLUDE_DIR AND NOT PROJ_LIBRARY_DIR)
    find_package(PROJ QUIET CONFIG)
endif()

if(PROJ_FOUND)
    # cmake configs only define `PROJ::proj`.
    # Guarded since find_package(PROJ) is invoked once per serializer plugin,
    # and re-defining the alias on a later call would error out.
    if(NOT TARGET proj::proj)
        add_library(proj::proj ALIAS PROJ::proj)
    endif()
else()
    find_path(PROJ_INCLUDE_DIR proj.h PATHS ${PROJ_INCLUDE_DIR} /usr/include/proj REQUIRED)
    message(STATUS "Found PROJ include files in: ${PROJ_INCLUDE_DIR}")

    find_library(PROJ_LIBRARY NAMES proj PATHS ${PROJ_LIBRARY_DIR} /usr/lib/x86_64-linux-gnu REQUIRED)
    message(STATUS "PROJ libraries ${PROJ_LIBRARY} found in: ${PROJ_LIBRARY_DIR}")
    set(PROJ_LIBRARIES ${PROJ_LIBRARY})

    if(NOT TARGET proj::proj)
        add_library(proj::proj INTERFACE IMPORTED)
        target_include_directories(proj::proj INTERFACE "${PROJ_INCLUDE_DIR}")
        target_link_libraries(proj::proj INTERFACE ${PROJ_LIBRARIES})
        target_link_directories(proj::proj INTERFACE "${PROJ_LIBRARY}")
    endif()
endif()

list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})
