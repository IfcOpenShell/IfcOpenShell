# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Thomas Krijnen <thomas@aecgeeks.com>
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

# This file was generated with the assistance of an AI coding tool.

"""Tests for the end point of a layout segment, as create_layout_segment returns it and as it places
the layout's zero length terminator.

Each case is a single 100 unit segment of one type. Its end frame is compared with the kernel's
evaluation of the same layout's part of the finished representation curve (the horizontal, vertical or
cant function), with the design parameters where the end follows from them directly, and with an
alignment built without geometry, in metres and in feet.
"""

import math

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.unit
import test.bootstrap
from ifcopenshell import ifcopenshell_wrapper

A = ifcopenshell.api.alignment
LENGTH = 100.0
POSITION_TOLERANCE = 1e-9  # metres
DIRECTION_TOLERANCE = 1e-9
SPIRALS = ["CLOTHOID", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "HELMERTCURVE", "CUBIC"]
SPIRAL_RADII = [(0.0, 300.0), (300.0, 0.0), (0.0, -300.0), (300.0, 1000.0), (-1000.0, -300.0)]

HORIZONTAL = (
    [("LINE", 0.0, 0.0)]
    + [("CIRCULARARC", r, r) for r in (300.0, -300.0)]
    + [(family, r0, r1) for family in SPIRALS for r0, r1 in SPIRAL_RADII]
)
VERTICAL = [
    ("CONSTANTGRADIENT", 0.01, 0.01, None),
    ("PARABOLICARC", 0.01, -0.02, None),
    ("PARABOLICARC", -0.015, 0.005, None),
    ("CIRCULARARC", 0.01, -0.02, 3000.0),
    ("CIRCULARARC", -0.015, 0.005, -4000.0),
]  # vertical CLOTHOID isn't mapped by the API yet
CANT_TRANSITIONS = ["LINEARTRANSITION", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "HELMERTCURVE"]
CANT = (
    [("CONSTANTCANT", 0.15, 0.15)]
    + [(kind, 0.0, 0.15) for kind in CANT_TRANSITIONS]
    + [(kind, 0.15, 0.0) for kind in CANT_TRANSITIONS]
)
UNITS = ["metre", "foot"]


def new_file(unit):
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    if unit == "foot":
        length = ifcopenshell.api.unit.add_conversion_based_unit(f, name="foot")
    else:
        length = ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(f, units=[length])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    return f


def horizontal_segment(f, kind, r0, r1, start=(10.0, 20.0), direction=0.3):
    return f.createIfcAlignmentHorizontalSegment(
        StartPoint=f.createIfcCartesianPoint(start),
        StartDirection=direction,
        StartRadiusOfCurvature=r0,
        EndRadiusOfCurvature=r1,
        SegmentLength=LENGTH,
        PredefinedType=kind,
    )


def straight(f, alignment):
    A.create_layout_segment(
        f, A.get_horizontal_layout(alignment), horizontal_segment(f, "LINE", 0.0, 0.0, (0.0, 0.0), 0.0)
    )


def constant_grade(f, alignment):
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=10.0,
            StartGradient=0.0,
            EndGradient=0.0,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )


def build_horizontal(unit, kind, r0, r1, direction=0.3, include_geometry=True):
    f = new_file(unit)
    alignment = A.create(f, "H", include_geometry=include_geometry)
    end = A.create_layout_segment(
        f, A.get_horizontal_layout(alignment), horizontal_segment(f, kind, r0, r1, direction=direction)
    )
    return f, alignment, np.array(end)


def build_vertical(unit, kind, g0, g1, radius, include_geometry=True):
    f = new_file(unit)
    alignment = A.create(f, "V", include_vertical=True, include_geometry=include_geometry)
    straight(f, alignment)
    end = A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=10.0,
            StartGradient=g0,
            EndGradient=g1,
            RadiusOfCurvature=radius,
            PredefinedType=kind,
        ),
    )
    return f, alignment, np.array(end)


