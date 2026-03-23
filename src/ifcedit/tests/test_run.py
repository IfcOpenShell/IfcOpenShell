# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root

from ifcedit.run import run_api, serialize_result


class TestRunApi:
    def test_create_entity(self, model):
        result = run_api(model, "root", "create_entity", {"ifc_class": "IfcWall", "name": "NewWall"})
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcWall"
        assert result["result"]["name"] == "NewWall"
        assert isinstance(result["result"]["id"], int)

    def test_create_entity_default_class(self, model):
        result = run_api(model, "root", "create_entity", {})
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcBuildingElementProxy"

    def test_assign_container(self, model):
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="TestWall2")
        storey = model.by_type("IfcBuildingStorey")[0]
        result = run_api(
            model,
            "spatial",
            "assign_container",
            {"products": str(wall.id()), "relating_structure": str(storey.id())},
        )
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcRelContainedInSpatialStructure"

    def test_add_pset(self, model):
        wall = model.by_type("IfcWall")[0]
        result = run_api(model, "pset", "add_pset", {"product": str(wall.id()), "name": "Pset_WallCommon"})
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcPropertySet"

    def test_unknown_function(self, model):
        result = run_api(model, "root", "nonexistent", {})
        assert result["ok"] is False
        assert "Cannot find" in result["error"]

    def test_unknown_parameter(self, model):
        result = run_api(model, "root", "create_entity", {"bogus_param": "value"})
        assert result["ok"] is False
        assert "Unknown parameter" in result["error"]

    def test_bad_entity_reference(self, model):
        result = run_api(model, "pset", "add_pset", {"product": "999999", "name": "Pset_WallCommon"})
        assert result["ok"] is False
        assert "not found" in result["error"]


class TestAppendAsset:
    def test_append_asset_from_library(self, model, library_file):
        lib = ifcopenshell.open(library_file)
        wall_type = lib.by_type("IfcWallType")[0]
        result = run_api(
            model,
            "project",
            "append_asset",
            {"library": library_file, "element": str(wall_type.id())},
        )
        assert result["ok"] is True
        assert result["result"]["type"] == "IfcWallType"
        assert model.by_type("IfcWallType"), "wall type should have been appended to the model"


class TestSerializeResult:
    def test_none(self):
        assert serialize_result(None) is None

    def test_string(self):
        assert serialize_result("hello") == "hello"

    def test_int(self):
        assert serialize_result(42) == 42

    def test_entity(self, model):
        wall = model.by_type("IfcWall")[0]
        result = serialize_result(wall)
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert result["name"] == "Wall001"

    def test_list(self, model):
        walls = model.by_type("IfcWall")
        result = serialize_result(walls)
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_dict(self):
        result = serialize_result({"key": "value"})
        assert result == {"key": "value"}
