find_package(Eigen3 ${EIGEN_MIN_VERSION} REQUIRED)

ifcopenshell_wasm_plugin_dependency(plugin_when_not_wasm)

if(WASM_BUILD)
    # Emscripten supports RPATH but its CMake platform does not define these.
    set(CMAKE_SHARED_LIBRARY_RUNTIME_CXX_FLAG "-Wl,-rpath,")
    set(CMAKE_SHARED_LIBRARY_RUNTIME_CXX_FLAG_SEP ":")
    # emcc's response-file parser preserves CMake's escape before '$ORIGIN'.
    # Keep the short library list on the command line so it is unescaped there.
    set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_LIBRARIES FALSE)
endif()

foreach(schema ${SCHEMA_VERSIONS})
    file(GLOB IFCGEOM_I_FILES *.i)
    file(GLOB IFCGEOM_H_FILES *.h)
    file(GLOB IFCGEOM_CPP_FILES *.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})

    add_library(geometry_mapping_ifc${schema} SHARED ${IFCGEOM_FILES})
    set_target_properties(geometry_mapping_ifc${schema} PROPERTIES
        COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
        OUTPUT_NAME "ifcopenshell_geometry_mapping_ifc${schema}"
        RUNTIME_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
    )
    ifcopenshell_native_plugin_target(geometry_mapping_ifc${schema} IfcGeom)
    if(WASM_BUILD)
        ifcopenshell_wasm_configure_plugin_target(
            geometry_mapping_ifc${schema}
            KIND mapping
            ID "ifc${schema}"
            SYMBOL_ID "ifc${schema}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_mapping_ifc${schema}"
            DEPENDS "schema:ifc${schema}"
        )
        # Pyodide loads side modules with RTLD_LOCAL. Record the schema as a
        # dynamic dependency and resolve it beside the mapping module, rather
        # than relying on exports from a previously loaded global module.
        set_target_properties(geometry_mapping_ifc${schema} PROPERTIES
            BUILD_WITH_INSTALL_RPATH TRUE
            INSTALL_RPATH "$ORIGIN"
        )
    endif()

    ifcopenshell_wasm_plugin_link_options(geometry_mapping_ifc${schema} ifcopenshell_register_mapping_plugin_v1)

    set(schema_plugin_library parse_schema_ifc${schema})

    ifcopenshell_wasm_plugin_target_link(geometry_mapping_ifc${schema}
        MAIN_TARGETS IfcGeom IfcParse
        PRIVATE ${plugin_when_not_wasm} ${schema_plugin_library} Eigen3::Eigen
    )

    list(APPEND mapping_libraries geometry_mapping_ifc${schema})

    install(TARGETS geometry_mapping_ifc${schema} EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endforeach()

set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)
