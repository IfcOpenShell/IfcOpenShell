# This file was generated with the assistance of an AI coding tool.

import warnings
from pathlib import Path
from shutil import rmtree

from sphinx.deprecation import RemovedInSphinx90Warning

warnings.filterwarnings("ignore", category=RemovedInSphinx90Warning, module=r"exhale\.configs")

generated_directories = (
    Path(__file__).parent / "output" / "api",
    Path(__file__).parent / "output" / "doxygen",
)
for generated_directory in generated_directories:
    if generated_directory.is_dir():
        rmtree(generated_directory)

project = "IfcOpenShell"
copyright = "2020, IfcOpenShell"

extensions = [
    "breathe",
    "exhale",
]

primary_domain = "cpp"
highlight_language = "cpp"
html_theme = "alabaster"

breathe_projects = {
    "IfcOpenShell": "./output/doxygen/xml",
}
breathe_default_project = "IfcOpenShell"

exhale_args = {
    "containmentFolder": "./output/api",
    "rootFileName": "library_root.rst",
    "rootFileTitle": "IfcOpenShell C++ API",
    "doxygenStripFromPath": "../..",
    "createTreeView": False,
    "exhaleExecutesDoxygen": True,
    "exhaleUseDoxyfile": True,
}

cpp_id_attributes = [
    "IFC_PARSE_API",
    "IFC_SCHEMA_API",
    "IFC_GEOM_API",
    "IFC_GEOMLIBRARY_API",
    "IFC_GEOMSERIALIZATION_API",
    "SERIALIZERS_API",
]

exclude_patterns = [
    "output/doctrees",
    "output/doxygen",
    "output/html",
]