def build_cant(unit, kind, c0, c1, include_geometry=True):
    f = new_file(unit)
    alignment = A.create(f, "C", include_vertical=True, include_cant=True, include_geometry=include_geometry)
    A.get_cant_layout(alignment).RailHeadDistance = 1.5
    straight(f, alignment)
    constant_grade(f, alignment)
    end = A.create_layout_segment(
        f,
        A.get_cant_layout(alignment),
        f.createIfcAlignmentCantSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartCantLeft=0.0,
            EndCantLeft=0.0,
            StartCantRight=c0,
            EndCantRight=c1,
            PredefinedType=kind,
        ),
    )
    return f, alignment, np.array(end)


def evaluate_end(part):
    """The kernel's frame at the end of one layout's function of the finished representation curve"""
    s = ifcopenshell.geom.settings()
    return np.array(ifcopenshell_wrapper.function_item_evaluator(s, part).evaluate(part.end()))


def representation_parts(f):
    s = ifcopenshell.geom.settings()
    if f.by_type("IfcSegmentedReferenceCurve"):
        fn = ifcopenshell_wrapper.map_shape(s, f.by_type("IfcSegmentedReferenceCurve")[0])
        gradient = fn.get_gradient()
        return {"horizontal": gradient.get_horizontal(), "vertical": gradient.get_vertical(), "cant": fn.get_cant()}
    if f.by_type("IfcGradientCurve"):
        fn = ifcopenshell_wrapper.map_shape(s, f.by_type("IfcGradientCurve")[0])
        return {"horizontal": fn.get_horizontal(), "vertical": fn.get_vertical()}
    curve = next(c for c in f.by_type("IfcCompositeCurve") if c.is_a() == "IfcCompositeCurve")
    return {"horizontal": ifcopenshell_wrapper.map_shape(s, curve)}


def assert_frames_equal(actual, expected, direction_tolerance=DIRECTION_TOLERANCE):
    assert np.allclose(actual[:3, 3], expected[:3, 3], rtol=0, atol=POSITION_TOLERANCE), (actual, expected)
    assert np.allclose(actual[:3, :3], expected[:3, :3], rtol=0, atol=direction_tolerance), (actual, expected)


def terminator(f, alignment, layout_name):
    layout = getattr(A, f"get_{layout_name}_layout")(alignment)
    return A.get_alignment_segment_nest(layout).RelatedObjects[-1].DesignParameters


# The end frame matches the kernel's evaluation of the finished curve


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,r0,r1", HORIZONTAL)
def test_horizontal_end(unit, kind, r0, r1):
    f, _, end = build_horizontal(unit, kind, r0, r1)
    assert_frames_equal(end, evaluate_end(representation_parts(f)["horizontal"]))


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,g0,g1,radius", VERTICAL)
def test_vertical_end(unit, kind, g0, g1, radius):
    f, _, end = build_vertical(unit, kind, g0, g1, radius)
    assert_frames_equal(end, evaluate_end(representation_parts(f)["vertical"]))


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,c0,c1", CANT)
def test_cant_end(unit, kind, c0, c1):
    f, _, end = build_cant(unit, kind, c0, c1)
    assert_frames_equal(end, evaluate_end(representation_parts(f)["cant"]))


