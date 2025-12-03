# IfcConvert
if(WITH_RELATIONSHIP_VALIDATION)
    file(GLOB IFCCONVERT_CPP_FILES *.cpp)
    file(GLOB IFCCONVERT_H_FILES *.h)
else()
    file(GLOB IFCCONVERT_CPP_FILES IfcConvert.cpp)
    file(GLOB IFCCONVERT_H_FILES)
endif()
set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
add_executable(IfcConvert ${IFCCONVERT_FILES})

target_link_libraries(IfcConvert IfcGeom IfcParse Serializers ${OpenCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})

install(TARGETS IfcConvert)
