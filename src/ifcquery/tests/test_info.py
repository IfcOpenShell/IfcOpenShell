# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder

from ifcquery.info import info


class TestInfo:
    def test_basic_attributes(self, model):
        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        assert result["id"] == wall.id()
        assert result["type"] == "IfcWall"
        assert result["attributes"]["Name"] == "Wall001"

    def test_container(self, model):
        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        assert result["container"]["type"] == "IfcBuildingStorey"
        assert result["container"]["name"] == "Ground Floor"

    def test_project_info(self, model):
        project = model.by_type("IfcProject")[0]
        result = info(model, project)
        assert result["type"] == "IfcProject"
        assert result["attributes"]["Name"] == "TestProject"

    def test_all_attributes_serializable(self, model):
        """All attribute values should be JSON-serializable (no entity instances)."""
        import json

        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        # Should not raise
        json.dumps(result)

    def test_no_geometry_summary_without_representation(self, model):
        wall = model.by_type("IfcWall")[0]
        result = info(model, wall)
        assert "geometry_summary" not in result


class TestGeometrySummary:
    def _make_model_with_wall(self):
        f = ifcopenshell.api.project.create_file()
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(f)
        model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
        ifcopenshell.api.context.add_context(
            f,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_ctx,
        )
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="W1")
        ifcopenshell.api.geometry.edit_object_placement(f, product=wall)
        return f, wall

    def _body_context(self, f):
        return ifcopenshell.util.representation.get_context(f, "Model", "Body", "MODEL_VIEW")

    def test_swept_solid_summary(self):
        f, wall = self._make_model_with_wall()
        body = self._body_context(f)
        rep = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5.0, height=3.0, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
        result = info(f, wall)
        gs = result["geometry_summary"]
        assert gs["representation_type"] == "SweptSolid"
        assert len(gs["solids"]) == 1
        solid = gs["solids"][0]
        assert solid["depth"] == 3000.0  # stored in project units (mm)
        assert solid["profile"]["type"] == "IfcArbitraryClosedProfileDef"
        assert len(solid["profile"]["points"]) == 5  # closed polyline

    def test_clipping_summary(self):
        f, wall = self._make_model_with_wall()
        body = self._body_context(f)
        rep = ifcopenshell.api.geometry.add_wall_representation(
            f,
            context=body,
            length=5.0,
            height=4.0,
            thickness=0.2,
            clippings=[{"location": (0.0, 0.0, 3.0), "normal": (0.0, 0.0, 1.0)}],
        )
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
        result = info(f, wall)
        gs = result["geometry_summary"]
        assert gs["representation_type"] == "Clipping"
        solid = gs["solids"][0]
        assert len(solid["clipping_planes"]) == 1
        plane = solid["clipping_planes"][0]
        assert plane["location"][2] == 3000.0  # stored in project units (mm)
        assert plane["normal"] == [0.0, 0.0, 1.0]

    def test_geometry_summary_json_serializable(self):
        import json

        f, wall = self._make_model_with_wall()
        body = self._body_context(f)
        rep = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5.0, height=3.0, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
        result = info(f, wall)
        json.dumps(result)
