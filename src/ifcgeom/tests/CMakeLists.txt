# This file was generated with the assistance of an AI coding tool.

add_executable(test_ifcopenshell_geometry
    test_ifcopenshell_geometry.cpp
)
target_link_libraries(test_ifcopenshell_geometry PRIVATE Catch2::Catch2WithMain)
catch_discover_tests(test_ifcopenshell_geometry
    DL_PATHS
        $<TARGET_FILE_DIR:Catch2::Catch2>
        $<TARGET_FILE_DIR:Catch2::Catch2WithMain>
)
