# This file was generated with the assistance of an AI coding tool.

add_executable(test_ifcopenshell_parse
    test_ifcopenshell_parse.cpp
)
target_compile_definitions(test_ifcopenshell_parse PRIVATE
    IFCOPENSHELL_TEST_FIXTURES="${CMAKE_CURRENT_SOURCE_DIR}/../../ifcopenshell-python/test/fixtures"
)
target_link_libraries(test_ifcopenshell_parse PRIVATE Catch2::Catch2WithMain IfcParse)
add_dependencies(test_ifcopenshell_parse parse_schema_ifc4)
catch_discover_tests(test_ifcopenshell_parse
    DL_PATHS
        $<TARGET_FILE_DIR:Catch2::Catch2>
        $<TARGET_FILE_DIR:Catch2::Catch2WithMain>
        $<TARGET_FILE_DIR:IfcParse>
        $<TARGET_FILE_DIR:plugin>
)
