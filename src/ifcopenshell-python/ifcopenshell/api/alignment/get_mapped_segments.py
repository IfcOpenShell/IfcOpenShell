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
import ifcopenshell.api.alignment
from ifcopenshell import entity_instance
from collections.abc import Sequence


def _get_curve_segment_count(segment: entity_instance) -> int:
    """
    returns the number of IfcCurveSegment that an IfcAlignmentSegment maps to.
    generally this is a 1 to 1 mapping, with helmert curve being the exception
    """
    if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        return 2 if segment.DesignParameters.PredefinedType == "HELMERTCURVE" else 1
    elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        return 1
    elif segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
        return 2 if segment.DesignParameters.PredefinedType == "HELMERTCURVE" else 1


def get_mapped_segments(layout_segment: entity_instance) -> Sequence[entity_instance]:
    """
    From an IfcAlignmentSegment, returns the related IfcCurveSegment. Typically the sequence has one entity,
    however there will be two for Helmert curve
    """
    expected_type = "IfcAlignmentSegment"
    if not layout_segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{layout_segment.is_a()}'.")

    layout = layout_segment.Nests[0].RelatingObject
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)

    index = 0
    for seg in layout.IsNestedBy[0].RelatedObjects:
        index += _get_curve_segment_count(seg)
        if seg == layout_segment:
            break

    segment_count = _get_curve_segment_count(layout_segment)
    if segment_count == 1:
        return (curve.Segments[index - segment_count], None)
    else:
        return (curve.Segments[index - segment_count], curve.Segments[index])
