add_subdirectory(schema_dependent)

file(GLOB SERIALIZERS_H_FILES *.h)
file(GLOB SERIALIZERS_CPP_FILES *.cpp)
file(GLOB SERIALIZERS_S_H_FILES schema_dependent/*.h)
set(SERIALIZERS_FILES ${SERIALIZERS_H_FILES} ${SERIALIZERS_CPP_FILES})

add_library(Serializers ${SERIALIZERS_FILES})
add_library(serialization ALIAS Serializers)
set_target_properties(Serializers PROPERTIES COMPILE_FLAGS "-DSERIALIZERS_EXPORTS" VERSION "${PROJECT_VERSION}" SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

if(WITH_PROJ)
    find_package(proj REQUIRED)
    target_compile_definitions(Serializers PRIVATE "WITH_PROJ")
    if(PROJ_STATIC)
        target_compile_definitions(Serializers PRIVATE "PROJ_DLL=")
    endif()
    target_link_libraries(Serializers PRIVATE proj::proj)
endif()

target_link_libraries(Serializers
    PRIVATE
    plugin ${OPENCOLLADA_LIBRARIES} ${USD_LIBRARIES}
    IfcGeom ${OpenCASCADE_LIBRARIES} IfcParse
)

if(WITH_OPENCASCADE)
    target_link_libraries(Serializers PRIVATE geometry_kernel_opencascade)
endif()

install(TARGETS Serializers ${document_serializer_libraries})

install(FILES ${SERIALIZERS_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/
)

install(FILES ${SERIALIZERS_S_H_FILES}
    DESTINATION ${INCLUDEDIR}/serializers/schema_dependent
)

set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} Serializers)
set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)
set(document_serializer_libraries ${document_serializer_libraries} PARENT_SCOPE)
