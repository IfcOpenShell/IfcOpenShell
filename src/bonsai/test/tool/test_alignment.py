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

import math
import pytest
import bpy
import ifcopenshell
import ifcopenshell.api.alignment as align_api
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

TOLERANCE = 1e-9


def assert_close(actual: float, expected: float, tol: float = TOLERANCE) -> None:
    assert abs(actual - expected) < tol, f"Expected {expected}, got {actual} (diff={abs(actual-expected):.2e})"


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
# calculate_pi_geometry
# ---------------------------------------------------------------------------


class TestCalculatePiGeometry(NewFile):
    def test_returns_empty_result_for_empty_pi_list(self):
        result = subject.calculate_pi_geometry([])
        assert result.stations == []
        assert result.total_length == 0.0

    def test_returns_single_point_result_for_one_pi(self):
        result = subject.calculate_pi_geometry([(50.0, 100.0)])
        assert len(result.stations) == 1
        assert result.total_length == 0.0

    def test_calculates_length_between_two_points(self):
        result = subject.calculate_pi_geometry([(0.0, 0.0), (100.0, 0.0)])
        assert_close(result.total_length, 100.0)
        assert_close(result.lengths[0], 100.0)

    def test_calculates_due_east_direction(self):
        result = subject.calculate_pi_geometry([(0.0, 0.0), (100.0, 0.0)])
        assert_close(result.directions[0], 0.0)

    def test_calculates_due_north_direction(self):
        result = subject.calculate_pi_geometry([(0.0, 0.0), (0.0, 100.0)])
        assert_close(result.directions[0], math.pi / 2)

    def test_calculates_diagonal_length(self):
        result = subject.calculate_pi_geometry([(0.0, 0.0), (3.0, 4.0)])
        assert_close(result.total_length, 5.0)

    def test_calculates_stations_for_three_pis(self):
        pis = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
        result = subject.calculate_pi_geometry(pis)
        assert_close(result.stations[0], 0.0)
        assert_close(result.stations[1], 100.0)
        assert_close(result.stations[2], 200.0)
        assert_close(result.total_length, 200.0)

    def test_applies_start_station_offset(self):
        pis = [(0.0, 0.0), (100.0, 0.0)]
        result = subject.calculate_pi_geometry(pis, start_station=1000.0)
        assert_close(result.stations[0], 1000.0)
        assert_close(result.stations[1], 1100.0)
        assert_close(result.total_length, 100.0)

    def test_last_pi_has_zero_length_and_direction(self):
        result = subject.calculate_pi_geometry([(0.0, 0.0), (100.0, 0.0)])
        assert_close(result.lengths[-1], 0.0)
        assert_close(result.directions[-1], 0.0)


# ---------------------------------------------------------------------------
# calculate_tangent_length   T = R * tan(Δ/2)
# ---------------------------------------------------------------------------


class TestCalculateTangentLength(NewFile):
    def test_returns_zero_for_zero_radius(self):
        assert_close(subject.calculate_tangent_length(0.0, math.pi / 2), 0.0)

    def test_returns_zero_for_zero_deflection(self):
        assert_close(subject.calculate_tangent_length(300.0, 0.0), 0.0)

    def test_calculates_tangent_for_30_degree_deflection(self):
        deflection = math.radians(30)
        expected = 300.0 * math.tan(deflection / 2)
        assert_close(subject.calculate_tangent_length(300.0, deflection), expected)

    def test_calculates_tangent_for_90_degree_deflection(self):
        deflection = math.pi / 2
        expected = 100.0 * math.tan(math.pi / 4)  # R * tan(45°) = R
        assert_close(subject.calculate_tangent_length(100.0, deflection), expected)


# ---------------------------------------------------------------------------
# calculate_arc_length   L = R * Δ
# ---------------------------------------------------------------------------


class TestCalculateArcLength(NewFile):
    def test_calculates_arc_for_90_degree_curve(self):
        expected = 100.0 * math.pi / 2
        assert_close(subject.calculate_arc_length(100.0, math.pi / 2), expected)

    def test_calculates_arc_for_full_circle(self):
        expected = 50.0 * 2 * math.pi
        assert_close(subject.calculate_arc_length(50.0, 2 * math.pi), expected)

    def test_zero_radius_yields_zero_length(self):
        assert_close(subject.calculate_arc_length(0.0, math.pi / 2), 0.0)

    def test_zero_deflection_yields_zero_length(self):
        assert_close(subject.calculate_arc_length(100.0, 0.0), 0.0)


