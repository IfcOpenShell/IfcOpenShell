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


def has_zero_length_segment(entity: entity_instance) -> bool:
    """
    Returns true if the entity ends with a zero length segment. If the entity is an IfcCompositeCurve the IfcCurveSegment.Transition must be DISCONTINUOUS

    :param entity: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant or IfcCompositeCurve
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
    if not entity.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{entity.is_a()}"
        )

    if entity.is_a("IfcCompositeCurve"):
        last_segment = entity.Segments[-1]
        return last_segment.Transition == "DISCONTINUOUS" and last_segment.SegmentLength.wrappedValue == 0.0
    else:
        segments = ifcopenshell.util.element.get_components(entity)
        for rel in entity.IsNestedBy:
            if 0 < len(rel.RelatedObjects):
                last_segment = rel.RelatedObjects[-1]
                if last_segment.is_a("IfcAlignmentSegment"):
                    if last_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
                        return last_segment.DesignParameters.SegmentLength == 0.0
                    elif last_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
                        return last_segment.DesignParameters.HorizontalLength == 0.0
                    elif last_segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
                        return last_segment.DesignParameters.HorizontalLength == 0.0

    return False
