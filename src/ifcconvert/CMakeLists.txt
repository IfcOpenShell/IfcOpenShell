# IfcConvert
add_executable(IfcConvert IfcConvert.cpp)

target_link_libraries(IfcConvert PRIVATE IfcGeom IfcParse ${Boost_LIBRARIES})
if(schema_libraries OR kernel_libraries OR mapping_libraries OR geometry_serializer_libraries OR document_serializer_libraries)
    add_dependencies(IfcConvert ${schema_libraries} ${kernel_libraries} ${mapping_libraries} ${geometry_serializer_libraries} ${document_serializer_libraries})
endif()

set(_plugin_targets
    ${schema_libraries}
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

if((NOT WIN32) AND BUILD_SHARED_LIBS AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_RPATHS)
    if(IS_ABSOLUTE "${CMAKE_INSTALL_LIBDIR}")
        SET_INSTALL_RPATHS(IfcConvert "${CMAKE_INSTALL_LIBDIR}")
    elseif(IS_ABSOLUTE "${CMAKE_INSTALL_BINDIR}")
        SET_INSTALL_RPATHS(IfcConvert "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
    else()
        file(RELATIVE_PATH _ifcconvert_libdir_from_bindir "/${CMAKE_INSTALL_BINDIR}" "/${CMAKE_INSTALL_LIBDIR}")
        if(APPLE)
            SET_INSTALL_RPATHS(IfcConvert "@executable_path/${_ifcconvert_libdir_from_bindir}")
        else()
            SET_INSTALL_RPATHS(IfcConvert "$ORIGIN/${_ifcconvert_libdir_from_bindir}")
        endif()
    endif()
endif()

install(TARGETS IfcConvert EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
