set(IFCPARSE_WRAPPERGEN_GENERATED_DIR "${CMAKE_CURRENT_SOURCE_DIR}/generated")

option(IFCPARSE_WRAPPERGEN_REGENERATE "Regenerate the experimental wrappergen outputs before building." OFF)

if(IFCPARSE_WRAPPERGEN_REGENERATE)
    find_package(Python COMPONENTS Interpreter REQUIRED)
    set(IFCPARSE_WRAPPERGEN_GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")

    add_custom_command(
        OUTPUT
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental_c_api.h"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental_c_api.cpp"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/_ifcopenshell_experimental.cpp"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental.py"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}"
        COMMAND ${Python_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/generate.py"
            --repo-root "${PROJECT_SOURCE_DIR}/.."
            --output-dir "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}"
        DEPENDS
            "${CMAKE_CURRENT_SOURCE_DIR}/generate.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/config.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/model.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/clang_frontend.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/emit.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/conventions.py"
            "${PROJECT_SOURCE_DIR}/../src/ifcparse/file.h"
            "${PROJECT_SOURCE_DIR}/../src/ifcparse/express.h"
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        COMMENT "Regenerating experimental ifcparse wrapper outputs"
        VERBATIM
    )

    add_custom_target(
        ifcopenshell_experimental_generate
        DEPENDS
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental_c_api.h"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental_c_api.cpp"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/_ifcopenshell_experimental.cpp"
            "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental.py"
    )
endif()

find_package(Python COMPONENTS Development.Module REQUIRED)

add_library(_ifcopenshell_experimental MODULE
    "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/ifcopenshell_experimental_c_api.cpp"
    "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}/_ifcopenshell_experimental.cpp"
)

if(TARGET ifcopenshell_experimental_generate)
    add_dependencies(_ifcopenshell_experimental ifcopenshell_experimental_generate)
endif()

target_include_directories(_ifcopenshell_experimental PRIVATE
    "${IFCPARSE_WRAPPERGEN_GENERATED_DIR}"
    "${PROJECT_SOURCE_DIR}/../src/ifcparse"
)

target_link_libraries(_ifcopenshell_experimental PRIVATE
    IfcParse
    Python::Module
)

set_target_properties(_ifcopenshell_experimental PROPERTIES PREFIX "")

if(WASM_BUILD)
    set(PYTHON_EXTENSION_SUFFIX ".cpython-${Python_VERSION_MAJOR}${Python_VERSION_MINOR}-wasm32-emscripten.so")
elseif(WIN32)
    set(PYTHON_EXTENSION_SUFFIX ".${Python_SOABI}.pyd")
else()
    set(PYTHON_EXTENSION_SUFFIX ".${Python_SOABI}.so")
endif()

set_target_properties(_ifcopenshell_experimental PROPERTIES SUFFIX "${PYTHON_EXTENSION_SUFFIX}")
