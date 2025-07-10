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
import ifcopenshell.api.nest
import ifcopenshell.util.stationing

from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._create_geometric_representation import _create_geometric_representation
from ifcopenshell.api.alignment._add_zero_length_segment import _add_zero_length_segment


def create(
    file: ifcopenshell.file,
    name: str,
    include_vertical: bool = False,
    include_cant: bool = False,
    start_station: float = 0.0,
) -> entity_instance:
    """
    Creates a new IfcAlignment with an IfcRelNests nesting an IfcReferent (for stationing) and IfcAlignmentHorizontal. The nest relationship can optionally
    include IfcAlignmentVertical and IfcAlignmentCant. Geometric representations for the alignment layouts (IfcCompositeCurve,
    IfcGradientCurve, IfcSegmentedReferenceCurve) are created as well.

    Zero length segments are added at the end.

    The IfcAlignment is aggreated to IfcProject

    Use get_horizontal_layout(alignment) to get the IfcAlignmentHorizontal layout.

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param include_vertical: If True, IfcAlignmentVertical and IfcGradientCurve are created
    :param include_cant: If True, IfcAlignmentCant and IfcSegmentedReferenceCurve are created
    :param start_station: station value at the start of the alignment
    :return: Returns an IfcAlignment
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )

    alignment_layouts = []

    alignment_layouts.append(file.createIfcAlignmentHorizontal(GlobalId=ifcopenshell.guid.new()))

    if include_vertical:
        alignment_layouts.append(file.createIfcAlignmentVertical(GlobalId=ifcopenshell.guid.new()))

    if include_cant:
        alignment_layouts.append(file.createIfcAlignmentCant(GlobalId=ifcopenshell.guid.new(), RailHeadDistance=1.0))

    ifcopenshell.api.nest.assign_object(file, related_objects=alignment_layouts, relating_object=alignment)

    _create_geometric_representation(file, alignment)

    for layout in alignment_layouts:
        _add_zero_length_segment(file, layout)

    # define stationing
    basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    name = ifcopenshell.util.stationing.station_as_string(file, start_station)
    referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, alignment, basis_curve, 0.0, start_station, name
    )
    ifcopenshell.api.nest.reorder_nesting(file, referent, -1, 0)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
