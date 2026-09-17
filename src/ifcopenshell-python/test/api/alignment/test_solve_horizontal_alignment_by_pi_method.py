# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import logging
import math

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.validate
from ifcopenshell import ifcopenshell_wrapper

try:
    ifcopenshell.file(schema="IFC4X3_ADD2")
    IFC4X3_AVAILABLE = True
except RuntimeError:
    IFC4X3_AVAILABLE = False


def _create_file():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    return file


def _reference_clothoid_end(length, start_curvature, end_curvature, steps=20000):
    """Composite Simpson integration of the clothoid position functions, as an independent check."""
    l = np.linspace(0.0, length, 2 * steps + 1)
    theta = start_curvature * l + (end_curvature - start_curvature) * l * l / (2.0 * length)
    h = length / (2.0 * steps)
    weights = np.ones(2 * steps + 1)
    weights[1:-1:2] = 4.0
    weights[2:-1:2] = 2.0
    dx = h / 3.0 * float(np.sum(weights * np.cos(theta)))
    dy = h / 3.0 * float(np.sum(weights * np.sin(theta)))
    return dx, dy


def test_compute_clothoid_end():
    for length, k1, k2 in [(200.0, 0.0, 1.0 / 1000.0), (150.0, 1.0 / 1000.0, 0.0), (120.0, -1.0 / 800.0, 1.0 / 500.0)]:
        dx, dy, dtheta = ifcopenshell.api.alignment.compute_clothoid_end(length, k1, k2)
        ref_dx, ref_dy = _reference_clothoid_end(length, k1, k2)
        assert dx == pytest.approx(ref_dx, abs=1.0e-12)
        assert dy == pytest.approx(ref_dy, abs=1.0e-12)
        assert dtheta == pytest.approx(0.5 * (k1 + k2) * length)

    # signed curvatures mirror the unsigned result
    dx, dy, dtheta = ifcopenshell.api.alignment.compute_clothoid_end(200.0, 0.0, 1.0 / 1000.0)
    mx, my, mtheta = ifcopenshell.api.alignment.compute_clothoid_end(200.0, 0.0, -1.0 / 1000.0)
    assert mx == pytest.approx(dx)
    assert my == pytest.approx(-dy)
    assert mtheta == pytest.approx(-dtheta)


def test_solve_produces_continuous_segments():
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0, 200.0, 150.0), (1250.0, 180.0, 180.0), (950.0, 0.0, 120.0)]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)

    expected_types = [
        "LINE",
        "CLOTHOID",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
        "CLOTHOID",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
    ]
    assert [s.predefined_type for s in segments] == expected_types

    # the solution starts at the POB, in the direction of the first PI
    assert segments[0].start_point == pytest.approx((500.0, 2500.0))
    assert segments[0].start_direction == pytest.approx(math.atan2(660.0 - 2500.0, 3340.0 - 500.0))

    # spirals run from zero curvature to the curve radius and vice versa
    entry_spiral = segments[1]
    assert entry_spiral.start_radius_of_curvature == 0.0
    assert entry_spiral.end_radius_of_curvature == pytest.approx(1000.0)  # positive, curve to the left
    assert entry_spiral.segment_length == pytest.approx(200.0)
    exit_spiral = segments[3]
    assert exit_spiral.start_radius_of_curvature == pytest.approx(1000.0)
    assert exit_spiral.end_radius_of_curvature == 0.0
    assert exit_spiral.segment_length == pytest.approx(150.0)
    assert segments[5].end_radius_of_curvature == pytest.approx(-1250.0)  # curve to the right

    # each segment ends exactly where the next one starts, in position and direction
    dist_along = 0.0
    for segment, next_segment in zip(segments[:-1], segments[1:]):
        assert segment.start_dist_along == pytest.approx(dist_along)
        end_x, end_y, end_direction = ifcopenshell.api.alignment.compute_horizontal_segment_end(segment)
        assert end_x == pytest.approx(next_segment.start_point[0], abs=1.0e-9)
        assert end_y == pytest.approx(next_segment.start_point[1], abs=1.0e-9)
        direction_gap = end_direction - next_segment.start_direction
        assert math.atan2(math.sin(direction_gap), math.cos(direction_gap)) == pytest.approx(0.0, abs=1.0e-12)
        dist_along += segment.segment_length


@pytest.mark.parametrize("family", ifcopenshell.api.alignment.SPIRAL_FAMILIES)
def test_solve_supports_all_spiral_families(family):
    """Pure-Python continuity check (no IFC file involved) for every spiral family, mirroring
    test_solve_produces_continuous_segments but for a single spiral-circular-spiral PI."""
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0)]
    radii = [(1000.0, 200.0, 150.0, family)]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)

    assert [s.predefined_type for s in segments] == ["LINE", family, "CIRCULARARC", family, "LINE"]

    for segment, next_segment in zip(segments[:-1], segments[1:]):
        end_x, end_y, end_direction = ifcopenshell.api.alignment.compute_horizontal_segment_end(segment)
        assert end_x == pytest.approx(next_segment.start_point[0], abs=1.0e-9)
        assert end_y == pytest.approx(next_segment.start_point[1], abs=1.0e-9)
        direction_gap = end_direction - next_segment.start_direction
        assert math.atan2(math.sin(direction_gap), math.cos(direction_gap)) == pytest.approx(0.0, abs=1.0e-9)


