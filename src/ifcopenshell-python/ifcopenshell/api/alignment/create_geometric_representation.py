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
import ifcopenshell.api.geometry
from ifcopenshell import entity_instance

import math
from typing import Sequence


def create_geometric_representation(file: ifcopenshell.file, alignment: entity_instance) -> None:
    """
    Create geometric representation for the alignment.

    There are 5 different cases:

    1) Horizontal only
    2) Horizontal + Vertical
    3) Horizontal + Vertical + Cant
    4) Vertical only (this occurs when horizontal is reused from a parent alignment)
    5) Vertical + Cant (this occurs when horizontal is reused from a parent alignment)

    :param alignment: The alignment for which the representation is being created
    :return: None
    """

    expected_type = "IfcAlignment"
    if not alignment.is_a(expected_type):
        raise TypeError("Expected '{expected_type}' but got '{alignment.is_a()}'")

    placement = file.createIfcLocalPlacement(
        PlacementRelTo=None,
        RelativePlacement=file.createIfcAxis2Placement2D(Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))),
    )

    alignment.ObjectPlacement = placement

    axis_geom_subcontext = ifcopenshell.api.alignment.get_axis_subcontext(file)

    layouts = ifcopenshell.api.alignment.get_alignment_layouts(alignment)
    children = ifcopenshell.api.alignment.get_child_alignments(alignment)

    if len(layouts) == 1 and len(children) == 0:
        assert layouts[0].is_a("IfcAlignmentHorizontal")
        # Horizontal only - IFC CT 4.1.7.1.1.1
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[0])
        composite_curve = file.createIfcCompositeCurve()
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[0], composite_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)
    elif len(layouts) == 2 and len(children) == 0:
        # Horizontal and Vertical - IFC CT 4.1.7.1.1.1
        assert layouts[0].is_a("IfcAlignmentHorizontal")
        assert layouts[1].is_a("IfcAlignmentVertical")
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[0])
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[1])
        composite_curve = file.createIfcCompositeCurve()
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[0], composite_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)

        gradient_curve = file.createIfcGradientCurve(BaseCurve=composite_curve)
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[1], gradient_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=(gradient_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)
    elif len(layouts) == 3 and len(children) == 0:
        # Horizontal, Vertical, and Cant - IFC CT 4.1.7.1.1.3
        assert layouts[0].is_a("IfcAlignmentHorizontal")
        assert layouts[1].is_a("IfcAlignmentVertical")
        assert layouts[2].is_a("IfcAlignmentCant")
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[0])
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[1])
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[2])
        composite_curve = file.createIfcCompositeCurve()
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[0], composite_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)

        gradient_curve = file.createIfcGradientCurve(BaseCurve=composite_curve)
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[1], gradient_curve)
        segmented_reference_curve = file.createIfcSegmentedReferenceCurve(BaseCurve=gradient_curve)
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[2], segmented_reference_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=(segmented_reference_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)
    else:
        # Reusing Horizontal - CT 4.1.4.4.1.2
        # Create a representation on the parent alignment
        ifcopenshell.api.alignment.add_zero_length_segment(file, layouts[0])
        composite_curve = file.createIfcCompositeCurve()
        ifcopenshell.api.alignment.map_alignment_segments(file, layouts[0], composite_curve)
        representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="FootPrint",
            RepresentationType="Curve2D",
            Items=(composite_curve,),
        )
        ifcopenshell.api.geometry.assign_representation(file, alignment, representation)

    for child_alignment in children:
        child_alignment.ObjectPlacement = placement
        child_layouts = ifcopenshell.api.alignment.get_alignment_layouts(child_alignment)
        if len(child_layouts) == 1:
            assert child_layouts[0].is_a("IfcAlignmentVertical")
            ifcopenshell.api.alignment.add_zero_length_segment(file, child_layouts[0])
            base_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
            gradient_curve = file.createIfcGradientCurve(BaseCurve=base_curve)
            ifcopenshell.api.alignment.map_alignment_segments(file, child_layouts[0], gradient_curve)
            representation = file.create_entity(
                type="IfcShapeRepresentation",
                ContextOfItems=axis_geom_subcontext,
                RepresentationIdentifier="Axis",
                RepresentationType="Curve3D",
                Items=(gradient_curve,),
            )
            ifcopenshell.api.geometry.assign_representation(file, child_alignment, representation)
        elif len(child_layouts) == 2:
            assert child_layouts[0].is_a("IfcAlignmentVertical")
            assert child_layouts[1].is_a("IfcAlignmentCant")
            ifcopenshell.api.alignment.add_zero_length_segment(file, child_layouts[0])
            ifcopenshell.api.alignment.add_zero_length_segment(file, child_layouts[1])
            base_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
            gradient_curve = file.createIfcGradientCurve(BaseCurve=base_curve)
            ifcopenshell.api.alignment.map_alignment_segments(file, child_layouts[0], gradient_curve)
            segmented_reference_curve = file.createIfcSegmentedReferenceCurve(BaseCurve=gradient_curve)
            ifcopenshell.api.alignment.map_alignment_segments(file, child_layouts[1], segmented_reference_curve)
            representation = file.create_entity(
                type="IfcShapeRepresentation",
                ContextOfItems=axis_geom_subcontext,
                RepresentationIdentifier="Axis",
                RepresentationType="Curve3D",
                Items=(segmented_reference_curve,),
            )
            ifcopenshell.api.geometry.assign_representation(file, child_alignment, representation)
        else:
            assert False  # should never get here - can't have more than one vertical and cant in a child alignment
