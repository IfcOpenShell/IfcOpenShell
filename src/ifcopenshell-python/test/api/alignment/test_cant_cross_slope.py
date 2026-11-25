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

"""Tests for the cross slope of the track along a cant segment.

At every point the centreline is raised by the deviating elevation, the mean of the cant at the two
rails, and the track is rolled so that its up axis leans by (cant right - cant left) / rail head
distance. A left hand curve raises the right rail, a right hand curve raises the left rail, and either
rail, or both, may be canted at the start and end of a segment.
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
import test.bootstrap
from ifcopenshell import ifcopenshell_wrapper

A = ifcopenshell.api.alignment
LENGTH = 100.0
HEIGHT = 10.0
RAIL_HEAD_DISTANCE = 1.5
TOLERANCE = 1e-9

TRANSITIONS = ["LINEARTRANSITION", "HELMERTCURVE", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "VIENNESEBEND"]
# ((start left, start right), (end left, end right))
RAILS = {
    "left-hand-entry": ((0.0, 0.0), (0.0, 0.16)),
    "left-hand-exit": ((0.0, 0.16), (0.0, 0.0)),
    "right-hand-entry": ((0.0, 0.0), (0.16, 0.0)),
    "right-hand-exit": ((0.16, 0.0), (0.0, 0.0)),
    "both-rails": ((0.02, 0.10), (0.04, 0.20)),
}


def new_file():
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, units=[ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    return f


def build(kind, start, end):
    """A straight, level alignment along x with one cant segment"""
    f = new_file()
    alignment = A.create(f, "C", include_vertical=True, include_cant=True)
    A.get_cant_layout(alignment).RailHeadDistance = RAIL_HEAD_DISTANCE
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint((0.0, 0.0)),
            StartDirection=0.0,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=LENGTH,
            PredefinedType="LINE",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=HEIGHT,
            StartGradient=0.0,
            EndGradient=0.0,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_cant_layout(alignment),
        f.createIfcAlignmentCantSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartCantLeft=start[0],
            EndCantLeft=end[0],
            StartCantRight=start[1],
            EndCantRight=end[1],
            PredefinedType=kind,
        ),
    )
    return f


def frames(f, distances):
    s = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(s, f.by_type("IfcSegmentedReferenceCurve")[0])
    evaluator = ifcopenshell_wrapper.function_item_evaluator(s, fn)
    return [np.array(evaluator.evaluate(u)) for u in distances]


def lean(left, right):
    """The angle the track's up axis leans towards the left of the alignment for the cant at each rail"""
    return math.asin((right - left) / RAIL_HEAD_DISTANCE)


def roll(frame):
    """The lean of the track's up axis towards the left of the alignment, as a sine: its component on the
    horizontal to the left, in the section normal to the track"""
    ref_dir, axis = frame[:3, 0], frame[:3, 2]
    return (axis[1] * ref_dir[0] - axis[0] * ref_dir[1]) / math.hypot(ref_dir[0], ref_dir[1])


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("rails", list(RAILS))
@pytest.mark.parametrize("kind", TRANSITIONS)
def test_cross_slope_at_start_and_end(kind, rails):
    start, end = RAILS[rails]
    f = build(kind, start, end)
    for frame, (left, right) in zip(frames(f, [0.0, LENGTH]), (start, end)):
        assert frame[2, 3] == pytest.approx(HEIGHT + (left + right) / 2.0, abs=TOLERANCE)
        assert roll(frame) == pytest.approx((right - left) / RAIL_HEAD_DISTANCE, abs=TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("rails", list(RAILS))
@pytest.mark.parametrize("kind", TRANSITIONS)
def test_cross_slope_at_middle(kind, rails):
    # Every transition is symmetric about its middle, where its deviating elevation is half way. The
    # cross slope angle changes in proportion to the deviating elevation, so it is half way too.
    start, end = RAILS[rails]
    f = build(kind, start, end)
    (frame,) = frames(f, [LENGTH / 2.0])
    angle = (lean(*start) + lean(*end)) / 2.0
    assert frame[2, 3] == pytest.approx(HEIGHT + (sum(start) + sum(end)) / 4.0, abs=TOLERANCE)
    assert roll(frame) == pytest.approx(math.sin(angle), abs=TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("rails", list(RAILS))
@pytest.mark.parametrize("kind", ["CONSTANTCANT"])
def test_constant_cant(kind, rails):
    _, (left, right) = RAILS[rails]
    f = build(kind, (left, right), (left, right))
    for frame in frames(f, [0.0, LENGTH / 2.0, LENGTH]):
        assert frame[2, 3] == pytest.approx(HEIGHT + (left + right) / 2.0, abs=TOLERANCE)
        assert roll(frame) == pytest.approx((right - left) / RAIL_HEAD_DISTANCE, abs=TOLERANCE)


def cross_slope_angle(frame):
    """The angle of the track's up axis from the left of the alignment (+Y), 90 degrees when level"""
    axis = frame[:3, 2]
    return math.degrees(math.atan2(axis[2], axis[1]))


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("hand", ["left", "right"])
@pytest.mark.parametrize("kind", TRANSITIONS)
def test_cross_slope_through_a_curve(kind, hand):
    # An entry transition, constant cant and an exit transition, raising the outside rail: the right rail
    # in a curve to the left and the left rail in a curve to the right. The cross slope angle is below 90
    # degrees through a curve to the left and above it through a curve to the right, and is continuous
    # where the segments meet.
    cant = 0.16
    outside = {"left": lambda c: (0.0, c), "right": lambda c: (c, 0.0)}[hand]
    f = new_file()
    alignment = A.create(f, "C", include_vertical=True, include_cant=True)
    A.get_cant_layout(alignment).RailHeadDistance = RAIL_HEAD_DISTANCE
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint((0.0, 0.0)),
            StartDirection=0.0,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=3 * LENGTH,
            PredefinedType="LINE",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=3 * LENGTH,
            StartHeight=HEIGHT,
            StartGradient=0.0,
            EndGradient=0.0,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )
    for i, (segment_kind, c0, c1) in enumerate([(kind, 0.0, cant), ("CONSTANTCANT", cant, cant), (kind, cant, 0.0)]):
        (l0, r0), (l1, r1) = outside(c0), outside(c1)
        A.create_layout_segment(
            f,
            A.get_cant_layout(alignment),
            f.createIfcAlignmentCantSegment(
                StartDistAlong=i * LENGTH,
                HorizontalLength=LENGTH,
                StartCantLeft=l0,
                EndCantLeft=l1,
                StartCantRight=r0,
                EndCantRight=r1,
                PredefinedType=segment_kind,
            ),
        )

    distances = list(np.linspace(0.0, 3 * LENGTH, 61))
    angles = [cross_slope_angle(frame) for frame in frames(f, distances)]
    if hand == "left":
        assert all(angle <= 90.0 + TOLERANCE for angle in angles), angles
    else:
        assert all(angle >= 90.0 - TOLERANCE for angle in angles), angles

    epsilon = 1e-6
    for junction in (LENGTH, 2 * LENGTH):
        before, after = frames(f, [junction - epsilon, junction + epsilon])
        assert cross_slope_angle(after) == pytest.approx(cross_slope_angle(before), abs=1e-4)
