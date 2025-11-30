find_package(Eigen3 REQUIRED)

foreach(schema ${SCHEMA_VERSIONS})
    file(GLOB IFCGEOM_I_FILES *.i)
    file(GLOB IFCGEOM_H_FILES *.h)
    file(GLOB IFCGEOM_CPP_FILES *.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})

    add_library(geometry_mapping_ifc${schema} OBJECT ${IFCGEOM_FILES})
    set_target_properties(geometry_mapping_ifc${schema} PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}")
    target_link_libraries(geometry_mapping_ifc${schema} IfcParse  Eigen3::Eigen)

    list(APPEND mapping_libraries geometry_mapping_ifc${schema})

    install(TARGETS geometry_mapping_ifc${schema})
endforeach()

set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)
