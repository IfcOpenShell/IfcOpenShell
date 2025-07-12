get_property(IFCOPENSHELL_LIBRARIES GLOBAL PROPERTY IFCOPENSHELL_LIBRARIES)

if(WITH_CGAL AND CITYJSON_SUPPORT)
    # add_subdirectory(cityjson)
    message(STATUS "Building CityJSON support")
    set(CITYJSON_CONVERT_FILES
        cityjson/geobim.cpp
        cityjson/global_execution_context.cpp
        cityjson/opening_collector.cpp
        cityjson/processing.cpp
        cityjson/radius_comparison.cpp
        cityjson/radius_execution_context.cpp
        cityjson/settings.cpp
        cityjson/writer.cpp
    )
    # message(STATUS "CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}/src")
    # include_directories()
    add_library(cityjson_converter ${CITYJSON_CONVERT_FILES})
    message(STATUS "CityJSON converter IFCOPENSHELL_LIBRARIES: ${IFCOPENSHELL_LIBRARIES}")
    # target_link_libraries(cityjson_converter ${IFCOPENSHELL_LIBRARIES})
    target_link_libraries(cityjson_converter IfcParse)

    get_target_property(IfcParse_INCLUDE_DIRECTORIES IfcParse INCLUDE_DIRECTORIES)
    message(STATUS "IfcParse include directories: ${IfcParse_INCLUDE_DIRECTORIES}")

    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} cityjson_converter)
    set_property(GLOBAL PROPERTY IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES})

    install(TARGETS cityjson_converter
        ARCHIVE DESTINATION ${LIBDIR}
        LIBRARY DESTINATION ${LIBDIR}
    )

    # target_include_directories(cityjson_converter_exe PRIVATE ../src)
    add_executable(cityjson_converter_exe ${CITYJSON_CONVERT_FILES})
    set_target_properties(cityjson_converter_exe PROPERTIES COMPILE_FLAGS "-DCITYJSON_EXECUTABLE")
    target_link_libraries(cityjson_converter_exe ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})

    install(TARGETS cityjson_converter_exe
        RUNTIME DESTINATION ${BINDIR}
    )
endif()

# IfcConvert
if(WITH_RELATIONSHIP_VALIDATION)
    file(GLOB IFCCONVERT_CPP_FILES *.cpp)
    file(GLOB IFCCONVERT_H_FILES *.h)
else()
    file(GLOB IFCCONVERT_CPP_FILES IfcConvert.cpp)
    file(GLOB IFCCONVERT_H_FILES)
endif()
set(IFCCONVERT_FILES ${IFCCONVERT_CPP_FILES} ${IFCCONVERT_H_FILES})
add_executable(IfcConvert ${IFCCONVERT_FILES})

target_link_libraries(IfcConvert ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${HDF5_LIBRARIES} ${USD_LIBRARIES})
if(WITH_RELATIONSHIP_VALIDATION)
    set_property(TARGET IfcConvert APPEND_STRING PROPERTY COMPILE_FLAGS " -DWITH_RELATIONSHIP_VALIDATION")
endif()

if(WITH_CGAL AND CITYJSON_SUPPORT)
    set_property(TARGET IfcConvert APPEND_STRING PROPERTY COMPILE_FLAGS " -DIFOPSH_WITH_CITYJSON")
endif()

install(TARGETS IfcConvert
    ARCHIVE DESTINATION ${LIBDIR}
    LIBRARY DESTINATION ${LIBDIR}
    RUNTIME DESTINATION ${BINDIR}
)
