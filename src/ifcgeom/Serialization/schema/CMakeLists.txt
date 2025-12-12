foreach(schema ${SCHEMA_VERSIONS})
    add_library(geometry_serializer_ifc${schema} Serialization.cpp)
    target_link_libraries(geometry_serializer_ifc${schema} ${OpenCASCADE_LIBRARIES})
    set_target_properties(
        geometry_serializer_ifc${schema}
        PROPERTIES COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS -DIfcSchema=Ifc${schema}"
    )
    install(
        TARGETS geometry_serializer_ifc${schema}
        EXPORT ${IFCOPENSHELL_EXPORT_TAGETS}
    )
    list(APPEND geometry_serializer_libraries geometry_serializer_ifc${schema})
endforeach()
set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
