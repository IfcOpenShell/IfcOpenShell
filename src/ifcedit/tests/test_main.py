# This file was generated with the assistance of an AI coding tool.
import json
import subprocess
import sys

import ifcopenshell
import pytest


def run_ifcedit(*args, stdin=None):
    """Run ifcedit as a subprocess and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, "-m", "ifcedit", *args],
        capture_output=True,
        text=True,
        input=stdin,
    )
    return result.stdout, result.stderr, result.returncode


class TestListCommand:
    def test_list_all_modules(self):
        stdout, stderr, rc = run_ifcedit("list")
        assert rc == 0
        data = json.loads(stdout)
        assert isinstance(data, list)
        module_names = [m["module"] for m in data]
        assert "root" in module_names
        assert "spatial" in module_names

    def test_list_module_functions(self):
        stdout, stderr, rc = run_ifcedit("list", "root")
        assert rc == 0
        data = json.loads(stdout)
        assert isinstance(data, list)
        names = [f["name"] for f in data]
        assert "create_entity" in names

    def test_list_text_format(self):
        stdout, stderr, rc = run_ifcedit("--format", "text", "list")
        assert rc == 0
        assert "root" in stdout


class TestDocsCommand:
    def test_docs_create_entity(self):
        stdout, stderr, rc = run_ifcedit("docs", "root.create_entity")
        assert rc == 0
        data = json.loads(stdout)
        assert data["module"] == "root"
        assert data["function"] == "create_entity"
        assert "params" in data

    def test_docs_invalid_path(self):
        stdout, stderr, rc = run_ifcedit("docs", "invalid_path")
        assert rc != 0
        assert "module.function" in stderr

    def test_docs_unknown_function(self):
        stdout, stderr, rc = run_ifcedit("docs", "root.nonexistent")
        assert rc != 0


class TestRunCommand:
    def test_create_entity(self, model_file):
        stdout, stderr, rc = run_ifcedit(
            "run", model_file, "root.create_entity", "--ifc_class", "IfcWall", "--name", "CLIWall"
        )
        assert rc == 0, f"stderr: {stderr}"
        data = json.loads(stdout)
        assert data["ok"] is True
        assert data["result"]["type"] == "IfcWall"
        assert data["result"]["name"] == "CLIWall"

    def test_dry_run(self, model_file):
        stdout, stderr, rc = run_ifcedit("run", model_file, "root.create_entity", "--dry-run", "--ifc_class", "IfcWall")
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is True
        assert data["dry_run"] is True

    def test_output_to_different_file(self, model_file, tmp_path):
        output = str(tmp_path / "output.ifc")
        stdout, stderr, rc = run_ifcedit(
            "run", model_file, "root.create_entity", "-o", output, "--ifc_class", "IfcSlab"
        )
        assert rc == 0, f"stderr: {stderr}"
        data = json.loads(stdout)
        assert data["ok"] is True

        import os

        assert os.path.exists(output)

    def test_run_error_bad_function(self, model_file):
        stdout, stderr, rc = run_ifcedit("run", model_file, "root.nonexistent")
        assert rc != 0

    def test_run_invalid_function_path(self, model_file):
        stdout, stderr, rc = run_ifcedit("run", model_file, "invalid_path")
        assert rc != 0
        assert "module.function" in stderr


class TestForeachCommand:
    def _select_json(self, model, ifc_class):
        """Build a JSON array like ifcquery select would produce."""
        elements = model.by_type(ifc_class)
        return json.dumps([{"id": e.id(), "type": e.is_a(), "name": getattr(e, "Name", None)} for e in elements])

    def test_foreach_rename(self, model, model_file):
        walls_json = self._select_json(model, "IfcWall")
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "attribute.edit_attributes",
            "--product",
            "{id}",
            "--attributes",
            '{"Name": "Renamed"}',
            stdin=walls_json,
        )
        assert rc == 0, f"stderr: {stderr}"
        data = json.loads(stdout)
        assert data["ok"] is True
        assert data["count"] == 1
        assert data["errors"] == []
        updated = ifcopenshell.open(model_file)
        assert updated.by_type("IfcWall")[0].Name == "Renamed"

    def test_foreach_multiple_elements(self, model, model_file):
        # Build a two-item list by selecting all IfcObject (includes spatial structure + elements)
        elements_json = self._select_json(model, "IfcObject")
        items = json.loads(elements_json)
        assert len(items) >= 2
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "attribute.edit_attributes",
            "--product",
            "{id}",
            "--attributes",
            '{"Name": "Bulk"}',
            stdin=elements_json,
        )
        assert rc == 0, f"stderr: {stderr}"
        data = json.loads(stdout)
        assert data["ok"] is True
        assert data["count"] == len(items)

    def test_foreach_empty_list(self, model_file):
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "attribute.edit_attributes",
            "--product",
            "{id}",
            "--attributes",
            '{"Name": "X"}',
            stdin="[]",
        )
        assert rc == 0
        data = json.loads(stdout)
        assert data["ok"] is True
        assert data["count"] == 0

    def test_foreach_invalid_json_stdin(self, model_file):
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "root.remove_product",
            "--product",
            "{id}",
            stdin="not json",
        )
        assert rc != 0
        assert "Error" in stderr

    def test_foreach_not_array_stdin(self, model_file):
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "root.remove_product",
            "--product",
            "{id}",
            stdin='{"id": 1}',
        )
        assert rc != 0
        assert "Error" in stderr

    def test_foreach_output_to_different_file(self, model, model_file, tmp_path):
        import os

        output = str(tmp_path / "out.ifc")
        walls_json = self._select_json(model, "IfcWall")
        stdout, stderr, rc = run_ifcedit(
            "foreach",
            model_file,
            "attribute.edit_attributes",
            "-o",
            output,
            "--product",
            "{id}",
            "--attributes",
            '{"Name": "OutFile"}',
            stdin=walls_json,
        )
        assert rc == 0, f"stderr: {stderr}"
        assert os.path.exists(output)
        updated = ifcopenshell.open(output)
        assert updated.by_type("IfcWall")[0].Name == "OutFile"
