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


def create_alignment_by_pi_method(
    file: ifcopenshell.file,
    alignment_name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[float],
    vpoints: Sequence[Sequence[float]] = None,
    lengths: Sequence[float] = None,
    alignment_description: str = None,
) -> entity_instance:
    """
    Create an alignment using the PI layout method for both horizontal and vertical alignments.
    If vpoints and lengths are omitted, only a horizontal alignment is created. Only the business logic
    entities are creaed. Use create_geometric_representation() to create the geometric entities.

    :param alignment_name: value for Name attribute
    :param points: (X,Y) pairs denoting the location of the horizontal PIs, including start and end
    :param radii: radii values to use for transition
    :param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    :param lengths: parabolic vertical curve horizontal length values to use for transition
    :param alignment_description: value for Description attribute
    :return: Returns an IfcAlignment
    """
    alignments = []

    horizontal_alignment = ifcopenshell.api.alignment.create_horizontal_alignment_by_pi_method(
        file, alignment_name, hpoints, radii
    )
    alignments.append(horizontal_alignment)

    if vpoints and lengths:
        vertical_alignment = ifcopenshell.api.alignment.create_vertical_alignment_by_pi_method(
            file, alignment_name, vpoints, lengths
        )
        alignments.append(vertical_alignment)

    # create the alignment
    alignment = file.create_entity(
        type="IfcAlignment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=alignment_name,
        Description=alignment_description,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        PredefinedType=None,
    )

    # nest the horizontal and vertical under the alignment
    ifcopenshell.api.nest.assign_object(file, related_objects=alignments, relating_object=alignment)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
