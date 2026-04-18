foreach(schema ${SCHEMA_VERSIONS})
    add_document_serializer_plugin(document_serializer_xml_ifc${schema} "document.xml.ifc${schema}" SOURCES XmlSerializer.cpp xml_plugin.cpp)
    target_compile_definitions(document_serializer_xml_ifc${schema} PRIVATE IfcSchema=Ifc${schema})

    if(GLTF_SUPPORT)
        add_document_serializer_plugin(document_serializer_json_ifc${schema} "document.json.ifc${schema}" SOURCES JsonSerializer.cpp json_plugin.cpp)
        target_compile_definitions(document_serializer_json_ifc${schema} PRIVATE IfcSchema=Ifc${schema})
    endif()
endforeach()

set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)
