# This file was generated with the assistance of an AI coding tool.

import re
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


def fix_generated_api_pages(app):
    for node in app.exhale_root.all_nodes:
        nested_type = (
            node.kind in ("class", "struct") and node.parent is not None and node.parent.kind in ("class", "struct")
        )
        if node.kind != "function" and not nested_type:
            continue
        path = Path(app.exhale_root.root_directory) / node.file_name
        source = path.read_text(encoding="utf-8")
        if node.kind == "function":
            # Exhale 0.3.7 emits unescaped function names in RST headings.
            title = re.sub(r"(?<!\\)_", r"\\_", node.title)
            source = source.replace(
                f"{node.title}\n{'=' * len(node.title)}",
                f"{title}\n{'=' * len(title)}",
                1,
            )
        if nested_type:
            # Breathe already renders the nested type and its members on the parent page.
            directive = f".. doxygen{node.kind}:: {node.breathe_identifier()}"
            source = source.split(directive, 1)[0]
            source += f"See :ref:`{node.parent.link_name}` for this nested type's documentation.\n"
        path.write_text(source, encoding="utf-8")


def setup(app):
    app.connect("builder-inited", fix_generated_api_pages, priority=600)
