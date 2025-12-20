find_package(Boost REQUIRED)

file(GLOB CPP_FILES *.cpp)
set(SOURCE_FILES ${CPP_FILES})
add_executable(IfcGeomServer ${SOURCE_FILES})
target_link_libraries(IfcGeomServer IfcGeom ${kernel_libraries} ${OpenCASCADE_LIBRARIES})

install(TARGETS IfcGeomServer EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
