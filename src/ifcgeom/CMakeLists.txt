add_subdirectory(kernels)
set(kernel_libraries ${kernel_libraries} PARENT_SCOPE)

if((BUILD_CONVERT OR BUILD_IFCPYTHON) AND WITH_OPENCASCADE)
    add_subdirectory(Serialization)
    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} PARENT_SCOPE)
endif()

