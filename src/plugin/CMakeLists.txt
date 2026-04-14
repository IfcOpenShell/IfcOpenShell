file(GLOB PLUGIN_H_FILES *.h)
file(GLOB PLUGIN_CPP_FILES *.cpp)

add_library(plugin ${PLUGIN_CPP_FILES} ${PLUGIN_H_FILES})
set_target_properties(plugin PROPERTIES
    COMPILE_FLAGS "-DPLUGIN_EXPORTS"
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

target_compile_definitions(plugin PRIVATE
    BOOST_DLL_USE_STD_FS
    PLUGIN_IFCOPENSHELL_VERSION="${PROJECT_VERSION}"
)

target_link_libraries(plugin PRIVATE ${Boost_LIBRARIES})

install(TARGETS plugin)

install(FILES ${PLUGIN_H_FILES}
    DESTINATION ${INCLUDEDIR}/plugin
)
