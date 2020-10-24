# The `extensions` list should already be in here from `sphinx-quickstart`
extensions = [
    # there may be others here already, e.g. 'sphinx.ext.mathjax'
    'breathe',
    'exhale',
    'sphinx.ext.intersphinx'
]

project = u'IfcOpenShell'
copyright = u'2020, IfcOpenShell'
author = u'Johan Luttun'

# Setup the breathe extension
# breathe_projects = {
#     "My Project": "./doxygen/xml"
# }
breathe_projects = {
    "My Project": "./output/doxygen/xml"
}
breathe_default_project = "My Project"

# Setup the exhale extension
exhale_args = {
    # These arguments are required
    "containmentFolder":     "./rst_files",
    "rootFileName":          "library_root.rst",
    "rootFileTitle":         "IfcOpenShell",
    "doxygenStripFromPath":  "..",
    # Suggested optional arguments
    "createTreeView":        True,
    # TIP: if using the sphinx-bootstrap-theme, you need
    # "treeViewIsBootstrap": True,
    "exhaleExecutesDoxygen": True,
    "exhaleDoxygenStdin":    "INPUT = ../src/testdoc ../src/ifcconvert"
}

# html_theme = 'sphinx_rtd_theme'
# html_theme = 'classic'

# Tell sphinx what the primary language being documented is.
primary_domain = 'cpp'

# Tell sphinx what the pygments highlight language should be.
highlight_language = 'cpp'

# html_sidebars = {
#    '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
#    'using/windows': ['windowssidebar.html', 'searchbox.html'],
# }




# html_sidebars = {'**': ['logo-text.html', 'globaltoc.html', 'searchbox.html']}

# html_theme_options = {
#     'navigation_depth': 4,
# }