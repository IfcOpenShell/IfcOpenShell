# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Michael Yoder <myoder@desertspringscivil.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""Headless operator tests for the Saikei alignment module.

Tests non-modal alignment operators end-to-end in Blender headless mode.
Follows Bonsai's existing test patterns (NewIfc4X3 base class from bootstrap).

Operators tested:
    CSV import: import_alignment_csv (EXEC_DEFAULT with explicit filepath)
"""

import pytest

import bpy
import ifcopenshell
import ifcopenshell.api.alignment as align_api

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc4X3


def _geometry_mapping_available() -> bool:
    """True when the modular geometry-mapping plugins are present.

    v0.9.0 evaluates segment endpoints through the geometry engine, which
    loads per-schema ifcopenshell_geometry_mapping_* plugins at runtime. The
    win64 v0.9.0alpha0 builds ship without them (IfcOpenShell#9301), so
    geometry-dependent tests skip locally and run in CI where builds are
    complete.
    """
    import pathlib

    package_root = pathlib.Path(ifcopenshell.__file__).parent
    return any(f.name.startswith("ifcopenshell_geometry_mapping_") for f in package_root.iterdir())


requires_geometry_engine = pytest.mark.skipif(
    not _geometry_mapping_available(),
    reason="geometry mapping plugins unavailable (IfcOpenShell#9301); covered in CI",
)

pytestmark = pytest.mark.alignment


@requires_geometry_engine
class TestImportAlignmentCsv(NewIfc4X3):
    """bim.import_alignment_csv — the single, merged CSV import path.

    CSV rows use full X,Y,R (or D,Z,L) triples: the first and last R/L values
    are placeholders per the API's create_from_csv contract.
    """

    def _write_csv(self, tmp_path, rows):
        path = tmp_path / "alignment.csv"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return str(path)

    def test_import_sets_active_alignment_and_builds_hierarchy(self, tmp_path):
        filepath = self._write_csv(tmp_path, ["0,0,0,1000,0,300,2000,800,0"])
        result = bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=filepath)
        assert result == {"FINISHED"}

        alignment = tool.Alignment.get_active_alignment()
        assert alignment is not None
        assert alignment.is_a("IfcAlignment")
        assert tool.Ifc.get_object(alignment) is not None

    def test_import_with_vertical_row_creates_vertical_layout(self, tmp_path):
        filepath = self._write_csv(
            tmp_path,
            [
                "0,0,0,1000,0,300,2000,800,0",
                "0,100,0,500,110,200,1000,105,0",
            ],
        )
        result = bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=filepath)
        assert result == {"FINISHED"}

        alignment = tool.Alignment.get_active_alignment()
        assert align_api.get_vertical_layout(alignment) is not None


@requires_geometry_engine
class TestGenerateAlignmentSegmentsFailsGracefully(NewIfc4X3):
    """_generate_alignment_segments() -- REQUIREMENTS.md #2's "curve too long" gap.

    solve_horizontal_alignment_by_pi_method() raises ValueError when a PI's requested
    spiral+circular curve needs more deflection than the PI itself turns through (curve too
    large for how close together the PIs are). That used to propagate uncaught out of
    ALIGN_OT_apply_pi_curve/_apply_horizontal_pi_table/_draw_horizontal_alignment, crashing the
    operator and leaving Blender's own "Operation partially completed" recovery message as the
    only feedback. It should instead report a specific, actionable error and leave the layout
    exactly as it was (no half-built segment list sitting in IFC).
    """

    def test_curve_too_long_reports_cleanly_and_leaves_no_partial_segments(self):
        from bonsai.bim.module.alignment.operator import _generate_alignment_segments

        ifc = tool.Ifc.get()
        alignment = align_api.create(ifc, "Test Alignment", include_vertical=False)
        h_layout = align_api.get_horizontal_layout(alignment)

        # Two PIs close together (1000m apart) but a curve radius/spiral lengths that need far
        # more room than that -- triggers solve_horizontal_alignment_by_pi_method's "spiral
        # transition curves are too long" ValueError.
        hpoints = [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (2000.0, 1000.0)]
        radii = [(500.0, 5000.0, 5000.0), 0.0]

        segments_before = align_api.get_layout_segments(h_layout)

        ok, message = _generate_alignment_segments(bpy.context, alignment, hpoints, radii)

        assert ok is False
        assert "PI 1" in message
        assert "too long" in message
        # No partial mutation left behind: still just the zero-length terminator, same as
        # before this call -- not a half-built segment list from the PIs solved before the
        # one that raised.
        segments_after = align_api.get_layout_segments(h_layout)
        assert len(segments_after) == len(segments_before) == 1


@requires_geometry_engine
class TestStartEndPointMarkers(NewIfc4X3):
    """Start/End Point marker dragging -- REQUIREMENTS.md #4's "not yet built" gap (2026-09-17).

    Previously, only interior PIs got a draggable marker (_create_pi_markers never made one for
    Start/End, and ALIGN_OT_apply_pi_curve always read the endpoints from
    tool.Alignment.get_alignment_start_end_points() instead of any marker); the only way to
    relocate either endpoint was redrawing the whole alignment. This mirrors the same
    draggable-Empty pattern used for interior PIs.
    """

    def test_create_pi_markers_always_creates_start_and_end(self):
        from bonsai.bim.module.alignment.operator import _create_pi_markers, _find_pi_markers

        ifc = tool.Ifc.get()
        alignment = align_api.create(ifc, "Test Alignment", include_vertical=False)
        tool.Alignment.create_object_for_alignment(alignment)

        # A dead-straight, two-point alignment has no interior PI at all -- it should still get
        # draggable Start/End markers.
        markers = _create_pi_markers(bpy.context, alignment.id(), [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0)])
        roles = sorted(m.bonsai_pi_curve_marker.role for m in markers)
        assert roles == ["END", "START"]
        assert _find_pi_markers(alignment.id()) == markers

    def test_dragging_start_and_end_markers_then_apply_moves_the_alignment(self):
        from bonsai.bim.module.alignment.operator import _create_pi_markers, _find_pi_markers

        ifc = tool.Ifc.get()
        alignment = align_api.create(ifc, "Test Alignment", include_vertical=False)
        h_layout = align_api.get_horizontal_layout(alignment)
        tool.Alignment.create_object_for_alignment(alignment)

        raw_points = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (100.0, 100.0, 0.0)]
        _create_pi_markers(bpy.context, alignment.id(), raw_points)
        markers = _find_pi_markers(alignment.id())
        start_marker = next(m for m in markers if m.bonsai_pi_curve_marker.role == "START")
        end_marker = next(m for m in markers if m.bonsai_pi_curve_marker.role == "END")

        start_marker.location = (10.0, -20.0, 0.0)
        end_marker.location = (100.0, 150.0, 0.0)

        bpy.context.view_layer.objects.active = start_marker
        assert bpy.ops.align.apply_pi_curve.poll()
        result = bpy.ops.align.apply_pi_curve()
        assert result == {"FINISHED"}

        real_segments = [s for s in align_api.get_layout_segments(h_layout) if s.DesignParameters.SegmentLength > 0]
        first_point = real_segments[0].DesignParameters.StartPoint.Coordinates
        assert first_point[0] == pytest.approx(10.0)
        assert first_point[1] == pytest.approx(-20.0)

    def test_finish_reselects_the_alignment(self):
        from bonsai.bim.module.alignment.operator import _create_pi_markers, _find_pi_markers

        ifc = tool.Ifc.get()
        alignment = align_api.create(ifc, "Test Alignment", include_vertical=False)
        alignment_obj = tool.Alignment.create_object_for_alignment(alignment)

        markers = _create_pi_markers(bpy.context, alignment.id(), [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0)])
        bpy.context.view_layer.objects.active = markers[0]
        markers[0].select_set(True)

        result = bpy.ops.align.finish_pi_editing()

        assert result == {"FINISHED"}
        assert _find_pi_markers(alignment.id()) == []
        assert bpy.context.view_layer.objects.active == tool.Ifc.get_object(alignment)
        assert tool.Ifc.get_object(alignment).select_get()