# ---------------------------------------------------------------------------
# deflection_angle_from_points
# ---------------------------------------------------------------------------


class TestDeflectionAngleFromPoints(NewFile):
    def test_returns_zero_for_straight_alignment(self):
        angle = subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (200.0, 0.0))
        assert_close(angle, 0.0)

    def test_positive_for_90_degree_left_turn(self):
        """Turning left (CCW) is a positive deflection."""
        angle = subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (100.0, 100.0))
        assert_close(angle, math.pi / 2)

    def test_negative_for_90_degree_right_turn(self):
        """Turning right (CW) is a negative deflection."""
        angle = subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (100.0, -100.0))
        assert_close(angle, -math.pi / 2)

    def test_returns_pi_for_u_turn(self):
        """180-degree turn."""
        angle = subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (0.0, 0.0))
        assert_close(abs(angle), math.pi)

    def test_normalises_angle_into_minus_pi_to_pi_range(self):
        """Result must always be in (-π, π]."""
        angle = subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (50.0, -50.0))
        assert -math.pi < angle <= math.pi


# ---------------------------------------------------------------------------
# arc_length_at_pi
# ---------------------------------------------------------------------------


class TestArcLengthAtPi(NewFile):
    def test_returns_zero_for_zero_radius(self):
        arc = subject.arc_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=0.0)
        assert_close(arc, 0.0)

    def test_returns_zero_for_negative_radius(self):
        arc = subject.arc_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=-100.0)
        assert_close(arc, 0.0)

    def test_calculates_arc_for_90_degree_left_turn(self):
        expected = 100.0 * math.pi / 2
        arc = subject.arc_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=100.0)
        assert_close(arc, expected)

    def test_calculates_arc_for_90_degree_right_turn(self):
        """Sign of deflection should not affect arc length."""
        expected = 100.0 * math.pi / 2
        arc = subject.arc_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, -100.0), radius=100.0)
        assert_close(arc, expected)


# ---------------------------------------------------------------------------
# tangent_length_at_pi
# ---------------------------------------------------------------------------


class TestTangentLengthAtPi(NewFile):
    def test_returns_zero_for_zero_radius(self):
        t = subject.tangent_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=0.0)
        assert_close(t, 0.0)

    def test_returns_zero_for_negative_radius(self):
        t = subject.tangent_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=-100.0)
        assert_close(t, 0.0)

    def test_calculates_tangent_for_90_degree_left_turn(self):
        expected = 100.0 * math.tan(math.pi / 4)  # R * tan(45°)
        t = subject.tangent_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=100.0)
        assert_close(t, expected)

    def test_matches_calculate_tangent_length_for_same_geometry(self):
        """tangent_length_at_pi must agree with calculate_tangent_length."""
        deflection = abs(subject.deflection_angle_from_points((0.0, 0.0), (100.0, 0.0), (100.0, 100.0)))
        expected = subject.calculate_tangent_length(300.0, deflection)
        actual = subject.tangent_length_at_pi((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), radius=300.0)
        assert_close(actual, expected)


# ---------------------------------------------------------------------------
# tangent_segment_length
# ---------------------------------------------------------------------------


class TestTangentSegmentLength(NewFile):
    def test_returns_full_distance_with_no_tangents(self):
        length = subject.tangent_segment_length((0.0, 0.0), (100.0, 0.0))
        assert_close(length, 100.0)

    def test_subtracts_start_tangent(self):
        length = subject.tangent_segment_length((0.0, 0.0), (100.0, 0.0), start_tangent=20.0)
        assert_close(length, 80.0)

    def test_subtracts_end_tangent(self):
        length = subject.tangent_segment_length((0.0, 0.0), (100.0, 0.0), end_tangent=30.0)
        assert_close(length, 70.0)

    def test_subtracts_both_tangents(self):
        length = subject.tangent_segment_length((0.0, 0.0), (100.0, 0.0), start_tangent=20.0, end_tangent=30.0)
        assert_close(length, 50.0)

    def test_clamps_to_zero_when_tangents_exceed_full_distance(self):
        length = subject.tangent_segment_length((0.0, 0.0), (100.0, 0.0), start_tangent=70.0, end_tangent=70.0)
        assert_close(length, 0.0)

    def test_works_on_diagonal_leg(self):
        """3-4-5 triangle: full_length=5, minus tangents=2 → 3."""
        length = subject.tangent_segment_length((0.0, 0.0), (3.0, 4.0), start_tangent=1.0, end_tangent=1.0)
        assert_close(length, 3.0)


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
# layout_has_real_segments
# ---------------------------------------------------------------------------


