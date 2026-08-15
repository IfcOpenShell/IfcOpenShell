file(GLOB IFCPARSE_H_FILES_ALL *.h)
file(GLOB IFCPARSE_CPP_FILES_ALL *.cpp)

foreach(file ${IFCPARSE_H_FILES_ALL})
    get_filename_component(filename "${file}" NAME)
    list(APPEND IFCPARSE_H_FILES "${file}")
endforeach()

foreach(file ${IFCPARSE_CPP_FILES_ALL})
    get_filename_component(filename "${file}" NAME)
    list(APPEND IFCPARSE_CPP_FILES "${file}")
endforeach()

list(REMOVE_ITEM IFCPARSE_CPP_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/schema_plugin.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/alignment_helper.cpp
)

message(STATUS "SCHEMA_VERSIONS from ifcparse: ${SCHEMA_VERSIONS}")
foreach(schema ${SCHEMA_VERSIONS})
    list(APPEND IFCPARSE_SCHEMA_H_FILES
        schemas/Ifc${schema}.h
        schemas/Ifc${schema}-definitions.h
    )
endforeach()

list(APPEND IFCPARSE_SCHEMA_H_FILES
    schemas/Header_section_schema.h
)
list(APPEND IFCPARSE_CPP_FILES
    schemas/Header_section_schema.cpp
    schemas/Header_section_schema-schema.cpp
)

set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES} ${IFCPARSE_SCHEMA_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
set_target_properties(IfcParse PROPERTIES
        OUTPUT_NAME "ifcopenshell.parse"
)
target_include_directories(IfcParse PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/..>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

if((NOT WIN32) AND BUILD_SHARED_LIBS AND NOT WASM_BUILD AND NOT CREATE_BUNDLE AND NOT CMAKE_INSTALL_RPATH AND COMMAND SET_INSTALL_SELF_RPATH)
    SET_INSTALL_SELF_RPATH(IfcParse)
endif()
target_compile_definitions(IfcParse PUBLIC ${SCHEMA_DEFINITIONS})
if(USE_MMAP)
    target_compile_definitions(IfcParse PUBLIC USE_MMAP)
endif()
if(WITH_ROCKSDB)
    target_compile_definitions(IfcParse PUBLIC IFOPSH_WITH_ROCKSDB)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_ROCKSDB PARENT_SCOPE)
endif()
set_target_properties(IfcParse PROPERTIES COMPILE_FLAGS -DIFC_PARSE_EXPORTS)
if (NOT CREATE_BUNDLE)
    set_target_properties(IfcParse PROPERTIES VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")
endif()
if(WASM_BUILD)
    target_link_libraries(IfcParse plugin ${BCRYPT_LIBRARIES})
else()
    target_link_libraries(IfcParse plugin ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES})
endif()

if(WITH_ROCKSDB)
    target_link_libraries(IfcParse ${IFCOPENSHELL_ROCKSDB_TARGET})
    if(WITH_ZSTD)
        target_link_libraries(IfcParse zstd::libzstd_static)
    endif()
endif()

if(WASM_BUILD)
    ifcopenshell_wasm_define_main_import_target(IfcParse)
endif()

ifcopenshell_wasm_plugin_dependency(plugin_when_not_wasm)

foreach(schema ${SCHEMA_VERSIONS})
    set(SCHEMA_PLUGIN_TARGET parse_schema_ifc${schema})
    set(SCHEMA_PLUGIN_SOURCES
        schema_plugin.cpp
        hierarchy_helper.i
        schemas/Ifc${schema}.cpp
        schemas/Ifc${schema}-schema.cpp
    )
    if(schema STREQUAL "4x3_add2")
        list(APPEND SCHEMA_PLUGIN_SOURCES alignment_helper.cpp)
    endif()

    add_library(${SCHEMA_PLUGIN_TARGET} SHARED ${SCHEMA_PLUGIN_SOURCES})
    target_compile_definitions(${SCHEMA_PLUGIN_TARGET} PRIVATE
        IFC_SCHEMA_EXPORTS
        BOOST_DLL_USE_STD_FS
        IfcSchema=Ifc${schema}
    )
    set_target_properties(${SCHEMA_PLUGIN_TARGET} PROPERTIES
        OUTPUT_NAME "ifcopenshell_parse_schema_ifc${schema}"
    )
    ifcopenshell_plugin_target(${SCHEMA_PLUGIN_TARGET})
    if(WASM_BUILD)
        ifcopenshell_wasm_configure_plugin_target(
            ${SCHEMA_PLUGIN_TARGET}
            KIND schema
            ID "ifc${schema}"
            SYMBOL_ID "ifc${schema}"
            EXPORT_SYMBOL "ifcopenshell_emscripten_register_schema_ifc${schema}"
        )
        ifcopenshell_wasm_plugin_link_options(${SCHEMA_PLUGIN_TARGET} ifcopenshell_register_schema_plugin_v1 EXPORT_DYNAMIC)
        ifcopenshell_wasm_plugin_target_link(${SCHEMA_PLUGIN_TARGET}
            MAIN_TARGETS IfcParse
            PRIVATE ${plugin_when_not_wasm}
        )
    else()
        ifcopenshell_wasm_plugin_target_link(${SCHEMA_PLUGIN_TARGET}
            MAIN_TARGETS IfcParse
            PRIVATE ${plugin_when_not_wasm}
        )
    endif()

    list(APPEND schema_libraries ${SCHEMA_PLUGIN_TARGET})
endforeach()

# CMake installation targets
install(FILES ${IFCPARSE_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcparse
)

install(FILES ${IFCPARSE_SCHEMA_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcparse/schemas
)

install(
    TARGETS IfcParse ${schema_libraries}
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
)

set(schema_libraries ${schema_libraries} PARENT_SCOPE)
