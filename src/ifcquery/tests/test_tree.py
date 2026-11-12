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


class TestTreeMaxDepth:
    def test_depth_1_is_the_project_alone(self, model):
        result = tree(model, max_depth=1)
        assert result["type"] == "IfcProject"
        assert result["children"] == {"truncated": True, "count": 1}

    def test_depth_2_shows_the_site(self, model):
        site = tree(model, max_depth=2)["children"][0]
        assert site["type"] == "IfcSite"
        assert site["children"] == {"truncated": True, "count": 1}

    def test_contained_elements_are_one_level_below_the_storey(self, model):
        storey = tree(model, max_depth=4)["children"][0]["children"][0]["children"][0]
        assert storey["type"] == "IfcBuildingStorey"
        assert storey["elements"] == {"truncated": True, "count": 2}

    def test_deep_enough_is_the_full_tree(self, model):
        assert tree(model, max_depth=5) == tree(model)

    def test_no_marker_when_there_is_nothing_to_truncate(self, model):
        storey = tree(model, max_depth=4)["children"][0]["children"][0]["children"][0]
        assert "children" not in storey