def test_solve_plain_radius_matches_spiral_free_tuple():
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (8480.0, 2010.0)]

    segments1 = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [1000.0, 1250.0])
    segments2 = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(
        hpoints, [(1000.0, 0.0, 0.0), (1250.0, 0.0, 0.0)]
    )
    assert segments1 == segments2


def test_solve_errors():
    hpoints = [(0.0, 0.0), (1000.0, 0.0), (2000.0, 1000.0)]

    with pytest.raises(ValueError):  # radii count mismatch
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [500.0, 500.0])
    with pytest.raises(ValueError):  # malformed radii element
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 50.0)])
    with pytest.raises(ValueError):  # spiral lengths without a radius
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(0.0, 50.0, 50.0)])
    with pytest.raises(ValueError):  # spirals deflect more than the PI deflection angle
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 5000.0, 5000.0)])
    with pytest.raises(ValueError):  # zero deflection angle
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(
            [(0.0, 0.0), (1000.0, 0.0), (2000.0, 0.0)], [(500.0, 50.0, 50.0)]
        )
    with pytest.raises(ValueError):  # unsupported spiral family
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 50.0, 50.0, "NOT_A_FAMILY")])


@pytest.mark.skipif(not IFC4X3_AVAILABLE, reason="IFC4X3 not available")
@pytest.mark.parametrize("family", ifcopenshell.api.alignment.SPIRAL_FAMILIES)
def test_author_transition_curve_alignment(family):
    """
    End-to-end example: author a tangent -> spiral -> circular arc -> spiral -> tangent alignment
    for every supported spiral family, then check the written geometry for continuity with the
    geometry engine and validate the file against the schema and express rules.

    This is the strongest check available for a new spiral family: it authors real IFC entities
    from the same start/end radius + length the solver computed, then asks the (independently
    implemented, C++) geometry kernel to evaluate the resulting IfcCurveSegments -- if
    _spiral_curvature's theta(l) doesn't exactly match what the kernel itself evaluates for that
    family, the segments won't be continuous and this test fails.
    """
    file = _create_file()

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file,
        "TestAlignment",
        [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0)],
        [(1000.0, 200.0, 150.0, family)],
        [(0.0, 100.0), (2000.0, 135.0), (4000.0, 105.0)],
        [1600.0],
    )

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal_layout)
    expected_types = ["LINE", family, "CIRCULARARC", family, "LINE", "LINE"]  # last is the zero length segment
    assert [s.DesignParameters.PredefinedType for s in segment_nest.RelatedObjects] == expected_types

    # verify continuity of position and direction between consecutive segments of the
    # geometric representation
    #
    # HELMERTCURVE gets a looser tolerance for a reason unrelated to the PI method: each
    # HELMERTCURVE business segment renders as *two* IfcCurveSegments (_map_helmert_curve splits
    # it at its midpoint), and ifcopenshell_wrapper.helmert_curve_point's own angle computation
    # (used to place the second half relative to the first) carries a small inherent approximation
    # -- present for any HELMERTCURVE, table-authored or PI-method, and independent of anything
    # this solver computes. The boundaries *between* business segments (LINE-to-spiral,
    # spiral-to-CIRCULARARC) that the PI method actually controls remain exact; only the internal
    # split within one HELMERTCURVE segment carries this pre-existing residual.
    direction_tolerance = 5.0e-5 if family == "HELMERTCURVE" else 1.0e-9
    position_tolerance = 5.0e-3 if family == "HELMERTCURVE" else 1.0e-5
    curve = ifcopenshell.api.alignment.get_layout_curve(horizontal_layout)
    settings = ifcopenshell.geom.settings()
    for segment, next_segment in zip(curve.Segments[:-1], curve.Segments[1:]):
        fn = ifcopenshell_wrapper.map_shape(settings, segment)
        evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, fn)
        end = np.array(evaluator.evaluate(fn.end()))
        end_position = end[0:2, 3]
        end_direction = math.atan2(end[1, 0], end[0, 0])
        start_position = next_segment.Placement.Location.Coordinates
        d = next_segment.Placement.RefDirection.DirectionRatios
        start_direction = math.atan2(d[1], d[0])
        assert end_position[0] == pytest.approx(start_position[0], abs=position_tolerance)
        assert end_position[1] == pytest.approx(start_position[1], abs=position_tolerance)
        direction_gap = math.atan2(math.sin(end_direction - start_direction), math.cos(end_direction - start_direction))
        assert direction_gap == pytest.approx(0.0, abs=direction_tolerance)

    # the file is schema and express rule valid
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(file, logger, express_rules=True)
    assert [entry for entry in logger.statements if entry["level"] == logging.ERROR] == []


