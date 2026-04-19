#
# Input variables:
# - `PROJ_INCLUDE_DIR`
# - `PROJ_LIBRARIES`
# If input variables are not specified, try to find PROJ config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `proj::proj`
#

# To avoid cyclic calls to this file
list(REMOVE_ITEM CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})

UNIFY_ENVVARS_AND_CACHE(PROJ_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(PROJ_LIBRARIES)

if((NOT PROJ_INCLUDE_DIR AND NOT PROJ_LIBRARIES))
    find_package(PROJ QUIET CONFIG)

    if(NOT PROJ_FOUND)
        find_path(PROJ_INCLUDE_DIR proj.h PATHS /usr/include/proj REQUIRED)
        if(PROJ_INCLUDE_DIR)
            message(STATUS "Found PROJ include files in: ${PROJ_INCLUDE_DIR}")
        else()
            message(FATAL_ERROR "Unable to find PROJ include directory, specify PROJ_INCLUDE_DIR manually.")
        endif()

        find_library(PROJ_LIBRARY NAMES proj PATHS /usr/lib/x86_64-linux-gnu)
        if(PROJ_LIBRARY)
            message(STATUS "PROJ libraries ${PROJ_LIBRARY} found in: ${PROJ_LIBRARY_DIR}")
            set(PROJ_LIBRARIES ${PROJ_LIBRARY})
        else()
            message(FATAL_ERROR "Unable to find PROJ libraries in: ${PROJ_LIBRARY_DIR}")
        endif()

        if(NOT TARGET proj::proj)
            add_library(proj::proj INTERFACE IMPORTED)
            target_include_directories(proj::proj INTERFACE "${PROJ_INCLUDE_DIR}")
            target_link_libraries(proj::proj INTERFACE ${PROJ_LIBRARIES})
            target_link_directories(proj::proj INTERFACE "${PROJ_LIBRARY}")
        endif()
    endif()
else()
    find_library(PROJ_LIBRARY NAMES proj PATHS ${PROJ_LIBRARY_DIR})
    if(PROJ_LIBRARY)
        message(STATUS "PROJ libraries ${PROJ_LIBRARY} found in: ${PROJ_LIBRARY_DIR}")
        set(PROJ_LIBRARIES ${PROJ_LIBRARY})
    else()
        message(FATAL_ERROR "Unable to find PROJ libraries in: ${PROJ_LIBRARY_DIR}")
    endif()

    set(PROJ_INCLUDE_DIR ${PROJ_INCLUDE_DIR} CACHE FILEPATH "PROJ header files")
    message(STATUS "Looking for PROJ include files in: ${PROJ_INCLUDE_DIR}")
    if(NOT TARGET proj::proj)
        add_library(proj::proj INTERFACE IMPORTED)
        target_include_directories(proj::proj INTERFACE "${PROJ_INCLUDE_DIR}")
        target_link_libraries(proj::proj INTERFACE ${PROJ_LIBRARIES})
    endif()
endif()

list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})
