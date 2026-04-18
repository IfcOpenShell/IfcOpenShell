# This file was generated with the assistance of an AI coding tool.
import json

import ifcopenshell
import pytest

from ifcmcp.core import IfcSession, IfcSessionError


class TestNoModel:
    def test_edit_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_edit("root.create_entity")


class TestList:
    def test_list_all_modules(self, loaded_session):
        result = loaded_session.ifc_list()
        assert isinstance(result, list)
        assert len(result) > 0
        modules = [m["module"] for m in result]
        assert "root" in modules
        assert "spatial" in modules

    def test_list_module_functions(self, loaded_session):
        result = loaded_session.ifc_list(module="root")
        assert isinstance(result, list)
        names = [f["name"] for f in result]
        assert "create_entity" in names

    def test_list_empty_string_returns_modules(self, loaded_session):
        result = loaded_session.ifc_list(module="")
        assert isinstance(result, list)
        assert any(m["module"] == "root" for m in result)


class TestDocs:
    def test_docs_create_entity(self, loaded_session):
        result = loaded_session.ifc_docs("root.create_entity")
        assert result["module"] == "root"
        assert result["function"] == "create_entity"
        assert "params" in result

    def test_docs_bad_format(self, loaded_session):
        with pytest.raises(ValueError):
            loaded_session.ifc_docs("no_dot_here")


class TestEdit:
    def test_create_entity(self, loaded_session):
        result = loaded_session.ifc_edit("root.create_entity", json.dumps({"ifc_class": "IfcWall", "name": "NewWall"}))
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcWall"
        assert result["result"]["name"] == "NewWall"

    def test_create_entity_default_params(self, loaded_session):
        result = loaded_session.ifc_edit("root.create_entity", "{}")
        assert result["ok"] is True

    def test_unknown_function(self, loaded_session):
        result = loaded_session.ifc_edit("root.nonexistent", "{}")
        assert result["ok"] is False
        assert "Cannot find" in result["error"]

    def test_unknown_parameter(self, loaded_session):
        result = loaded_session.ifc_edit("root.create_entity", json.dumps({"bogus": "value"}))
        assert result["ok"] is False
        assert "Unknown parameter" in result["error"]

    def test_bad_json(self, loaded_session):
        with pytest.raises(json.JSONDecodeError):
            loaded_session.ifc_edit("root.create_entity", "not json")

    def test_edit_does_not_save(self, loaded_session, tmp_path):
        """Verify that ifc_edit mutates the in-memory model but does not write to disk."""
        path = str(tmp_path / "test.ifc")
        loaded_session.model.write(path)
        loaded_session.model_path = path

        before_count = sum(1 for _ in loaded_session.model)
        loaded_session.ifc_edit("root.create_entity", json.dumps({"ifc_class": "IfcWall", "name": "Unsaved"}))
        after_count = sum(1 for _ in loaded_session.model)
        assert after_count == before_count + 1

        on_disk = ifcopenshell.open(path)
        disk_count = sum(1 for _ in on_disk)
        assert disk_count == before_count

    def test_assign_container(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        storey = loaded_session.model.by_type("IfcBuildingStorey")[0]
        result = loaded_session.ifc_edit(
            "spatial.assign_container",
            json.dumps({"products": str(wall.id()), "relating_structure": str(storey.id())}),
        )
        assert result["ok"] is True
