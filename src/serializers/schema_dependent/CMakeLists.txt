set(document_serializer_plugin_runtime_dir "${CMAKE_BINARY_DIR}/serializers/$<CONFIG>")

foreach(schema ${SCHEMA_VERSIONS})
    add_library(document_serializer_xml_ifc${schema} SHARED XmlSerializer.cpp xml_plugin.cpp)
    target_link_libraries(document_serializer_xml_ifc${schema} PRIVATE plugin Serializers IfcGeom IfcParse)
    set_target_properties(document_serializer_xml_ifc${schema} PROPERTIES
        COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
        OUTPUT_NAME "document.xml.ifc${schema}"
        RUNTIME_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
    )
    list(APPEND document_serializer_libraries document_serializer_xml_ifc${schema})

    if(WITH_GLTF)
        add_library(document_serializer_json_ifc${schema} SHARED JsonSerializer.cpp json_plugin.cpp)
        target_link_libraries(document_serializer_json_ifc${schema} PRIVATE plugin Serializers IfcGeom IfcParse)
        set_target_properties(document_serializer_json_ifc${schema} PROPERTIES
            COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
            OUTPUT_NAME "document.json.ifc${schema}"
            RUNTIME_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
            LIBRARY_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
        )
        list(APPEND document_serializer_libraries document_serializer_json_ifc${schema})
    endif()
endforeach()

set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)
