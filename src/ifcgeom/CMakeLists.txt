add_subdirectory(Serialization)
add_subdirectory(kernels)
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

get_property(kernel_libraries GLOBAL PROPERTY kernel_libraries)
get_property(mapping_libraries GLOBAL PROPERTY mapping_libraries)
get_property(IFCOPENSHELL_LIBRARIES GLOBAL PROPERTY IFCOPENSHELL_LIBRARIES)

message(STATUS "IfcGeom kernel_libraries: ${kernel_libraries}")
message(STATUS "IfcGeom mapping_libraries: ${mapping_libraries}")
message(STATUS "IfcGeom IFCOPENSHELL_LIBRARIES: ${IFCOPENSHELL_LIBRARIES}")
if(WASM_BUILD)
    target_link_libraries(IfcGeom ${kernel_libraries} ${mapping_libraries} ${CMAKE_THREAD_LIBS_INIT} "Eigen3::Eigen")
else()
    target_link_libraries(IfcGeom IfcParse ${kernel_libraries} ${mapping_libraries} ${CMAKE_THREAD_LIBS_INIT} "Eigen3::Eigen")
endif()

install(FILES ${IFCGEOM_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcgeom
)

install(FILES ${SCHEMA_AGNOSTIC_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcgeom
)

install(TARGETS IfcGeom
    ARCHIVE DESTINATION ${LIBDIR}
    LIBRARY DESTINATION ${LIBDIR}
    RUNTIME DESTINATION ${BINDIR}
)