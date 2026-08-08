find_package(Doxygen REQUIRED)
find_program(
    SPHINX_EXECUTABLE
    NAMES sphinx-build
    REQUIRED
    DOC "Path to the sphinx-build executable"
)

add_custom_target(
    cpp_api_docs
    COMMAND ${SPHINX_EXECUTABLE} -M html . output -W --keep-going
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating the IfcOpenShell C++ API documentation"
    VERBATIM
)
