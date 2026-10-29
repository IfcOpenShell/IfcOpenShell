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

import bpy
import ifcopenshell
import ifcopenshell.api.alignment as align_api
import pytest

import bonsai.tool as tool
from bonsai.tool.alignment import Alignment as subject
from test.bim.bootstrap import NewFile, NewIfc4X3


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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeDesignParams:
    """Minimal stand-in for an IfcAlignmentHorizontalSegment or similar."""

    def __init__(self, ifc_class: str, segment_length: float = 0.0, horizontal_length: float = 0.0):
        self._ifc_class = ifc_class
        self.SegmentLength = segment_length
        self.HorizontalLength = horizontal_length

    def is_a(self, ifc_class: str) -> bool:
        return self._ifc_class == ifc_class


class _FakeSegment:
    """Minimal stand-in for an IfcAlignmentSegment."""

    def __init__(self, design_params=None):
        self.DesignParameters = design_params


# ---------------------------------------------------------------------------
# is_zero_length_segment
# ---------------------------------------------------------------------------


class TestIsZeroLengthSegment(NewFile):
    def test_returns_false_when_segment_has_no_design_parameters(self):
        seg = _FakeSegment(design_params=None)
        assert subject.is_zero_length_segment(seg) is False

    def test_returns_true_for_horizontal_segment_with_zero_length(self):
        dp = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=0.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is True

    def test_returns_false_for_horizontal_segment_with_nonzero_length(self):
        dp = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=100.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is False

    def test_returns_true_for_vertical_segment_with_zero_horizontal_length(self):
        dp = _FakeDesignParams("IfcAlignmentVerticalSegment", horizontal_length=0.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is True

    def test_returns_false_for_vertical_segment_with_nonzero_horizontal_length(self):
        dp = _FakeDesignParams("IfcAlignmentVerticalSegment", horizontal_length=50.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is False

    def test_returns_true_for_cant_segment_with_zero_horizontal_length(self):
        dp = _FakeDesignParams("IfcAlignmentCantSegment", horizontal_length=0.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is True

    def test_returns_false_for_unknown_segment_type(self):
        dp = _FakeDesignParams("IfcUnknownSegmentType", segment_length=0.0)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is False

    def test_uses_near_zero_tolerance(self):
        """Lengths below 1e-6 should be considered zero."""
        dp = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=1e-7)
        seg = _FakeSegment(dp)
        assert subject.is_zero_length_segment(seg) is True


# ---------------------------------------------------------------------------
# safe_layout_horizontal_by_pi_method
# ---------------------------------------------------------------------------


@requires_geometry_engine
class TestSafeLayoutHorizontalByPiMethod(NewFile):
    def test_raises_when_layout_has_no_parent_alignment(self):
        """An orphan layout (no parent IfcAlignment) must raise ValueError."""
        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        orphan_layout = ifc.createIfcAlignmentHorizontal()
        with pytest.raises(ValueError, match="no parent IfcAlignment"):
            subject.safe_layout_horizontal_by_pi_method(
                ifc, orphan_layout, hpoints=[(0.0, 0.0), (100.0, 0.0)], radii=[]
            )

    def test_succeeds_when_layout_has_parent_alignment(self):
        """A layout properly nested under an IfcAlignment should not raise."""
        import ifcopenshell.api.alignment
        import ifcopenshell.api.root

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        # Create a minimal alignment hierarchy
        project = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        alignment = ifc.createIfcAlignment()
        layout = ifc.createIfcAlignmentHorizontal()
        ifc.createIfcRelNests(RelatingObject=alignment, RelatedObjects=[layout])
        result = subject.safe_layout_horizontal_by_pi_method(ifc, layout, hpoints=[(0.0, 0.0), (100.0, 0.0)], radii=[])
        assert result is True


# ===========================================================================
# Blender-Dependent Tool Tests (require full Bonsai IFC4X3 project)
# ===========================================================================
# These tests exercise methods that create or query Blender objects.
# They use NewIfc4X3 which sets up a clean Blender scene with a Bonsai-managed
# IFC4X3 project (IfcProject + geometric contexts + IfcStore integration).


def _create_alignment_with_pis(name="Test Alignment", hpoints=None, radii=None):
    """Helper: create an IfcAlignment, add PI segments, return (alignment, h_layout).

    Uses align_api.create() to build the full alignment hierarchy (IfcAlignment
    + IfcAlignmentHorizontal + zero-length terminator + geometry + project
    aggregation), then lays out horizontal segments via PI method.
    """
    if hpoints is None:
        hpoints = [(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)]
    if radii is None:
        radii = [300.0]

    ifc_file = tool.Ifc.get()
    alignment = align_api.create(ifc_file, name=name)
    h_layout = align_api.get_horizontal_layout(alignment)

    # Add real segments via PI method
    align_api.layout_horizontal_alignment_by_pi_method(ifc_file, h_layout, hpoints, radii)

    return alignment, h_layout


# ---------------------------------------------------------------------------
# get_horizontal_layout (IFC queries, no bpy needed)
# ---------------------------------------------------------------------------


class TestGetHorizontalLayout(NewIfc4X3):
    """Tests for Alignment.get_horizontal_layout()."""

    def test_returns_horizontal_layout_from_alignment(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="HL Test")
        h_layout = subject.get_horizontal_layout(alignment)
        assert h_layout is not None
        assert h_layout.is_a("IfcAlignmentHorizontal")

    def test_returns_none_for_alignment_without_horizontal(self):
        ifc_file = tool.Ifc.get()
        # Create a bare alignment without the helper (no nesting)
        alignment = ifc_file.createIfcAlignment(GlobalId=ifcopenshell.guid.new(), Name="Bare")
        h_layout = subject.get_horizontal_layout(alignment)
        assert h_layout is None


# ---------------------------------------------------------------------------
# Blender Object Creation Methods
# ---------------------------------------------------------------------------


class TestCreateObjectForAlignment(NewIfc4X3):
    """Tests for Alignment.create_object_for_alignment()."""

    def test_creates_empty_object_for_alignment(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="ObjTest")
        obj = subject.create_object_for_alignment(alignment)
        assert obj is not None
        assert obj.type == "EMPTY"
        assert "IfcAlignment" in obj.name

    def test_links_blender_object_to_ifc_entity(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="LinkTest")
        obj = subject.create_object_for_alignment(alignment)
        # Verify bidirectional IFC link
        assert tool.Ifc.get_object(alignment) == obj
        assert tool.Ifc.get_entity(obj) == alignment

    def test_returns_existing_object_if_already_linked(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="DupTest")
        obj1 = subject.create_object_for_alignment(alignment)
        obj2 = subject.create_object_for_alignment(alignment)
        assert obj1 == obj2  # Same object returned, not a duplicate


class TestCreateObjectForLayout(NewIfc4X3):
    """Tests for Alignment.create_object_for_layout()."""

    def test_creates_empty_object_for_horizontal_layout(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="LayoutObj")
        h_layout = align_api.get_horizontal_layout(alignment)
        alignment_obj = subject.create_object_for_alignment(alignment)
        layout_obj = subject.create_object_for_layout(h_layout, alignment_obj)
        assert layout_obj is not None
        assert layout_obj.type == "EMPTY"
        assert "IfcAlignmentHorizontal" in layout_obj.name

    def test_layout_object_is_parented_to_alignment_object(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="ParentTest")
        h_layout = align_api.get_horizontal_layout(alignment)
        alignment_obj = subject.create_object_for_alignment(alignment)
        layout_obj = subject.create_object_for_layout(h_layout, alignment_obj)
        assert layout_obj.parent == alignment_obj


class TestCreateHierarchyForAlignment(NewIfc4X3):
    """Tests for Alignment.create_hierarchy_for_alignment() — full hierarchy creation."""

    def test_creates_alignment_and_layout_objects(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="Hierarchy")
        root_obj = subject.create_hierarchy_for_alignment(alignment)
        assert root_obj is not None
        assert tool.Ifc.get_entity(root_obj) == alignment
        # Should have at least one child (the horizontal layout object)
        child_objects = [o for o in bpy.data.objects if o.parent == root_obj]
        assert len(child_objects) >= 1
        # One of the children should be linked to the horizontal layout
        h_layout = align_api.get_horizontal_layout(alignment)
        layout_obj = tool.Ifc.get_object(h_layout)
        assert layout_obj is not None
        assert layout_obj.parent == root_obj

    def test_creates_vertical_layout_object_when_present(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="WithVert", include_vertical=True)
        root_obj = subject.create_hierarchy_for_alignment(alignment)
        v_layout = align_api.get_vertical_layout(alignment)
        assert v_layout is not None
        v_layout_obj = tool.Ifc.get_object(v_layout)
        assert v_layout_obj is not None
        assert v_layout_obj.parent == root_obj


# ---------------------------------------------------------------------------
# get_active_alignment
# ---------------------------------------------------------------------------


class TestGetActiveAlignment(NewIfc4X3):
    """Tests for Alignment.get_active_alignment() — scene context queries."""

    def test_returns_none_when_no_object_is_active(self):
        bpy.context.view_layer.objects.active = None
        result = subject.get_active_alignment()
        assert result is None

    def test_returns_none_when_active_object_is_not_alignment(self):
        # Active object is some random cube, not an IFC alignment
        bpy.ops.mesh.primitive_cube_add()
        assert subject.get_active_alignment() is None

    def test_returns_alignment_when_active_object_is_linked(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="Active")
        obj = subject.create_object_for_alignment(alignment)
        bpy.context.view_layer.objects.active = obj
        result = subject.get_active_alignment()
        assert result is not None
        assert result.id() == alignment.id()


# ---------------------------------------------------------------------------
# Remove alignment hierarchy
# ---------------------------------------------------------------------------


class TestRemoveAlignmentHierarchy(NewIfc4X3):
    """Tests for Alignment.remove_alignment_hierarchy() — cleanup."""

    def test_removes_all_blender_objects_for_alignment(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="RemoveMe")
        root_obj = subject.create_hierarchy_for_alignment(alignment)
        assert root_obj is not None

        # Count objects before removal (excluding default camera/light)
        alignment_objects_before = [o for o in bpy.data.objects if tool.Ifc.get_entity(o)]
        assert len(alignment_objects_before) > 0

        removed = subject.remove_alignment_hierarchy(alignment)
        assert removed > 0

        # The alignment object should be gone
        assert tool.Ifc.get_object(alignment) is None


# ---------------------------------------------------------------------------
# IFC Roundtrip (save + reload)
# ---------------------------------------------------------------------------


@requires_geometry_engine
class TestIfcSaveReloadRoundtrip(NewIfc4X3):
    """Tests verifying alignment data survives IFC file save/reload."""

    def test_alignment_entities_survive_roundtrip(self):
        import os
        import tempfile

        alignment, _ = _create_alignment_with_pis(hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0])

        ifc_file = tool.Ifc.get()
        alignment_count_before = len(ifc_file.by_type("IfcAlignment"))
        segment_count_before = len(ifc_file.by_type("IfcAlignmentSegment"))

        tmp = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
        tmp.close()
        try:
            ifc_file.write(tmp.name)
            reloaded = ifcopenshell.open(tmp.name)

            assert len(reloaded.by_type("IfcAlignment")) == alignment_count_before
            assert len(reloaded.by_type("IfcAlignmentSegment")) == segment_count_before
            assert len(reloaded.by_type("IfcAlignmentHorizontal")) >= 1

            # Verify segment types survived
            segments = reloaded.by_type("IfcAlignmentSegment")
            predefined_types = set()
            for seg in segments:
                dp = seg.DesignParameters
                if dp and hasattr(dp, "PredefinedType") and dp.PredefinedType:
                    predefined_types.add(dp.PredefinedType)
            assert "LINE" in predefined_types
            assert "CIRCULARARC" in predefined_types
        finally:
            os.unlink(tmp.name)


# ---------------------------------------------------------------------------
# clear_layout_segments  (re-implemented after upstream removed the API helper)
# ---------------------------------------------------------------------------


@requires_geometry_engine
def _has_real_segments(layout) -> bool:
    """Whether ``layout`` has any segment beyond the zero-length terminator."""
    return any(not subject.is_zero_length_segment(s) for s in align_api.get_layout_segments(layout))


class TestClearLayoutSegments(NewFile):
    """The alignment API exposes no segment-clearing helper and its layout
    functions only append, so editing relies on tool.Alignment.clear_layout_segments.
    These verify it removes real segments (both halves) without orphans and
    keeps the zero-length terminator, for horizontal and vertical layouts."""

    @staticmethod
    def _new_ifc():
        import ifcopenshell.api.root
        import ifcopenshell.api.unit

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        return ifc

    def test_clear_horizontal_keeps_only_terminator(self):
        ifc = self._new_ifc()
        alignment = align_api.create(ifc, name="Clr", include_vertical=False)
        h = align_api.get_horizontal_layout(alignment)
        align_api.layout_horizontal_alignment_by_pi_method(
            ifc, h, hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        assert _has_real_segments(h) is True
        subject.clear_layout_segments(h)
        assert _has_real_segments(h) is False
        assert len(align_api.get_layout_segments(h)) == 1  # terminator only

    def test_relayout_after_clear_has_no_doubling_or_orphans(self):
        ifc = self._new_ifc()
        alignment = align_api.create(ifc, name="Clr2", include_vertical=False)
        h = align_api.get_horizontal_layout(alignment)
        align_api.layout_horizontal_alignment_by_pi_method(
            ifc, h, hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        subject.clear_layout_segments(h)
        align_api.layout_horizontal_alignment_by_pi_method(ifc, h, hpoints=[(0.0, 0.0), (1000.0, 0.0)], radii=[])
        nested = align_api.get_layout_segments(h)
        real = [s for s in nested if not subject.is_zero_length_segment(s)]
        assert len(real) == 1  # exactly one LINE — no leftover from the first layout
        # No orphaned semantic segments left in the file.
        assert len(ifc.by_type("IfcAlignmentSegment")) == len(nested)

    def test_clear_vertical_keeps_only_terminator(self):
        ifc = self._new_ifc()
        alignment = align_api.create(ifc, name="ClrV", include_vertical=False)
        h = align_api.get_horizontal_layout(alignment)
        align_api.layout_horizontal_alignment_by_pi_method(ifc, h, hpoints=[(0.0, 0.0), (1000.0, 0.0)], radii=[])
        v = align_api.add_vertical_layout(ifc, alignment)
        align_api.layout_vertical_alignment_by_pi_method(
            ifc, v, [(0.0, 100.0), (500.0, 110.0), (1000.0, 100.0)], [100.0]
        )
        assert _has_real_segments(v) is True
        subject.clear_layout_segments(v)
        assert _has_real_segments(v) is False


class TestFormatStation(NewFile):
    """tool.Alignment.format_station — project-unit-driven stationing notation."""

    def _make_file(self, length):
        import ifcopenshell.api.root
        import ifcopenshell.api.unit

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc, length=length)
        return ifc

    def test_metric_metre_project_uses_three_digit_groups(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        assert subject.format_station(10050.0) == "10+050.000"

    def test_imperial_foot_project_uses_two_digit_groups(self):
        self._make_file(length={"is_metric": False, "raw": "FEET"})
        assert subject.format_station(10050.0) == "100+50.00"

    def test_zero_station_metric(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        assert subject.format_station(0.0) == "0+000.000"

    def test_negative_station_keeps_sign(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        assert subject.format_station(-50.0) == "-0+050.000"

    def test_without_project_falls_back_to_plain_number(self):
        assert subject.format_station(1234.5) == "1234.50"


class TestParseStation(NewFile):
    """tool.Alignment.parse_station — the inverse of format_station()."""

    def _make_file(self, length):
        import ifcopenshell.api.root
        import ifcopenshell.api.unit

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc, length=length)
        return ifc

    def test_plain_number_is_taken_literally(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        assert subject.parse_station("1000") == 1000.0
        assert subject.parse_station("1000.5") == 1000.5

    def test_metric_stationing_notation(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        assert subject.parse_station("10+050.000") == 10050.0
        assert subject.parse_station("1+000") == 1000.0

    def test_imperial_stationing_notation(self):
        self._make_file(length={"is_metric": False, "raw": "FEET"})
        assert subject.parse_station("100+50.00") == 10050.0
        assert subject.parse_station("10+00") == 1000.0

    def test_round_trips_with_format_station(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        for value in (0.0, 100.0, 10050.0, -50.0):
            assert subject.parse_station(subject.format_station(value)) == pytest.approx(value, abs=0.01)

    def test_without_project_falls_back_to_plain_float_parse(self):
        assert subject.parse_station("1234.5") == 1234.5

    def test_raises_on_invalid_input(self):
        self._make_file(length={"is_metric": True, "raw": "METERS"})
        with pytest.raises(ValueError):
            subject.parse_station("not a station")


# ---------------------------------------------------------------------------
# Cant follows horizontal edits
# ---------------------------------------------------------------------------


class _FakeHorizontalParams:
    def __init__(self, predefined_type: str, length: float, radius: float = 0.0):
        self.PredefinedType = predefined_type
        self.SegmentLength = length
        self.StartRadiusOfCurvature = radius


class TestBuildCantSpecsFromHorizontal(NewFile):
    def test_tangent_after_a_curve_without_spirals_is_not_canted(self):
        h_segments = [
            _FakeSegment(_FakeHorizontalParams("LINE", 100.0)),
            _FakeSegment(_FakeHorizontalParams("CIRCULARARC", 50.0, -300.0)),
            _FakeSegment(_FakeHorizontalParams("LINE", 100.0)),
            _FakeSegment(_FakeHorizontalParams("CIRCULARARC", 50.0, 300.0)),
            _FakeSegment(_FakeHorizontalParams("LINE", 100.0)),
        ]
        specs = subject.build_cant_specs_from_horizontal(h_segments, 0.1)
        assert [(left, right) for _, _, left, right, _, _ in specs] == [
            (0.0, 0.0),
            (0.1, 0.0),
            (0.0, 0.0),
            (0.0, 0.1),
            (0.0, 0.0),
        ]


@requires_geometry_engine
class TestFollowHorizontalWithCant(NewFile):
    H = [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0)]

    def _alignment(self, radii, hpoints=None):
        import ifcopenshell.api.root
        import ifcopenshell.api.unit

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        hpoints = hpoints or self.H
        alignment = align_api.create_by_pi_method(ifc, "C", hpoints, radii, [(0.0, 100.0), (2000.0, 110.0)], [])
        return ifc, alignment

    @staticmethod
    def _set_cant(ifc, alignment, rows):
        """rows: (type, length, start right cant, end right cant or None); the left rail stays at 0"""
        cant_layout = subject.get_or_create_cant_layout(alignment)
        segments, dist_along = [], 0.0
        for predefined_type, length, start, end in rows:
            dp = ifc.createIfcAlignmentCantSegment(
                StartDistAlong=dist_along,
                HorizontalLength=length,
                StartCantLeft=0.0,
                EndCantLeft=None if end is None else 0.0,
                StartCantRight=start,
                EndCantRight=end,
                PredefinedType=predefined_type,
            )
            segments.append((None, dp))
            dist_along += length
        align_api.update_layout_segments(ifc, cant_layout, segments)
        return cant_layout

    @staticmethod
    def _edit_horizontal(ifc, alignment, hpoints, radii):
        from bonsai.bim.module.alignment.operator import _update_horizontal_pi_segments

        pairs = subject.pair_cant_with_horizontal(alignment)
        assert _update_horizontal_pi_segments(ifc, align_api.get_horizontal_layout(alignment), hpoints, radii)
        return subject.follow_horizontal_with_cant(alignment, pairs)

    @staticmethod
    def _values(layout, attribute):
        return [getattr(s.DesignParameters, attribute) for s in subject.get_real_layout_segments(layout)]

    def _assert_contiguous_to_horizontal_end(self, alignment, cant_layout):
        h_total = sum(self._values(align_api.get_horizontal_layout(alignment), "SegmentLength"))
        dist_along = 0.0
        for segment in subject.get_real_layout_segments(cant_layout):
            assert segment.DesignParameters.StartDistAlong == pytest.approx(dist_along, abs=1e-9)
            dist_along += segment.DesignParameters.HorizontalLength
        assert dist_along == pytest.approx(h_total, abs=1e-9)

    def test_paired_cant_follows_a_curve_gaining_spirals(self):
        ifc, alignment = self._alignment([(300.0, 0.0, 0.0), (400.0, 0.0, 0.0)])
        h_layout = align_api.get_horizontal_layout(alignment)
        specs = subject.build_cant_specs_from_horizontal(subject.get_real_layout_segments(h_layout), 0.1)
        cant_layout = self._set_cant(ifc, alignment, [(t, length, sr, er) for t, length, _, sr, _, er in specs])

        assert self._edit_horizontal(ifc, alignment, self.H, [(300.0, 60.0, 60.0), (400.0, 0.0, 0.0)]) == 1
        h_types = self._values(h_layout, "PredefinedType")
        assert self._values(cant_layout, "PredefinedType") == [
            subject.CANT_TYPE_FOR_HORIZONTAL_TYPE[t] for t in h_types
        ]
        assert self._values(cant_layout, "HorizontalLength") == pytest.approx(
            self._values(h_layout, "SegmentLength"), abs=1e-9
        )
        self._assert_contiguous_to_horizontal_end(alignment, cant_layout)

    def test_anchored_cant_keeps_its_breaks_at_the_same_fraction(self):
        radii = [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0)]
        ifc, alignment = self._alignment(radii)
        h_layout = align_api.get_horizontal_layout(alignment)
        lengths = self._values(h_layout, "SegmentLength")
        line, spiral, arc = lengths[:3]
        # the first tangent split by hand at 40%, the first curve one to one, then flat to the end
        cant_layout = self._set_cant(
            ifc,
            alignment,
            [
                ("CONSTANTCANT", 0.4 * line, 0.0, None),
                ("CONSTANTCANT", 0.6 * line, 0.0, None),
                ("LINEARTRANSITION", spiral, 0.0, 0.1),
                ("CONSTANTCANT", arc, 0.1, None),
                ("LINEARTRANSITION", spiral, 0.1, 0.0),
                ("CONSTANTCANT", sum(lengths[4:]), 0.0, None),
            ],
        )
        guids = [s.GlobalId for s in subject.get_real_layout_segments(cant_layout)]

        assert self._edit_horizontal(ifc, alignment, self.H, [(250.0, 60.0, 60.0), radii[1]]) == 1
        new_line, new_spiral, new_arc = self._values(h_layout, "SegmentLength")[:3]
        assert new_arc != pytest.approx(arc)
        assert [s.GlobalId for s in subject.get_real_layout_segments(cant_layout)] == guids
        assert self._values(cant_layout, "HorizontalLength")[:5] == pytest.approx(
            [0.4 * new_line, 0.6 * new_line, new_spiral, new_arc, new_spiral], abs=1e-9
        )
        assert self._values(cant_layout, "StartCantRight") == [0.0, 0.0, 0.0, 0.1, 0.1, 0.0]
        self._assert_contiguous_to_horizontal_end(alignment, cant_layout)

    def test_anchored_cant_follows_a_spiral_family_change(self):
        hpoints = self.H[:3]
        ifc, alignment = self._alignment([(300.0, 60.0, 60.0)], hpoints)
        h_layout = align_api.get_horizontal_layout(alignment)
        lengths = self._values(h_layout, "SegmentLength")
        cant_layout = self._set_cant(
            ifc,
            alignment,
            [
                ("CONSTANTCANT", lengths[0] / 2, 0.0, None),
                ("CONSTANTCANT", lengths[0] / 2, 0.0, None),
                ("LINEARTRANSITION", lengths[1], 0.0, 0.1),
                ("CONSTANTCANT", lengths[2], 0.1, None),
                ("LINEARTRANSITION", lengths[3], 0.1, 0.0),
                ("CONSTANTCANT", lengths[4], 0.0, None),
            ],
        )

        assert self._edit_horizontal(ifc, alignment, hpoints, [(300.0, 60.0, 60.0, "BLOSSCURVE")]) == 1
        assert self._values(cant_layout, "PredefinedType") == [
            "CONSTANTCANT",
            "CONSTANTCANT",
            "BLOSSCURVE",
            "CONSTANTCANT",
            "BLOSSCURVE",
            "CONSTANTCANT",
        ]
        self._assert_contiguous_to_horizontal_end(alignment, cant_layout)

    def test_anchored_cant_drops_the_segments_of_a_deleted_pi(self):
        radii = [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0)]
        ifc, alignment = self._alignment(radii)
        h_layout = align_api.get_horizontal_layout(alignment)
        lengths = self._values(h_layout, "SegmentLength")
        # the first tangent split by hand, then one cant segment per horizontal segment
        rows = [("CONSTANTCANT", lengths[0] / 2, 0.0, None), ("CONSTANTCANT", lengths[0] / 2, 0.0, None)]
        rows += [
            ("LINEARTRANSITION", lengths[1], 0.0, 0.1),
            ("CONSTANTCANT", lengths[2], 0.1, None),
            ("LINEARTRANSITION", lengths[3], 0.1, 0.0),
            ("CONSTANTCANT", lengths[4], 0.0, None),
            ("LINEARTRANSITION", lengths[5], 0.0, 0.12),
            ("CONSTANTCANT", lengths[6], 0.12, None),
            ("LINEARTRANSITION", lengths[7], 0.12, 0.0),
            ("CONSTANTCANT", lengths[8], 0.0, None),
        ]
        cant_layout = self._set_cant(ifc, alignment, rows)
        guids = [s.GlobalId for s in subject.get_real_layout_segments(cant_layout)]

        # deleting PI 1 removes its back tangent, spirals and arc; PI 2's segments are kept
        assert self._edit_horizontal(ifc, alignment, [self.H[0], self.H[2], self.H[3]], [radii[1]]) == 1
        assert [s.GlobalId for s in subject.get_real_layout_segments(cant_layout)] == guids[5:]
        assert self._values(cant_layout, "StartCantRight") == [0.0, 0.0, 0.12, 0.12, 0.0]
        self._assert_contiguous_to_horizontal_end(alignment, cant_layout)


@requires_geometry_engine
class TestStretchVerticalsWithHorizontal(NewFile):
    H = [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0)]

    def _alignment(self):
        import ifcopenshell.api.root
        import ifcopenshell.api.unit

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        vpoints = [(0.0, 100.0), (700.0, 110.0), (1200.0, 108.0)]
        alignment = align_api.create_by_pi_method(ifc, "S", self.H, [(300.0, 0.0, 0.0)], vpoints, [200.0])
        return ifc, alignment

    @staticmethod
    def _add_spirals(ifc, alignment):
        """A horizontal edit that changes the alignment's length."""
        from bonsai.bim.module.alignment.operator import _update_horizontal_pi_segments

        h_layout = align_api.get_horizontal_layout(alignment)
        before = subject.get_horizontal_alignment_length(h_layout)
        verticals = subject.verticals_ending_with_horizontal(alignment)
        assert _update_horizontal_pi_segments(
            ifc, h_layout, TestStretchVerticalsWithHorizontal.H, [(300.0, 60.0, 60.0)]
        )
        assert subject.get_horizontal_alignment_length(h_layout) != pytest.approx(before, abs=1e-3)
        return subject.stretch_verticals_with_horizontal(verticals)

    def test_match_keeps_the_vertical_segments(self):
        # Match (match_layout_length_to_horizontal) stretches with this, then refreshes the Blender object
        ifc, alignment = self._alignment()
        v_layout = align_api.get_vertical_layout(alignment)
        guids = [s.GlobalId for s in subject.get_real_layout_segments(v_layout)]
        assert subject.get_length_mismatch(v_layout) is not None
        assert subject._stretch_last_segment_to_horizontal(v_layout) is None
        assert subject.get_length_mismatch(v_layout) is None
        assert [s.GlobalId for s in subject.get_real_layout_segments(v_layout)] == guids

    def test_a_vertical_that_matched_the_horizontal_still_does(self):
        ifc, alignment = self._alignment()
        v_layout = align_api.get_vertical_layout(alignment)
        assert subject._stretch_last_segment_to_horizontal(v_layout) is None
        guids = [s.GlobalId for s in subject.get_real_layout_segments(v_layout)]
        lengths = [s.DesignParameters.HorizontalLength for s in subject.get_real_layout_segments(v_layout)]

        assert self._add_spirals(ifc, alignment) == []
        assert subject.get_length_mismatch(v_layout) is None
        segments = subject.get_real_layout_segments(v_layout)
        assert [s.GlobalId for s in segments] == guids
        assert [s.DesignParameters.HorizontalLength for s in segments][:-1] == lengths[:-1]

    def test_a_vertical_shorter_on_purpose_is_left_alone(self):
        ifc, alignment = self._alignment()
        v_layout = align_api.get_vertical_layout(alignment)
        end = subject.get_layout_end_distance(v_layout)

        assert self._add_spirals(ifc, alignment) == []
        assert subject.get_layout_end_distance(v_layout) == pytest.approx(end, abs=1e-9)
