# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = "IfcOpenShell"
copyright = "2020-2022, IfcOpenShell Contributors"
author = "IfcOpenShell Contributors"

# The full version, including alpha/beta/rc tags
release = "0.7.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# I considered autodoc+autosummary but it had showstopper glitches:
# - Some modules couldn't be accessed https://github.com/sphinx-doc/sphinx/issues/7912#issuecomment-1120508738
# - No subnav making it really hard to navigate
# - Kinda hacky setup https://stackoverflow.com/questions/2701998/sphinx-autodoc-is-not-automatic-enough
# - I couldn't customise the template to show submodules above members which makes API discovery hard for users
extensions = ["autoapi.extension"]

# We're only documenting Python here
autoapi_type = 'python'

# autoapi works by reading source code instead of importing modules
autoapi_dirs = ['../ifcopenshell', '../../ifcdiff']

# autoapi_options doesn't have show-module-summary, as it tends to create one
# page per function which contradicts the presentation of showing all functions
# as a list. This creates two possible locations where a function is documented
# which is really disorienting. I also exclude imported-members. For example,
# ifcopenshell.file is imported from ifcopenshell.file.file, but it gets pretty
# confusing to see the docs again in multiple places (seriously,
# ifcopenshell.file.file is everywhere).
autoapi_options = ['members', 'undoc-members', 'private-members', 'special-members', 'show-inheritance']

# This option is set to both to allow both class docstrings and __init__ docstrings.
autoapi_python_class_content = 'both'

# Group by type (e.g. attribute, class, function, etc) then alphabetically.
autoapi_member_order = "groupwise"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["custom.css"]
