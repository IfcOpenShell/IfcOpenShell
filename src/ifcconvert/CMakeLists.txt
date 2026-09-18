# IfcConvert
add_executable(IfcConvert IfcConvert.cpp)

target_link_libraries(
    IfcConvert
    PRIVATE
        IfcGeom
        IfcParse
        Serializers
        ${kernel_libraries}
        ${OpenCASCADE_LIBRARIES}
        ${Boost_LIBRARIES}
        ${HDF5_LIBRARIES}
        ${USD_LIBRARIES}
        ${CGAL_LIBRARIES}
        ${GLTF_LIBRARIES}
)

install(TARGETS IfcConvert EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
