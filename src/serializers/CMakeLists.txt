set(document_serializer_plugin_runtime_dir "$<TARGET_FILE_DIR:IfcGeom>")
set(geometry_serializer_plugin_runtime_dir "$<TARGET_FILE_DIR:IfcGeom>")
ifcopenshell_wasm_plugin_dependency(plugin_when_not_wasm)

file(GLOB SERIALIZERS_H_FILES *.h)
file(GLOB SERIALIZERS_S_H_FILES schema_dependent/*.h)

function(add_document_serializer_plugin target output_name)
    cmake_parse_arguments(PLUGIN "" "" "SOURCES;LIBRARIES;DEFINITIONS" ${ARGN})
    string(REPLACE "." "_" plugin_output_name "${output_name}")

    add_library(${target} SHARED ${PLUGIN_SOURCES})
    target_compile_definitions(${target} PRIVATE SERIALIZERS_EXPORTS BOOST_DLL_USE_STD_FS ${PLUGIN_DEFINITIONS})
    ifcopenshell_wasm_plugin_target_link(${target}
        MAIN_TARGETS IfcGeom IfcParse
        PRIVATE ${plugin_when_not_wasm} ${PLUGIN_LIBRARIES}
    )
    set_target_properties(${target} PROPERTIES
        OUTPUT_NAME "ifcopenshell_${plugin_output_name}"
        RUNTIME_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
    )
    ifcopenshell_native_plugin_target(${target} IfcGeom)

    list(APPEND document_serializer_libraries ${target})
    set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)

    string(REGEX REPLACE "^document\\." "" plugin_id "${output_name}")
    ifcopenshell_wasm_plugin_link_options(${target} ifcopenshell_register_document_serializer_plugin_v1)
    if(WASM_BUILD)
        string(REPLACE "." "_" plugin_symbol_id "${plugin_id}")
        ifcopenshell_wasm_configure_plugin_target(
            ${target}
            KIND document
            ID "${plugin_id}"
            SYMBOL_ID "${plugin_symbol_id}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_document_serializer_${plugin_symbol_id}"
        )
    endif()
endfunction()

function(add_geometry_serializer_plugin target output_name)
    cmake_parse_arguments(PLUGIN "" "WASM_DEPENDS" "SOURCES;LIBRARIES;DEFINITIONS" ${ARGN})
    string(REPLACE "." "_" plugin_output_name "${output_name}")

    add_library(${target} SHARED ${PLUGIN_SOURCES})
    target_compile_definitions(${target} PRIVATE SERIALIZERS_EXPORTS BOOST_DLL_USE_STD_FS ${PLUGIN_DEFINITIONS})
    if(WITH_OPENCASCADE AND OCC_INCLUDE_DIR)
        # OCCT headers are needed for compilation even when not linking against the kernel.
        target_include_directories(${target} PRIVATE "${OCC_INCLUDE_DIR}")
    endif()
    ifcopenshell_wasm_plugin_target_link(${target}
        MAIN_TARGETS IfcGeom IfcParse
        PRIVATE ${plugin_when_not_wasm} ${PLUGIN_LIBRARIES}
    )
    if(WITH_PROJ)
        find_package(proj REQUIRED)
        target_compile_definitions(${target} PRIVATE "WITH_PROJ")
        if(PROJ_STATIC)
            target_compile_definitions(${target} PRIVATE "PROJ_DLL=")
        endif()
        target_link_libraries(${target} PRIVATE proj::proj)
    endif()
    set_target_properties(${target} PROPERTIES
        OUTPUT_NAME "ifcopenshell_${plugin_output_name}"
        RUNTIME_OUTPUT_DIRECTORY "${geometry_serializer_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${geometry_serializer_plugin_runtime_dir}"
    )
    ifcopenshell_native_plugin_target(${target} IfcGeom)

    list(APPEND geometry_serializer_libraries ${target})
    set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)

    string(REGEX REPLACE "^geometry\\." "" plugin_id "${output_name}")
    ifcopenshell_wasm_plugin_link_options(${target} ifcopenshell_register_geometry_serializer_plugin_v1)
    if(WASM_BUILD)
        ifcopenshell_wasm_configure_plugin_target(
            ${target}
            KIND geometry_serializer
            ID "${plugin_id}"
            SYMBOL_ID "${plugin_id}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_geometry_serializer_${plugin_id}"
            DEPENDS ${PLUGIN_WASM_DEPENDS}
        )
    endif()
endfunction()

if(WITH_ROCKSDB)
    add_document_serializer_plugin(document_serializer_rdb "document.rdb" SOURCES document_rdb_plugin.cpp rocks_db_serializer.cpp LIBRARIES ${IFCOPENSHELL_ROCKSDB_TARGET})
endif()

add_subdirectory(schema_dependent)

set(ttl_geometry_serializer_libraries)
set(ttl_geometry_serializer_wasm_depends)
if(WITH_OPENCASCADE)
    if(WASM_BUILD)
        set(ttl_geometry_serializer_wasm_depends "kernel:opencascade")
    else()
        set(ttl_geometry_serializer_libraries geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES})
    endif()
endif()
add_geometry_serializer_plugin(
    geometry_serializer_ttl
    "geometry.ttl"
    SOURCES geometry_ttl_plugin.cpp ttl_wkt_serializer.cpp
    LIBRARIES ${ttl_geometry_serializer_libraries}
    WASM_DEPENDS ${ttl_geometry_serializer_wasm_depends}
)

add_geometry_serializer_plugin(geometry_serializer_obj "geometry.obj" SOURCES geometry_obj_plugin.cpp wavefront_obj_serializer.cpp)

if(OPENCOLLADA_FOUND)
    add_geometry_serializer_plugin(geometry_serializer_dae "geometry.dae" SOURCES geometry_dae_plugin.cpp collada_serializer.cpp LIBRARIES OpenCOLLADA::OpenCOLLADA DEFINITIONS WITH_OPENCOLLADA)
endif()

if(GLTF_SUPPORT)
    add_geometry_serializer_plugin(geometry_serializer_glb "geometry.glb" SOURCES geometry_glb_plugin.cpp gltf_serializer.cpp LIBRARIES nlohmann_json::nlohmann_json DEFINITIONS WITH_GLTF)
endif()

if(USD_SUPPORT)
    add_geometry_serializer_plugin(geometry_serializer_usd "geometry.usd" SOURCES geometry_usd_plugin.cpp usd_serializer.cpp LIBRARIES pxr::USD)
endif()

if(WITH_OPENCASCADE)
    if(WASM_BUILD)
        set(opencascade_geometry_serializer_wasm_depends "kernel:opencascade")
    else()
        set(opencascade_geometry_serializer_libraries geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES})
    endif()
    add_geometry_serializer_plugin(geometry_serializer_stp "geometry.stp"
        SOURCES geometry_stp_plugin.cpp open_cascade_based_serializer.cpp
        LIBRARIES ${opencascade_geometry_serializer_libraries}
        WASM_DEPENDS ${opencascade_geometry_serializer_wasm_depends})
    add_geometry_serializer_plugin(geometry_serializer_igs "geometry.igs"
        SOURCES geometry_igs_plugin.cpp open_cascade_based_serializer.cpp
        LIBRARIES ${opencascade_geometry_serializer_libraries}
        WASM_DEPENDS ${opencascade_geometry_serializer_wasm_depends})
    add_geometry_serializer_plugin(geometry_serializer_svg "geometry.svg"
        SOURCES geometry_svg_plugin.cpp svg_serializer.cpp util.cpp
        LIBRARIES ${opencascade_geometry_serializer_libraries}
        WASM_DEPENDS ${opencascade_geometry_serializer_wasm_depends})
endif()

install(TARGETS ${document_serializer_libraries} ${geometry_serializer_libraries})

install(FILES ${SERIALIZERS_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/
)

install(FILES ${SERIALIZERS_S_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/schema_dependent
)
set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)
set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
