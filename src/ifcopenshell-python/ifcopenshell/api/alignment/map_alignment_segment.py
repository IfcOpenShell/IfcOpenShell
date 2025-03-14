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
import ifcopenshell.api
from ifcopenshell import entity_instance
from typing import Sequence


def map_alignment_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentSegment business logic entity instance.
    A pair of entities is returned because a single business logic segment of type HELMERTCURVE maps to two representaiton entities.

    The IfcCurveSegment.Transition transition code is set to DISCONTINUOUS, except for the transition between helmert curve segments.

    This function will evaluate the IfcAlignmentSegment.DesignParameters type and call the correct lower level mapping function.
    """
    expected_type = "IfcAlignmentSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment.is_a()}'.")

    if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        return ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, segment.DesignParameters)
    elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        return ifcopenshell.api.alignment.map_alignment_vertical_segment(file, segment.DesignParameters)
    elif segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
        return ifcopenshell.api.alignment.map_alignment_cant_segment(file, segment.DesignParameters)
    else:
        raise TypeError("Unexpected type for segment.DesignParameters")

    return (None, None)
