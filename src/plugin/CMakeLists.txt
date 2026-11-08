file(GLOB PLUGIN_H_FILES *.h)
file(GLOB PLUGIN_CPP_FILES *.cpp)

add_library(plugin ${PLUGIN_CPP_FILES} ${PLUGIN_H_FILES})
set_target_properties(plugin PROPERTIES
    OUTPUT_NAME "ifcopenshell_plugin"
    COMPILE_FLAGS "-DPLUGIN_EXPORTS")
target_include_directories(plugin PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/..>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

if (NOT CREATE_BUNDLE)
set_target_properties(plugin PROPERTIES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)
endif()

target_compile_definitions(plugin PRIVATE
    BOOST_DLL_USE_STD_FS
    PLUGIN_IFCOPENSHELL_VERSION="${PROJECT_VERSION}"
    IFCOPENSHELL_INSTALL_PLUGIN_DIRECTORY="${CMAKE_INSTALL_FULL_LIBDIR}"
    # The postfix CMake gives this configuration's plug-ins (CMAKE_DEBUG_POSTFIX in a Debug
    # build, nothing otherwise), and the Debug postfix itself, so plug-in discovery only loads
    # modules built in the same configuration as the host.
    PLUGIN_MODULE_POSTFIX="$<$<CONFIG:Debug>:${CMAKE_DEBUG_POSTFIX}>"
    PLUGIN_DEBUG_MODULE_POSTFIX="${CMAKE_DEBUG_POSTFIX}"
)
target_compile_definitions(plugin PUBLIC $<$<BOOL:${IFOPSH_SAFE_INSTANCE}>:IFOPSH_SAFE_INSTANCE>)

target_link_libraries(plugin PRIVATE ${Boost_LIBRARIES})

install(TARGETS plugin EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${PLUGIN_H_FILES}
    DESTINATION ${INCLUDEDIR}/plugin
)
