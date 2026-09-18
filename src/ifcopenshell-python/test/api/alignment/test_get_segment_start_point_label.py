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

import ifcopenshell
import ifcopenshell.guid
from ifcopenshell.api.alignment._get_segment_start_point_label import (
    _get_segment_start_point_label,
)


def test_vertical_constant_gradient_to_constant_gradient_label_has_trailing_period():
    # Every other label in the lookup tables ends with a period (e.g. "P.C.", "P.V.C.",
    # "P.V.T."); CONSTANTGRADIENT -> CONSTANTGRADIENT ("P.V.I") was missing its trailing period.
    file = ifcopenshell.file(schema="IFC4X3")

    dp1 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=0.0,
        StartGradient=0.01,
        EndGradient=0.01,
        PredefinedType="CONSTANTGRADIENT",
    )
    dp2 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=100.0,
        HorizontalLength=100.0,
        StartHeight=1.0,
        StartGradient=0.02,
        EndGradient=0.02,
        PredefinedType="CONSTANTGRADIENT",
    )
    prev_segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=dp1)
    segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=dp2)

    assert _get_segment_start_point_label(prev_segment, segment) == "P.V.I."


def _make_horizontal_arc(file, radius):
    dp = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=radius,
        EndRadiusOfCurvature=radius,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )
    return file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=dp)


def test_circulararc_to_circulararc_same_direction_is_pcc():
    # Two arcs turning the same way (StartRadiusOfCurvature same sign: +left/-right) with no
    # intervening LINE is a compound curve (a join_next junction, see
    # solve_horizontal_alignment_by_pi_method) -- Point of Compound Curvature.
    file = ifcopenshell.file(schema="IFC4X3")
    left1 = _make_horizontal_arc(file, 500.0)
    left2 = _make_horizontal_arc(file, 300.0)
    assert _get_segment_start_point_label(left1, left2) == "P.C.C."

    right1 = _make_horizontal_arc(file, -500.0)
    right2 = _make_horizontal_arc(file, -300.0)
    assert _get_segment_start_point_label(right1, right2) == "P.C.C."


def test_circulararc_to_circulararc_opposite_direction_is_prc():
    # Two arcs turning opposite ways with no intervening LINE is a reverse curve -- Point of
    # Reverse Curvature. Was previously mislabeled "P.C.C." regardless of direction (the lookup
    # table had one static entry for any CIRCULARARC -> CIRCULARARC transition).
    file = ifcopenshell.file(schema="IFC4X3")
    left = _make_horizontal_arc(file, 500.0)
    right = _make_horizontal_arc(file, -300.0)
    assert _get_segment_start_point_label(left, right) == "P.R.C."
    assert _get_segment_start_point_label(right, left) == "P.R.C."


test_vertical_constant_gradient_to_constant_gradient_label_has_trailing_period()
test_circulararc_to_circulararc_same_direction_is_pcc()
test_circulararc_to_circulararc_opposite_direction_is_prc()
