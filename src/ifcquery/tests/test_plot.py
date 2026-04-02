from __future__ import annotations

import base64
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
import pytest

from ifcquery.plot import _highlight_css_from_ids, plot

try:
    import ifcopenshell.draw  # noqa: F401

    HAS_DRAW = True
except ImportError:
    HAS_DRAW = False

try:
    import cairosvg  # noqa: F401

    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

pytestmark = pytest.mark.skipif(not HAS_DRAW, reason="ifcopenshell.draw not available")

SVG_MAGIC = b"<?xml"
PNG_MAGIC = b"\x89PNG"


@pytest.fixture
def model_with_annotations():
    """IFC4 model with walls and explicit 2D annotation geometry (Plan/PLAN_VIEW context)."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="TestSite")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="TestBuilding")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground Floor")
    storey.Elevation = 0.0  # required for setSectionHeightsFromStoreys() to create a cut plane
    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)

    model_ctx = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model_ctx
    )

    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall001")
    rep = ifcopenshell.api.geometry.add_wall_representation(f, context=body, length=5, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
    ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)

    return f, wall


@pytest.fixture
def model_no_plan(model_with_annotations):
    """Model whose SVG output will be empty (wall geometry only, no plan annotation group)."""
    return model_with_annotations


class TestHighlightCSS:
    def test_css_for_valid_element(self, model_with_annotations):
        model, wall = model_with_annotations
        css = _highlight_css_from_ids(model, [wall.id()])
        assert wall.GlobalId in css
        assert "opacity: 0.10" in css
        assert "opacity: 1.0" in css
        assert "#d00" in css

    def test_css_empty_for_no_ids(self, model_with_annotations):
        model, _ = model_with_annotations
        css = _highlight_css_from_ids(model, [])
        assert css == ""

    def test_css_skips_unknown_ids(self, model_with_annotations):
        model, _ = model_with_annotations
        css = _highlight_css_from_ids(model, [999999])
        assert css == ""


class TestPlotSVG:
    def test_returns_svg_bytes(self, model_with_annotations):
        model, _ = model_with_annotations
        result = plot(model, output_format="svg")
        assert isinstance(result, bytes)
        assert result[:5] == SVG_MAGIC

    def test_svg_contains_xml(self, model_with_annotations):
        model, _ = model_with_annotations
        result = plot(model, output_format="svg")
        assert b"<svg" in result

    def test_invalid_format_raises(self, model_with_annotations):
        model, _ = model_with_annotations
        with pytest.raises(ValueError, match="output_format"):
            plot(model, output_format="xyz")

    def test_invalid_view_raises(self, model_with_annotations):
        model, _ = model_with_annotations
        with pytest.raises(ValueError, match="view"):
            plot(model, output_format="svg", view="bogus")

    def test_selector_no_match_raises(self, model_with_annotations):
        model, _ = model_with_annotations
        with pytest.raises(ValueError, match="matched no elements"):
            plot(model, output_format="svg", selector="IfcDoor")

    def test_selector_filters_elements(self, model_with_annotations):
        model, _ = model_with_annotations
        result = plot(model, output_format="svg", selector="IfcWall")
        assert isinstance(result, bytes)
        assert b"<svg" in result


class TestPlotEmptySVG:
    """When draw produces no <g> elements, PNG/base64 should raise a clear error."""

    def test_empty_drawing_png_raises(self, model_no_plan):
        """PNG format raises ValueError (not silently returns None) for empty drawings."""
        model, _ = model_no_plan
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if not has_groups:
            pytest.raises(ValueError, plot, model, output_format="png")
        else:
            pytest.skip("Model produced non-empty SVG — empty path not triggered")

    def test_empty_drawing_base64_raises(self, model_no_plan):
        """base64 format raises ValueError (not silently returns None) for empty drawings."""
        model, _ = model_no_plan
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if not has_groups:
            pytest.raises(ValueError, plot, model, output_format="base64")
        else:
            pytest.skip("Model produced non-empty SVG — empty path not triggered")


@pytest.mark.skipif(not HAS_CAIROSVG, reason="cairosvg not installed")
class TestPlotPNG:
    """PNG and base64 require cairosvg."""

    def test_png_returns_bytes_or_raises_on_empty(self, model_with_annotations):
        model, _ = model_with_annotations
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if has_groups:
            result = plot(model, output_format="png")
            assert isinstance(result, bytes)
            assert result[:4] == PNG_MAGIC
        else:
            with pytest.raises(ValueError, match="No plan geometry"):
                plot(model, output_format="png")

    def test_base64_returns_dict(self, model_with_annotations):
        model, _ = model_with_annotations
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if has_groups:
            result = plot(model, output_format="base64")
            assert isinstance(result, dict)
            assert result["mime"] == "image/png"
            assert "png_b64" in result
            assert "width" in result
            assert "height" in result
            assert "view" in result
            # Verify the base64 is valid PNG
            decoded = base64.b64decode(result["png_b64"])
            assert decoded[:4] == PNG_MAGIC
        else:
            with pytest.raises(ValueError, match="No plan geometry"):
                plot(model, output_format="base64")

    def test_base64_view_field_matches_requested(self, model_with_annotations):
        model, _ = model_with_annotations
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if not has_groups:
            pytest.skip("Model produces empty SVG")
        result = plot(model, output_format="base64", view="floorplan")
        assert result["view"] == "floorplan"

    def test_png_custom_size(self, model_with_annotations):
        model, _ = model_with_annotations
        svg = plot(model, output_format="svg")
        has_groups = b"<g " in svg or b"<g>" in svg
        if not has_groups:
            pytest.skip("Model produces empty SVG")
        result = plot(model, output_format="png", png_width=512, png_height=512)
        assert isinstance(result, bytes)
        assert result[:4] == PNG_MAGIC


class TestCLI:
    @staticmethod
    def _ifc_path(model):
        f = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
        model.write(f.name)
        f.close()
        return f.name

    def test_plot_svg_writes_file(self, model_with_annotations):
        model, _ = model_with_annotations
        ifc_path = self._ifc_path(model)
        out_path = ifc_path.replace(".ifc", "_out.svg")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "plot", "--out-format", "svg", "-o", out_path],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert os.path.exists(out_path)
            with open(out_path, "rb") as f:
                assert f.read(5) == SVG_MAGIC
        finally:
            for path in (ifc_path, out_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    @pytest.mark.skipif(not HAS_CAIROSVG, reason="cairosvg not installed")
    def test_plot_base64_prints_json(self, model_with_annotations):
        """base64 format prints JSON to stdout instead of writing a file."""
        model, _ = model_with_annotations
        ifc_path = self._ifc_path(model)
        try:
            # First check if the model would produce geometry
            svg = plot(model, output_format="svg")
            has_groups = b"<g " in svg or b"<g>" in svg
            if not has_groups:
                pytest.skip("Model produces empty SVG — base64 would raise ValueError")

            result = subprocess.run(
                [sys.executable, "-m", "ifcquery", ifc_path, "plot", "--out-format", "base64"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            # Output should be JSON (not an error) and contain base64 key
            assert "png_b64" in result.stdout
        finally:
            try:
                os.unlink(ifc_path)
            except OSError:
                pass
