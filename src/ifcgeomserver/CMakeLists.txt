find_package(Boost REQUIRED)

file(GLOB CPP_FILES *.cpp)
set(SOURCE_FILES ${CPP_FILES})
add_executable(IfcGeomServer ${SOURCE_FILES})
target_link_libraries(IfcGeomServer IfcGeom ${OpenCASCADE_LIBRARIES})
if(WITH_OPENCASCADE)
    target_link_libraries(IfcGeomServer geometry_kernel_opencascade)
endif()
if(kernel_libraries OR mapping_libraries)
    add_dependencies(IfcGeomServer ${kernel_libraries} ${mapping_libraries})
endif()

install(TARGETS IfcGeomServer)
