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
    Horizontal: add_pi, remove_pi, recalculate_pis, clear_pis, create_alignment_by_pi
    Stationing: add_stationing_referent, name_segments
    CSV import: import_alignment_csv (EXEC_DEFAULT with explicit filepath)

Operators skipped (modal / viewport):
    pick_pi_from_viewport, enter_pi_edit_mode
"""

import types

import bpy
import ifcopenshell
import ifcopenshell.api.alignment as align_api
import ifcopenshell.api.georeference
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.alignment
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
import pytest

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_alignment_props():
    """Shortcut to CivilAlignmentProperties on the scene."""
    return bpy.context.scene.CivilAlignmentProperties


def create_empty_alignment(name="Test Alignment"):
    """Create an IfcAlignment with an empty IfcAlignmentHorizontal layout.

    Uses align_api.create() which creates IfcAlignment + IfcAlignmentHorizontal
    + zero-length terminator + geometric representations + aggregation to project.

    This is the minimal setup required for operators that need an active
    alignment (e.g. create_alignment_by_pi, recalculate_pis).

    Returns:
        tuple: (alignment_entity, alignment_blender_obj)
    """
    ifc_file = tool.Ifc.get()

    # create() handles: IfcAlignment, IfcAlignmentHorizontal, IfcRelNests,
    # zero-length terminator, geometric representation, project aggregation
    alignment = align_api.create(ifc_file, name=name)

    # Create Blender objects via the tool layer
    alignment_obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

    # Set as active so operators can find it via get_active_alignment()
    if alignment_obj:
        bpy.context.view_layer.objects.active = alignment_obj
        alignment_obj.select_set(True)

    # Set active alignment ID in properties
    props = get_alignment_props()
    props.active_alignment_id = alignment.id()
    props.active_alignment_name = name

    return alignment, alignment_obj


def add_pis_to_props(pi_data):
    """Add PIs to the props collection with specified coordinates.

    Args:
        pi_data: list of (e, n, radius) tuples.
                 First and last are auto-typed as ENDPOINT.
    """
    props = get_alignment_props()
    for i, (e, n, radius) in enumerate(pi_data):
        bpy.ops.civil.add_pi()
        pi = props.pis[len(props.pis) - 1]
        pi.e = str(e)
        pi.n = str(n)
        if radius > 0:
            pi.radius = radius


def real_segments(alignment):
    """The alignment's horizontal segments, without the zero-length terminator."""
    segments = align_api.get_layout_segments(align_api.get_horizontal_layout(alignment))
    return [s for s in segments if not tool.Alignment.is_zero_length_segment(s)]


# ===========================================================================
# Horizontal PI Operators
# ===========================================================================


