# This file was generated with the assistance of an AI coding tool.
from ifcquery.select import select


class TestSelect:
    def test_select_by_type(self, model):
        result = select(model, "IfcWall")
        assert len(result) == 1
        assert result[0]["type"] == "IfcWall"
        assert result[0]["name"] == "Wall001"

    def test_select_multiple_types(self, model):
        result = select(model, "IfcWall, IfcSlab")
        assert len(result) == 2
        types = {r["type"] for r in result}
        assert types == {"IfcWall", "IfcSlab"}

    def test_select_no_match(self, model):
        result = select(model, "IfcDoor")
        assert result == []

    def test_results_sorted_by_id(self, model):
        result = select(model, "IfcWall, IfcSlab")
        ids = [r["id"] for r in result]
        assert ids == sorted(ids)

    def test_result_has_id_type_name(self, model):
        result = select(model, "IfcWall")
        entry = result[0]
        assert "id" in entry
        assert "type" in entry
        assert "name" in entry
