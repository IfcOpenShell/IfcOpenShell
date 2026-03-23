# This file was generated with the assistance of an AI coding tool.
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
import ifcopenshell.guid
import numpy as np
import pytest

from ifcquery.render import _make_profile_occurrence, _make_type_occurrence, render

try:
    import pyvista  # noqa: F401

    HAS_PYVISTA = True
except ImportError:
    HAS_PYVISTA = False

pytestmark = pytest.mark.skipif(not HAS_PYVISTA, reason="pyvista not installed")

PNG_MAGIC = b"\x89PNG"


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

    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    wall1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall001")
    rep1 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall1, representation=rep1)
    ifcopenshell.api.spatial.assign_container(f, products=[wall1], relating_structure=storey)

    wall2 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall002")
    rep2 = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=4, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall2, representation=rep2)
    ifcopenshell.api.spatial.assign_container(f, products=[wall2], relating_structure=storey)
    matrix2 = np.eye(4)
    matrix2[1, 3] = 3.0
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall2, matrix=matrix2)

    return f


@pytest.fixture
def library_with_type():
    """IFC4 library file: a WallType with a RepresentationMap but no instances."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="LibProject")
    ifcopenshell.api.unit.assign_unit(f)

    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    # Build the shape representation and wrap it in an IfcRepresentationMap.
    shape_rep = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=3, height=2.5, thickness=0.2)
    origin = f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    z_dir = f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0))
    x_dir = f.create_entity("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0))
    map_origin = f.create_entity("IfcAxis2Placement3D", Location=origin, Axis=z_dir, RefDirection=x_dir)
    rep_map = f.create_entity("IfcRepresentationMap", MappingOrigin=map_origin, MappedRepresentation=shape_rep)

    wall_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name="LibWallType")
    wall_type.RepresentationMaps = [rep_map]

    return f, wall_type


@pytest.fixture
def library_with_profile_type():
    """IFC4 library: a BeamType with an IfcMaterialProfileSet but no RepresentationMaps."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="ProfileLibProject")
    ifcopenshell.api.unit.assign_unit(f)

    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    # Rectangular profile 0.2m x 0.3m
    profile = f.create_entity(
        "IfcRectangleProfileDef",
        ProfileType="AREA",
        ProfileName="200x300",
        XDim=0.2,
        YDim=0.3,
    )
    material = f.create_entity("IfcMaterial", Name="Steel")
    mat_profile = f.create_entity("IfcMaterialProfile", Material=material, Profile=profile)
    profile_set = f.create_entity("IfcMaterialProfileSet", MaterialProfiles=[mat_profile])

    beam_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBeamType", name="200x300 Steel Beam")
    rel = f.create_entity(
        "IfcRelAssociatesMaterial",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[beam_type],
        RelatingMaterial=profile_set,
    )

    return f, beam_type


class TestRenderBasic:
    def test_returns_png_bytes(self, model_with_geometry):
        result = render(model_with_geometry)
        assert isinstance(result, bytes)
        assert result[:4] == PNG_MAGIC

    def test_iso_view(self, model_with_geometry):
        result = render(model_with_geometry, view="iso")
        assert result[:4] == PNG_MAGIC

    def test_top_view(self, model_with_geometry):
        result = render(model_with_geometry, view="top")
        assert result[:4] == PNG_MAGIC

    def test_south_view(self, model_with_geometry):
        result = render(model_with_geometry, view="south")
        assert result[:4] == PNG_MAGIC

    def test_unknown_view_falls_back_to_iso(self, model_with_geometry):
        # Unknown view strings fall through to isometric
        result = render(model_with_geometry, view="diagonal")
        assert result[:4] == PNG_MAGIC


class TestRenderSelector:
    def test_selector_restricts_elements(self, model_with_geometry):
        result = render(model_with_geometry, selector="IfcWall")
        assert result[:4] == PNG_MAGIC

    def test_selector_no_match_raises(self, model_with_geometry):
        with pytest.raises(ValueError, match="matched no elements"):
            render(model_with_geometry, selector="IfcDoor")


class TestRenderHighlight:
    def test_highlight_single_element(self, model_with_geometry):
        wall = model_with_geometry.by_type("IfcWall")[0]
        result = render(model_with_geometry, element_ids=[wall.id()])
        assert result[:4] == PNG_MAGIC

    def test_highlight_multiple_elements(self, model_with_geometry):
        walls = model_with_geometry.by_type("IfcWall")
        result = render(model_with_geometry, element_ids=[w.id() for w in walls])
        assert result[:4] == PNG_MAGIC


