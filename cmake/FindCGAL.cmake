#
# Input variables:
# - `CGAL_INCLUDE_DIR`
# - `CGAL_LIBRARY_DIR`
# - `GMP_INCLUDE_DIR`
# - `GMP_LIBRARY_DIR`
# - `MPFR_INCLUDE_DIR`
# - `MPFR_LIBRARY_DIR`
# If input variables are not specified, try to find HDF5 config.
# Input variables could also be provided as environment variables.
#
# Output variables:
# - `CGAL_INCLUDE_DIR`
#

UNIFY_ENVVARS_AND_CACHE(CGAL_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(CGAL_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_LIBRARY_DIR)

if(NOT CGAL_INCLUDE_DIR)
    # CGAL is not respecting default Boost_USE_STATIC_LIBS value
    # and sometiems it's getting in the way.
    if(NOT DEFINED Boost_USE_STATIC_LIBS)
        set(CGAL_Boost_USE_STATIC_LIBS OFF)
    else()
        set(CGAL_Boost_USE_STATIC_LIBS "${Boost_USE_STATIC_LIBS}")
    endif()
    find_package(CGAL CONFIG REQUIRED)
    if(NOT CGAL_DIR)
        message(
            FATAL_ERROR
            "CGAL_SUPPORT enabled, but CGAL_INCLUDE_DIR wasn't provided and CGAL package couldn't be found."
        )
    endif()
    message(STATUS "CGAL: found config at '${CGAL_DIR}'.")
endif()

add_definitions(-DIFOPSH_WITH_CGAL)
set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_CGAL)
