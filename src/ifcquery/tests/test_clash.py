# This file was generated with the assistance of an AI coding tool.
import json
import os
import subprocess
import sys
import tempfile

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import numpy as np
import pytest

from ifcquery.clash import clash

try:
    import ifcopenshell.geom

    HAS_GEOM = True
except ImportError:
    HAS_GEOM = False

pytestmark = pytest.mark.skipif(not HAS_GEOM, reason="ifcopenshell geometry engine not available")


@pytest.fixture
def model_with_geometry():
    """Create an IFC4 model with walls that have geometric representations."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="TestSite")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="TestBuilding")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground Floor")

    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)

    # Create geometry context
    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    # Wall 1 at origin
    wall1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall001")
    rep1 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall1, representation=rep1)
    ifcopenshell.api.spatial.assign_container(f, products=[wall1], relating_structure=storey)

    # Wall 2 perpendicular, crossing through wall 1
    wall2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall002")
    rep2 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall2, representation=rep2)
    ifcopenshell.api.spatial.assign_container(f, products=[wall2], relating_structure=storey)
    matrix2 = np.array([[0, -1, 0, 2.5], [1, 0, 0, -2.0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall2, matrix=matrix2)

    # Wall 3 far away (10m offset in Y)
    wall3 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall003")
    rep3 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall3, representation=rep3)
    ifcopenshell.api.spatial.assign_container(f, products=[wall3], relating_structure=storey)
    matrix3 = np.eye(4)
    matrix3[1, 3] = 10.0  # 10m in Y direction
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall3, matrix=matrix3)

    # Wall 4 close but not overlapping (0.3m offset in Y, wall thickness is 0.2m)
    wall4 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall004")
    rep4 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall4, representation=rep4)
    ifcopenshell.api.spatial.assign_container(f, products=[wall4], relating_structure=storey)
    matrix4 = np.eye(4)
    matrix4[1, 3] = 0.3  # 0.3m in Y (gap of 0.1m from wall1)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall4, matrix=matrix4)

    return f


@pytest.fixture
def model_two_storeys():
    """Create a model with walls in different storeys."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="TestSite")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="TestBuilding")
    storey1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground Floor")
    storey2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="First Floor")

    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey1, storey2], relating_object=building)

    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    # Wall in storey 1
    wall1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="GroundWall")
    rep1 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall1, representation=rep1)
    ifcopenshell.api.spatial.assign_container(f, products=[wall1], relating_structure=storey1)

    # Wall in storey 2, perpendicular and crossing wall1
    wall2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="FirstFloorWall")
    rep2 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall2, representation=rep2)
    ifcopenshell.api.spatial.assign_container(f, products=[wall2], relating_structure=storey2)
    matrix2 = np.array([[0, -1, 0, 2.5], [1, 0, 0, -2.0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall2, matrix=matrix2)

    return f


class TestNoClashes:
    def test_no_clashes_far_apart(self, model_with_geometry):
        wall3 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall003")
        result = clash(model_with_geometry, wall3)
        assert result["pass"] is True
        assert result["checks"]["intersection"]["pass"] is True
        assert result["checks"]["intersection"]["clashes"] == []

    def test_no_clashes_empty_scope(self, model_with_geometry):
        """A model where the element is the only one in scope should pass."""
        # Create a model with a single wall
        f = ifcopenshell.api.project.create_file()
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
        project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="P")
        ifcopenshell.api.unit.assign_unit(f)
        site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="S")
        building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="B")
        storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="GF")
        ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
        ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)
        model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
        )
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="OnlyWall")
        rep = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
        ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)

        result = clash(f, wall)
        assert result["pass"] is True


class TestIntersectionDetected:
    def test_overlapping_walls(self, model_with_geometry):
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1)
        assert result["pass"] is False
        assert result["checks"]["intersection"]["pass"] is False
        clashes = result["checks"]["intersection"]["clashes"]
        assert len(clashes) > 0
        # Wall002 should be in the clashes (it overlaps wall1)
        clash_ids = {c["element"]["id"] for c in clashes}
        wall2 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall002")
        assert wall2.id() in clash_ids

    def test_clash_has_points(self, model_with_geometry):
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1)
        clashes = result["checks"]["intersection"]["clashes"]
        for c in clashes:
            assert "p1" in c
            assert "p2" in c
            assert len(c["p1"]) == 3
            assert len(c["p2"]) == 3
            assert "type" in c
            assert "distance" in c


