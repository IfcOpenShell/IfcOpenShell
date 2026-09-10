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
import ifcopenshell.util.element
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along


def station_from_distance_along(file: ifcopenshell.file, alignment: entity_instance, dist_along: float) -> float:
    """
    Given a distance along a horizontal alignment, returns the corresponding station value.

    This is the inverse of distance_along_from_station(). Every distance along the alignment maps
    to exactly one station, so this function always returns a float (never None).

    If the alignment does not have stationing defined with an IfcReferent, the start of the
    alignment is taken from get_alignment_start_station() (or 0.0 if none is defined), and the
    station is simply start_station + dist_along.

    Station equations (where Pset_Stationing.IncomingStation is set on a referent) and reverse
    (decreasing) stationing (where Pset_Stationing.HasIncreasingStation is False) are taken into
    account using the same referent walk as distance_along_from_station():

    For each STATION referent nested to the alignment, DistanceAlong (D) and the outgoing station
    (S, i.e. Pset_Stationing.Station) are read off and sorted by DistanceAlong. A direction sign
    is tracked while walking the sorted referents: it starts at +1 and is set to +1 or -1 at any
    referent that carries an explicit Pset_Stationing.HasIncreasingStation. The governing referent
    is the last one whose DistanceAlong does not exceed dist_along, and the station is:

        station = S + sigma * (dist_along - D)

    If dist_along precedes the first referent's DistanceAlong, the station is extrapolated
    backward from the first referent using the same formula.

    :param file: the IFC file
    :param alignment: the alignment entity
    :param dist_along: distance along the horizontal alignment
    :return: the station value at the given distance along

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]  # alignment with start station 1+00.00
        station = ifcopenshell.api.alignment.station_from_distance_along(model, alignment, 200.0)
        print(station)  # 300.0  (100 + 200)
    """
    stationing_nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    if stationing_nest is None:
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment) or 0.0
        return float(start_station) + dist_along

    referents = [
        (
            _referent_distance_along(referent),
            ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station"),
            ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="HasIncreasingStation"),
        )
        for referent in stationing_nest.RelatedObjects
    ]
    referents.sort(key=lambda entry: entry[0])

    # Assign each referent's region a direction sign: +1 increasing, -1 decreasing. The sign
    # starts increasing and flips at any referent carrying an explicit HasIncreasingStation.
    sigma = 1.0
    stations = []
    for distance_along_ref, outgoing_station, has_increasing_station in referents:
        if has_increasing_station is not None:
            sigma = 1.0 if has_increasing_station else -1.0
        if outgoing_station is not None:
            stations.append((distance_along_ref, float(outgoing_station), sigma))

    if not stations:
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment) or 0.0
        return float(start_station) + dist_along

    # Find governing referent: the last one whose DistanceAlong does not exceed dist_along.
    # If dist_along precedes the first referent, extrapolate backward from it.
    governing = stations[0]
    for entry in stations:
        if entry[0] <= dist_along + 1e-9:
            governing = entry

    ref_dist, ref_station, ref_sigma = governing
    return ref_station + ref_sigma * (dist_along - ref_dist)
