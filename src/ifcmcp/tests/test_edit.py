import json

import pytest

from ifcmcp.server import ifc_docs, ifc_edit, ifc_list


class TestNoModel:
    def test_edit_no_model(self):
        with pytest.raises(ValueError, match="No model loaded"):
            ifc_edit("root.create_entity")


class TestList:
    def test_list_all_modules(self, loaded_model):
        result = ifc_list()
        assert isinstance(result, list)
        assert len(result) > 0
        modules = [m["module"] for m in result]
        assert "root" in modules
        assert "spatial" in modules

    def test_list_module_functions(self, loaded_model):
        result = ifc_list(module="root")
        assert isinstance(result, list)
        names = [f["name"] for f in result]
        assert "create_entity" in names

    def test_list_empty_string_returns_modules(self, loaded_model):
        result = ifc_list(module="")
        assert isinstance(result, list)
        assert any(m["module"] == "root" for m in result)


class TestDocs:
    def test_docs_create_entity(self, loaded_model):
        result = ifc_docs("root.create_entity")
        assert result["module"] == "root"
        assert result["function"] == "create_entity"
        assert "params" in result

    def test_docs_bad_format(self, loaded_model):
        with pytest.raises(ValueError):
            ifc_docs("no_dot_here")


class TestEdit:
    def test_create_entity(self, loaded_model):
        result = ifc_edit("root.create_entity", json.dumps({"ifc_class": "IfcWall", "name": "NewWall"}))
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcWall"
        assert result["result"]["name"] == "NewWall"

    def test_create_entity_default_params(self, loaded_model):
        result = ifc_edit("root.create_entity", "{}")
        assert result["ok"] is True

    def test_unknown_function(self, loaded_model):
        result = ifc_edit("root.nonexistent", "{}")
        assert result["ok"] is False
        assert "Cannot find" in result["error"]

    def test_unknown_parameter(self, loaded_model):
        result = ifc_edit("root.create_entity", json.dumps({"bogus": "value"}))
        assert result["ok"] is False
        assert "Unknown parameter" in result["error"]

    def test_bad_json(self, loaded_model):
        with pytest.raises(json.JSONDecodeError):
            ifc_edit("root.create_entity", "not json")

    def test_edit_does_not_save(self, loaded_model, tmp_path):
        """Verify that ifc_edit mutates the in-memory model but does not write to disk."""
        import ifcmcp.server as server_mod

        path = str(tmp_path / "test.ifc")
        loaded_model.write(path)
        server_mod._model_path = path

        before_count = sum(1 for _ in loaded_model)
        ifc_edit("root.create_entity", json.dumps({"ifc_class": "IfcWall", "name": "Unsaved"}))
        after_count = sum(1 for _ in loaded_model)
        assert after_count == before_count + 1

        # Re-read the file — it should not have the new entity
        import ifcopenshell

        on_disk = ifcopenshell.open(path)
        disk_count = sum(1 for _ in on_disk)
        assert disk_count == before_count

    def test_assign_container(self, loaded_model):
        wall = loaded_model.by_type("IfcWall")[0]
        storey = loaded_model.by_type("IfcBuildingStorey")[0]
        result = ifc_edit(
            "spatial.assign_container",
            json.dumps({"products": str(wall.id()), "relating_structure": str(storey.id())}),
        )
        assert result["ok"] is True
