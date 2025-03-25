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
import ifcopenshell.api.nest
import ifcopenshell.guid
from ifcopenshell import entity_instance


def distance_along_from_station(file: ifcopenshell.file, alignment: entity_instance, station: float) -> float:
    """
    Given a station, returns the distance along the horizontal alignment.

    If the alignment does not have stationing defined with an IfcReferent, the start of the alignment is assumed
    to be at station 0.0. That is, the station is the distance along.

    .. note:: The current implementation does not account for station equations and assumes stationing is increasing along the alignment.

    :param alignment: the alignment
    :param station: station value
    :return: distance along the horizontal alignment

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0] # alignment with start station 1+00.00
        dist_along = ifcopenshell.api.alignment.distance_along_from_station(model,alignment=alignment,station=200.0)
        print(dist_along) # 100.00
    """

    start_station = 0.0
    components = ifcopenshell.util.element.get_components(alignment)
    for c in components:
        if c.is_a("IfcReferent") and ifcopenshell.util.element.get_predefined_type(c) == "STATION":
            start_station = ifcopenshell.util.element.get_pset(c, name="Pset_Stationing", prop="Station")
            break

    dist_along = station - start_station
    return dist_along
