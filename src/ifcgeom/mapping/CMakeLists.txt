find_package(Eigen3 REQUIRED)

ifcopenshell_wasm_plugin_dependency(plugin_when_not_wasm)

foreach(schema ${SCHEMA_VERSIONS})
    file(GLOB IFCGEOM_I_FILES *.i)
    file(GLOB IFCGEOM_H_FILES *.h)
    file(GLOB IFCGEOM_CPP_FILES *.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})

    add_library(geometry_mapping_ifc${schema} SHARED ${IFCGEOM_FILES})
    set_target_properties(geometry_mapping_ifc${schema} PROPERTIES
        COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
        OUTPUT_NAME "ifcopenshell_geometry_mapping_ifc${schema}"
        RUNTIME_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
    )
    ifcopenshell_native_plugin_target(geometry_mapping_ifc${schema} IfcGeom)
    if(WASM_BUILD)
        ifcopenshell_wasm_configure_plugin_target(
            geometry_mapping_ifc${schema}
            KIND mapping
            ID "ifc${schema}"
            SYMBOL_ID "ifc${schema}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_mapping_ifc${schema}"
        )
    endif()

    ifcopenshell_wasm_plugin_link_options(geometry_mapping_ifc${schema} ifcopenshell_register_mapping_plugin_v1)

    if(NOT WASM_BUILD)
        set(schema_plugin_library parse_schema_ifc${schema})
    else()
        set(schema_plugin_library)
    endif()

    ifcopenshell_wasm_plugin_target_link(geometry_mapping_ifc${schema}
        MAIN_TARGETS IfcGeom IfcParse
        PRIVATE ${plugin_when_not_wasm} ${schema_plugin_library} Eigen3::Eigen
    )

    list(APPEND mapping_libraries geometry_mapping_ifc${schema})

    install(TARGETS geometry_mapping_ifc${schema} EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endforeach()

set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)
