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

from collections.abc import Sequence

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.util.alignment
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._create_offset_curve_representation import (
    _create_offset_curve_representation,
)


def create_as_offset_curve(
    file: ifcopenshell.file,
    name: str,
    offsets: Sequence[entity_instance],
    start_station: float = 0.0,
) -> entity_instance:
    """
    Creates a new IfcAlignment with an IfcOffsetCurveByDistances representation.

    The IfcAlignment is aggregated to IfcProject

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param offsets: offsets from the basis curve that defines the offset curve, expected to be IfcPointByDistanceExpression.
        Use the parent alignment's IfcGradientCurve as the BasisCurve for a 3D offset curve (one that follows
        the parent's profile), or its IfcCompositeCurve for a 2D one.
    :param start_station: station value at the start of the alignment
    :return: Returns an IfcAlignment

    Example:

    .. code:: python

        # A curb line 3.6 left of an existing centerline, widening to 5.4 at distance along 500
        centerline = model.by_type("IfcAlignment")[0]
        basis_curve = ifcopenshell.api.alignment.get_curve(centerline)  # the centerline's IfcGradientCurve
        offsets = [
            model.createIfcPointByDistanceExpression(
                DistanceAlong=model.createIfcLengthMeasure(distance_along), OffsetLateral=offset, BasisCurve=basis_curve
            )
            for distance_along, offset in [(0.0, 3.6), (500.0, 5.4), (1500.0, 5.4)]
        ]
        curb = ifcopenshell.api.alignment.create_as_offset_curve(model, "Left Curb", offsets, start_station=0.0)
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )

    _create_offset_curve_representation(file, alignment, offsets)

    # establish the alignment's stationing scheme, same as create() does for start_station
    referent_name = ifcopenshell.util.alignment.station_as_string(file, start_station)
    ifcopenshell.api.alignment.add_stationing_referent(file, referent_name, alignment, 0.0, start_station)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
