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
import ifcopenshell.util.element
from ifcopenshell import entity_instance


def has_zero_length_segment(layout: entity_instance) -> bool:
    """
    Returns true if the layout ends with a zero length segment.

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcCompositeCurve, IfcGradientCurve, or IfcSegmentedReferenceCurve
    :return: True if the zero length segment is present
    """
    expected_types = [
        "IfcAlignmentHorizontal",
        "IfcAlignmentVertical",
        "IfcAlignmentCant",
        "IfcCompositeCurve",
        "IfcGradientCurve",
        "IfcSegmentedReferenceCurve",
    ]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{layout.is_a()}"
        )

    result = False

    if layout.is_a("IfcCompositeCurve") or layout.is_a("IfcGradientCurve") or layout.is_a("IfcSegmentedReferenceCurve"):
        result = (
            True
            if layout.Segments and 0 < len(layout.Segments) and layout.Segments[-1].SegmentLength.wrappedValue == 0.0
            else False
        )
    else:
        for rel in layout.IsNestedBy:
            if 0 < len(rel.RelatedObjects):
                last_segment = rel.RelatedObjects[-1]
                if last_segment.is_a("IfcAlignmentSegment"):
                    if last_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
                        result = last_segment.DesignParameters.SegmentLength == 0.0
                    elif last_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
                        result = last_segment.DesignParameters.HorizontalLength == 0.0
                    elif last_segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
                        result = last_segment.DesignParameters.HorizontalLength == 0.0

    return result
