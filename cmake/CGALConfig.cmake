
if(NOT CGAL_INCLUDE_DIR)
    # CGAL is not respecting default Boost_USE_STATIC_LIBS value
    # and sometiems it's getting in the way.
    if(NOT DEFINED Boost_USE_STATIC_LIBS)
        set(CGAL_Boost_USE_STATIC_LIBS OFF)
    else()
        set(CGAL_Boost_USE_STATIC_LIBS "${Boost_USE_STATIC_LIBS}")
    endif()
    find_package(CGAL REQUIRED)
    if(NOT CGAL_DIR)
        message(
            FATAL_ERROR
            "CGAL_SUPPORT enabled, but CGAL_INCLUDE_DIR wasn't provided and CGAL package couldn't be found."
        )
    endif()
    message(STATUS "CGAL: found config at '${CGAL_DIR}'.")
    link_libraries(CGAL::CGAL)

    if(WITH_CGAL AND CGAL_DIR)
        set(CGAL_LIBRARIES CGAL::CGAL)
        message(STATUS "Using found CGAL package at '${CGAL_DIR}'")
    elseif(WITH_CGAL AND NOT CGAL_DIR)
        clear_wasm_sysroot()
        find_library(libGMP NAMES gmp mpir PATHS ${GMP_LIBRARY_DIR} NO_DEFAULT_PATH)
        find_library(libMPFR NAMES mpfr PATHS ${MPFR_LIBRARY_DIR} NO_DEFAULT_PATH)
        restore_wasm_sysroot()
        if(NOT libGMP)
            message(FATAL_ERROR "Unable to find GMP library files, aborting")
        endif()
        if(NOT libMPFR)
            message(FATAL_ERROR "Unable to find MPFR library files, aborting")
        endif()

        list(APPEND CGAL_LIBRARIES "${libMPFR}")
        list(APPEND CGAL_LIBRARIES "${libGMP}")
    endif()
