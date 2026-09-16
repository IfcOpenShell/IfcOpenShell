message(STATUS "GEOMETRY_KERNELS ${GEOMETRY_KERNELS}")

ifcopenshell_wasm_plugin_dependency(plugin_when_not_wasm)

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
    if((NOT WIN32) AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
        SET_INSTALL_SELF_RPATH(${KERNEL_TARGET})
    endif()

    ifcopenshell_wasm_plugin_link_options(${KERNEL_TARGET} ifcopenshell_register_kernel_plugin_v1 EXPORT_DYNAMIC)

    set_target_properties(${KERNEL_TARGET} PROPERTIES
        COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS"
        OUTPUT_NAME "ifcopenshell_geometry_kernel_${kernel}"
        RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
    )
    ifcopenshell_native_plugin_target(${KERNEL_TARGET} IfcGeom)
    if(WASM_BUILD)
        ifcopenshell_wasm_configure_plugin_target(
            ${KERNEL_TARGET}
            KIND kernel
            ID "${kernel}"
            SYMBOL_ID "${kernel}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_kernel_${kernel}"
        )
    endif()
    list(APPEND kernel_libraries ${KERNEL_TARGET})
    ifcopenshell_wasm_plugin_target_link(${KERNEL_TARGET}
        MAIN_TARGETS IfcParse IfcGeom
        PRIVATE ${plugin_when_not_wasm} ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen
    )

    install(TARGETS ${KERNEL_TARGET})

    if(${kernel} STREQUAL "cgal")
        set_property(TARGET ${KERNEL_TARGET} APPEND_STRING PROPERTY COMPILE_FLAGS " -DCGAL_HAS_THREADS")

        set(KERNEL_TARGET_SIMPLE "${KERNEL_TARGET}_simple")
        add_library(${KERNEL_TARGET_SIMPLE} SHARED ${IFCGEOM_FILES})
        if((NOT WIN32) AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
            SET_INSTALL_SELF_RPATH(${KERNEL_TARGET_SIMPLE})
        endif()

        ifcopenshell_wasm_plugin_link_options(${KERNEL_TARGET_SIMPLE} ifcopenshell_register_kernel_plugin_v1 EXPORT_DYNAMIC)

        set_target_properties(${KERNEL_TARGET_SIMPLE} PROPERTIES
            COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS -DIFOPSH_SIMPLE_KERNEL -DCGAL_HAS_THREADS"
            OUTPUT_NAME "ifcopenshell_geometry_kernel_cgalsimple"
            RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
            LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
        )
        ifcopenshell_native_plugin_target(${KERNEL_TARGET_SIMPLE} IfcGeom)
        if(WASM_BUILD)
            ifcopenshell_wasm_configure_plugin_target(
                ${KERNEL_TARGET_SIMPLE}
                KIND kernel
                ID "cgalsimple"
                SYMBOL_ID "cgalsimple"
                EXPORT_SYMBOL "ifcopenshell_emscripten_register_kernel_cgalsimple"
            )
        endif()
        list(APPEND kernel_libraries ${KERNEL_TARGET_SIMPLE})
        ifcopenshell_wasm_plugin_target_link(${KERNEL_TARGET_SIMPLE}
            MAIN_TARGETS IfcParse IfcGeom
            PRIVATE ${plugin_when_not_wasm} ${${KERNEL_UPPER}_LIBRARIES} Eigen3::Eigen IFCOPENSHELL_CGAL
        )
        install(TARGETS ${KERNEL_TARGET_SIMPLE})
    elseif(${kernel} STREQUAL "opencascade")
        if (WASM_BUILD)
            # TKMesh and TKXMesh both export the same DISCRETALGO meshing plugin entry point.
            # Keep TKMesh and drop TKXMesh so wasm-ld sees a single OCCT discretizer.
            set(OCCT_LIBS_FILTERED ${OpenCASCADE_LIBRARIES})
            list(FILTER OCCT_LIBS_FILTERED EXCLUDE REGEX "TKXMesh")
            target_link_libraries(${KERNEL_TARGET} PRIVATE
                "-Wl,--start-group"
                ${OCCT_LIBS_FILTERED}
                "-Wl,--end-group"
            )
        else()
            target_link_libraries(${KERNEL_TARGET} PRIVATE ${OpenCASCADE_LIBRARIES})
        endif()

        foreach(tree_backend brep trianglebvh)
            set(TREE_TARGET "geometry_tree_opencascade_${tree_backend}")
            add_library(${TREE_TARGET} SHARED
                ${kernel}/tree_${tree_backend}_plugin.cpp
                ${kernel}/tree_backends.h
            )
            if((NOT WIN32) AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
                SET_INSTALL_SELF_RPATH(${TREE_TARGET})
            endif()
            set_target_properties(${TREE_TARGET} PROPERTIES
                COMPILE_FLAGS "-DIFC_GEOMLIBRARY_EXPORTS"
                OUTPUT_NAME "ifcopenshell_geometry_tree_opencascade_${tree_backend}"
                RUNTIME_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
                LIBRARY_OUTPUT_DIRECTORY "${kernel_plugin_runtime_dir}"
            )
            ifcopenshell_native_plugin_target(${TREE_TARGET} IfcGeom)
            if(WASM_BUILD)
                ifcopenshell_wasm_configure_plugin_target(
                    ${TREE_TARGET}
                    KIND tree
                    ID "opencascade.${tree_backend}"
                    SYMBOL_ID "opencascade_${tree_backend}"
                    EXPORT_SYMBOL "ifcopenshell_emscripten_register_tree_opencascade_${tree_backend}"
                    DEPENDS "kernel:opencascade"
                )
            endif()
            list(APPEND tree_libraries ${TREE_TARGET})
            if(WASM_BUILD)
                # Tree plugins compile against OCCT headers but do NOT link OCCT
                # libraries. OCCT symbols resolve at runtime from the kernel
                # provider (which uses --export-dynamic to make all its symbols
                # available). This matches the serializer plugin pattern and
                # avoids duplicating OCCT code across side modules.
                if(WITH_OPENCASCADE AND OCC_INCLUDE_DIR)
                    target_include_directories(${TREE_TARGET} PRIVATE "${OCC_INCLUDE_DIR}")
                endif()
                ifcopenshell_wasm_plugin_target_link(${TREE_TARGET}
                    MAIN_TARGETS IfcParse IfcGeom
                    PRIVATE ${plugin_when_not_wasm} Eigen3::Eigen
                )
                add_dependencies(${TREE_TARGET} geometry_kernel_opencascade)
            else()
                target_link_libraries(${TREE_TARGET} PRIVATE plugin IfcGeom geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES} Eigen3::Eigen)
            endif()
            ifcopenshell_wasm_plugin_link_options(${TREE_TARGET} ifcopenshell_register_tree_plugin_v1)
            install(TARGETS ${TREE_TARGET})
        endforeach()
    endif()

    install(FILES ${IFCGEOM_H_FILES}
        DESTINATION ${INCLUDEDIR}/ifcgeom/kernels/${kernel}
    )
endforeach()

set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)
set(tree_libraries ${tree_libraries} PARENT_SCOPE)
