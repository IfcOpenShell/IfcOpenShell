set(geometry_serialization_plugin_runtime_dir "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>")

add_subdirectory(schema)

add_library(geometry_serializer Serialization.cpp opencascade_geometry_ifc_writer_plugin.cpp)
target_include_directories(geometry_serializer PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../..>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
if((NOT WIN32) AND BUILD_SHARED_LIBS AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
    SET_INSTALL_SELF_RPATH(geometry_serializer)
endif()
set_target_properties(geometry_serializer PROPERTIES
    OUTPUT_NAME "ifcopenshell.geometry.writer"
    COMPILE_FLAGS "-DIFC_GEOMSERIALIZATION_EXPORTS"
    RUNTIME_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
    LIBRARY_OUTPUT_DIRECTORY "${geometry_serialization_plugin_runtime_dir}"
)
target_link_libraries(geometry_serializer plugin IfcGeom IfcParse geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES})
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} "geometry_serializer")
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)

install(FILES Serialization.h
    DESTINATION ${INCLUDEDIR}/ifcgeom/Serialization
)

install(
    TARGETS geometry_serializer ${geometry_serializer_libraries}
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
)

set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
