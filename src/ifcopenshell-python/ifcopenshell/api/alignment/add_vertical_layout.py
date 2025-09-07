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
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.geometry
import ifcopenshell.api.nest
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.api
from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._add_zero_length_segment import _add_zero_length_segment


def _move_vertical_layout_to_child_alignment(
    file: ifcopenshell.file, parent_alignment: entity_instance, vertical_layout: entity_instance
):
    """
    Creates a new child alignment and aggregates it to the parent alignment. Moves the vertical alignment from the parent
    alignment to the child alignment. Also moves the "Axis/Curve3D" representation to the child alignment, if present.
    This function supports the transition of vertical alignment between CT 4.1.4.4.1.1 and 4.1.4.4.1.2 because a subsequent
    vertical alignment is being added and the Alignment Layout - Reusing Horizontal Layout concept applies.
    """
    # unhook the vertical layout from the parent alignment
    ifcopenshell.api.nest.unassign_object(file, related_objects=[vertical_layout])

    # create the child alignment
    child_alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(), Name=f"Child of {parent_alignment.Name}"
    )

    # nest the vertical layout onto the child alignment
    ifcopenshell.api.nest.assign_object(file, related_objects=[vertical_layout], relating_object=child_alignment)

    # aggregate the child alignment to the parent alignment
    ifcopenshell.api.aggregate.assign_object(file, products=[child_alignment], relating_object=parent_alignment)

    # move all referents positioning segments of the vertical layout to the referent nest of the child alignment
    child_referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, child_alignment)
    parent_referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, parent_alignment)
    for referent in parent_referent_nest.RelatedObjects:
        for product in referent.Positions[0].RelatedProducts:
            if product.is_a("IfcAlignmentSegment") and product.Nests[0].RelatingObject == vertical_layout:
                # ifcopenshell.api.nest.change_nest(file,referent,child_alignment) - this doesn't work because referent is assigned to child_alignment.IsNestedBy[0].RelatedObjects
                # and it needs to be assigned to child_alignment.IsNestedBy[1].RelatedObjects
                # move the referent manually - unassign it and add it to the child alignment's referent nest
                ifcopenshell.api.nest.unassign_object(file, [referent])
                child_referent_nest.RelatedObjects += (referent,)

    # if the parent alignment has a representation, move the Axis/Curve3D represention to the child alignment
    base_curve = ifcopenshell.api.alignment.get_basis_curve(parent_alignment)
    if base_curve:
        representations = ifcopenshell.util.representation.get_representations_iter(parent_alignment)
        for representation in representations:
            if representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve3D":
                ifcopenshell.api.geometry.unassign_representation(file, parent_alignment, representation)
                ifcopenshell.api.geometry.assign_representation(file, child_alignment, representation)
                child_alignment.ObjectPlacement = parent_alignment.ObjectPlacement
                break


