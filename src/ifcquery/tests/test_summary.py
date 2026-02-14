# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.project

from ifcquery.summary import summary


class TestSummary:
    def test_schema(self, model):
        result = summary(model)
        assert result["schema"] == "IFC4"

    def test_total_entities(self, model):
        result = summary(model)
        assert result["total_entities"] == len(list(model))
        assert result["total_entities"] > 0

    def test_project_info(self, model):
        result = summary(model)
        assert result["project"]["name"] == "TestProject"

    def test_type_counts(self, model):
        result = summary(model)
        types = result["types"]
        assert "IfcWall" in types
        assert types["IfcWall"] == 1
        assert "IfcSlab" in types
        assert types["IfcSlab"] == 1

    def test_empty_model(self):
        f = ifcopenshell.api.project.create_file()
        result = summary(f)
        assert result["schema"] == "IFC4"
        assert "project" not in result