class TestClearance:
    def test_clearance_violation(self, model_with_geometry):
        """Wall004 is 0.1m from wall1; clearance of 0.5m should fail."""
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1, clearance=0.5)
        assert "clearance" in result["checks"]
        # Wall004 should violate clearance
        clearance_clashes = result["checks"]["clearance"]["clashes"]
        clash_ids = {c["element"]["id"] for c in clearance_clashes}
        wall4 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall004")
        assert wall4.id() in clash_ids
        assert result["checks"]["clearance"]["pass"] is False

    def test_clearance_pass(self, model_with_geometry):
        """Wall003 is 10m away; clearance of 0.5m should pass for wall003."""
        wall3 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall003")
        result = clash(model_with_geometry, wall3, clearance=0.5)
        assert result["checks"]["clearance"]["pass"] is True
        assert result["checks"]["clearance"]["clashes"] == []

    def test_clearance_not_included_by_default(self, model_with_geometry):
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1)
        assert "clearance" not in result["checks"]


class TestScope:
    def test_scope_storey_excludes_other_storeys(self, model_two_storeys):
        wall1 = next(w for w in model_two_storeys.by_type("IfcWall") if w.Name == "GroundWall")
        result = clash(model_two_storeys, wall1, scope="storey")
        assert result["scope"] == "storey"
        # No clashes because the overlapping wall is in a different storey
        assert result["pass"] is True

    def test_scope_all_includes_other_storeys(self, model_two_storeys):
        wall1 = next(w for w in model_two_storeys.by_type("IfcWall") if w.Name == "GroundWall")
        result = clash(model_two_storeys, wall1, scope="all")
        assert result["scope"] == "all"
        # Should detect clash with the other-storey wall
        assert result["pass"] is False
        clash_ids = {c["element"]["id"] for c in result["checks"]["intersection"]["clashes"]}
        wall2 = next(w for w in model_two_storeys.by_type("IfcWall") if w.Name == "FirstFloorWall")
        assert wall2.id() in clash_ids


class TestNoGeometry:
    def test_no_geometry_error(self, model):
        """Element without geometry reports error."""
        wall = model.by_type("IfcWall")[0]
        result = clash(model, wall)
        assert result["pass"] is None
        assert "error" in result
        assert "No geometry" in result["error"]


class TestJsonSerializable:
    def test_result_serializable(self, model_with_geometry):
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1)
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        assert parsed["element"]["type"] == "IfcWall"

    def test_clearance_result_serializable(self, model_with_geometry):
        wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
        result = clash(model_with_geometry, wall1, clearance=0.5)
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        assert "clearance" in parsed["checks"]


class TestCLI:
    @staticmethod
    def _ifc_path(model):
        f = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
        model.write(f.name)
        f.close()
        return f.name

    def test_clash_json(self, model_with_geometry):
        path = self._ifc_path(model_with_geometry)
        try:
            wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "clash", str(wall1.id())],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data["element"]["type"] == "IfcWall"
            assert "checks" in data
            assert "intersection" in data["checks"]
        finally:
            os.unlink(path)

    def test_clash_with_clearance(self, model_with_geometry):
        path = self._ifc_path(model_with_geometry)
        try:
            wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "clash", str(wall1.id()), "--clearance", "0.5"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert "clearance" in data["checks"]
        finally:
            os.unlink(path)

    def test_clash_scope_all(self, model_with_geometry):
        path = self._ifc_path(model_with_geometry)
        try:
            wall1 = next(w for w in model_with_geometry.by_type("IfcWall") if w.Name == "Wall001")
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "clash", str(wall1.id()), "--scope", "all"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data["scope"] == "all"
        finally:
            os.unlink(path)

    def test_clash_bad_id(self, model_with_geometry):
        path = self._ifc_path(model_with_geometry)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", path, "clash", "999999"],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0
            assert "Error" in result.stderr
        finally:
            os.unlink(path)
