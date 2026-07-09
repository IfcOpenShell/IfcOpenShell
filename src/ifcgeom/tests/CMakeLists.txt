# This file was generated with the assistance of an AI coding tool.

add_executable(test_ifcopenshell_geometry
    test_ifcopenshell_geometry.cpp
)
if(NOT TARGET parse_schema_ifc2x3)
    message(FATAL_ERROR "test_ifcopenshell_geometry requires SCHEMA_VERSIONS to include 2x3.")
endif()
target_include_directories(test_ifcopenshell_geometry PRIVATE "${CMAKE_SOURCE_DIR}/../src")
target_link_libraries(test_ifcopenshell_geometry PRIVATE Catch2::Catch2WithMain IfcGeom IfcParse parse_schema_ifc2x3)
add_dependencies(test_ifcopenshell_geometry geometry_mapping_ifc2x3 geometry_kernel_passthrough)
catch_discover_tests(test_ifcopenshell_geometry
    DL_PATHS
        $<TARGET_FILE_DIR:Catch2::Catch2>
        $<TARGET_FILE_DIR:Catch2::Catch2WithMain>
        $<TARGET_FILE_DIR:IfcGeom>
        $<TARGET_FILE_DIR:IfcParse>
        $<TARGET_FILE_DIR:parse_schema_ifc2x3>
        $<TARGET_FILE_DIR:plugin>
        # Catch2 discovery uses DL_PATHS in order; CTest PATH prepends reverse it.
        $<TARGET_FILE_DIR:IfcGeom>
)
