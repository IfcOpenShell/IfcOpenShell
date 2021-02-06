import textwrap
# The `extensions` list should already be in here from `sphinx-quickstart`
extensions = [
    # there may be others here already, e.g. 'sphinx.ext.mathjax'
    'breathe',
    'exhale',
    'sphinx.ext.intersphinx'
]

project = 'IfcOpenShell'
copyright = '2020, IfcOpenShell'
author = ''

# Setup the breathe extension
breathe_projects = {
    "My Project": "./output/doxygen/xml"
}
breathe_default_project = "My Project"

# Setup the exhale extension
exhale_args = {
    # These arguments are required
    "containmentFolder":     "./rst_files",
    "rootFileName":          "library_root.rst",
    "rootFileTitle":         "IfcOpenShell C++",
    "doxygenStripFromPath":  "..",
    # Suggested optional arguments
    "createTreeView":        True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    # "treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    # "exhaleDoxygenStdin":    "INPUT = ../src/serializers/ ../src/ifcgeom",
    "exhaleUseDoxyfile": True

}

cpp_id_attributes = ['IFC_PARSE_API', 'IFC_GEOM_API']
