#
# Input variables:
# - `LIBXML2_INCLUDE_DIR`
# - `LIBXML2_LIBRARIES`
# If input variables are not specified, try to find LibXml2 config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `LibXml2::LibXml2`
#

# To avoid cyclic calls to this file
list(REMOVE_ITEM CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})

UNIFY_ENVVARS_AND_CACHE(LIBXML2_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(LIBXML2_LIBRARIES)

if((NOT LIBXML2_INCLUDE_DIR AND NOT LIBXML2_LIBRARIES))
    # First try config mode (probably works with vcpkg, Conan, macOS brew installs, but not on ubuntu 22.04)
    # CONFIG is provided using root path, so no need to clear sysroot here.
    find_package(LibXml2 QUIET CONFIG)

    if(NOT LibXml2_FOUND)
        # Fallback to CMake's builtin FindLibXml2 module (works on Ubuntu)
        find_package(LibXml2 REQUIRED)
    else()
        message(STATUS "Found LibXml2 config: ${LibXml2_DIR}")
    endif()
else()
    find_package(LibXml2 REQUIRED)
    if(MSVC)
        # Unset `IMPORTED_LOCATION` and set it manually.
        set_property(TARGET LibXml2::LibXml2 PROPERTY IMPORTED_LOCATION)
        get_release_variant(LIBXML2_RELEASE_LIB "${LIBXML2_LIBRARIES}" "d")
        get_debug_variant(LIBXML2_DEBUG_LIB "${LIBXML2_LIBRARIES}" "d")
        set_target_properties(
            LibXml2::LibXml2
            PROPERTIES
                IMPORTED_CONFIGURATIONS "Release;Debug"
                IMPORTED_LOCATION_RELEASE "${LIBXML2_RELEASE_LIB}"
                IMPORTED_LOCATION_DEBUG "${LIBXML2_DEBUG_LIB}"
        )
    endif()
endif()

# Restore module path.
list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})
