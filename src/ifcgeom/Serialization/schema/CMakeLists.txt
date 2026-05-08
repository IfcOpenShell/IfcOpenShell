if (NOT WASM_BUILD)

foreach(schema ${SCHEMA_VERSIONS})
    add_library(geometry_serializer_ifc${schema} SHARED Serialization.cpp plugin.cpp)
    target_link_libraries(geometry_serializer_ifc${schema} PRIVATE plugin geometry_serializer IfcGeom IfcParse parse_schema_ifc${schema} ${OpenCASCADE_LIBRARIES})
    set_target_properties(geometry_serializer_ifc${schema} PROPERTIES
        COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
        OUTPUT_NAME "ifcopenshell.geometry.writer.ifc${schema}"
        RUNTIME_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
    )
    ifcopenshell_wasm_plugin_link_options(
        geometry_serializer_ifc${schema}
        ifcopenshell_register_opencascade_geometry_ifc_writer_plugin_v1
    )
    list(APPEND geometry_serializer_libraries geometry_serializer_ifc${schema})
endforeach()
set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)

endif()
