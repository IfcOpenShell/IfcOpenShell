# This file was generated with the assistance of an AI coding tool.

add_executable(test_ifcopenshell_geometry
    test_ifcopenshell_geometry.cpp
    test_taxonomy.cpp
)
list(GET SCHEMA_VERSIONS -1 IFCGEOM_TEST_SCHEMA_VERSION)
set(IFCGEOM_TEST_SCHEMA_TARGET parse_schema_ifc${IFCGEOM_TEST_SCHEMA_VERSION})
set(IFCGEOM_TEST_MAPPING_TARGET geometry_mapping_ifc${IFCGEOM_TEST_SCHEMA_VERSION})
if(NOT TARGET ${IFCGEOM_TEST_SCHEMA_TARGET})
    message(FATAL_ERROR "test_ifcopenshell_geometry requires ${IFCGEOM_TEST_SCHEMA_TARGET}.")
endif()
foreach(backend cgal cgal_simple manifold)
    if(TARGET geometry_kernel_${backend})
        add_dependencies(test_ifcopenshell_geometry geometry_kernel_${backend})
        string(TOUPPER ${backend} backend_definition)
        target_compile_definitions(test_ifcopenshell_geometry PRIVATE TAXONOMY_TEST_${backend_definition})
    endif()
endforeach()
if(NOT TARGET ${IFCGEOM_TEST_MAPPING_TARGET})
    message(FATAL_ERROR "test_ifcopenshell_geometry requires ${IFCGEOM_TEST_MAPPING_TARGET}.")
endif()
target_include_directories(test_ifcopenshell_geometry PRIVATE "${CMAKE_SOURCE_DIR}/../src")
target_compile_definitions(test_ifcopenshell_geometry PRIVATE
    IfcSchema=Ifc${IFCGEOM_TEST_SCHEMA_VERSION}
    "IFCGEOM_TEST_SCHEMA_HEADER=\"ifcparse/schemas/Ifc${IFCGEOM_TEST_SCHEMA_VERSION}.h\""
)
target_link_libraries(test_ifcopenshell_geometry PRIVATE
    Catch2::Catch2WithMain
    IfcGeom
    IfcParse
    ${IFCGEOM_TEST_SCHEMA_TARGET}
)
add_dependencies(test_ifcopenshell_geometry ${IFCGEOM_TEST_MAPPING_TARGET} geometry_kernel_passthrough)
if(TARGET geometry_kernel_opencascade)
    add_dependencies(test_ifcopenshell_geometry geometry_kernel_opencascade)
    target_compile_definitions(test_ifcopenshell_geometry PRIVATE TAXONOMY_TEST_OPENCASCADE)
endif()
catch_discover_tests(test_ifcopenshell_geometry
    DL_PATHS
        $<TARGET_FILE_DIR:Catch2::Catch2>
        $<TARGET_FILE_DIR:Catch2::Catch2WithMain>
        $<TARGET_FILE_DIR:IfcGeom>
        $<TARGET_FILE_DIR:IfcParse>
        $<TARGET_FILE_DIR:${IFCGEOM_TEST_SCHEMA_TARGET}>
        $<TARGET_FILE_DIR:plugin>
        # Catch2 discovery uses DL_PATHS in order; CTest PATH prepends reverse it.
        $<TARGET_FILE_DIR:IfcGeom>
)