# The end frame follows from the design parameters


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,g0,g1,radius", [v for v in VERTICAL if v[0] in ("CONSTANTGRADIENT", "PARABOLICARC")])
def test_vertical_end_from_design(unit, kind, g0, g1, radius):
    f, _, end = build_vertical(unit, kind, g0, g1, radius)
    scale = ifcopenshell.util.unit.calculate_unit_scale(f)
    # a parabola's grade changes linearly, so it ends at the mean grade times the length higher
    height = 10.0 + LENGTH * (g0 + g1) / 2.0
    assert end[0, 3] == pytest.approx(LENGTH * scale, abs=POSITION_TOLERANCE)
    assert end[1, 3] == pytest.approx(height * scale, abs=POSITION_TOLERANCE)
    assert end[1, 0] / end[0, 0] == pytest.approx(g1, abs=DIRECTION_TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,c0,c1", CANT)
def test_cant_end_from_design(unit, kind, c0, c1):
    f, _, end = build_cant(unit, kind, c0, c1)
    scale = ifcopenshell.util.unit.calculate_unit_scale(f)
    # the rail heads end at 0 (left) and c1 (right): superelevation at the centre is half of it, and
    # the cross section is rolled by its slope over the rail head distance: Axis's component on the
    # horizontal to the left, (0, 1, 0) in the cant frame
    assert end[0, 3] == pytest.approx(LENGTH * scale, abs=POSITION_TOLERANCE)
    assert end[1, 3] == pytest.approx(c1 / 2.0 * scale, abs=POSITION_TOLERANCE)
    assert end[1, 2] == pytest.approx(c1 / 1.5, abs=DIRECTION_TOLERANCE)


# The same end without geometry


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("kind,r0,r1", HORIZONTAL)
def test_horizontal_end_without_geometry(kind, r0, r1):
    _, _, with_geometry = build_horizontal("metre", kind, r0, r1)
    _, _, without_geometry = build_horizontal("metre", kind, r0, r1, include_geometry=False)
    assert_frames_equal(without_geometry, with_geometry)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("kind,g0,g1,radius", VERTICAL)
def test_vertical_end_without_geometry(kind, g0, g1, radius):
    _, _, with_geometry = build_vertical("metre", kind, g0, g1, radius)
    _, _, without_geometry = build_vertical("metre", kind, g0, g1, radius, include_geometry=False)
    assert_frames_equal(without_geometry, with_geometry)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("kind,c0,c1", CANT)
def test_cant_end_without_geometry(kind, c0, c1):
    _, _, with_geometry = build_cant("metre", kind, c0, c1)
    _, _, without_geometry = build_cant("metre", kind, c0, c1, include_geometry=False)
    assert_frames_equal(without_geometry, with_geometry)


# The terminator is placed at the end


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize(
    "direction",
    [
        0.3,
        2.5,
    ],
)
def test_horizontal_terminator_at_end(direction):
    f, alignment, end = build_horizontal("metre", "CLOTHOID", 0.0, 300.0, direction=direction)
    p = terminator(f, alignment, "horizontal")
    assert p.StartPoint.Coordinates == pytest.approx(tuple(end[:2, 3]), abs=POSITION_TOLERANCE)
    assert math.cos(p.StartDirection) == pytest.approx(end[0, 0], abs=DIRECTION_TOLERANCE)
    assert math.sin(p.StartDirection) == pytest.approx(end[1, 0], abs=DIRECTION_TOLERANCE)


@test.bootstrap.requires_ifc4x3
def test_vertical_terminator_at_end():
    f, alignment, end = build_vertical("metre", "PARABOLICARC", 0.01, -0.02, None)
    p = terminator(f, alignment, "vertical")
    assert (p.StartDistAlong, p.StartHeight) == pytest.approx((end[0, 3], end[1, 3]), abs=POSITION_TOLERANCE)
    assert p.StartGradient == pytest.approx(end[1, 0] / end[0, 0], abs=DIRECTION_TOLERANCE)


@test.bootstrap.requires_ifc4x3
def test_cant_terminator_at_end():
    f, alignment, end = build_cant("metre", "LINEARTRANSITION", 0.0, 0.15)
    p = terminator(f, alignment, "cant")
    assert p.StartDistAlong == pytest.approx(LENGTH, abs=POSITION_TOLERANCE)
    assert (p.StartCantLeft, p.StartCantRight) == pytest.approx((0.0, 0.15), abs=POSITION_TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("kind,c0,c1", CANT)
def test_cant_terminal_curve_segment_placement(kind, c0, c1):
    """The zero-length curve segment ending the cant curve is placed as cant segments are: RefDirection in the
    plane of distance along and deviating elevation, Axis in the cross section. The cant frame it is placed at
    has RefDirection pitched up by the slope, (cos θ, 0, sin θ), and Axis rolled in the section normal to it."""
    f, _, end = build_cant("metre", kind, c0, c1)
    placement = f.by_type("IfcSegmentedReferenceCurve")[0].Segments[-1].Placement
    assert placement.RefDirection.DirectionRatios == pytest.approx((end[0, 0], end[2, 0], 0.0), abs=1e-12)
    sine = c1 / 1.5
    assert placement.Axis.DirectionRatios == pytest.approx(
        (0.0, sine, math.sqrt(1.0 - sine**2)), abs=DIRECTION_TOLERANCE
    )
