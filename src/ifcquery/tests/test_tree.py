# This file was generated with the assistance of an AI coding tool.
from ifcquery.tree import tree


class TestTree:
    def test_root_is_project(self, model):
        result = tree(model)
        assert result["type"] == "IfcProject"
        assert result["name"] == "TestProject"

    def test_spatial_hierarchy(self, model):
        result = tree(model)
        # Project > Site > Building > Storey
        site = result["children"][0]
        assert site["type"] == "IfcSite"
        assert site["name"] == "TestSite"

        building = site["children"][0]
        assert building["type"] == "IfcBuilding"
        assert building["name"] == "TestBuilding"

        storey = building["children"][0]
        assert storey["type"] == "IfcBuildingStorey"
        assert storey["name"] == "Ground Floor"

    def test_contained_elements(self, model):
        result = tree(model)
        storey = result["children"][0]["children"][0]["children"][0]
        elements = storey["elements"]
        element_types = {e["type"] for e in elements}
        assert "IfcWall" in element_types
        assert "IfcSlab" in element_types

    def test_element_ids_present(self, model):
        result = tree(model)
        assert "id" in result
        assert isinstance(result["id"], int)
