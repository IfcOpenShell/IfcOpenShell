add_subdirectory(schema_dependent)

file(GLOB SERIALIZERS_H_FILES *.h)
file(GLOB SERIALIZERS_CPP_FILES *.cpp)
set(SERIALIZERS_FILES ${SERIALIZERS_H_FILES} ${SERIALIZERS_CPP_FILES})

add_library(Serializers ${SERIALIZERS_FILES})
set_target_properties(
    Serializers
    PROPERTIES
        COMPILE_FLAGS "-DSERIALIZERS_EXPORTS"
        VERSION "${PROJECT_VERSION}"
        SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)
set(SERIALIZER_SCHEMA_LIBRARIES Serializers ${SERIALIZER_SCHEMA_LIBRARIES} PARENT_SCOPE)

if(WITH_PROJ)
    find_package(PROJ REQUIRED)
    target_compile_definitions(Serializers PRIVATE "WITH_PROJ")
    if(PROJ_STATIC)
        target_compile_definitions(Serializers PRIVATE "PROJ_DLL=")
    endif()
    target_link_libraries(Serializers PRIVATE PROJ::proj)
endif()

target_link_libraries(
    Serializers
    PRIVATE
        ${SERIALIZER_SCHEMA_LIBRARIES}
        ${OPENCOLLADA_LIBRARIES}
        ${USD_LIBRARIES}
        ${GLTF_LIBRARIES}
        IfcGeom
        ${OpenCASCADE_LIBRARIES}
        ${kernel_libraries}
        IfcParse
)

install(TARGETS Serializers EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

# Can't use `PUBLIC_HEADER` since we need two folders.
install(FILES ${SERIALIZERS_H_FILES} DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/serializers/")
install(FILES ${SERIALIZERS_S_H_FILES} DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/serializers/schema_dependent")
