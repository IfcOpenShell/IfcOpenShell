set(document_serializer_plugin_runtime_dir "$<TARGET_FILE_DIR:IfcGeom>")
set(geometry_serializer_plugin_runtime_dir "$<TARGET_FILE_DIR:IfcGeom>")

file(GLOB SERIALIZERS_H_FILES *.h)
file(GLOB SERIALIZERS_S_H_FILES schema_dependent/*.h)

if (NOT WASM_BUILD)
# wasm-ld (?) trips up on multiple defined symbols. IfcParse already brings
# in plugin so we skip it here.
set(plugin_when_not_wasm plugin)
endif()

function(add_document_serializer_plugin target output_name)
    cmake_parse_arguments(PLUGIN "" "" "SOURCES;LIBRARIES;DEFINITIONS" ${ARGN})
    string(REPLACE "." "_" plugin_output_name "${output_name}")

    add_library(${target} SHARED ${PLUGIN_SOURCES})
    target_compile_definitions(${target} PRIVATE SERIALIZERS_EXPORTS BOOST_DLL_USE_STD_FS ${PLUGIN_DEFINITIONS})
    target_link_libraries(${target} PRIVATE ${plugin_when_not_wasm} IfcGeom IfcParse ${PLUGIN_LIBRARIES})
    set_target_properties(${target} PROPERTIES
        OUTPUT_NAME "ifcopenshell_${plugin_output_name}"
        RUNTIME_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${document_serializer_plugin_runtime_dir}"
    )

    list(APPEND document_serializer_libraries ${target})
    set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)

    ifcopenshell_wasm_plugin_link_options(${target} ifcopenshell_register_document_serializer_plugin_v1)
endfunction()

function(add_geometry_serializer_plugin target output_name)
    cmake_parse_arguments(PLUGIN "" "" "SOURCES;LIBRARIES;DEFINITIONS" ${ARGN})
    string(REPLACE "." "_" plugin_output_name "${output_name}")

    add_library(${target} SHARED ${PLUGIN_SOURCES})
    target_compile_definitions(${target} PRIVATE SERIALIZERS_EXPORTS BOOST_DLL_USE_STD_FS ${PLUGIN_DEFINITIONS})
    target_link_libraries(${target} PRIVATE ${plugin_when_not_wasm} IfcGeom IfcParse ${PLUGIN_LIBRARIES})
    if(WITH_PROJ)
        find_package(PROJ ${PROJ_MIN_VERSION} REQUIRED)
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

    list(APPEND geometry_serializer_libraries ${target})
    set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)

    ifcopenshell_wasm_plugin_link_options(${target} ifcopenshell_register_geometry_serializer_plugin_v1)

endfunction()

if(WITH_ROCKSDB)
    add_document_serializer_plugin(document_serializer_rdb "document.rdb" SOURCES document_rdb_plugin.cpp rocks_db_serializer.cpp LIBRARIES ${IFCOPENSHELL_ROCKSDB_TARGET})
    # Still not fully a plugin and ifcwrap depends on it directly.
    install(TARGETS document_serializer_rdb EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endif()

add_subdirectory(schema_dependent)

if (NOT WASM_BUILD)
set(ttl_geometry_serializer_libraries)
if(WITH_OPENCASCADE)
    set(ttl_geometry_serializer_libraries geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES})
endif()
add_geometry_serializer_plugin(geometry_serializer_ttl "geometry.ttl" SOURCES geometry_ttl_plugin.cpp ttl_wkt_serializer.cpp LIBRARIES ${ttl_geometry_serializer_libraries})
endif()

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

if(WITH_OPENCASCADE AND NOT WASM_BUILD)
    set(opencascade_geometry_serializer_libraries geometry_kernel_opencascade ${OpenCASCADE_LIBRARIES})
    add_geometry_serializer_plugin(geometry_serializer_stp "geometry.stp" SOURCES geometry_stp_plugin.cpp open_cascade_based_serializer.cpp LIBRARIES ${opencascade_geometry_serializer_libraries})
    add_geometry_serializer_plugin(geometry_serializer_igs "geometry.igs" SOURCES geometry_igs_plugin.cpp open_cascade_based_serializer.cpp LIBRARIES ${opencascade_geometry_serializer_libraries})
    add_geometry_serializer_plugin(geometry_serializer_svg "geometry.svg" SOURCES geometry_svg_plugin.cpp svg_serializer.cpp util.cpp LIBRARIES ${opencascade_geometry_serializer_libraries})
endif()

# .ifcview: the viewer's cached-geometry format (instanced, Morton-chunked,
# zstd-compressed). The plugin compiles the ifcviewer sidecar sources directly
# (no Qt, no wgpu) so it writes exactly the layout the viewer/loader expect.
if(NOT WASM_BUILD)
    find_package(zstd ${ZSTD_MIN_VERSION} CONFIG REQUIRED)
    # The imported Eigen target is directory-scoped (created by ifcgeom), so
    # this directory needs its own lookup before it can link against it.
    find_package(Eigen3 ${EIGEN_MIN_VERSION} REQUIRED)
    set(ifcviewer_sidecar_dir ${CMAKE_CURRENT_SOURCE_DIR}/../ifcviewer)
    add_geometry_serializer_plugin(geometry_serializer_ifcview "geometry.ifcview"
        SOURCES
            geometry_ifcview_plugin.cpp
            ${ifcviewer_sidecar_dir}/IfcViewSerializer.cpp
            ${ifcviewer_sidecar_dir}/SidecarSerializer.cpp
            ${ifcviewer_sidecar_dir}/StreamedRecords.cpp
            ${ifcviewer_sidecar_dir}/SidecarCache.cpp
            ${ifcviewer_sidecar_dir}/SidecarCompress.cpp
            ${ifcviewer_sidecar_dir}/SidecarLayout.cpp
            ${ifcviewer_sidecar_dir}/ChunkPlanner.cpp
            ${ifcviewer_sidecar_dir}/LodBuilder.cpp
        LIBRARIES Eigen3::Eigen zstd::libzstd_static
    )
    target_include_directories(geometry_serializer_ifcview PRIVATE ${ifcviewer_sidecar_dir})
    if(WITH_MESH_OPTIMIZER)
        find_package(meshoptimizer REQUIRED)
        target_compile_definitions(geometry_serializer_ifcview PRIVATE WITH_MESH_OPTIMIZER)
        target_link_libraries(geometry_serializer_ifcview PRIVATE meshoptimizer::meshoptimizer)
    endif()
    if(UNIX AND NOT APPLE)
        find_package(Threads REQUIRED)
        target_link_libraries(geometry_serializer_ifcview PRIVATE Threads::Threads)
    endif()
endif()

install(TARGETS ${document_serializer_libraries} ${geometry_serializer_libraries})
ifcopenshell_install_runtime_dlls(TARGETS ${document_serializer_libraries} ${geometry_serializer_libraries})

install(FILES ${SERIALIZERS_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/
)

install(FILES ${SERIALIZERS_S_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/schema_dependent
)
set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)
set(geometry_serializer_libraries ${geometry_serializer_libraries} PARENT_SCOPE)
