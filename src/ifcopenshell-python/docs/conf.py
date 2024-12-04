# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2020-2024 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

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

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "IfcOpenShell"
copyright = "2011-2024 IfcOpenShell Contributors"
author = "IfcOpenShell Contributors"

# The full version, including alpha/beta/rc tags
cwd = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(cwd, "..", "..", "..", "VERSION"), "r") as f:
    release = f.read().strip()

from docutils import nodes


def ios_python_url(name, rawtext, text, lineno, inliner, options={}, content=[]):
    url = f"https://github.com/IfcOpenShell/IfcOpenShell/releases/download/ifcopenshell-python-{release}/ifcopenshell-python-{release}-{text}.zip"
    node = nodes.reference(rawtext, text, refuri=url, **options)
    return [node], []


def ifcconvert_url(name, rawtext, text, lineno, inliner, options={}, content=[]):
    url = f"https://github.com/IfcOpenShell/IfcOpenShell/releases/download/ifcconvert-{release}/ifcconvert-{release}-{text}.zip"
    node = nodes.reference(rawtext, text, refuri=url, **options)
    return [node], []


def setup(app):
    app.add_role("ios_python_url", ios_python_url)
    app.add_role("ifcconvert_url", ifcconvert_url)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# I considered autodoc+autosummary but it had showstopper glitches:
# - Some modules couldn't be accessed https://github.com/sphinx-doc/sphinx/issues/7912#issuecomment-1120508738
# - No subnav making it really hard to navigate
# - Kinda hacky setup https://stackoverflow.com/questions/2701998/sphinx-autodoc-is-not-automatic-enough
# - I couldn't customise the template to show submodules above members which makes API discovery hard for users
extensions = ["autoapi.extension", "sphinx.ext.autosectionlabel", "sphinx_copybutton"]

# Auto add document prefixes to help guarantee uniqueness of automatic section references.
autosectionlabel_prefix_document = True

# We'll add the toctree entry ourselves to distinguish between C++ and Python
autoapi_add_toctree_entry = True

# We're only documenting Python here
autoapi_type = "python"

# autoapi works by reading source code instead of importing modules
autoapi_dirs = [
    "../ifcopenshell",
    "../../bcf/bcf",
    "../../bsdd",
    "../../ifccsv",
    "../../ifcdiff",
    "../../ifcpatch/ifcpatch",
    "../../ifctester/ifctester",
]
# autoapi_dirs = ['../../ifcdiff']
# autoapi_dirs = ['../../ifcdiff', '../ifcopenshell/util']
# autoapi_dirs = ['../../bcf/bcf', '../../bsdd', '../../ifccsv', '../../ifcdiff', '../../ifcpatch/ifcpatch', '../../ifctester/ifctester']

# These are auto-generated based on the IFC schema, so exclude them
autoapi_ignore = ["*ifcopenshell/express/rules*"]

# Custom autoapi templates to make it easier to read our docs
autoapi_template_dir = "_autoapi_templates"

# autoapi_options doesn't have show-module-summary, as it tends to create one
# page per function which contradicts the presentation of showing all functions
# as a list. This creates two possible locations where a function is documented
# which is really disorienting. I also exclude imported-members. For example,
# ifcopenshell.file is imported from ifcopenshell.file.file, but it gets pretty
# confusing to see the docs again in multiple places (seriously,
# ifcopenshell.file.file is everywhere).
autoapi_options = ["members", "undoc-members", "show-inheritance", "imported-members"]

# This option is set to both to allow both class docstrings and __init__ docstrings.
autoapi_python_class_content = "both"

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
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["custom.css"]

# Code block styles. Dark styling helps important code examples "pop" on the
# page even on light themes.
pygments_style = "one-dark"
pygments_dark_style = "one-dark"

html_favicon = "https://ifcopenshell.org/assets/images/logo.png"
html_logo = "https://ifcopenshell.org/assets/images/logo.png"
html_theme_options = {
    "source_repository": "https://github.com/IfcOpenShell/IfcOpenShell/",
    "source_branch": "v0.8.0",
    "source_directory": "src/ifcopenshell-python/docs/",
    "light_css_variables": {
        "color-brand-primary": "#39b54a",
        "color-brand-content": "#39b54a",
        "color-brand-visited": "#d9e021",
        "color-background-primary": "#f7f7f6",
        "color-background-secondary": "#eeeeec",
        "color-background-border": "#cfd0cb",
        "color-foreground-primary": "#2e3436",
        "color-sidebar-item-background--hover": "#f7f7f6",
        "color-link": "#39b54a",
        "color-link--visited": "#39b54a",
        "color-link--hover": "#d98014",
        "color-link--visited--hover": "#d98014",
        "font-stack": "Nunito, -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji",
    },
    "dark_css_variables": {
        "color-brand-primary": "#39b54a",
        "color-brand-content": "#39b54a",
        "color-brand-visited": "#d9e021",
        "color-background-primary": "#2e3436",
        "color-background-border": "#2e3436",
        "color-foreground-primary": "#eeeeec",
        "color-sidebar-item-background--hover": "#2e3436",
        "color-link": "#39b54a",
        "color-link--visited": "#39b54a",
        "color-link--hover": "#d98014",
        "color-link--visited--hover": "#d98014",
        "font-stack": "Nunito, -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji",
    },
    "footer_icons": [
        {
            "name": "IfcOpenShell",
            "url": "https://ifcopenshell.org",
            "html": """
                <img src="https://ifcopenshell.org/assets/images/logo.png" style="width: auto;" />
            """,
            "class": "",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/ifcopenshell-python/docs",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}
