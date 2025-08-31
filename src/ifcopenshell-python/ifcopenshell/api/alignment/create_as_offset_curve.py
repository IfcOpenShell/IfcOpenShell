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
import ifcopenshell.util.alignment

from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._create_offset_curve_representation import _create_offset_curve_representation

from collections.abc import Sequence


def create_as_offset_curve(
    file: ifcopenshell.file,
    name: str,
    offsets: Sequence[entity_instance],
    start_station: float = 0.0,
) -> entity_instance:
    """
    Creates a new IfcAlignment with an IfcOffsetCurveByDistances representation.

    The IfcAlignment is aggreated to IfcProject

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param offsets: offsets from the basis curve that defines the offset curve, expected to be IfcOffsetCurveByDistances.
    :param start_station: station value at the start of the alignment
    :return: Returns an IfcAlignment
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )

    _create_offset_curve_representation(file, alignment, offsets)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
