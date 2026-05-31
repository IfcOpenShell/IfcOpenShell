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
from ifcopenshell.api.alignment._add_segment_to_curve import _add_segment_to_curve
from ifcopenshell.api.alignment._create_geometric_representation import (
    _create_geometric_representation,
)
from ifcopenshell.api.alignment.update_fallback_position import update_fallback_position


def create_representation(
    file: ifcopenshell.file,
    alignment: entity_instance,
) -> None:
    """
    Creates the geometric representation of an alignment if it does not already exist.
    This function is intended to be used when a model has only the semantic definition of an alignment
    and you want to add the geometric representation.

    If the alignments are complete, it is recommended that add_zero_length_segment is called before this method to ensure
    the proper structure of the semantic and geometric definitions of the alignment.

    It is presumed that the alignment does not have any geometric representation. However, if the alignment has stationing defined,
    the referent defining the stationing is not related to the alignment geometry (it can't be because the geometry doesn't exist yet).
    When the geometric representation is created, the referent is updated to have an IfcLinearPlacement that references the basis curve geometry.
    This function assumes the referent defines the stationing at the start of the alignment, and therefore sets the IfcLinearPlacement.RelativePlacement.Location.DistanceAlong to 0.0.

    :param alignment: The alignment to create the representation.
    """
    expected_type = "IfcAlignment"
    if not alignment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{alignment.is_a()}'.")

    if alignment.Representation:
        return

    _create_geometric_representation(file, alignment)

    layouts = ifcopenshell.api.alignment.get_alignment_layouts(alignment)
    for layout in layouts:
        curve = ifcopenshell.api.alignment.get_layout_curve(layout)

        layout_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
        for segment in layout_nest.RelatedObjects:
            _add_segment_to_curve(file, segment, curve)

    # if the alignment is created without geometry it's stationing referent isn't related to the alignment geometry.
    # the stationing referent needs to be updated to have an IfcLinearPlacement that references the basis curve geometry
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    if (
        referent_nest
        and 0 < len(referent_nest.RelatedObjects)
        and referent_nest.RelatedObjects[0].ObjectPlacement
        and not referent_nest.RelatedObjects[0].ObjectPlacement.is_a("IfcLinearPlacement")
    ):
        basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)

        if referent_nest.RelatedObjects[0].ObjectPlacement:
            if referent_nest.RelatedObjects[0].ObjectPlacement.RelativePlacement.Location:
                file.remove(referent_nest.RelatedObjects[0].ObjectPlacement.RelativePlacement.Location)
            if referent_nest.RelatedObjects[0].ObjectPlacement.RelativePlacement.RefDirection:
                file.remove(referent_nest.RelatedObjects[0].ObjectPlacement.RelativePlacement.RefDirection)
            file.remove(referent_nest.RelatedObjects[0].ObjectPlacement.RelativePlacement)
            file.remove(referent_nest.RelatedObjects[0].ObjectPlacement)

        lp = file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(0.0),
                    OffsetLateral=None,
                    OffsetVertical=None,
                    OffsetLongitudinal=None,
                    BasisCurve=basis_curve,
                )
            )
        )
        update_fallback_position(file, lp)
        referent_nest.RelatedObjects[0].ObjectPlacement = lp
