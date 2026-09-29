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
import ifcopenshell.api.nest
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._add_zero_length_segment import _add_zero_length_segment
from ifcopenshell.api.alignment._create_geometric_representation import (
    _create_geometric_representation,
)


def create(
    file: ifcopenshell.file,
    name: str,
    include_vertical: bool = False,
    include_cant: bool = False,
    include_geometry: bool = True,
) -> entity_instance:
    """
    Creates a new alignment with a horizontal layout. Optionally, vertical and cant layouts can be created as well.
    The geometric representations are created as well, unless they are explicitly excluded.
    Zero length segments are added at the end of the layouts and geometric representations.
    The alignment is automatically aggreated to the project if it exists.

    Use get_horizontal_layout(alignment), get_vertical_layout(alignment) and get_cant_layout(alignment) to get the
     corresponding IfcAlignmentHorizontal, IfcAlignmentVertical, and IfcAlignmentCant layout entities.

    If the alignment has Viennese Bend transition curves, create the segments in the cant layout before the horizontal layout using create_layout_segment().
    The horizontal geometry in the Viennese Bend transition curves depends on the Viennese Bend cant parameters. create_layout_segment() automatically creates
    the geometric representation from the semantic definition. The horizontal segment geometric representation will fail if the cant segment is not defined.

    This function does not define the alignment's stationing. Call add_stationing_referent() once the layout
    segments (and therefore the basis curve geometry) exist to place the starting-station IfcReferent, and again
    for any station equations. Until stationing is defined, get_alignment_start_station() reports 0.0.

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param include_vertical: If True, IfcAlignmentVertical is created. IfcGradientCurve is created if include_geometry is True
    :param include_cant: If True, IfcAlignmentCant is created. IfcSegmentedReferenceCurve is created if include_geometry is True
    :param include_geometry: If True, the geometric representations are added
    :return: Returns an IfcAlignment
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
        ObjectPlacement=file.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))
            ),
        ),
    )

    alignment_layouts = []

    alignment_layouts.append(file.createIfcAlignmentHorizontal(GlobalId=ifcopenshell.guid.new()))

    if include_vertical:
        alignment_layouts.append(file.createIfcAlignmentVertical(GlobalId=ifcopenshell.guid.new()))

    if include_cant:
        alignment_layouts.append(file.createIfcAlignmentCant(GlobalId=ifcopenshell.guid.new(), RailHeadDistance=1.0))

    ifcopenshell.api.nest.assign_object(file, related_objects=alignment_layouts, relating_object=alignment)

    if include_geometry:
        _create_geometric_representation(file, alignment)

    for layout in alignment_layouts:
        _add_zero_length_segment(file, layout)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
