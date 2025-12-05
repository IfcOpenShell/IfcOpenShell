find_package(Eigen3 REQUIRED)

foreach(kernel ${GEOMETRY_KERNELS})
    string(TOUPPER ${kernel} KERNEL_UPPER)
    file(GLOB IFCGEOM_H_FILES ${kernel}/*.h)
    file(GLOB IFCGEOM_CPP_FILES ${kernel}/*.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

    set(KERNEL_TARGET "geometry_kernel_${kernel}")

    add_library(${KERNEL_TARGET} OBJECT ${IFCGEOM_FILES})
    set_property(TARGET ${KERNEL_TARGET} APPEND PROPERTY COMPILE_FLAGS "-DIFC_GEOM_EXPORTS")
    list(APPEND kernel_libraries ${KERNEL_TARGET})
    target_link_libraries(${KERNEL_TARGET} ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)

    if(${kernel} STREQUAL "cgal")
        find_package(CGAL REQUIRED)
        target_link_libraries(${KERNEL_TARGET} CGAL::CGAL)
        set_property(TARGET ${KERNEL_TARGET} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

        set(KERNEL_TARGET_SIMPLE "${KERNEL_TARGET}_simple")
        add_library(${KERNEL_TARGET_SIMPLE} OBJECT ${IFCGEOM_FILES})
        set_target_properties(${KERNEL_TARGET_SIMPLE} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS")
        list(APPEND kernel_libraries ${KERNEL_TARGET_SIMPLE})
        target_link_libraries(${KERNEL_TARGET_SIMPLE} ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)
        target_link_libraries(${KERNEL_TARGET_SIMPLE} CGAL::CGAL)
    elseif(${kernel} STREQUAL "opencascade")
        target_link_libraries(${KERNEL_TARGET} ${OpenCASCADE_LIBRARIES})
    endif()

    install(FILES ${IFCGEOM_H_FILES}
        DESTINATION ${INCLUDEDIR}/ifcgeom/kernels/${kernel}
    )
endforeach()

set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)