class _FakeAlignmentSegment:
    """Stand-in for IfcAlignmentSegment: is_a() returns True for IfcAlignmentSegment."""

    def __init__(self, design_params=None):
        self.DesignParameters = design_params

    def is_a(self, ifc_class: str) -> bool:
        return ifc_class == "IfcAlignmentSegment"


class _FakeRelNests:
    def __init__(self, related_objects):
        self.RelatedObjects = related_objects


class _FakeLayout:
    def __init__(self, rels=None):
        self.IsNestedBy = rels or []


class TestLayoutHasRealSegments(NewFile):
    def test_returns_false_for_layout_with_no_nested_relationships(self):
        layout = _FakeLayout(rels=[])
        assert subject.layout_has_real_segments(layout) is False

    def test_returns_false_for_layout_with_empty_related_objects(self):
        layout = _FakeLayout(rels=[_FakeRelNests(related_objects=[])])
        assert subject.layout_has_real_segments(layout) is False

    def test_returns_false_when_only_segment_is_zero_length_terminator(self):
        dp = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=0.0)
        terminator = _FakeAlignmentSegment(dp)
        layout = _FakeLayout(rels=[_FakeRelNests([terminator])])
        assert subject.layout_has_real_segments(layout) is False

    def test_returns_true_when_one_real_segment_exists(self):
        dp = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=100.0)
        real_seg = _FakeAlignmentSegment(dp)
        layout = _FakeLayout(rels=[_FakeRelNests([real_seg])])
        assert subject.layout_has_real_segments(layout) is True

    def test_returns_true_when_real_segment_follows_terminator(self):
        dp_zero = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=0.0)
        dp_real = _FakeDesignParams("IfcAlignmentHorizontalSegment", segment_length=50.0)
        layout = _FakeLayout(rels=[_FakeRelNests([_FakeAlignmentSegment(dp_zero), _FakeAlignmentSegment(dp_real)])])
        assert subject.layout_has_real_segments(layout) is True

    def test_ignores_non_alignment_segment_objects(self):
        """Non-IfcAlignmentSegment objects in RelatedObjects should be ignored."""

        class _FakeOtherObject:
            def is_a(self, ifc_class):
                return False

        layout = _FakeLayout(rels=[_FakeRelNests([_FakeOtherObject()])])
        assert subject.layout_has_real_segments(layout) is False


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
        import ifcopenshell.api.root
        import ifcopenshell.api.alignment

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        tool.Ifc.set(ifc)
        # Create a minimal alignment hierarchy
        project = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        alignment = ifc.createIfcAlignment()
        layout = ifc.createIfcAlignmentHorizontal()
        ifc.createIfcRelNests(RelatingObject=alignment, RelatedObjects=[layout])
        result = subject.safe_layout_horizontal_by_pi_method(
            ifc, layout, hpoints=[(0.0, 0.0), (100.0, 0.0)], radii=[]
        )
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
        alignment = ifc_file.createIfcAlignment(
            GlobalId=ifcopenshell.guid.new(), Name="Bare"
        )
        h_layout = subject.get_horizontal_layout(alignment)
        assert h_layout is None


# ---------------------------------------------------------------------------
# layout_by_pi_method (IFC + tool.Ifc integration)
# ---------------------------------------------------------------------------


