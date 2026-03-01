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
import numpy as np
import pytest

from ifcquery.render import render

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
