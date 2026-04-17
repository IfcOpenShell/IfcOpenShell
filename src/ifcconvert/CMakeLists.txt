# IfcConvert
add_executable(IfcConvert IfcConvert.cpp)

target_link_libraries(IfcConvert IfcGeom IfcParse Serializers ${OpenCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})
if(kernel_libraries OR mapping_libraries OR document_serializer_libraries)
    add_dependencies(IfcConvert ${kernel_libraries} ${mapping_libraries} ${document_serializer_libraries})
endif()

install(TARGETS IfcConvert)