@pytest.mark.skipif(not IFC4X3_AVAILABLE, reason="IFC4X3 not available")
def test_solve_viennese_bend_with_cant_factor():
    """
    VIENNESEBEND with a real, non-zero cant contribution (every other VIENNESEBEND case in this
    module leaves gravity_centerline_height/cant_params unset, so cant_factor is always 0 there --
    this is the one exercising the actual cant-derived curvature term).

    Builds a real cant layout matching the solved horizontal segments' station ranges, feeds the
    same gravity centerline height/cant/rail head distance into the solver via radii's 5th element,
    then checks the written geometry against the geometry kernel -- same cross-check
    test_author_transition_curve_alignment does for every other family/case.
    """
    file = _create_file()
    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", include_vertical=True, include_cant=True)
    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment)
    cant_layout.RailHeadDistance = 1.5
    rail_head_distance = cant_layout.RailHeadDistance

    # a vertical layout is required alongside cant (see _create_geometric_representation's case
    # list) -- its own shape doesn't matter for this test, which only checks horizontal continuity
    vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    ifcopenshell.api.alignment.create_layout_segment(
        file,
        vertical_layout,
        file.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=10000.0,
            StartHeight=0.0,
            StartGradient=0.0,
            EndGradient=0.0,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )

    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0)]
    gravity_centerline_height = 1.8
    cant = 0.12
    radii = [(1000.0, 200.0, 150.0, "VIENNESEBEND", (gravity_centerline_height, cant, rail_head_distance))]

    segment_defs = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segment_defs] == ["LINE", "VIENNESEBEND", "CIRCULARARC", "VIENNESEBEND", "LINE"]
    back_tangent, entry_spiral, arc, exit_spiral, forward_tangent = segment_defs

    # this PI curves left (positive radius survives into entry_spiral.end_radius_of_curvature),
    # so per _create_cant_segment's convention the outer (right) rail is the one raised
    assert entry_spiral.end_radius_of_curvature == pytest.approx(1000.0)

    def _add_cant_segment(seg, start_right, end_right, predefined_type):
        design_parameters = file.createIfcAlignmentCantSegment(
            StartDistAlong=seg.start_dist_along,
            HorizontalLength=seg.segment_length,
            StartCantLeft=0.0,
            EndCantLeft=0.0,
            StartCantRight=start_right,
            EndCantRight=end_right,
            PredefinedType=predefined_type,
        )
        ifcopenshell.api.alignment.create_layout_segment(file, cant_layout, design_parameters)

    _add_cant_segment(back_tangent, 0.0, 0.0, "CONSTANTCANT")
    _add_cant_segment(entry_spiral, 0.0, cant, "LINEARTRANSITION")
    _add_cant_segment(arc, cant, cant, "CONSTANTCANT")
    _add_cant_segment(exit_spiral, cant, 0.0, "LINEARTRANSITION")
    _add_cant_segment(forward_tangent, 0.0, 0.0, "CONSTANTCANT")

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    for seg in segment_defs:
        design_parameters = file.createIfcAlignmentHorizontalSegment(
            StartTag=None,
            EndTag=None,
            StartPoint=file.createIfcCartesianPoint(Coordinates=seg.start_point),
            StartDirection=seg.start_direction / angle_unit_scale,
            StartRadiusOfCurvature=seg.start_radius_of_curvature,
            EndRadiusOfCurvature=seg.end_radius_of_curvature,
            SegmentLength=seg.segment_length,
            GravityCenterLineHeight=seg.gravity_centerline_height or None,
            PredefinedType=seg.predefined_type,
        )
        ifcopenshell.api.alignment.create_layout_segment(file, horizontal_layout, design_parameters)

    # sanity check: cant_factor is genuinely non-zero for this scenario, or this test wouldn't be
    # exercising anything test_author_transition_curve_alignment[VIENNESEBEND] doesn't already
    cant_angle_full = cant / rail_head_distance
    entry_cant_factor = -420.0 * (gravity_centerline_height / entry_spiral.segment_length) * cant_angle_full
    assert abs(entry_cant_factor) > 1.0e-3

    curve = ifcopenshell.api.alignment.get_layout_curve(horizontal_layout)
    settings = ifcopenshell.geom.settings()
    for segment, next_segment in zip(curve.Segments[:-1], curve.Segments[1:]):
        fn = ifcopenshell_wrapper.map_shape(settings, segment)
        evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, fn)
        end = np.array(evaluator.evaluate(fn.end()))
        end_position = end[0:2, 3]
        end_direction = math.atan2(end[1, 0], end[0, 0])
        start_position = next_segment.Placement.Location.Coordinates
        d = next_segment.Placement.RefDirection.DirectionRatios
        start_direction = math.atan2(d[1], d[0])
        assert end_position[0] == pytest.approx(start_position[0], abs=1.0e-5)
        assert end_position[1] == pytest.approx(start_position[1], abs=1.0e-5)
        direction_gap = math.atan2(math.sin(end_direction - start_direction), math.cos(end_direction - start_direction))
        assert direction_gap == pytest.approx(0.0, abs=1.0e-9)
