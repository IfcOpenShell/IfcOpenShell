#
# Input variables:
# - `LIBXML2_INCLUDE_DIR`
# - `LIBXML2_LIBRARIES`
# If input variables are not specified, try to find LibXml2 config.
# Input variables could also be provided as environment variables.
#
# Output variables:
# - `LIBXML2_INCLUDE_DIR`
# - `LIBXML2_LIBRARIES`
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

    if(TARGET LibXml2::LibXml2)
        # Config mode already gives us the target
        set(LIBXML2_LIBRARIES LibXml2::LibXml2)
        get_target_property(LIBXML2_INCLUDE_DIR LibXml2::LibXml2 INTERFACE_INCLUDE_DIRECTORIES)
    else()
        # Module mode (Ubuntu)
        set(LIBXML2_LIBRARIES ${LibXml2_LIBRARIES})
        set(LIBXML2_INCLUDE_DIR ${LibXml2_INCLUDE_DIRS})
    endif()
else()
    find_package(LibXml2 REQUIRED)
endif()

if(MSVC AND NOT LibXml2_DIR)
    add_debug_variants(LIBXML2_LIBRARIES "${LIBXML2_LIBRARIES}" d)
endif()

# Restore module path.
list(PREPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR})
