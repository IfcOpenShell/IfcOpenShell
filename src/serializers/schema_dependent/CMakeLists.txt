file(GLOB SERIALIZERS_S_H_FILES *.h)
file(GLOB SERIALIZERS_S_CPP_FILES *.cpp)
set(SERIALIZERS_S_FILES ${SERIALIZERS_S_H_FILES} ${SERIALIZERS_S_CPP_FILES})

foreach(schema ${SCHEMA_VERSIONS})
    add_library(Serializers_ifc${schema} OBJECT ${SERIALIZERS_S_FILES})
    set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} Serializers_ifc${schema})
    set_target_properties(
        Serializers_ifc${schema}
        PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}"
    )
    target_link_libraries(Serializers_ifc${schema} IfcGeom ${HDF5_LIBRARIES} ${GLTF_LIBRARIES})
    if(NOT WASM_BUILD)
        target_link_libraries(Serializers_ifc${schema} ${OpenCASCADE_LIBRARIES})
    endif()
    install(TARGETS Serializers_ifc${schema} EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endforeach()

set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} PARENT_SCOPE)
