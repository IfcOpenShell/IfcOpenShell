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

import numpy as np

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.util.placement
from ifcopenshell import entity_instance


def update_end_point(file: ifcopenshell.file, curve: entity_instance):
    """
    Updates the IfcGradientCurve.EndPoint and IfcSegmentedReferenceCurve.EndPoint.

    If the curve does not have a zero length segment, one is added. The EndPoint is then updated to match the placement of the zero length segment.

    :param curve: The gradient curve or segmented reference curve
    :return: None
    """
    expected_types = ["IfcGradientCurve", "IfcSegmentedReferenceCurve"]
    if not curve.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{curve.is_a()}"
        )

    if not ifcopenshell.api.alignment.has_zero_length_segment(curve):
        ifcopenshell.api.alignment.add_zero_length_segment(file, curve)

    zero_length_segment = curve.Segments[-1]

    if not curve.EndPoint:
        if curve.is_a("IfcGradientCurve"):
            curve.EndPoint = file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint((0.0, 0.0)),
                RefDirection=file.createIfcDirection((1.0, 0.0)),
            )
        else:
            curve.EndPoint = file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                RefDirection=file.createIfcDirection((1.0, 0.0, 0.0)),
                Axis=file.createIfcDirection((0.0, 0.0, 1.0)),
            )

    p = np.array(ifcopenshell.util.placement.get_axis2placement(zero_length_segment.Placement))

    x = float(p[0, 3])
    y = float(p[1, 3])
    z = float(p[2, 3])

    rx = float(p[0, 0])
    ry = float(p[1, 0])
    rz = float(p[2, 0])

    ax = float(p[0, 2])
    ay = float(p[1, 2])
    az = float(p[2, 2])

    if curve.is_a("IfcGradientCurve"):
        curve.EndPoint.Location.Coordinates = (x, y)

        if not curve.EndPoint.RefDirection:
            curve.EndPoint.RefDirection = file.createIfcDirection((1.0, 0.0))

        curve.EndPoint.RefDirection.DirectionRatios = (rx, ry)
    else:
        curve.EndPoint.Location.Coordinates = (x, y, z)

        if not curve.EndPoint.RefDirection:
            curve.EndPoint.RefDirection = file.createIfcDirection((1.0, 0.0, 0.0))

        if not curve.EndPoint.Axis:
            curve.EndPoint.Axis = file.createIfcDirection((0.0, 0.0, 1.0))

        curve.EndPoint.RefDirection.DirectionRatios = (rx, ry, rz)
        curve.EndPoint.Axis.DirectionRatios = (ax, ay, az)
