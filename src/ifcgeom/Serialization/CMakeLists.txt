add_subdirectory(schema)

add_library(geometry_serializer OBJECT Serialization.cpp)
set_target_properties(geometry_serializer PROPERTIES COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS")
target_link_libraries(geometry_serializer ${geometry_serializer_libraries} IfcParse)
set(geometry_serializer_libraries "geometry_serializer" ${geometry_serializer_libraries})

file(GLOB IFCGEOM_SERIALIZATION_H_FILE *.h)
install(FILES ${IFCGEOM_SERIALIZATION_H_FILE}
    DESTINATION ${INCLUDEDIR}/ifcgeom/Serialization
)

install(TARGETS geometry_serializer ${geometry_serializer_libraries})

set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
