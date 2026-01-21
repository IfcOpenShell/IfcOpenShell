file(GLOB IFCPARSE_H_FILES_ALL *.h)
file(GLOB IFCPARSE_CPP_FILES_ALL *.cpp)

foreach(file ${IFCPARSE_H_FILES_ALL})
    get_filename_component(filename "${file}" NAME)

    if(NOT "${filename}" MATCHES "[0-9]")
        list(APPEND IFCPARSE_H_FILES "${file}")
    endif()
endforeach()

foreach(file ${IFCPARSE_CPP_FILES_ALL})
    get_filename_component(filename "${file}" NAME)

    if(NOT "${filename}" MATCHES "[0-9]")
        list(APPEND IFCPARSE_CPP_FILES "${file}")
    endif()
endforeach()

foreach(schema ${SCHEMA_VERSIONS})
    list(APPEND IFCPARSE_H_FILES Ifc${schema}.h Ifc${schema}-definitions.h)
    list(APPEND IFCPARSE_CPP_FILES Ifc${schema}.cpp Ifc${schema}-schema.cpp)
endforeach()

set(IFCPARSE_FILES ${IFCPARSE_CPP_FILES} ${IFCPARSE_H_FILES})

add_library(IfcParse ${IFCPARSE_FILES})
target_compile_definitions(IfcParse PUBLIC ${SCHEMA_DEFINITIONS})
set_target_properties(
    IfcParse
    PROPERTIES
        COMPILE_FLAGS -DIFC_PARSE_EXPORTS
        VERSION "${PROJECT_VERSION}"
        SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
        PUBLIC_HEADER "${IFCPARSE_H_FILES}"
)

if(IFCXML_SUPPORT)
    find_package(LibXml2 REQUIRED)
    target_compile_definitions(IfcParse PUBLIC WITH_IFCXML)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_IFCXML PARENT_SCOPE)

    target_link_libraries(IfcParse LibXml2::LibXml2)
endif()

if(WASM_BUILD)
    target_link_libraries(IfcParse ${BCRYPT_LIBRARIES})
else()
    target_link_libraries(IfcParse ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES})
endif()

target_link_libraries(IfcParse ${ROCKSDB_LIBRARIES})

install(
    TARGETS IfcParse
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/ifcparse"
    INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
