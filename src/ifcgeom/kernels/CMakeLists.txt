foreach(kernel ${GEOMETRY_KERNELS})
    string(TOUPPER ${kernel} KERNEL_UPPER)
    file(GLOB IFCGEOM_H_FILES ${kernel}/*.h)
    file(GLOB IFCGEOM_CPP_FILES ${kernel}/*.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

    add_library(geometry_kernel_${kernel} OBJECT ${IFCGEOM_FILES})
    set_property(TARGET geometry_kernel_${kernel} APPEND PROPERTY COMPILE_FLAGS "-DIFC_GEOM_EXPORTS")
    list(APPEND kernel_libraries geometry_kernel_${kernel})
    target_link_libraries(geometry_kernel_${kernel} ${${KERNEL_UPPER}_LIBRARIES})

    install(TARGETS geometry_kernel_${kernel}
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
    )

    if(${kernel} STREQUAL "cgal")
        set_property(TARGET geometry_kernel_${kernel} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

        add_library(geometry_kernel_${kernel}_simple OBJECT ${IFCGEOM_FILES})
        set_target_properties(geometry_kernel_${kernel}_simple PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS")
        list(APPEND kernel_libraries geometry_kernel_${kernel}_simple)
        target_link_libraries(geometry_kernel_${kernel}_simple ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)
        install(TARGETS geometry_kernel_${kernel}_simple
            ARCHIVE DESTINATION ${LIBDIR}
            LIBRARY DESTINATION ${LIBDIR}
            RUNTIME DESTINATION ${BINDIR}
        )
    endif()

    install(FILES ${IFCGEOM_H_FILES}
        DESTINATION ${INCLUDEDIR}/ifcgeom/kernels/${kernel}
    )
endforeach()

set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)