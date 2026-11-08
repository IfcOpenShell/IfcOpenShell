# This file was generated with the assistance of an AI coding tool.
import ifcopenshell.api.root
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

    def test_max_depth(self, loaded_session):
        result = loaded_session.ifc_tree(max_depth=1)
        assert result["children"] == {"truncated": True, "count": 1}

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

    def test_by_global_id(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        assert loaded_session.ifc_info(wall.GlobalId)["id"] == wall.id()

    def test_by_step_id_as_string(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        assert loaded_session.ifc_info(str(wall.id()))["id"] == wall.id()

    def test_by_step_id_with_hash(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        assert loaded_session.ifc_info(f"#{wall.id()}")["id"] == wall.id()

    def test_step_id_with_hash_is_never_a_global_id(self, loaded_session):
        with pytest.raises(Exception, match="#111111111111111111111 not found"):
            loaded_session.ifc_info("#" + "1" * 21)

    def test_surrounding_whitespace(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        assert loaded_session.ifc_info(f" {wall.id()} ")["id"] == wall.id()
        assert loaded_session.ifc_info(f" {wall.GlobalId}\n")["id"] == wall.id()

    def test_hash_without_a_number(self, loaded_session):
        with pytest.raises(IfcSessionError, match="Not a STEP id or GlobalId"):
            loaded_session.ifc_info("#abc")

    def test_unknown_global_id(self, loaded_session):
        with pytest.raises(Exception, match="0000000000000000000000"):
            loaded_session.ifc_info("0000000000000000000000")

    def test_neither_id_nor_global_id(self, loaded_session):
        with pytest.raises(Exception, match="Wall001"):
            loaded_session.ifc_info("Wall001")


class TestSelect:
    def test_select_walls(self, loaded_session):
        result = loaded_session.ifc_select("IfcWall")
        assert result["total"] == 1
        assert result["elements"][0]["type"] == "IfcWall"
        assert result["elements"][0]["name"] == "Wall001"

    def test_select_slabs(self, loaded_session):
        result = loaded_session.ifc_select("IfcSlab")
        assert result["total"] == 1
        assert result["elements"][0]["name"] == "Slab001"

    def test_select_no_match(self, loaded_session):
        result = loaded_session.ifc_select("IfcWindow")
        assert result == {"total": 0, "offset": 0, "elements": []}

    def test_limit(self, loaded_session):
        result = loaded_session.ifc_select("IfcWall, IfcSlab", limit=1)
        assert result["total"] == 2
        assert len(result["elements"]) == 1

    def test_pages_cover_every_match_once(self, loaded_session):
        everything = loaded_session.ifc_select("IfcWall, IfcSlab")["elements"]
        first = loaded_session.ifc_select("IfcWall, IfcSlab", limit=1)
        second = loaded_session.ifc_select("IfcWall, IfcSlab", limit=1, offset=1)
        assert second["offset"] == 1
        assert first["elements"] + second["elements"] == everything

    def test_default_limit(self, loaded_session):
        for i in range(250):
            ifcopenshell.api.root.create_entity(loaded_session.model, ifc_class="IfcColumn", name=f"C{i}")
        result = loaded_session.ifc_select("IfcColumn")
        assert result["total"] == 250
        assert len(result["elements"]) == 200

    def test_limit_0_counts(self, loaded_session):
        assert loaded_session.ifc_select("IfcWall, IfcSlab", limit=0) == {"total": 2, "offset": 0, "elements": []}

    @pytest.mark.parametrize("page", [{"limit": -1}, {"offset": -1}])
    def test_negative_page(self, loaded_session, page):
        with pytest.raises(IfcSessionError, match="negative"):
            loaded_session.ifc_select("IfcWall", **page)

    def test_offset_past_the_end(self, loaded_session):
        result = loaded_session.ifc_select("IfcWall", offset=5)
        assert result == {"total": 1, "offset": 5, "elements": []}


class TestRelations:
    def test_wall_relations(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        result = loaded_session.ifc_relations(wall.id())
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert "hierarchy" in result

    def test_by_global_id(self, loaded_session):
        wall = loaded_session.model.by_type("IfcWall")[0]
        assert loaded_session.ifc_relations(wall.GlobalId)["id"] == wall.id()

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
