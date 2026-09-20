# Configuration file for the Sphinx documentation builder.

import os
from datetime import datetime

project = "Bonsai Viewer"
copyright = f"2020-{datetime.now().year} IfcOpenShell Contributors"
author = "IfcOpenShell Contributors"

cwd = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(cwd, "..", "..", "..", "VERSION"), "r") as f:
    release = f.read().strip()


extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosectionlabel", "sphinx_copybutton"]

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]


html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

pygments_style = "one-dark"
pygments_dark_style = "one-dark"

html_favicon = "https://ifcopenshell.org/assets/images/logo.png"
html_logo = "https://ifcopenshell.org/assets/images/logo.png"
html_theme_options = {
    "source_repository": "https://github.com/IfcOpenShell/IfcOpenShell/",
    "source_branch": "v0.8.0",
    "source_directory": "src/bonsaiviewer/docs/",
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
        "color-admonition-text": "#651fff",
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
        "color-admonition-text": "#EEEEEC",
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
            "url": "https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/bonsaiviewer/docs",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}
