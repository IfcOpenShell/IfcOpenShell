add_subdirectory(schema)

add_library(geometry_serializer STATIC Serialization.cpp)
set_target_properties(geometry_serializer PROPERTIES COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS")
target_link_libraries(geometry_serializer ${geometry_serializer_libraries} IfcParse)
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} "geometry_serializer" ${geometry_serializer_libraries})
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)

file(GLOB IFCGEOM_SERIALIZATION_H_FILE *.h)
install(FILES ${IFCGEOM_SERIALIZATION_H_FILE}
    DESTINATION ${INCLUDEDIR}/ifcgeom/Serialization
)

install(TARGETS geometry_serializer ${geometry_serializer_libraries}
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
)

set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
