add_subdirectory(mapping)
set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)

# IfcGeom (schema agnostic)
file(GLOB SCHEMA_AGNOSTIC_H_FILES *.h)
file(GLOB SCHEMA_AGNOSTIC_CPP_FILES *.cpp)
set(SERIALIZER_RUNTIME_CPP_FILES
    ../serializers/document_serializer_plugin.cpp
    ../serializers/geometry_serializer_plugin.cpp
)
set(SCHEMA_AGNOSTIC_FILES ${SCHEMA_AGNOSTIC_H_FILES} ${SCHEMA_AGNOSTIC_CPP_FILES} ${SERIALIZER_RUNTIME_CPP_FILES})

add_library(IfcGeom ${SCHEMA_AGNOSTIC_FILES})
set_target_properties(IfcGeom PROPERTIES
        OUTPUT_NAME "ifcopenshell.geometry"
)
set_target_properties(IfcGeom PROPERTIES COMPILE_FLAGS -DIFC_GEOM_EXPORTS)
if (NOT CREATE_BUNDLE)
set_target_properties(IfcGeom PROPERTIES VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
endif()
target_compile_definitions(IfcGeom PRIVATE BOOST_DLL_USE_STD_FS SERIALIZERS_EXPORTS)
if(WITH_CGAL)
    target_compile_definitions(IfcGeom PUBLIC IFOPSH_WITH_CGAL)
endif()
if(WITH_OPENCASCADE)
    target_compile_definitions(IfcGeom PUBLIC IFOPSH_WITH_OPENCASCADE)
endif()
if(WITH_MANIFOLD)
    target_compile_definitions(IfcGeom PUBLIC IFOPSH_WITH_MANIFOLD)
endif()
if(HDF5_SUPPORT)
    target_compile_definitions(IfcGeom PUBLIC WITH_HDF5)
endif()

if(UNIX)
    find_package(Threads)
endif()

find_package(Eigen3 REQUIRED)

add_subdirectory(kernels)
set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)
set(tree_libraries ${tree_libraries} PARENT_SCOPE)

if(WASM_BUILD)
    target_link_libraries(IfcGeom plugin ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} "Eigen3::Eigen")
else()
    target_link_libraries(IfcGeom plugin IfcParse ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} "Eigen3::Eigen")
endif()

if((BUILD_CONVERT OR BUILD_IFCPYTHON) AND WITH_OPENCASCADE)
    add_subdirectory(Serialization)
    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)
    set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
endif()

install(FILES ${SCHEMA_AGNOSTIC_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcgeom
)
