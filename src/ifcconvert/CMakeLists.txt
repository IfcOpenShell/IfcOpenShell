# IfcConvert
add_executable(IfcConvert IfcConvert.cpp)

target_link_libraries(IfcConvert PRIVATE IfcGeom IfcParse ${OpenCASCADE_LIBRARIES} ${Boost_LIBRARIES})
if(kernel_libraries OR mapping_libraries OR geometry_serializer_libraries OR document_serializer_libraries)
    add_dependencies(IfcConvert ${kernel_libraries} ${mapping_libraries} ${geometry_serializer_libraries} ${document_serializer_libraries})
endif()

set(_plugin_targets
    ${kernel_libraries}
    ${mapping_libraries}
    ${geometry_serializer_libraries}
    ${document_serializer_libraries}
)

set(_plugin_paths "")
foreach(t IN LISTS _plugin_targets)
    string(APPEND _plugin_paths ";$<TARGET_FILE_DIR:${t}>")
endforeach()

set_target_properties(IfcConvert PROPERTIES
    VS_DEBUGGER_ENVIRONMENT
        "PATH=%PATH%;$<JOIN:$<TARGET_RUNTIME_DLL_DIRS:IfcConvert>,;>;${_plugin_paths}"
)

install(TARGETS IfcConvert)
