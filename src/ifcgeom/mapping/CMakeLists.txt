find_package(Eigen3 REQUIRED)

# When using `ENABLE_BUILD_OPTIMIZATIONS``/GL` compilation flags makes resulting mapping libs huge (e.g. 1.5GB each)
# and combining them together to a single IfcGeom won't be possible due to 4GB file size limit.
# So in this case we have to ensure each mapping is built as separate libs instead of .obj files to be linked together.
if(ENABLE_BUILD_OPTIMIZATIONS AND MSVC)
    set(mapping_library_type "STATIC")
else()
    set(mapping_library_type "OBJECT")
endif()

foreach(schema ${SCHEMA_VERSIONS})
    file(GLOB IFCGEOM_I_FILES *.i)
    file(GLOB IFCGEOM_H_FILES *.h)
    file(GLOB IFCGEOM_CPP_FILES *.cpp)
    set(IFCGEOM_FILES ${IFCGEOM_CPP_FILES} ${IFCGEOM_H_FILES} ${IFCGEOM_I_FILES})

    add_library(geometry_mapping_ifc${schema} ${mapping_library_type} ${IFCGEOM_FILES})
    set_target_properties(
        geometry_mapping_ifc${schema}
        PROPERTIES COMPILE_FLAGS "-DIFC_GEOM_EXPORTS -DIfcSchema=Ifc${schema}"
    )
    target_link_libraries(geometry_mapping_ifc${schema} IfcParse Eigen3::Eigen)

    list(APPEND mapping_libraries geometry_mapping_ifc${schema})
    install(TARGETS geometry_mapping_ifc${schema} EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
endforeach()

set(mapping_libraries ${mapping_libraries} PARENT_SCOPE)
