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
import math
import ifcopenshell.api.alignment
import ifcopenshell.util.unit
from ifcopenshell import entity_instance


def _update_zero_length_segment_placement(
    file: ifcopenshell.file, zero_length_segment: entity_instance, placement: np.array
) -> None:
    """
    Updates the placement of a zero length segment (i.e. a segment with identical start and end point) based on a 4x4 placement matrix.
    The zero_length_segment can be an IfcAlignmentSegment or IfcCurveSegment.
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    x = float(placement[0, 3]) / unit_scale
    y = float(placement[1, 3]) / unit_scale
    z = float(placement[2, 3]) / unit_scale
    Rdx = float(placement[0, 0])
    Rdy = float(placement[1, 0])
    Rdz = float(placement[2, 0])
    Adx = float(placement[0, 2])
    Ady = float(placement[1, 2])
    Adz = float(placement[2, 2])

    if zero_length_segment.is_a("IfcCurveSegment"):
        if zero_length_segment.Placement.is_a("IfcAxis2Placement2D"):
            zero_length_segment.Placement.Location.Coordinates = (x, y)
            zero_length_segment.Placement.RefDirection.DirectionRatios = (Rdx, Rdy)
        else:
            zero_length_segment.Placement.Location.Coordinates = (x, y, z)
            zero_length_segment.Placement.RefDirection.DirectionRatios = (Rdx, Rdy, Rdz)
            zero_length_segment.Placement.Axis.DirectionRatios = (Adx, Ady, Adz)
    elif zero_length_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        zero_length_segment.DesignParameters.StartPoint.Coordinates = (x, y)
        zero_length_segment.DesignParameters.StartDirection = math.atan(Rdy / Rdx)
    elif zero_length_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        zero_length_segment.DesignParameters.StartDistAlong = x
        zero_length_segment.DesignParameters.StartHeight = y
        zero_length_segment.DesignParameters.StartGradient = Rdy / Rdx
        zero_length_segment.DesignParameters.EndGradient = zero_length_segment.DesignParameters.StartGradient
    else:
        slope = Ady / math.sqrt(Ady**2 + Adz**2)
        layout = ifcopenshell.api.alignment.get_layout(zero_length_segment)
        railhead = layout.RailHeadDistance

        zero_length_segment.DesignParameters.StartDistAlong = x
        zero_length_segment.DesignParameters.StartCantLeft = y - slope * railhead / 2.0
        zero_length_segment.DesignParameters.StartCantRight = y + slope * railhead / 2.0
        zero_length_segment.DesignParameters.EndCantLeft = zero_length_segment.DesignParameters.StartCantLeft
        zero_length_segment.DesignParameters.EndCantRight = zero_length_segment.DesignParameters.StartCantRight
