find_package(Eigen3 REQUIRED)

set(mapping_plugin_runtime_dir "${CMAKE_BINARY_DIR}/ifcgeom/$<CONFIG>")

if (NOT WASM_BUILD)
# wasm-ld (?) trips up on multiple defined symbols. IfcParse already brings
# in plugin so we skip it here.
set(plugin_when_not_wasm plugin)
endif()

foreach(schema ${SCHEMA_VERSIONS})
    file(GLOB IFCGEOM_I_FILES *.i)
    file(GLOB IFCGEOM_H_FILES *.h)
    file(GLOB IFCGEOM_CPP_FILES *.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})

    add_library(geometry_mapping_ifc${schema} SHARED ${IFCGEOM_FILES})
    set_target_properties(geometry_mapping_ifc${schema} PROPERTIES
        COMPILE_FLAGS "-DIfcSchema=Ifc${schema}"
        OUTPUT_NAME "geometry.mapping.ifc${schema}"
        RUNTIME_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
        LIBRARY_OUTPUT_DIRECTORY "${mapping_plugin_runtime_dir}"
    )

    if (WASM_BUILD)
        target_link_options(
            geometry_mapping_ifc${schema}
            PRIVATE "SHELL:-s -s SIDE_MODULE=1"
        )
    endif()

    target_link_libraries(geometry_mapping_ifc${schema} PRIVATE ${plugin_when_not_wasm} IfcGeom IfcParse Eigen3::Eigen)

    list(APPEND mapping_libraries geometry_mapping_ifc${schema})

    install(TARGETS geometry_mapping_ifc${schema})
endforeach()

set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)
