"""Package tests that fail when a plug-in packaged with BonsaiViewer can't be loaded.

Runs `BonsaiViewer --list-plugins`, which tries to load every plug-in next to the executable.
"""

import functools
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from run_against_package import run_bonsaiviewer

BONSAIVIEWER = os.environ.get("IFCOPENSHELL_PACKAGE_TESTS_BONSAIVIEWER")
if BONSAIVIEWER is None:
    pytest.skip("BonsaiViewer is not provided (--skip-bonsaiviewer).", allow_module_level=True)

PLUGINS = [
    "ifcopenshell_document_rdb",
    "ifcopenshell_geometry_kernel_cgal",
    "ifcopenshell_geometry_kernel_cgalsimple",
    "ifcopenshell_geometry_kernel_manifold",
    "ifcopenshell_geometry_kernel_opencascade",
    "ifcopenshell_geometry_kernel_passthrough",
    "ifcopenshell_geometry_mapping_ifc2x3",
    "ifcopenshell_geometry_mapping_ifc4",
    "ifcopenshell_geometry_mapping_ifc4x3_add2",
    "ifcopenshell_parse_schema_ifc2x3",
    "ifcopenshell_parse_schema_ifc4",
    "ifcopenshell_parse_schema_ifc4x3_add2",
]
# E.g.:
# OK    ifcopenshell_parse_schema_ifc4.so (parse_schema, ...)
# FAIL  ifcopenshell_parse_schema_ifc4.so: error
LINE_PATTERN = re.compile(r"(OK|FAIL)\s+(ifcopenshell_\w+)\.\w+")


@functools.cache
def list_plugins() -> subprocess.CompletedProcess[str]:
    return run_bonsaiviewer(BONSAIVIEWER, "--list-plugins")


def get_plugin_statuses() -> dict[str, str]:
    return {m[2]: m[1] for line in list_plugins().stdout.splitlines() if (m := LINE_PATTERN.match(line))}


def test_list_plugins_succeeds():
    assert list_plugins().returncode == 0


def test_no_plugin_fails():
    assert [plugin for plugin, status in get_plugin_statuses().items() if status == "FAIL"] == []


@pytest.mark.parametrize("plugin", PLUGINS)
def test_plugin_loads(plugin: str):
    assert get_plugin_statuses().get(plugin) == "OK"


def test_every_plugin_is_tested():
    plugins_dir = Path(BONSAIVIEWER).parent
    if sys.platform == "darwin":
        # Plug-ins are staged into `BonsaiViewer.app/Contents/Frameworks`.
        plugins_dir = plugins_dir.parent / "Frameworks"
    packaged = {
        path.name.split(".")[0]
        for path in plugins_dir.iterdir()
        if path.name.startswith("ifcopenshell_") and path.suffix in (".so", ".dylib", ".dll")
    }
    assert packaged == set(PLUGINS)
