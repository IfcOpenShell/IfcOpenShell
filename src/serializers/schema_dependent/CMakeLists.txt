file(GLOB SERIALIZERS_S_H_FILES *.h)
file(GLOB SERIALIZERS_S_CPP_FILES *.cpp)
set(SERIALIZERS_S_FILES ${SERIALIZERS_S_H_FILES} ${SERIALIZERS_S_CPP_FILES})

foreach(schema ${SCHEMA_VERSIONS})
    add_library(Serializers_ifc${schema} OBJECT ${SERIALIZERS_S_FILES})
    set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} Serializers_ifc${schema})
    set_target_properties(Serializers_ifc${schema} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}")
    if(WASM_BUILD)
        target_link_libraries(Serializers_ifc${schema} ${HDF5_LIBRARIES})
    else()
        target_link_libraries(Serializers_ifc${schema} IfcGeom ${OPENCASCADE_LIBRARIES} ${HDF5_LIBRARIES})
    endif()

    install(TARGETS Serializers_ifc${schema}
        ARCHIVE DESTINATION ${LIBDIR}
        RUNTIME DESTINATION ${BINDIR}
        LIBRARY DESTINATION ${LIBDIR}
    )
endforeach()


set(SERIALIZER_SCHEMA_LIBRARIES ${SERIALIZER_SCHEMA_LIBRARIES} PARENT_SCOPE)
