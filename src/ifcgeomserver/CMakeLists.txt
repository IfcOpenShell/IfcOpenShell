find_package(Boost REQUIRED)

file(GLOB CPP_FILES *.cpp)
file(GLOB H_FILES *.h)
set(SOURCE_FILES ${CPP_FILES} ${H_FILES})
add_executable(IfcGeomServer ${SOURCE_FILES})
target_link_libraries(IfcGeomServer IfcGeom ${kernel_libraries} ${OPENCASCADE_LIBRARIES})

install(TARGETS IfcGeomServer)
