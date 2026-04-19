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

message(STATUS "SCHEMA_VERSIONS from ifcparse: ${SCHEMA_VERSIONS}")
foreach(schema ${SCHEMA_VERSIONS})
    list(APPEND IFCPARSE_H_FILES
        schemas/Ifc${schema}.h
        schemas/Ifc${schema}-definitions.h
    )
    list(APPEND IFCPARSE_CPP_FILES
        schemas/Ifc${schema}.cpp
        schemas/Ifc${schema}-schema.cpp
    )
endforeach()

list(APPEND IFCPARSE_H_FILES
    schemas/Header_section_schema.h
)
list(APPEND IFCPARSE_CPP_FILES
    schemas/Header_section_schema.cpp
    schemas/Header_section_schema-schema.cpp
)

set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
add_library(parse ALIAS IfcParse)
target_compile_definitions(IfcParse PUBLIC ${SCHEMA_DEFINITIONS})
set_target_properties(IfcParse PROPERTIES COMPILE_FLAGS -DIFC_PARSE_EXPORTS VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

if(WASM_BUILD)
    target_link_libraries(IfcParse plugin ${BCRYPT_LIBRARIES})
else()
    target_link_libraries(IfcParse plugin ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES})
endif()

# CMake installation targets
install(FILES ${IFCPARSE_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcparse
)

install(TARGETS IfcParse)
