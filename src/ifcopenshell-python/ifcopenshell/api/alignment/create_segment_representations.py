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
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.api.alignment
from ifcopenshell import entity_instance


def create_segment_representations(
    file: ifcopenshell.file,
    alignment: entity_instance,
) -> None:
    """
    Creates curve segment representations for the alignment for IFC CT 4.1.7.1.1.4. The alignment is expected to have representations
    for "Axis/Curve2D" (horizontal only) or "FootPrint/Curve2D" and "Axis/Curve3D" (horizontal + vertical/cant). There is the additional
    expectation that there is a 1-to-1 relationship between IfcAlignmentSegment and IfcCurveSegment.
    That is, no Helmert curves in the alignment which have a 1-to-2 relationship

    :param alignment: The alignment to create segment representations.
    """
    expected_type = "IfcAlignment"
    if not alignment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{alignment.is_a()}'.")

    axis_geom_subcontext = ifcopenshell.api.alignment.get_axis_subcontext(file)
    representations = ifcopenshell.util.representation.get_representations_iter(alignment)
    for representation in representations:
        curve = None
        nested_alignment = None
        if (representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve2D") or (
            representation.RepresentationIdentifier == "FootPrint" and representation.RepresentationType == "Curve2D"
        ):
            curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
            nested_alignment = next(
                c for c in ifcopenshell.util.element.get_components(alignment) if c.is_a("IfcAlignmentHorizontal")
            )
        elif representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve3D":
            curve = ifcopenshell.api.alignment.get_curve(alignment)
            nested_alignment = next(
                c for c in ifcopenshell.util.element.get_components(alignment) if c.is_a("IfcAlignmentVertical")
            )

        curve_segments = curve.Segments
        segments = nested_alignment.IsNestedBy[0].RelatedObjects

        for curve_segment, alignment_segment in zip(curve_segments, segments):
            axis_representation = file.create_entity(
                type="IfcShapeRepresentation",
                ContextOfItems=axis_geom_subcontext,
                RepresentationIdentifier="Axis",
                RepresentationType="Segment",
                Items=(curve_segment,),
            )
            product = file.create_entity(
                type="IfcProductDefinitionShape", Name=None, Description=None, Representations=(axis_representation,)
            )
            alignment_segment.ObjectPlacement = alignment.ObjectPlacement
            alignment_segment.Representation = product
