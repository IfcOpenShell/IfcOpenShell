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
# Output targets:
# - `CGAL::CGAL`
#

if(TARGET CGAL::CGAL)
    return()
endif()

UNIFY_ENVVARS_AND_CACHE(CGAL_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(CGAL_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(GMP_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(MPFR_LIBRARY_DIR)

if(CGAL_INCLUDE_DIR)
    find_library(libGMP NAMES gmp mpir PATHS ${GMP_LIBRARY_DIR} NO_DEFAULT_PATH)
    find_library(libMPFR NAMES mpfr PATHS ${MPFR_LIBRARY_DIR} NO_DEFAULT_PATH)
    if(NOT libGMP)
        message(FATAL_ERROR "Unable to find GMP library files, aborting")
    endif()
    if(NOT libMPFR)
        message(FATAL_ERROR "Unable to find MPFR library files, aborting")
    endif()

    add_library(CGAL::CGAL INTERFACE IMPORTED)
    target_include_directories(CGAL::CGAL INTERFACE "${CGAL_INCLUDE_DIR}")
    target_include_directories(CGAL::CGAL INTERFACE "${GMP_INCLUDE_DIR}" "${MPFR_INCLUDE_DIR}")
    target_link_libraries(CGAL::CGAL INTERFACE "${libMPFR}" "${libGMP}")
else()
    # CGAL is not respecting default Boost_USE_STATIC_LIBS value
    # and sometiems it's getting in the way.
    if(NOT DEFINED Boost_USE_STATIC_LIBS)
        set(CGAL_Boost_USE_STATIC_LIBS OFF)
    else()
        set(CGAL_Boost_USE_STATIC_LIBS "${Boost_USE_STATIC_LIBS}")
    endif()
    find_package(CGAL CONFIG)
    if(NOT CGAL::CGAL)
        message(
            FATAL_ERROR
            "CGAL_SUPPORT enabled, but CGAL_INCLUDE_DIR wasn't provided and CGAL package couldn't be found."
        )
    endif()
    message(STATUS "CGAL: found config at '${CGAL_DIR}'.")
endif()

target_compile_definitions(CGAL::CGAL INTERFACE IFOPSH_WITH_CGAL)
set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_CGAL)