class TestAddPi(NewIfc4X3):
    """Tests for CIVIL_OT_add_pi (civil.add_pi)."""

    def test_add_first_pi_sets_endpoint_at_origin(self):
        props = get_alignment_props()
        result = bpy.ops.civil.add_pi()
        assert result == {"FINISHED"}
        assert len(props.pis) == 1
        assert float(props.pis[0].e) == 0.0
        assert float(props.pis[0].n) == 0.0
        assert props.pis[0].pi_type == "ENDPOINT"

    def test_add_second_pi_offsets_from_first(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 2
        assert props.pis[1].pi_type == "ENDPOINT"
        # Second PI should be offset 100 units east
        assert float(props.pis[1].e) == pytest.approx(100.0)
        assert float(props.pis[1].n) == pytest.approx(0.0)

    def test_add_third_pi_extrapolates_and_changes_second_type(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 3
        # Second PI (index 1) should have been changed from ENDPOINT to TANGENT
        assert props.pis[1].pi_type == "TANGENT"
        # Third PI extrapolates direction
        assert float(props.pis[2].e) == pytest.approx(200.0)

    def test_active_pi_index_tracks_last_added(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        assert props.active_pi_index == 0
        bpy.ops.civil.add_pi()
        assert props.active_pi_index == 1
        bpy.ops.civil.add_pi()
        assert props.active_pi_index == 2

    def test_add_pi_triggers_geometry_recalculation(self):
        """After adding 2+ PIs, display_rows should be populated."""
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        # With 2 PIs, we should have at least 2 point rows and 1 segment row
        assert len(props.display_rows) >= 2


class TestRemovePi(NewIfc4X3):
    """Tests for CIVIL_OT_remove_pi (civil.remove_pi)."""

    def test_remove_pi_decrements_collection(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 3

        # Select first point row in display_rows
        if props.display_rows:
            props.active_display_row_index = 0
        result = bpy.ops.civil.remove_pi()
        assert result == {"FINISHED"}
        assert len(props.pis) == 2

    def test_remove_pi_from_single_item_list(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 1

        # Use active_pi_index fallback (no display_rows for 1 PI)
        props.active_pi_index = 0
        # display_rows may be empty with 1 PI, so remove_pi uses active_pi_index
        props.display_rows.clear()
        result = bpy.ops.civil.remove_pi()
        assert result == {"FINISHED"}
        assert len(props.pis) == 0

    def test_remove_pi_updates_active_index(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()

        # Select last point row
        props.active_pi_index = 2
        props.display_rows.clear()
        bpy.ops.civil.remove_pi()
        # active_pi_index should clamp to valid range
        assert props.active_pi_index <= len(props.pis) - 1


class TestClearPis(NewIfc4X3):
    """Tests for CIVIL_OT_clear_pis (civil.clear_pis).

    Note: clear_pis defines invoke() with invoke_confirm, but calling via
    bpy.ops in Python uses EXEC_DEFAULT by default, skipping invoke.
    """

    def test_clear_pis_removes_all(self):
        props = get_alignment_props()
        for _ in range(5):
            bpy.ops.civil.add_pi()
        assert len(props.pis) == 5

        result = bpy.ops.civil.clear_pis()
        assert result == {"FINISHED"}
        assert len(props.pis) == 0
        assert len(props.display_rows) == 0

    def test_clear_pis_resets_indices(self):
        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.clear_pis()
        assert props.active_pi_index == 0
        assert props.active_display_row_index == 0

    def test_clear_pis_with_active_alignment_removes_ifc(self):
        """When an active alignment exists, clear_pis should remove it from IFC."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()

        props = get_alignment_props()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()

        alignment_count_before = len(ifc_file.by_type("IfcAlignment"))
        bpy.ops.civil.clear_pis()

        alignment_count_after = len(ifc_file.by_type("IfcAlignment"))
        assert alignment_count_after < alignment_count_before
        assert len(props.pis) == 0

    def test_clear_pis_resolves_alignment_from_props_not_viewport(self):
        """The alignment is resolved via props.active_alignment_id, so it is
        deleted even when the viewport's active object is something else
        (typically a segment curve after PI editing)."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()
        bpy.context.view_layer.objects.active = None

        props = get_alignment_props()
        bpy.ops.civil.add_pi()

        alignment_count_before = len(ifc_file.by_type("IfcAlignment"))
        bpy.ops.civil.clear_pis()

        assert len(ifc_file.by_type("IfcAlignment")) < alignment_count_before
        assert props.active_alignment_id == 0
        assert props.active_alignment_name == ""

    def test_clear_pis_resets_a_reference_to_a_deleted_alignment(self):
        alignment, _ = create_empty_alignment("A")
        add_pis_to_props([(0, 0, 0), (500, 0, 0)])
        tool.Alignment.remove_alignment_hierarchy(alignment)
        ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=alignment)

        assert bpy.ops.civil.clear_pis() == {"FINISHED"}

        props = get_alignment_props()
        assert props.active_alignment_id == 0
        assert props.active_alignment_name == ""


class TestRecalculatePis(NewIfc4X3):
    """Tests for CIVIL_OT_recalculate_pis (civil.recalculate_pis)."""

    def test_recalculate_populates_display_rows(self):
        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        result = bpy.ops.civil.recalculate_pis()
        assert result == {"FINISHED"}
        assert len(props.display_rows) > 0

    def test_recalculate_computes_geometry_values(self):
        """PI geometry values (station, length_to_next) should be reasonable."""
        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 0, 0)])

        bpy.ops.civil.recalculate_pis()

        # Straight line: each segment should be 500 units
        assert props.pis[0].length_to_next == pytest.approx(500.0, abs=1.0)
        assert props.pis[1].length_to_next == pytest.approx(500.0, abs=1.0)

    @requires_geometry_engine
    def test_recalculate_with_active_alignment_updates_ifc(self):
        """When an active alignment exists, recalculate should update IFC segments."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()

        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        # First, create alignment segments
        bpy.ops.civil.create_alignment_by_pi()

        # Re-select alignment object (create_alignment_by_pi may change selection)
        bpy.context.view_layer.objects.active = alignment_obj
        alignment_obj.select_set(True)

        # Modify a PI
        props.pis[1].e = str(600.0)

        # Recalculate should update IFC in-place
        result = bpy.ops.civil.recalculate_pis()
        assert result == {"FINISHED"}

        # IFC should still have segments
        segments = ifc_file.by_type("IfcAlignmentSegment")
        assert len(segments) >= 2

    @requires_geometry_engine
    def test_layout_starts_stationing_at_the_table_start_station(self):
        """The first build adds the starting-station referent on the curve at
        props.start_station; later builds move it with the curve."""
        ifc_file = tool.Ifc.get()
        alignment = tool.Alignment.create_alignment("R")
        props = get_alignment_props()
        props.start_station = 1000.0
        props.active_alignment_id = alignment.id()
        bpy.context.view_layer.objects.active = tool.Ifc.get_object(alignment)
        add_pis_to_props([(500, 300, 0), (1000, 300, 0), (1500, 700, 0)])

        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}
        referent = align_api.get_stationing_nest(ifc_file, alignment).RelatedObjects[0]
        assert referent.Name == f"R {ifcopenshell.util.alignment.station_as_string(ifc_file, props.start_station)}"
        assert align_api.get_alignment_start_station(ifc_file, alignment) == pytest.approx(props.pis[0].station)
        position = referent.ObjectPlacement.CartesianPosition.Location.Coordinates
        assert position == pytest.approx((500.0, 300.0, 0.0), abs=1e-6)

        props.pis[0].e = str(600.0)
        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}
        assert align_api.get_stationing_nest(ifc_file, alignment).RelatedObjects == (referent,)
        position = referent.ObjectPlacement.CartesianPosition.Location.Coordinates
        assert position == pytest.approx((600.0, 300.0, 0.0), abs=1e-6)


@requires_geometry_engine
class TestPiTableAlignment(NewIfc4X3):
    """The PI table belongs to props.active_alignment_id.

    Operators that write the table to IFC target that alignment, never the
    active viewport object, and every path that sets the id or rewrites the
    alignment's segments outside the table re-seeds the table from IFC.
    """

    def _author(self, name):
        alignment, obj = create_empty_alignment(name)
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])
        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}
        return alignment, obj

    def _import_csv(self, tmp_path):
        path = tmp_path / "alignment.csv"
        path.write_text("0,0,0,1000,0,300,2000,800,0\n", encoding="utf-8")
        assert bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=str(path)) == {"FINISHED"}
        return tool.Ifc.get().by_id(get_alignment_props().active_alignment_id)

    def _lengths(self, alignment):
        return [s.DesignParameters.SegmentLength for s in real_segments(alignment)]

    def test_recalculate_writes_to_table_alignment_not_active_object(self):
        alignment_a, _ = self._author("A")
        alignment_b, obj_b = create_empty_alignment("B")
        props = get_alignment_props()
        props.active_alignment_id = alignment_a.id()
        bpy.context.view_layer.objects.active = obj_b

        props.pis[1].e = str(600.0)
        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        assert real_segments(alignment_b) == []
        assert self._lengths(alignment_a)[0] == pytest.approx(600.0)
        assert props.active_alignment_id == alignment_a.id()

    def test_recalculate_without_recorded_alignment_uses_active_object(self):
        alignment, _ = create_empty_alignment("A")
        props = get_alignment_props()
        props.active_alignment_id = 0
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        assert len(real_segments(alignment)) == 2
        assert props.active_alignment_id == alignment.id()

    def test_recalculate_with_deleted_alignment_clears_table_and_reference(self):
        alignment_a, _ = self._author("A")
        alignment_b, obj_b = create_empty_alignment("B")
        props = get_alignment_props()
        props.active_alignment_id = alignment_a.id()
        tool.Alignment.remove_alignment_hierarchy(alignment_a)
        ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=alignment_a)
        bpy.context.view_layer.objects.active = obj_b

        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        assert real_segments(alignment_b) == []
        assert len(props.pis) == 0
        assert props.active_alignment_id == 0

    def test_create_by_pi_writes_to_table_alignment_not_active_object(self):
        alignment_a, _ = create_empty_alignment("A")
        alignment_b, obj_b = create_empty_alignment("B")
        props = get_alignment_props()
        props.active_alignment_id = alignment_a.id()
        bpy.context.view_layer.objects.active = obj_b
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}

        assert len(real_segments(alignment_a)) == 2
        assert real_segments(alignment_b) == []

    def test_create_by_pi_is_unavailable_once_the_alignment_has_segments(self):
        self._author("A")
        assert not bpy.ops.civil.create_alignment_by_pi.poll()

    def test_create_by_pi_poll_reports_a_deleted_alignment(self):
        alignment, _ = create_empty_alignment("A")
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])
        tool.Alignment.remove_alignment_hierarchy(alignment)
        ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=alignment)

        with pytest.raises(RuntimeError, match="Recorded alignment no longer exists"):
            bpy.ops.civil.create_alignment_by_pi()

    def test_recalculate_after_csv_import_keeps_imported_segments(self, tmp_path):
        _, obj_a = self._author("A")
        imported = self._import_csv(tmp_path)
        props = get_alignment_props()
        coordinates = [float(value) for pi in props.pis for value in (pi.e, pi.n)]
        assert coordinates == pytest.approx([0.0, 0.0, 1000.0, 0.0, 2000.0, 800.0], abs=1e-3)
        lengths = self._lengths(imported)

        bpy.context.view_layer.objects.active = obj_a
        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        assert self._lengths(imported) == pytest.approx(lengths, abs=1e-3)

    def test_csv_import_seeds_the_table_in_map_coordinates(self, tmp_path):
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.georeference.add_georeferencing(ifc_file)
        ifcopenshell.api.georeference.edit_georeferencing(
            ifc_file, coordinate_operation={"Eastings": 1000.0, "Northings": 2000.0}
        )
        imported = self._import_csv(tmp_path)
        props = get_alignment_props()
        easting, northing, _ = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, 0.0, 0.0, 0.0)
        assert (float(props.pis[0].e), float(props.pis[0].n)) == pytest.approx((easting, northing))

        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        start = real_segments(imported)[0].DesignParameters.StartPoint.Coordinates
        assert start == pytest.approx((0.0, 0.0), abs=1e-3)

    def test_recalculate_after_pi_edit_keeps_the_edit(self):
        import bonsai.core.alignment as core
        from bonsai.bim.module.alignment.operator import CIVIL_OT_enter_pi_edit_mode

        alignment, _ = self._author("A")
        empties = core.enter_pi_edit_mode(tool.Ifc, tool.Alignment, alignment.id())
        empties[1].location.y += 150.0 * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.view_layer.update()
        # PI edit mode is modal; apply it as pressing Enter does.
        operator = types.SimpleNamespace(_alignment_id=alignment.id(), _area=None, report=lambda *args: None)
        CIVIL_OT_enter_pi_edit_mode._cleanup_and_finish(operator, bpy.context, apply=True)
        props = get_alignment_props()
        assert float(props.pis[1].n) == pytest.approx(150.0, abs=1e-3)
        lengths = self._lengths(alignment)

        bpy.context.view_layer.objects.active = None
        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        assert self._lengths(alignment) == pytest.approx(lengths, abs=1e-3)

    def test_applying_a_pi_edit_moves_the_start_referent_with_the_curve(self):
        import bonsai.core.alignment as core
        from bonsai.bim.module.alignment.operator import CIVIL_OT_enter_pi_edit_mode

        alignment, _ = self._author("A")
        empties = core.enter_pi_edit_mode(tool.Ifc, tool.Alignment, alignment.id())
        empties[0].location.x += 50.0 * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.view_layer.update()
        operator = types.SimpleNamespace(_alignment_id=alignment.id(), _area=None, report=lambda *args: None)
        CIVIL_OT_enter_pi_edit_mode._cleanup_and_finish(operator, bpy.context, apply=True)

        referent = align_api.get_stationing_nest(tool.Ifc.get(), alignment).RelatedObjects[0]
        position = referent.ObjectPlacement.CartesianPosition.Location.Coordinates
        assert position == pytest.approx((50.0, 0.0, 0.0), abs=1e-6)


@requires_geometry_engine
class TestCreateAlignmentByPi(NewIfc4X3):
    """Tests for CIVIL_OT_create_alignment_by_pi (civil.create_alignment_by_pi).

    This operator requires an existing empty alignment set as active.
    """

    def test_create_alignment_creates_ifc_segments(self):
        """Basic 3-PI alignment: creates tangent + tangent segments in IFC."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()

        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        result = bpy.ops.civil.create_alignment_by_pi()
        assert result == {"FINISHED"}

        # IFC should contain alignment segments
        segments = ifc_file.by_type("IfcAlignmentSegment")
        assert len(segments) >= 2

        # Alignment should still exist
        alignments = ifc_file.by_type("IfcAlignment")
        assert len(alignments) == 1

        # Horizontal layout should exist
        horizontals = ifc_file.by_type("IfcAlignmentHorizontal")
        assert len(horizontals) == 1

    def test_create_alignment_with_curve_creates_arc_segment(self):
        """3-PI alignment with radius on middle PI creates LINE + ARC + LINE."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()

        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 300), (1000, 200, 0)])

        result = bpy.ops.civil.create_alignment_by_pi()
        assert result == {"FINISHED"}

        # Check segment design parameter types
        segments = ifc_file.by_type("IfcAlignmentSegment")
        segment_types = []
        for seg in segments:
            dp = seg.DesignParameters
            if dp and hasattr(dp, "PredefinedType"):
                segment_types.append(dp.PredefinedType)

        # Should have at least LINE and CIRCULARARC
        assert "LINE" in segment_types
        assert "CIRCULARARC" in segment_types

    def test_create_alignment_produces_blender_objects(self):
        """After creation, Blender scene should contain alignment objects."""
        alignment, alignment_obj = create_empty_alignment()

        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        bpy.ops.civil.create_alignment_by_pi()

        # Should have at least the alignment object in the scene
        alignment_objects = [
            obj
            for obj in bpy.data.objects
            if tool.Ifc.get_entity(obj) and tool.Ifc.get_entity(obj).is_a("IfcAlignment")
        ]
        assert len(alignment_objects) >= 1

    def test_create_straight_alignment_two_pis(self):
        """Minimal alignment: 2 PIs producing a single tangent."""
        alignment, alignment_obj = create_empty_alignment()
        ifc_file = tool.Ifc.get()

        props = get_alignment_props()
        add_pis_to_props([(0, 0, 0), (1000, 0, 0)])

        result = bpy.ops.civil.create_alignment_by_pi()
        assert result == {"FINISHED"}

        segments = ifc_file.by_type("IfcAlignmentSegment")
        assert len(segments) >= 1

    def test_adds_start_station_referent(self):
        alignment, _ = create_empty_alignment()
        get_alignment_props().start_station = 1000.0
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}

        start_station = align_api.get_alignment_start_station(tool.Ifc.get(), alignment)
        assert start_station == pytest.approx(1000.0)

    def test_new_alignment_is_stationed_from_zero_by_default(self):
        """A new alignment is stationed from 0, the station the alignment API assumes
        before any stationing referent exists (distance_along_from_station)."""
        ifc_file = tool.Ifc.get()
        alignment, _ = create_empty_alignment("A")
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}

        referent = align_api.get_stationing_nest(ifc_file, alignment).RelatedObjects[0]
        assert referent.Name == f"A {ifcopenshell.util.alignment.station_as_string(ifc_file, 0.0)}"
        assert align_api.get_alignment_start_station(ifc_file, alignment) == 0.0
        assert get_alignment_props().pis[0].station == 0.0

    def test_radius_is_converted_to_project_units(self):
        """pi.radius is a Blender length in metres; a feet project gets feet."""
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": False, "raw": "FEET"})
        alignment, _ = create_empty_alignment()
        add_pis_to_props([(0, 0, 0), (1000, 0, 100), (2000, 800, 0)])

        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}

        arc = next(s for s in real_segments(alignment) if s.DesignParameters.PredefinedType == "CIRCULARARC")
        radius = abs(arc.DesignParameters.StartRadiusOfCurvature)
        assert radius == pytest.approx(100.0 / ifcopenshell.util.unit.calculate_unit_scale(ifc_file))


@requires_geometry_engine
class TestEndToEndAlignmentCreation(NewIfc4X3):
    """Full workflow: create alignment, add PIs, create IFC, validate."""

    def test_basic_three_pi_alignment_workflow(self):
        """Scenario 1: Create a basic 3-PI alignment end-to-end."""
        alignment, alignment_obj = create_empty_alignment("E2E Test Alignment")
        ifc_file = tool.Ifc.get()
        props = get_alignment_props()

        # Add 3 PIs: straight segment then angled
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])
        assert len(props.pis) == 3

        # Create alignment
        result = bpy.ops.civil.create_alignment_by_pi()
        assert result == {"FINISHED"}

        # Validate IFC entities
        alignments = ifc_file.by_type("IfcAlignment")
        assert len(alignments) == 1
        assert alignments[0].Name == "E2E Test Alignment"

        horizontals = ifc_file.by_type("IfcAlignmentHorizontal")
        assert len(horizontals) == 1

        segments = ifc_file.by_type("IfcAlignmentSegment")
        # At minimum: tangent + tangent (+ zero-length terminator possibly)
        assert len(segments) >= 2

        # All segment design params should be IfcAlignmentHorizontalSegment
        for seg in segments:
            dp = seg.DesignParameters
            if dp:
                assert dp.is_a("IfcAlignmentHorizontalSegment")

    def test_three_pi_with_curve_workflow(self):
        """Scenario 2: 3-PI alignment with curve produces correct IFC segments."""
        alignment, alignment_obj = create_empty_alignment("Curved Alignment")
        ifc_file = tool.Ifc.get()
        props = get_alignment_props()

        # PI with 300m radius on middle point
        add_pis_to_props([(0, 0, 0), (500, 0, 300), (1000, 500, 0)])

        bpy.ops.civil.create_alignment_by_pi()

        segments = ifc_file.by_type("IfcAlignmentSegment")
        predefined_types = set()
        for seg in segments:
            dp = seg.DesignParameters
            if dp and hasattr(dp, "PredefinedType"):
                predefined_types.add(dp.PredefinedType)

        assert "LINE" in predefined_types
        assert "CIRCULARARC" in predefined_types

    def test_five_pi_complex_alignment(self):
        """Scenario 3: 5-PI alignment with multiple curves."""
        alignment, alignment_obj = create_empty_alignment("Complex Alignment")
        ifc_file = tool.Ifc.get()
        props = get_alignment_props()

        add_pis_to_props(
            [
                (0, 0, 0),
                (300, 0, 200),
                (600, 300, 150),
                (900, 300, 250),
                (1200, 0, 0),
            ]
        )

        result = bpy.ops.civil.create_alignment_by_pi()
        assert result == {"FINISHED"}

        segments = ifc_file.by_type("IfcAlignmentSegment")
        # 5 PIs with 3 interior curves → many segments
        assert len(segments) >= 4

    def test_add_remove_pi_cycle(self):
        """Scenario 4: Add/remove PIs cycle - props stay consistent."""
        props = get_alignment_props()

        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 3

        # Remove middle PI
        props.display_rows.clear()
        props.active_pi_index = 1
        bpy.ops.civil.remove_pi()
        assert len(props.pis) == 2

        # Add two more
        bpy.ops.civil.add_pi()
        bpy.ops.civil.add_pi()
        assert len(props.pis) == 4

        # Clear all
        bpy.ops.civil.clear_pis()
        assert len(props.pis) == 0
        assert len(props.display_rows) == 0


@requires_geometry_engine
class TestEndToEndIfcRoundtrip(NewIfc4X3):
    """IFC save/reload roundtrip validation."""

    def test_alignment_survives_ifc_roundtrip(self):
        """Create alignment, save to temp file, reload, verify entities."""
        import os
        import tempfile

        alignment, alignment_obj = create_empty_alignment("Roundtrip Test")
        ifc_file = tool.Ifc.get()
        props = get_alignment_props()

        add_pis_to_props([(0, 0, 0), (500, 0, 300), (1000, 200, 0)])
        bpy.ops.civil.create_alignment_by_pi()

        # Count entities before save
        alignment_count = len(ifc_file.by_type("IfcAlignment"))
        horizontal_count = len(ifc_file.by_type("IfcAlignmentHorizontal"))
        segment_count = len(ifc_file.by_type("IfcAlignmentSegment"))

        assert alignment_count == 1
        assert horizontal_count == 1
        assert segment_count >= 2

        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), "alignment_roundtrip_test.ifc")
        ifc_file.write(temp_path)

        # Reload
        reloaded = ifcopenshell.open(temp_path)

        # Verify entity counts match
        assert len(reloaded.by_type("IfcAlignment")) == alignment_count
        assert len(reloaded.by_type("IfcAlignmentHorizontal")) == horizontal_count
        assert len(reloaded.by_type("IfcAlignmentSegment")) == segment_count

        # Verify alignment name survived
        assert reloaded.by_type("IfcAlignment")[0].Name == "Roundtrip Test"

        # Cleanup
        os.unlink(temp_path)


# Station formatting is tool-layer now (tool.Alignment.format_station wrapping
# ifcopenshell.util.alignment.station_as_string) — see TestFormatStation in
# test/tool/test_alignment.py.


class TestStationingOperators(NewIfc4X3):
    """civil.add_stationing_referent and civil.name_segments (Stationing sub-panel)."""

    def _author(self):
        alignment, _ = create_empty_alignment("A")
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])
        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}
        return alignment

    def _referent(self, alignment, station):
        referents = align_api.get_stationing_nest(tool.Ifc.get(), alignment).RelatedObjects
        return next(r for r in referents if r.Name == tool.Alignment.format_station(station))

    def _distance_along(self, referent):
        return referent.ObjectPlacement.RelativePlacement.Location.DistanceAlong.wrappedValue

    @requires_geometry_engine
    def test_add_stationing_referent_adds_a_station_referent(self):
        alignment = self._author()
        station = get_alignment_props().start_station + 200.0

        assert bpy.ops.civil.add_stationing_referent("EXEC_DEFAULT", station=station) == {"FINISHED"}

        assert self._distance_along(self._referent(alignment, station)) == pytest.approx(200.0)

    @requires_geometry_engine
    def test_add_stationing_referent_uses_the_alignments_own_stationing(self, tmp_path):
        """A CSV import is stationed from 0, whatever the Creation panel's start station."""
        get_alignment_props().start_station = 10000.0
        path = tmp_path / "alignment.csv"
        path.write_text("0,0,0,1000,0,300,2000,800,0\n", encoding="utf-8")
        assert bpy.ops.bim.import_alignment_csv("EXEC_DEFAULT", filepath=str(path)) == {"FINISHED"}
        ifc_file = tool.Ifc.get()
        alignment = ifc_file.by_id(get_alignment_props().active_alignment_id)

        assert bpy.ops.civil.add_stationing_referent("EXEC_DEFAULT", station=500.0) == {"FINISHED"}

        assert self._distance_along(self._referent(alignment, 500.0)) == pytest.approx(500.0)
        assert align_api.get_alignment_start_station(ifc_file, alignment) == pytest.approx(0.0)

    @requires_geometry_engine
    def test_add_stationing_referent_rejects_a_station_off_the_alignment(self):
        alignment = self._author()
        start_station = align_api.get_alignment_start_station(tool.Ifc.get(), alignment)

        for station in (start_station - 1.0, start_station + 5000.0):
            with pytest.raises(RuntimeError, match="is not on the alignment"):
                bpy.ops.civil.add_stationing_referent("EXEC_DEFAULT", station=station)

        assert len(align_api.get_stationing_nest(tool.Ifc.get(), alignment).RelatedObjects) == 1

    @requires_geometry_engine
    def test_add_stationing_referent_rejects_a_point_already_marked(self):
        """Re-adding the start station, or the back station of an equation, must not
        add a second referent that redefines that point's station."""
        ifc_file = tool.Ifc.get()
        alignment = self._author()
        start_station = align_api.get_alignment_start_station(ifc_file, alignment)
        align_api.add_stationing_referent(
            ifc_file, "EQ", alignment, 200.0, start_station + 1000.0, incoming_station=start_station + 200.0
        )

        for station in (start_station, start_station + 200.0):
            with pytest.raises(RuntimeError, match="already marks this point"):
                bpy.ops.civil.add_stationing_referent("EXEC_DEFAULT", station=station)

        assert len(align_api.get_stationing_nest(ifc_file, alignment).RelatedObjects) == 2

    def test_add_stationing_referent_needs_a_built_alignment(self):
        create_empty_alignment("A")

        with pytest.raises(RuntimeError, match="Build the alignment first"):
            bpy.ops.civil.add_stationing_referent("EXEC_DEFAULT", station=0.0)

    @requires_geometry_engine
    def test_name_segments_names_each_layout_in_sequence(self):
        alignment = self._author()
        align_api.add_vertical_layout(tool.Ifc.get(), alignment)

        assert bpy.ops.civil.name_segments() == {"FINISHED"}

        horizontal = align_api.get_layout_segments(align_api.get_horizontal_layout(alignment))
        vertical = align_api.get_layout_segments(align_api.get_vertical_layout(alignment))
        assert [s.Name for s in horizontal] == ["H1", "H2", "H3"]
        assert vertical
        assert [s.Name for s in vertical] == [f"V{i}" for i in range(1, len(vertical) + 1)]


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

        props = get_alignment_props()
        assert props.active_alignment_id != 0
        alignment = tool.Ifc.get().by_id(props.active_alignment_id)
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

        props = get_alignment_props()
        alignment = tool.Ifc.get().by_id(props.active_alignment_id)
        assert align_api.get_vertical_layout(alignment) is not None


class TestAddElementAlignment(NewIfc4X3):
    """Shift-A Add Element route for IfcAlignment (spec intro / 1.1).

    Reinstated from the 0.8 saikei branch in minimal scope: IfcAlignment in
    the Definition dropdown; creating one bootstraps the horizontal layout,
    zero-length terminator, and project aggregation, landing in the same
    state as panel creation. Stationing starts with the first layout.
    """

    def _add_alignment(self, name=""):
        import bonsai.bim.module.root.data

        bonsai.bim.module.root.data.IfcClassData.load()
        root_props = tool.Root.get_root_props()
        root_props.ifc_product = "IfcAlignment"
        root_props.ifc_class = "IfcAlignment"
        if name:
            root_props.name = name
        return bpy.ops.bim.add_element()

    def test_ifc_alignment_offered_in_products(self):
        products = tool.Root.get_ifc_products()
        assert "IfcAlignment" in products

    def test_add_element_bootstraps_horizontal_layout(self):
        result = self._add_alignment(name="Route 66")
        assert result == {"FINISHED"}

        ifc_file = tool.Ifc.get()
        alignments = ifc_file.by_type("IfcAlignment")
        assert len(alignments) == 1
        alignment = alignments[0]

        h_layout = align_api.get_horizontal_layout(alignment)
        assert h_layout is not None
        assert align_api.has_zero_length_segment(h_layout)

    def test_add_element_alignment_is_aggregated_not_contained(self):
        self._add_alignment()
        alignment = tool.Ifc.get().by_type("IfcAlignment")[0]
        assert alignment.Decomposes
        assert alignment.Decomposes[0].RelatingObject.is_a("IfcProject")
        assert not alignment.ContainedInStructure

    def test_add_element_sets_active_and_leaves_stationing_to_first_layout(self):
        self._add_alignment(name="Route 66")
        alignment = tool.Ifc.get().by_type("IfcAlignment")[0]

        assert align_api.get_stationing_nest(tool.Ifc.get(), alignment) is None

        props = get_alignment_props()
        assert props.active_alignment_id == alignment.id()
        assert props.active_alignment_name == "Route 66"

    def test_add_element_clears_the_previous_alignments_pi_table(self):
        alignment_a, _ = create_empty_alignment("A")
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        self._add_alignment(name="Route 66")

        props = get_alignment_props()
        assert len(props.pis) == 0
        assert props.active_alignment_id != alignment_a.id()

    @requires_geometry_engine
    def test_add_element_adopts_an_unbound_pi_table(self):
        """PIs picked before any alignment existed are not bound to one; the
        new alignment takes them, and Create by PI Method builds them into it."""
        add_pis_to_props([(0, 0, 0), (500, 0, 0), (1000, 200, 0)])

        self._add_alignment(name="Route 66")

        assert len(get_alignment_props().pis) == 3
        assert bpy.ops.civil.create_alignment_by_pi() == {"FINISHED"}
        alignment = tool.Ifc.get().by_type("IfcAlignment")[0]
        assert len(real_segments(alignment)) == 2

    @requires_geometry_engine
    def test_first_layout_adds_stationing_referent_on_the_curve(self):
        self._add_alignment(name="Route 66")
        ifc_file = tool.Ifc.get()
        alignment = ifc_file.by_type("IfcAlignment")[0]
        props = get_alignment_props()
        props.start_station = 1000.0
        add_pis_to_props([(500, 300, 0), (1000, 300, 0), (1500, 700, 0)])

        assert bpy.ops.civil.recalculate_pis() == {"FINISHED"}

        referent = align_api.get_stationing_nest(ifc_file, alignment).RelatedObjects[0]
        station = ifcopenshell.util.alignment.station_as_string(ifc_file, props.start_station)
        assert referent.Name == f"Route 66 {station}"
        position = referent.ObjectPlacement.CartesianPosition.Location.Coordinates
        assert position == pytest.approx((500.0, 300.0, 0.0), abs=1e-6)


class TestSubPanelVisibility(NewIfc4X3):
    """Sub-panels follow their CIVIL root panel, as Bonsai's own sub-panels do.

    Only root panels have panel_visibilities entries, so on the Bookmark tab
    should_show_panel is False for a sub-panel's own idname. Polling it hid
    the sub-panels whenever the root panel was shown there.
    """

    def test_sub_panels_poll_true_when_should_show_panel_rejects_them(self, monkeypatch):
        from bonsai.bim.module.alignment import ui

        monkeypatch.setattr(tool.Blender, "should_show_panel", classmethod(lambda cls, *args: False))
        for panel in (ui.CIVIL_PT_alignment_creation, ui.CIVIL_PT_pi_editor, ui.CIVIL_PT_alignment_stationing):
            assert panel.poll(bpy.context)
