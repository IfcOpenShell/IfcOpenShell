add_subdirectory(schema)

add_library(geometry_serializer Serialization.cpp)
file(GLOB IFCGEOM_SERIALIZATION_H_FILE *.h)

set_target_properties(
    geometry_serializer
    PROPERTIES COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS" PUBLIC_HEADER "${IFCGEOM_SERIALIZATION_H_FILE}"
)
target_link_libraries(geometry_serializer ${geometry_serializer_libraries} IfcParse)
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} "geometry_serializer" ${geometry_serializer_libraries})
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)

install(
    TARGETS geometry_serializer ${geometry_serializer_libraries}
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/ifcgeom/Serialization"
)

set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