@requires_geometry_engine
class TestLayoutByPiMethod(NewIfc4X3):
    """Tests for Alignment.layout_by_pi_method() — IFC segment creation."""

    def test_creates_ifc_segments_for_straight_alignment(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="Straight")
        h_layout = subject.get_horizontal_layout(alignment)

        subject.layout_by_pi_method(h_layout, [(0.0, 0.0), (1000.0, 0.0)], [])

        segments = align_api.get_layout_segments(h_layout)
        real_segments = [s for s in segments if not subject.is_zero_length_segment(s)]
        assert len(real_segments) >= 1  # At least one tangent

    def test_creates_arc_segment_for_curve(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="Curve")
        h_layout = subject.get_horizontal_layout(alignment)

        subject.layout_by_pi_method(
            h_layout, [(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], [300.0]
        )

        segments = align_api.get_layout_segments(h_layout)
        real_segments = [s for s in segments if not subject.is_zero_length_segment(s)]
        segment_types = [s.DesignParameters.PredefinedType for s in real_segments if s.DesignParameters]
        assert "LINE" in segment_types
        assert "CIRCULARARC" in segment_types


# ---------------------------------------------------------------------------
# back_calculate_pis_from_alignment (IFC + unit conversion)
# ---------------------------------------------------------------------------


@requires_geometry_engine
class TestBackCalculatePisFromAlignment(NewIfc4X3):
    """Tests for Alignment.back_calculate_pis_from_alignment() — PI recovery."""

    def test_recovers_endpoints_from_straight_alignment(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (1000.0, 0.0)], radii=[]
        )
        pis = subject.back_calculate_pis_from_alignment(alignment)
        assert len(pis) >= 2
        assert pis[0]["pi_type"] == "ENDPOINT"
        assert pis[-1]["pi_type"] == "ENDPOINT"
        assert_close(pis[0]["e"], 0.0, tol=0.01)
        assert_close(pis[0]["n"], 0.0, tol=0.01)
        assert_close(pis[-1]["e"], 1000.0, tol=0.01)
        assert_close(pis[-1]["n"], 0.0, tol=0.01)

    def test_recovers_curve_pi_with_radius(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        pis = subject.back_calculate_pis_from_alignment(alignment)
        # Should have 3 PIs: start endpoint, curve PI, end endpoint
        assert len(pis) == 3
        curve_pis = [p for p in pis if p["pi_type"] == "CURVE"]
        assert len(curve_pis) == 1
        assert_close(curve_pis[0]["e"], 500.0, tol=1.0)
        assert_close(curve_pis[0]["n"], 0.0, tol=1.0)
        assert curve_pis[0]["radius"] > 0

    def test_raises_for_alignment_without_horizontal_layout(self):
        ifc_file = tool.Ifc.get()
        alignment = ifc_file.createIfcAlignment(
            GlobalId=ifcopenshell.guid.new(), Name="Bare"
        )
        with pytest.raises(ValueError, match="no horizontal layout"):
            subject.back_calculate_pis_from_alignment(alignment)

    def test_raises_for_alignment_with_only_terminator(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="EmptyLayout")
        # align_api.create() produces a horizontal layout with only a zero-length terminator
        with pytest.raises(ValueError, match="no real segments"):
            subject.back_calculate_pis_from_alignment(alignment)

    def test_roundtrip_preserves_pi_positions(self):
        """Create alignment from PIs, back-calculate, verify positions match."""
        original_hpoints = [(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)]
        original_radii = [300.0]
        alignment, _ = _create_alignment_with_pis(
            hpoints=original_hpoints, radii=original_radii
        )

        recovered_pis = subject.back_calculate_pis_from_alignment(alignment)
        assert len(recovered_pis) == len(original_hpoints)

        for original, recovered in zip(original_hpoints, recovered_pis):
            assert_close(recovered["e"], original[0], tol=1.0)
            assert_close(recovered["n"], original[1], tol=1.0)


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
# PI Edit Empties
# ---------------------------------------------------------------------------


@requires_geometry_engine
class TestCreatePiEditEmpties(NewIfc4X3):
    """Tests for Alignment.create_pi_edit_empties()."""

    def test_creates_empties_at_pi_positions(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        bpy.context.view_layer.objects.active = alignment_obj

        pis = subject.back_calculate_pis_from_alignment(alignment)
        empties = subject.create_pi_edit_empties(alignment, pis)

        assert len(empties) == len(pis)
        for empty in empties:
            assert empty.type == "EMPTY"
            assert empty.get("civil_is_pi_empty") is True
            assert empty.get("civil_alignment_id") == alignment.id()

    def test_empties_are_parented_to_alignment_object(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0)], radii=[]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        empties = subject.create_pi_edit_empties(alignment, pis)
        for empty in empties:
            assert empty.parent == alignment_obj

    def test_empties_have_sequential_pi_indices(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        empties = subject.create_pi_edit_empties(alignment, pis)
        indices = [e.get("civil_pi_index") for e in empties]
        assert indices == list(range(len(pis)))


@requires_geometry_engine
class TestGetPiEditEmpties(NewIfc4X3):
    """Tests for Alignment.get_pi_edit_empties()."""

    def test_finds_empties_for_given_alignment_id(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0)], radii=[]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        subject.create_pi_edit_empties(alignment, pis)

        found = subject.get_pi_edit_empties(alignment.id())
        assert len(found) == len(pis)

    def test_returns_empty_list_when_no_empties_exist(self):
        found = subject.get_pi_edit_empties(99999)
        assert found == []

    def test_returns_sorted_by_pi_index(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        subject.create_pi_edit_empties(alignment, pis)

        found = subject.get_pi_edit_empties(alignment.id())
        indices = [e.get("civil_pi_index") for e in found]
        assert indices == sorted(indices)


@requires_geometry_engine
class TestRemovePiEditEmpties(NewIfc4X3):
    """Tests for Alignment.remove_pi_edit_empties()."""

    def test_removes_all_empties_for_alignment(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        subject.create_pi_edit_empties(alignment, pis)

        removed = subject.remove_pi_edit_empties(alignment.id())
        assert removed == len(pis)
        assert subject.get_pi_edit_empties(alignment.id()) == []

    def test_returns_zero_when_no_empties_exist(self):
        removed = subject.remove_pi_edit_empties(99999)
        assert removed == 0


@requires_geometry_engine
class TestCollectPisFromEmpties(NewIfc4X3):
    """Tests for Alignment.collect_pis_from_empties() — reading positions back."""

    def test_roundtrip_positions_through_empties(self):
        """Create empties from PIs, collect back, verify positions match."""
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)

        pis = subject.back_calculate_pis_from_alignment(alignment)
        subject.create_pi_edit_empties(alignment, pis)

        # Force Blender to update transforms (empties are parented)
        bpy.context.view_layer.update()

        hpoints_back, radii_back = subject.collect_pis_from_empties(alignment.id())
        assert len(hpoints_back) == len(pis)

        # Positions should round-trip: empties created from pis, collected back
        for pi, (back_e, back_n) in zip(pis, hpoints_back):
            assert_close(back_e, pi["e"], tol=2.0)  # Generous tolerance for georef
            assert_close(back_n, pi["n"], tol=2.0)

    def test_collects_radii_for_interior_pis_only(self):
        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        alignment_obj = subject.create_hierarchy_for_alignment(alignment)
        pis = subject.back_calculate_pis_from_alignment(alignment)
        subject.create_pi_edit_empties(alignment, pis)

        _, radii_back = subject.collect_pis_from_empties(alignment.id())
        # Radii should have one entry (for the interior PI)
        assert len(radii_back) == 1
        assert radii_back[0] > 0

    def test_returns_empty_when_fewer_than_two_empties(self):
        hpoints, radii = subject.collect_pis_from_empties(99999)
        assert hpoints == []
        assert radii == []


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
        alignment_objects_before = [
            o for o in bpy.data.objects if tool.Ifc.get_entity(o)
        ]
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
        import tempfile
        import os

        alignment, _ = _create_alignment_with_pis(
            hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )

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
        assert subject.layout_has_real_segments(h) is True
        subject.clear_layout_segments(h)
        assert subject.layout_has_real_segments(h) is False
        assert len(align_api.get_layout_segments(h)) == 1  # terminator only

    def test_relayout_after_clear_has_no_doubling_or_orphans(self):
        ifc = self._new_ifc()
        alignment = align_api.create(ifc, name="Clr2", include_vertical=False)
        h = align_api.get_horizontal_layout(alignment)
        align_api.layout_horizontal_alignment_by_pi_method(
            ifc, h, hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        subject.clear_layout_segments(h)
        align_api.layout_horizontal_alignment_by_pi_method(
            ifc, h, hpoints=[(0.0, 0.0), (1000.0, 0.0)], radii=[]
        )
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
        assert subject.layout_has_real_segments(v) is True
        subject.clear_layout_segments(v)
        assert subject.layout_has_real_segments(v) is False


@requires_geometry_engine
class TestSetLayoutSegmentsSelectable(NewIfc4X3):
    """PI edit mode disables segment-curve selection so clicks hit the PI
    empties; set_layout_segments_selectable toggles hide_select accordingly."""

    def test_toggles_segment_hide_select(self):
        ifc_file = tool.Ifc.get()
        alignment = align_api.create(ifc_file, name="Sel", include_vertical=False)
        h = align_api.get_horizontal_layout(alignment)
        align_api.layout_horizontal_alignment_by_pi_method(
            ifc_file, h, hpoints=[(0.0, 0.0), (500.0, 0.0), (1000.0, 200.0)], radii=[300.0]
        )
        subject.create_hierarchy_for_alignment(alignment)
        segment_objects = [o for o in bpy.data.objects if "IfcAlignmentSegment" in o.name]
        assert len(segment_objects) >= 1

        subject.set_layout_segments_selectable(h, False)
        assert all(o.hide_select for o in segment_objects)

        subject.set_layout_segments_selectable(h, True)
        assert all(not o.hide_select for o in segment_objects)


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
