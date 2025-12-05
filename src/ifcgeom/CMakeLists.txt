add_subdirectory(kernels)
set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)

if((BUILD_CONVERT OR BUILD_IFCPYTHON) AND WITH_OPENCASCADE)
    add_subdirectory(Serialization)
    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)
endif()

add_subdirectory(mapping)

# IfcGeom (schema agnostic)
file(GLOB SCHEMA_AGNOSTIC_H_FILES *.h)
file(GLOB SCHEMA_AGNOSTIC_CPP_FILES *.cpp)
set(SCHEMA_AGNOSTIC_FILES ${SCHEMA_AGNOSTIC_H_FILES} ${SCHEMA_AGNOSTIC_CPP_FILES})

add_library(IfcGeom ${SCHEMA_AGNOSTIC_FILES})
set_target_properties(IfcGeom PROPERTIES COMPILE_FLAGS -DIFC_GEOM_EXPORTS VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

if(UNIX)
    find_package(Threads)
endif()

find_package(Eigen3 REQUIRED)

target_link_libraries(IfcGeom
    ${kernel_libraries} ${mapping_libraries}
    ${CMAKE_THREAD_LIBS_INIT} "Eigen3::Eigen"
    ${CGAL_LIBRARIES}
)
if(NOT WASM_BUILD)
    target_link_libraries(IfcGeom IfcParse)
endif()

install(TARGETS IfcGeom)

install(FILES ${SCHEMA_AGNOSTIC_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcgeom
)