# This file was generated with the assistance of an AI coding tool.

# Builds the documentation that is published to https://docs.ifcopenshell.org.
#
# Configure the main project with -DBUILD_DOCUMENTATION=ON, or add this
# directory as a subdirectory of your own project, and then build the ``docs``
# target. Before doing so, install the Python dependencies from
# requirements.txt, and make sure that Doxygen and Graphviz are on PATH for the
# C++ API reference.

find_package(Doxygen REQUIRED)

find_program(
    SPHINX_EXECUTABLE
    NAMES sphinx-build
    REQUIRED
    DOC "Path to the sphinx-build executable"
)

add_custom_target(
    docs
    COMMAND ${SPHINX_EXECUTABLE} -M html . _build
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating the IfcOpenShell documentation"
    USES_TERMINAL
    VERBATIM
)