def add_vertical_layout(file: ifcopenshell.file, parent_alignment: entity_instance) -> entity_instance:
    """
    Adds a vertical layout to a previously created alignment.

    If this is the first vertical layout assigned to the parent_alignment the IFC CT 4.1.4.4.1.1 Alignment Layout - Horizontal, Vertical and Cant
    is followed. If this is the second or subsequent vertical layout assigned to the parent_alignment the
    IFC CT 4.1.4.4.1.2 Alignment Layout - Reusing Horizontal Layout is followed.

    When the second vertical layout is added, the structure of the IFC model must transition from one concept template to the other.
    Specifically, the following occurs:

    1) The first child IfcAlignment is created and is IfcRelAggregates with the parent alignment.
    2) The first vertical layout is unassigned from the IfcRelNests of the parent alignment and is IfcRelNests to the new child alignment.
    3) A second child IfcAlignment is created and it is IfcRelAggregates with the parent alignment.
    4) The vertical layout is IfcRelNests to the second child alignment

    For the third and subsequent vertical layouts, a new child alignment is created and aggregated to the parent alignment.

    A zero segment length terminated IfcGradientCurve is created for the new vertical layout

    :param parent_alignment: The parent alignment
    :return: The new vertical layout, including the manditory zero length segment
    """

    vertical_layout = file.createIfcAlignmentVertical(GlobalId=ifcopenshell.guid.new())

    # get all the child alignments under alignment
    child_alignments = [
        c for c in ifcopenshell.util.element.get_decomposition(parent_alignment) if c.is_a("IfcAlignment")
    ]

    # Get all the IfcAlignmentVertical that are nesting alignment (there should be 0 or 1)
    # if 0, alignment is just horizontal and we are adding the first vertical so it will nest to the alignment,
    # or there are multiple vertical and they nest to the aggregated child alignments
    # if 1, there is one vertical alignments. Move it to a child alignment
    vertical_layouts_nesting_alignment = [
        c for c in ifcopenshell.util.element.get_components(parent_alignment) if c.is_a("IfcAlignmentVertical")
    ]

    # move the vertical layout to a child alignment because there is going to be more than one vertical
    assert len(vertical_layouts_nesting_alignment) == 0 or len(vertical_layouts_nesting_alignment) == 1
    for vertical_layout_nesting_alignment in vertical_layouts_nesting_alignment:
        _move_vertical_layout_to_child_alignment(file, parent_alignment, vertical_layout_nesting_alignment)

    if len(child_alignments) == 0 and len(vertical_layouts_nesting_alignment) == 0:
        # this is the first vertical layout so nest it into the parent alignment (IFC CT 4.1.4.4.1.1)
        ifcopenshell.api.nest.assign_object(file, related_objects=[vertical_layout], relating_object=parent_alignment)

        base_curve = ifcopenshell.api.alignment.get_basis_curve(parent_alignment)

        # the parent alignment has a Representation so create a representation for the vertical
        gradient_curve = file.createIfcGradientCurve(
            Segments=[], SelfIntersect=False, BaseCurve=base_curve, EndPoint=None
        )

        # Per IFC CT 4.1.7.1.1.1, the shape representation for Horizontal geometry only is
        # RepresentationIdentifier="Axis" and RepresentationType="Curve2D".
        # However, per IFC CT 4.1.7.1.1.2 and 3 the shape represenation with Horizontal, Vertical and Cant
        # is RepresentationIdentifier="FootPrint" and RepresentationType="Curve2D" for the horizontal and
        # RepresentationIdentifier="Axis" and RepresentationType="Curve3D" for the 2.5D curve.
        # Since the alignment is transitioning from horizontal only to horizontal+vertical, the
        # RepresentationIdentifier must change from "Axis" to "FootPrint"
        representations = ifcopenshell.util.representation.get_representations_iter(parent_alignment)
        for representation in representations:
            if representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve2D":
                representation.RepresentationIdentifier = "FootPrint"
                break

        # create the Axis,Curve3D representation
        axis_geom_subcontext = ifcopenshell.api.alignment.get_axis_subcontext(file)
        axis3d_shape_representation = file.createIfcShapeRepresentation(
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=(gradient_curve,),
        )

        ifcopenshell.api.geometry.assign_representation(file, parent_alignment, axis3d_shape_representation)
    else:
        # there are multiple vertical reusing the horizontal (IFC CT 4.1.4.4.1.2)
        # this is the second or subsequent vertical reusing the horizontal

        # create a new child alignment for the new vertical
        child_alignment = file.createIfcAlignment(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=f"Child of {parent_alignment.Name}",
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            PredefinedType=None,
        )

        # Aggregate the child alignment to the parent alignment
        ifcopenshell.api.aggregate.assign_object(file, (child_alignment,), parent_alignment)

        # nest the vertical under the child alignment
        ifcopenshell.api.nest.assign_object(file, related_objects=[vertical_layout], relating_object=child_alignment)

        child_alignment.ObjectPlacement = parent_alignment.ObjectPlacement

        # the parent alignment has a Representation so create a representation for the vertical
        base_curve = ifcopenshell.api.alignment.get_basis_curve(parent_alignment)
        gradient_curve = file.createIfcGradientCurve(
            Segments=[], SelfIntersect=False, BaseCurve=base_curve, EndPoint=None
        )

        axis_geom_subcontext = ifcopenshell.api.alignment.get_axis_subcontext(file)

        # create the Curve3D representation
        axis3d_shape_representation = file.createIfcShapeRepresentation(
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve3D",
            Items=(gradient_curve,),
        )

        # add the representation to the child alignment
        ifcopenshell.api.geometry.assign_representation(file, child_alignment, axis3d_shape_representation)

    # All alignment layouts must end with a zero length segment. Their geometric representations must also end with a zero length segment.
    # Now that all the geometry is setup, add the zero length segment to the layout, which also adds a zero length segment to the representation
    _add_zero_length_segment(file, vertical_layout)

    return vertical_layout
