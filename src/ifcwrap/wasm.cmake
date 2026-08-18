if(NOT WASM_BUILD)
    return()
endif()


set(IFCOPENSHELL_WASM_PLUGINS_DIR "${IFCOPENSHELL_WASM_OUTPUT_DIR}/plugins")
set(IFCOPENSHELL_WASM_PLUGINS_JSON "${IFCOPENSHELL_WASM_OUTPUT_DIR}/ifcopenshell_plugins.json")
set(IFCOPENSHELL_WASM_MATH_IMPORTS_JS "${CMAKE_CURRENT_SOURCE_DIR}/wasm_math_imports.js")

set(IFCOPENSHELL_WASM_ENTRYPOINT "${CMAKE_CURRENT_BINARY_DIR}/ifcopenshell_wasm_entrypoint.cpp")
file(WRITE "${IFCOPENSHELL_WASM_ENTRYPOINT}"
    "// WASM main module entrypoint. Schema and geometry plugins load lazily at runtime.\n"
    "#include <setjmp.h>\n"
    "#include <emscripten.h>\n"
    "extern \"C\" void ifcopenshell_wasm_entrypoint(void) {}\n"
    "extern \"C\" EMSCRIPTEN_KEEPALIVE void ifcopenshell_wasm_keep_setjmp(void) { jmp_buf env; if (setjmp(env)) {} }\n"
)

function(ifcopenshell_configure_wasm_main TARGET ENVIRONMENT OUTPUT_NAME)
    ifcopenshell_wasm_main_module_link(${TARGET})
    add_dependencies(${TARGET} ifcopenshell_capi ifcopenshell_bindings_codegen)
    # Keep IfcParse symbols in the main module for SIDE_MODULE plugins that import from it.
    target_link_libraries(
        ${TARGET}
        PRIVATE
            ifcopenshell_capi
            "-Wl,--whole-archive"
            IfcParse
            "-Wl,--no-whole-archive"
            plugin
    )
    if(TARGET IfcGeom)
        target_link_libraries(${TARGET} PRIVATE IfcGeom)
    endif()

    target_compile_options(${TARGET} PRIVATE -fwasm-exceptions)
    set_property(TARGET ${TARGET} APPEND PROPERTY LINK_DEPENDS "${IFCOPENSHELL_WASM_MATH_IMPORTS_JS}")

    target_link_options(
        ${TARGET}
        PRIVATE
            "SHELL:--no-entry"
            "SHELL:-fwasm-exceptions"
            "SHELL:-sWASM=1"
            "SHELL:-sMAIN_MODULE=1"
            "SHELL:-sMODULARIZE=1"
            "SHELL:-sEXPORT_ES6=1"
            "SHELL:-sEXPORT_NAME=initIfcOpenShellWasmModule"
            "SHELL:-sENVIRONMENT=${ENVIRONMENT}"
            "SHELL:--js-library=${IFCOPENSHELL_WASM_MATH_IMPORTS_JS}"
            "SHELL:-sEXPORTED_RUNTIME_METHODS=[\"stringToUTF8\",\"UTF8ToString\",\"lengthBytesUTF8\",\"getValue\",\"setValue\",\"HEAP32\",\"HEAPU32\",\"loadDynamicLibrary\",\"FS\"]"
            "SHELL:-sALLOW_MEMORY_GROWTH=1"
            "SHELL:-sMAXIMUM_MEMORY=4294967296"
            "SHELL:-sALLOW_TABLE_GROWTH=1"
            "SHELL:-sAUTOLOAD_DYLIBS=0"
            "SHELL:-sERROR_ON_UNDEFINED_SYMBOLS=0"
            "SHELL:-sWASM_BIGINT=1"
            "SHELL:-Wl,--export=__c_longjmp"
            "SHELL:-Wl,--export=__wasm_longjmp"
            "SHELL:-Wl,--export=__wasm_setjmp"
            "SHELL:-sSUPPORT_LONGJMP=wasm"
            -Oz
    )
    set_target_properties(${TARGET} PROPERTIES
        OUTPUT_NAME "${OUTPUT_NAME}"
        SUFFIX ".mjs"
        RUNTIME_OUTPUT_DIRECTORY "${IFCOPENSHELL_WASM_OUTPUT_DIR}"
    )
