foreach(schema ${SCHEMA_VERSIONS})
    add_library(geometry_serializer_ifc${schema} OBJECT Serialization.cpp)
    target_link_libraries(geometry_serializer_ifc${schema} ${OpenCASCADE_LIBRARIES})
    set_target_properties(
        geometry_serializer_ifc${schema}
        PROPERTIES COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS -DIfcSchema=Ifc${schema}"
    )
    list(APPEND geometry_serializer_libraries geometry_serializer_ifc${schema})
endforeach()
set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
