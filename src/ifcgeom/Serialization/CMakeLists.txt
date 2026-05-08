set(geometry_serialization_plugin_runtime_dir "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>")

add_subdirectory(schema)

add_library(geometry_serializer Serialization.cpp opencascade_geometry_ifc_writer_plugin.cpp)
set_target_properties(geometry_serializer PROPERTIES
    OUTPUT_NAME "ifcopenshell.geometry.writer"
    COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS"
    RUNTIME_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
    LIBRARY_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
)
target_link_libraries(geometry_serializer plugin IfcGeom IfcParse ${OpenCASCADE_LIBRARIES})
target_link_libraries(geometry_serializer geometry_kernel_opencascade)
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} "geometry_serializer")
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)

install(FILES Serialization.h
    DESTINATION ${INCLUDEDIR}/ifcgeom/Serialization
)

install(TARGETS geometry_serializer ${geometry_serializer_libraries})

set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