endfunction()

add_executable(ifcopenshell_wasm "${IFCOPENSHELL_WASM_ENTRYPOINT}")
ifcopenshell_configure_wasm_main(ifcopenshell_wasm "web,worker" "ifcopenshell_wasm")

add_executable(ifcopenshell_wasm_node "${IFCOPENSHELL_WASM_ENTRYPOINT}")
ifcopenshell_configure_wasm_main(ifcopenshell_wasm_node "node" "ifcopenshell_wasm.node")

# Collect plugin targets and manifest entries. Each plugin target copies its
# output to the plugins directory via an aggregate custom target so that the
# manifest generator only needs to write JSON (no filesystem probing).
set(ifcopenshell_wasm_plugin_entries)
set(ifcopenshell_wasm_plugin_copy_commands)
foreach(plugin_target IN LISTS schema_libraries kernel_libraries tree_libraries mapping_libraries geometry_serializer_libraries document_serializer_libraries)
    if(NOT TARGET ${plugin_target})
        continue()
    endif()
    add_dependencies(ifcopenshell_wasm ${plugin_target})
    add_dependencies(ifcopenshell_wasm_node ${plugin_target})

    ifcopenshell_wasm_plugin_manifest_entry(${plugin_target} plugin_entry)
    if(plugin_entry)
        list(APPEND ifcopenshell_wasm_plugin_entries ${plugin_entry})

        get_target_property(output_name ${plugin_target} OUTPUT_NAME)
        if(NOT output_name)
            set(output_name ${plugin_target})
        endif()

        list(APPEND ifcopenshell_wasm_plugin_copy_commands
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:${plugin_target}>"
                "${IFCOPENSHELL_WASM_PLUGINS_DIR}/${output_name}.wasm"
        )
    endif()
endforeach()
string(REPLACE ";" "@" ifcopenshell_wasm_plugin_entries_arg "${ifcopenshell_wasm_plugin_entries}")

add_custom_target(ifcopenshell_wasm_plugins_bundle
    COMMAND ${CMAKE_COMMAND} -E make_directory "${IFCOPENSHELL_WASM_PLUGINS_DIR}"
    ${ifcopenshell_wasm_plugin_copy_commands}
    DEPENDS
        ${schema_libraries}
        ${kernel_libraries}
        ${tree_libraries}
        ${mapping_libraries}
        ${geometry_serializer_libraries}
        ${document_serializer_libraries}
    VERBATIM
)
add_dependencies(ifcopenshell_wasm ifcopenshell_wasm_plugins_bundle)
add_dependencies(ifcopenshell_wasm_node ifcopenshell_wasm_plugins_bundle)

# Generate the plugin manifest JSON after all plugins have been copied.
add_custom_target(ifcopenshell_wasm_plugin_manifest
    COMMAND ${CMAKE_COMMAND}
        -DIFCOPENSHELL_WASM_PLUGINS_JSON=${IFCOPENSHELL_WASM_PLUGINS_JSON}
        -DIFCOPENSHELL_WASM_PLUGIN_ENTRIES=${ifcopenshell_wasm_plugin_entries_arg}
        -P "${CMAKE_CURRENT_SOURCE_DIR}/wasm_plugins.cmake"
    DEPENDS ifcopenshell_wasm_plugins_bundle
    VERBATIM
)
add_dependencies(ifcopenshell_wasm ifcopenshell_wasm_plugin_manifest)
add_dependencies(ifcopenshell_wasm_node ifcopenshell_wasm_plugin_manifest)
