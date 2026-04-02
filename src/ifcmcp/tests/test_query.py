# This file was generated with the assistance of an AI coding tool.
import pytest

from ifcmcp.core import IfcSessionError


class TestNoModel:
    """All query tools should fail when no model is loaded."""

    def test_summary_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_summary()

    def test_tree_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_tree()

    def test_info_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_info(1)

    def test_select_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_select("IfcWall")

    def test_relations_no_model(self, session):
        with pytest.raises(IfcSessionError, match="No model loaded"):
            session.ifc_relations(1)


class TestSummary:
    def test_schema(self, loaded_session):
        result = loaded_session.ifc_summary()
        assert result["schema"] == "IFC4"

    def test_total_entities(self, loaded_session):
        result = loaded_session.ifc_summary()
        assert result["total_entities"] > 0

    def test_project_name(self, loaded_session):
        result = loaded_session.ifc_summary()
        assert result["project"]["name"] == "TestProject"

    def test_type_counts(self, loaded_session):
        result = loaded_session.ifc_summary()
        assert result["types"]["IfcWall"] == 1
        assert result["types"]["IfcSlab"] == 1


class TestTree:
    def test_root_is_project(self, loaded_session):
        result = loaded_session.ifc_tree()
        assert result["type"] == "IfcProject"
        assert result["name"] == "TestProject"

    def test_hierarchy_depth(self, loaded_session):
        result = loaded_session.ifc_tree()
        site = result["children"][0]
        assert site["type"] == "IfcSite"
        building = site["children"][0]
        assert building["type"] == "IfcBuilding"
        storey = building["children"][0]
        assert storey["type"] == "IfcBuildingStorey"


class TestInfo:
    def test_wall_info(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        result = loaded_session.ifc_info(wall.id())
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"

    def test_invalid_id(self, loaded_session):
        with pytest.raises(Exception):
            loaded_session.ifc_info(999999)


class TestSelect:
    def test_select_walls(self, loaded_session):
        result = loaded_session.ifc_select("IfcWall")
        assert len(result) == 1
        assert result[0]["type"] == "IfcWall"
        assert result[0]["name"] == "Wall001"

    def test_select_slabs(self, loaded_session):
        result = loaded_session.ifc_select("IfcSlab")
        assert len(result) == 1
        assert result[0]["name"] == "Slab001"

    def test_select_no_match(self, loaded_session):
        result = loaded_session.ifc_select("IfcWindow")
        assert result == []


class TestRelations:
    def test_wall_relations(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        result = loaded_session.ifc_relations(wall.id())
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert "hierarchy" in result

    def test_traverse_up(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        result = loaded_session.ifc_relations(wall.id(), traverse="up")
        assert isinstance(result, list)
        assert result[0]["type"] == "IfcWall"
        assert result[-1]["type"] == "IfcProject"

    def test_traverse_empty_string_means_no_traverse(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        result = loaded_session.ifc_relations(wall.id(), traverse="")
        assert isinstance(result, dict)
