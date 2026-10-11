"""Package tests that fail when a plug-in packaged with BonsaiViewer can't be loaded.

Runs `BonsaiViewer --list-plugins`, which tries to load every plug-in next to the executable.
"""

import functools
import re
import subprocess
import sys
from pathlib import Path

import pytest
from run_against_package import run_bonsaiviewer

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


@pytest.fixture(scope="module")
def bonsaiviewer(request: pytest.FixtureRequest) -> Path:
    path = request.config.getoption("bonsaiviewer")
    if path is None:
        pytest.skip("BonsaiViewer is not provided (--skip-bonsaiviewer).")
    return path


@functools.cache
def list_plugins(bonsaiviewer: Path) -> subprocess.CompletedProcess[str]:
    return run_bonsaiviewer(bonsaiviewer, "--list-plugins")


def get_plugin_statuses(bonsaiviewer: Path) -> dict[str, str]:
    return {m[2]: m[1] for line in list_plugins(bonsaiviewer).stdout.splitlines() if (m := LINE_PATTERN.match(line))}


def test_list_plugins_succeeds(bonsaiviewer: Path):
    assert list_plugins(bonsaiviewer).returncode == 0


def test_no_plugin_fails(bonsaiviewer: Path):
    assert [plugin for plugin, status in get_plugin_statuses(bonsaiviewer).items() if status == "FAIL"] == []


@pytest.mark.parametrize("plugin", PLUGINS)
def test_plugin_loads(plugin: str, bonsaiviewer: Path):
    assert get_plugin_statuses(bonsaiviewer).get(plugin) == "OK"


def test_every_plugin_is_tested(bonsaiviewer: Path):
    plugins_dir = bonsaiviewer.parent
    if sys.platform == "darwin":
        # Plug-ins are staged into `BonsaiViewer.app/Contents/Frameworks`.
        plugins_dir = plugins_dir.parent / "Frameworks"
    packaged = {
        path.name.split(".")[0]
        for path in plugins_dir.iterdir()
        if path.name.startswith("ifcopenshell_") and path.suffix in (".so", ".dylib", ".dll")
    }
    assert packaged == set(PLUGINS)
