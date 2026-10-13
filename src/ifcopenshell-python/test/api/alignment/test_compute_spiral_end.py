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

"""Tests that the PI method solver's own spiral end points agree with the geometry the API writes.

The solver predicts where each transition ends with compute_horizontal_segment_end; the API maps the
same design parameters to IfcCurveSegments that the kernel evaluates. The two are separate
implementations of the same curvature laws, so these tests keep them from drifting apart.
"""

import math

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.geom
import test.bootstrap
from ifcopenshell import ifcopenshell_wrapper
from ifcopenshell.api.alignment import _spiral_curvature
from test.api.alignment.test_segment_end_point import (
    LENGTH,
    SPIRAL_RADII,
    SPIRALS,
    build_horizontal,
    evaluate_end,
    representation_parts,
)

# The kernel integrates a spiral's position numerically to about this, the solver to about 1e-13
POSITION_TOLERANCE = 2e-6  # metres
DIRECTION_TOLERANCE = 1e-8
# A curve segment starts exactly where the one before it ends
JOIN_POSITION_TOLERANCE = 1e-6  # metres
JOIN_DIRECTION_TOLERANCE = 1e-9

HELMERT_KINK = pytest.mark.xfail(
    strict=True,
    reason="helmert_curve_point returns the heading at x instead of at s, so the second half of a "
    "helmert curve is placed with a kink",
)


def spiral_cases():
    for family in SPIRALS:
        for r0, r1 in SPIRAL_RADII:
            marks = [HELMERT_KINK] if family == "HELMERTCURVE" else []
            yield pytest.param(family, r0, r1, marks=marks, id=f"{family}-{r0:g}-{r1:g}")


def helmert_cases():
    for r0, r1 in SPIRAL_RADII:
        yield pytest.param(r0, r1, marks=[HELMERT_KINK], id=f"{r0:g}-{r1:g}")


def heading(frame):
    return math.atan2(frame[1, 0], frame[0, 0])


def angle_between(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("family,r0,r1", list(spiral_cases()))
def test_solver_end_matches_kernel(family, r0, r1):
    f, alignment, _ = build_horizontal("metre", family, r0, r1)
    p = next(
        s.DesignParameters for s in f.by_type("IfcAlignmentSegment") if s.DesignParameters.SegmentLength > 0
    )
    segment = ifcopenshell.api.alignment.HorizontalSegmentDefinition(
        tuple(p.StartPoint.Coordinates), p.StartDirection, r0, r1, LENGTH, family
    )
    x, y, direction = ifcopenshell.api.alignment.compute_horizontal_segment_end(segment)
    end = evaluate_end(representation_parts(f)["horizontal"])
    assert math.hypot(x - end[0, 3], y - end[1, 3]) < POSITION_TOLERANCE
    assert abs(angle_between(direction, heading(end))) < DIRECTION_TOLERANCE


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("r0,r1", list(helmert_cases()))
def test_helmert_halves_join_smoothly(r0, r1):
    f, alignment, _ = build_horizontal("metre", "HELMERTCURVE", r0, r1)
    first, second = [s for s in f.by_type("IfcCurveSegment") if s.SegmentLength.wrappedValue > 0]
    settings = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(settings, first)
    end = np.array(ifcopenshell_wrapper.function_item_evaluator(settings, fn).evaluate(fn.end()))
    d = second.Placement.RefDirection.DirectionRatios
    assert math.dist(end[:2, 3], second.Placement.Location.Coordinates) < JOIN_POSITION_TOLERANCE
    assert abs(angle_between(heading(end), math.atan2(d[1], d[0]))) < JOIN_DIRECTION_TOLERANCE


@pytest.mark.parametrize("r0,r1", list(helmert_cases()))
def test_helmert_curve_point_heading(r0, r1):
    # the heading at arc length s is theta(s), which every polynomial spiral has in closed form
    (a0, a1, a2), _ = _spiral_curvature.helmert_coefficients(LENGTH, r0, r1)
    theta = _spiral_curvature.polynomial_spiral_theta((a0, a1, a2))
    s = LENGTH / 2.0
    assert ifcopenshell_wrapper.helmert_curve_point(a0, a1, a2, s)[2] == pytest.approx(theta(s), abs=1e-12)
