message(STATUS "GEOMETRY_KERNELS ${GEOMETRY_KERNELS}")

set(kernel_plugin_runtime_dir "${CMAKE_BINARY_DIR}/ifcgeom/$<CONFIG>")

foreach(kernel ${GEOMETRY_KERNELS})
    string(TOUPPER ${kernel} KERNEL_UPPER)
    file(GLOB IFCGEOM_H_FILES ${kernel}/*.h)
    file(GLOB IFCGEOM_CPP_FILES ${kernel}/*.cpp)
    if(${kernel} STREQUAL "opencascade")
        list(REMOVE_ITEM IFCGEOM_CPP_FILES
            ${CMAKE_CURRENT_SOURCE_DIR}/${kernel}/tree_brep_plugin.cpp
            ${CMAKE_CURRENT_SOURCE_DIR}/${kernel}/tree_trianglebvh_plugin.cpp
        )
    endif()
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES})

    set(KERNEL_TARGET "geometry_kernel_${kernel}")
    add_library(${KERNEL_TARGET} SHARED ${IFCGEOM_FILES})
    set_target_properties(${KERNEL_TARGET} PROPERTIES
        COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS"
        OUTPUT_NAME "geometry.kernel.${kernel}"
        RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
    )
    list(APPEND kernel_libraries ${KERNEL_TARGET})
    target_link_libraries(${KERNEL_TARGET} PRIVATE plugin IfcGeom ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)

    install(TARGETS ${KERNEL_TARGET})

    if(${kernel} STREQUAL "cgal")
        set_property(TARGET ${KERNEL_TARGET} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

        set(KERNEL_TARGET_SIMPLE "${KERNEL_TARGET}_simple")
        add_library(${KERNEL_TARGET_SIMPLE} SHARED ${IFCGEOM_FILES})
        set_target_properties(${KERNEL_TARGET_SIMPLE} PROPERTIES
            COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS"
            OUTPUT_NAME "geometry.kernel.cgalsimple"
            RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
            LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
        )
        list(APPEND kernel_libraries ${KERNEL_TARGET_SIMPLE})
        target_link_libraries(${KERNEL_TARGET_SIMPLE} PRIVATE plugin IfcGeom ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen)
        install(TARGETS ${KERNEL_TARGET_SIMPLE})
    elseif(${kernel} STREQUAL "opencascade")
        target_link_libraries(${KERNEL_TARGET} PRIVATE ${OpenCASCADE_LIBRARIES})

        foreach(tree_backend brep trianglebvh)
            set(TREE_TARGET "geometry_tree_opencascade_${tree_backend}")
            add_library(${TREE_TARGET} SHARED
                ${kernel}/tree_${tree_backend}_plugin.cpp
                ${kernel}/tree_backends.h
            )
            set_target_properties(${TREE_TARGET} PROPERTIES
                COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS"
                OUTPUT_NAME "geometry.tree.opencascade.${tree_backend}"
                RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
                LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
            )
            list(APPEND tree_libraries ${TREE_TARGET})
            target_link_libraries(${TREE_TARGET} PRIVATE plugin IfcGeom geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES} Eigen3::Eigen)
            install(TARGETS ${TREE_TARGET})
        endforeach()
    endif()

    install(FILES ${IFCGEOM_H_FILES}
        DESTINATION ${INCLUDEDIR}/ifcgeom/kernels/${kernel}
    )
endforeach()

set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)
set(tree_libraries ${tree_libraries} PARENT_SCOPE)