class TestRenderTypes:
    def test_render_type_by_selector(self, library_with_type):
        """Selecting a type class renders its RepresentationMap geometry."""
        model, wall_type = library_with_type
        result = render(model, selector="IfcWallType")
        assert result[:4] == PNG_MAGIC

    def test_render_type_by_element_id(self, library_with_type):
        """Passing a type step-ID via element_ids renders it highlighted."""
        model, wall_type = library_with_type
        result = render(model, element_ids=[wall_type.id()])
        assert result[:4] == PNG_MAGIC

    def test_original_model_unmodified(self, library_with_type):
        """Rendering a type must not add entities to the original model."""
        model, wall_type = library_with_type
        entity_count_before = len(list(model))
        render(model, selector="IfcWallType")
        assert len(list(model)) == entity_count_before

    def test_make_type_occurrence_no_rep_maps(self, library_with_type):
        """_make_type_occurrence returns None for a type with no RepresentationMaps."""
        model, _ = library_with_type
        bare_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType", name="Bare")
        assert _make_type_occurrence(model, bare_type) is None

    def test_type_without_rep_maps_raises(self):
        """Selecting a type that has no RepresentationMaps raises ValueError."""
        f = ifcopenshell.api.project.create_file()
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="P")
        ifcopenshell.api.unit.assign_unit(f)
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name="Bare")
        with pytest.raises(ValueError):
            render(f, selector="IfcWallType")


class TestRenderProfileTypes:
    def test_render_profile_type_by_element_id(self, library_with_profile_type):
        """A type with only a material profile set renders via temporary extrusion."""
        model, beam_type = library_with_profile_type
        result = render(model, element_ids=[beam_type.id()])
        assert result[:4] == PNG_MAGIC

    def test_make_profile_occurrence_creates_occurrence(self, library_with_profile_type):
        """_make_profile_occurrence returns an occurrence entity for a profile-set type."""
        model, beam_type = library_with_profile_type
        occ = _make_profile_occurrence(model, beam_type)
        assert occ is not None

    def test_make_profile_occurrence_no_profile_returns_none(self, library_with_type):
        """_make_profile_occurrence returns None when type has no material profile set."""
        model, wall_type = library_with_type
        # wall_type has RepresentationMaps but no material profile set
        occ = _make_profile_occurrence(model, wall_type)
        assert occ is None

    def test_original_model_unmodified_for_profile_type(self, library_with_profile_type):
        """Rendering a profile-based type does not modify the original model."""
        model, beam_type = library_with_profile_type
        entity_count_before = len(list(model))
        render(model, element_ids=[beam_type.id()])
        assert len(list(model)) == entity_count_before


class TestRenderNoGeometry:
    def test_no_geometry_raises(self):
        """A model without geometry representations raises ValueError."""
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
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wallless")
        ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)

        with pytest.raises(ValueError, match="No renderable geometry"):
            render(f)


class TestCLI:
    @staticmethod
    def _ifc_path(model):
        f = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
        model.write(f.name)
        f.close()
        return f.name

    def test_render_writes_png(self, model_with_geometry):
        ifc_path = self._ifc_path(model_with_geometry)
        out_path = ifc_path.replace(".ifc", "_out.png")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "render", "-o", out_path],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert os.path.exists(out_path)
            with open(out_path, "rb") as f:
                assert f.read(4) == PNG_MAGIC
        finally:
            for path in (ifc_path, out_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def test_render_default_output_path(self, model_with_geometry):
        ifc_path = self._ifc_path(model_with_geometry)
        expected_png = ifc_path.replace(".ifc", ".png")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "render"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert os.path.exists(expected_png)
        finally:
            for path in (ifc_path, expected_png):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def test_render_with_selector(self, model_with_geometry):
        ifc_path = self._ifc_path(model_with_geometry)
        out_path = ifc_path.replace(".ifc", "_sel.png")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "render", "-o", out_path, "--selector", "IfcWall"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            with open(out_path, "rb") as f:
                assert f.read(4) == PNG_MAGIC
        finally:
            for path in (ifc_path, out_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def test_render_with_view(self, model_with_geometry):
        ifc_path = self._ifc_path(model_with_geometry)
        out_path = ifc_path.replace(".ifc", "_top.png")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "render", "-o", out_path, "--view", "top"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            with open(out_path, "rb") as f:
                assert f.read(4) == PNG_MAGIC
        finally:
            for path in (ifc_path, out_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
