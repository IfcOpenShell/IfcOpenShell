find_package(Eigen3 REQUIRED)

foreach(kernel ${GEOMETRY_KERNELS})
    string(TOUPPER ${kernel} KERNEL_UPPER)
    file(GLOB IFCGEOM_H_FILES ${kernel}/*.h)
    file(GLOB IFCGEOM_CPP_FILES ${kernel}/*.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

    set(KERNEL_TARGET "geometry_kernel_${kernel}")

    add_library(${KERNEL_TARGET} ${IFCGEOM_FILES})
    set_target_properties(
        ${KERNEL_TARGET}
        PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS" PUBLIC_HEADER "${IFCGEOM_H_FILES}"
    )
    list(APPEND kernel_libraries ${KERNEL_TARGET})
    target_link_libraries(${KERNEL_TARGET} ${${KERNEL_UPPER}_LIBRARIES} IfcGeom Eigen3::Eigen)
    install(
        TARGETS ${KERNEL_TARGET}
        EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
        PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/ifcgeom/kernels/${kernel}"
    )

    if(${kernel} STREQUAL "cgal")
        find_package(CGAL REQUIRED)
        target_link_libraries(${KERNEL_TARGET} IFCOPENSHELL_CGAL)
        set_property(TARGET ${KERNEL_TARGET} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

        set(KERNEL_TARGET_SIMPLE "${KERNEL_TARGET}_simple")
        add_library(${KERNEL_TARGET_SIMPLE} ${IFCGEOM_FILES})
        set_target_properties(
            ${KERNEL_TARGET_SIMPLE}
            PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS"
        )
        list(APPEND kernel_libraries ${KERNEL_TARGET_SIMPLE})
        target_link_libraries(${KERNEL_TARGET_SIMPLE} ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)
        target_link_libraries(${KERNEL_TARGET_SIMPLE} IFCOPENSHELL_CGAL)
        install(TARGETS ${KERNEL_TARGET_SIMPLE} EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
    elseif(${kernel} STREQUAL "opencascade")
        target_link_libraries(${KERNEL_TARGET} ${OpenCASCADE_LIBRARIES})
    endif()
endforeach()

set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)

install(FILES ifc_geomlibrary_api.h DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/ifcgeom/kernels/")
