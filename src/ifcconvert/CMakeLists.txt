# IfcConvert
add_executable(IfcConvert IfcConvert.cpp)

target_link_libraries(IfcConvert IfcGeom IfcParse Serializers ${OpenCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})

install(TARGETS IfcConvert)
