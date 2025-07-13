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

from ifcopenshell.api.alignment._create_polyline_representation import _create_polyline_representation
from ifcopenshell.api.alignment._add_zero_length_segment import _add_zero_length_segment
from collections.abc import Sequence


def create_as_polyline(
    file: ifcopenshell.file,
    name: str,
    points: Sequence[entity_instance],
    start_station: float = 0.0,
) -> entity_instance:
    """
    Creates a new IfcAlignment with an IfcPolyline representation.

    The IfcAlignment is aggreated to IfcProject

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param points: sequence of points defining the polyline
    :param start_station: station value at the start of the alignment
    :return: Returns an IfcAlignment
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )

    _create_polyline_representation(file, alignment, points)

    # define stationing
    name = ifcopenshell.util.stationing.station_as_string(file, start_station)
    referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, alignment, 0.0, start_station, name
    )
    ifcopenshell.api.nest.reorder_nesting(file, referent, -1, 0)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment