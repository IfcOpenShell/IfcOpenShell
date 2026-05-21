# This file was generated with the assistance of an AI coding tool.
import json
import os
import subprocess
import sys
import tempfile

import ifcopenshell
import ifcopenshell.api.project
import pytest


@pytest.fixture
def ifc_path(model):
    """Write the model fixture to a temp file and return its path."""
    with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as f:
        model.write(f.name)
        yield f.name
    os.unlink(f.name)


def run_ifcquery(*args):
    """Run ifcquery as a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "ifcquery", *args],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestCLI:
    def test_summary_json(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "summary")
        assert rc == 0
        data = json.loads(stdout)
        assert data["schema"] == "IFC4"
        assert "types" in data

    def test_tree_json(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "tree")
        assert rc == 0
        data = json.loads(stdout)
        assert data["type"] == "IfcProject"

    def test_info_json(self, ifc_path, model):
        wall = model.by_type("IfcWall")[0]
        rc, stdout, stderr = run_ifcquery(ifc_path, "info", str(wall.id()))
        assert rc == 0
        data = json.loads(stdout)
        assert data["type"] == "IfcWall"

    def test_info_hash_id(self, ifc_path, model):
        wall = model.by_type("IfcWall")[0]
        rc, stdout, stderr = run_ifcquery(ifc_path, "info", f"#{wall.id()}")
        assert rc == 0
        data = json.loads(stdout)
        assert data["type"] == "IfcWall"

    def test_select_json(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "select", "IfcWall")
        assert rc == 0
        data = json.loads(stdout)
        assert len(data) == 1
        assert data[0]["type"] == "IfcWall"

    def test_text_format(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "text", "summary")
        assert rc == 0
        assert "schema:" in stdout

    def test_bad_file(self):
        rc, stdout, stderr = run_ifcquery("/nonexistent.ifc", "summary")
        assert rc != 0
        assert "Error" in stderr

    def test_bad_element_id(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "info", "999999")
        assert rc != 0
        assert "Error" in stderr

    def test_no_command(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path)
        assert rc != 0

    def test_select_ids_format(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "ids", "select", "IfcWall")
        assert rc == 0
        # Should be a comma-separated string of integers with no surrounding whitespace
        ids = stdout.strip()
        assert ids != ""
        for part in ids.split(","):
            assert part.isdigit()

    def test_select_ids_format_multiple(self, ifc_path, model):
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "ids", "select", "IfcElement")
        assert rc == 0
        ids = stdout.strip().split(",")
        assert len(ids) >= 2

    def test_ids_format_empty_result(self, ifc_path):
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "ids", "select", "IfcDoor")
        assert rc == 0
        assert stdout.strip() == ""

    def test_relations_ids_format(self, ifc_path, model):
        storey = model.by_type("IfcBuildingStorey")[0]
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "ids", "relations", str(storey.id()))
        assert rc == 0
        ids = stdout.strip().split(",")
        assert all(i.isdigit() for i in ids)
        # should include the storey itself and its contained elements
        assert str(storey.id()) in ids
        wall_id = str(model.by_type("IfcWall")[0].id())
        assert wall_id in ids

    def test_info_ids_format(self, ifc_path, model):
        wall = model.by_type("IfcWall")[0]
        rc, stdout, stderr = run_ifcquery(ifc_path, "--format", "ids", "info", str(wall.id()))
        assert rc == 0
        assert stdout.strip() == str(wall.id())
