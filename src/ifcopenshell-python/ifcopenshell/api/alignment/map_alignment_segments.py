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
from typing import Sequence


def map_alignment_segments(
    file: ifcopenshell.file, alignment: entity_instance, composite_curve: entity_instance
) -> None:
    """
    Creates IfcCurveSegment entities for the supplied alignment business logic entity instance and assigns them to the composite curve.
    End-Start points of adjacent segments are evaluated and the IfcCurveSegment.Transition is set.

    This function does not create an IfcShapeRepresentation. Use create_geometric_representation to create all the representations
    for an alignment. This function only populates the composite curve with IfcCurveSegment entities.

    :param alignment: The business logic alignment, expected to be IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :param composite_curve: The IfcCompositeCurve (or subclass) which will receive the IfcCurveSegment
    :return: None
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not alignment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{alignment.is_a()}"
        )

    if alignment.is_a("IfcAlignmentHorizontal") and not composite_curve.is_a("IfcCompositeCurve"):
        raise TypeError(f"Expected to see IfcCompositeCurve, instead received '{composite_curve.is_a()}'.")
    elif alignment.is_a("IfcAlignmentVertical") and not composite_curve.is_a("IfcGradientCurve"):
        raise TypeError(f"Expected to see IfcGradientCurve, instead received '{composite_curve.is_a()}'.")
    elif alignment.is_a("IfcAlignmentCant") and not composite_curve.is_a("IfcSegmentedReferenceCurve"):
        raise TypeError(f"Expected to see IfcSegmentedReferenceCurve, instead received '{composite_curve.is_a()}'.")

    settings = ifcopenshell.geom.settings()

    composite_curve.SelfIntersect = False

    for rel_nests in alignment.IsNestedBy:
        for layout in rel_nests.RelatedObjects:
            if layout.is_a("IfcLinearElement"):
                if alignment.is_a("IfcAlignmentHorizontal"):
                    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, layout)
                elif alignment.is_a("IfcAlignmentVertical"):
                    mapped_segments = ifcopenshell.api.alignment.map_alignment_vertical_segment(file, layout)
                elif alignment.is_a("IfcAlignmentCant"):
                    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(
                        file, layout, alignment.RailHeadDistance
                    )
                for mapped_segment in mapped_segments:
                    if mapped_segment:
                        ifcopenshell.api.alignment.add_segment_to_curve(file, mapped_segment, composite_curve)
