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
endif()

