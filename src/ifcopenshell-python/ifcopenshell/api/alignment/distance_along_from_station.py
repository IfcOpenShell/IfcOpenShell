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

from typing import Optional

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.util.element
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along


def distance_along_from_station(file: ifcopenshell.file, alignment: entity_instance, station: float) -> Optional[float]:
    """
    Given a station, returns the distance along the horizontal alignment.

    If the alignment does not have stationing defined with an IfcReferent, the start of the alignment is assumed
    to be at station 0.0. That is, the station is the distance along.

    Station equations (where Pset_Stationing.IncomingStation is set on a referent) and reverse
    (decreasing) stationing (where Pset_Stationing.HasIncreasingStation is False) are taken into account.

    For each STATION referent nested to the alignment, DistanceAlong (D) and the outgoing station (S, i.e.
    Pset_Stationing.Station) are read off and sorted by DistanceAlong. A direction sign is tracked while
    walking the sorted referents: it starts at +1 and is set to +1 or -1 at any referent that carries an
    explicit Pset_Stationing.HasIncreasingStation, so each referent's region has a sign sigma of +1
    (increasing) or -1 (decreasing). HasIncreasingStation may flip any number of times along the alignment -
    unrealistic, but valid IFC, and handled. The governing referent is the last one, by DistanceAlong, for
    which sigma * (station - S) >= 0, and the distance along is D + sigma * (station - S).

    If the station falls within a gap introduced by a station equation - that is, it was skipped over by the
    equation - there is no distance along that corresponds to it, and None is returned.

    Note that an overlap station equation - or a HasIncreasingStation direction reversal, which creates an
    equivalent overlap zone - causes a range of stations to correspond to two (or more) distinct distances
    along the alignment. This implementation returns the most downstream one (largest DistanceAlong), i.e.
    the match in the region following the last equation / reversal.

    :param alignment: the alignment
    :param station: station value
    :return: distance along the horizontal alignment, or None if the station falls inside a station equation gap

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0] # alignment with start station 1+00.00
        dist_along = ifcopenshell.api.alignment.distance_along_from_station(model,alignment=alignment,station=200.0)
        print(dist_along) # 100.00
    """

    stationing_nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    if stationing_nest is None:
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
        return station - start_station

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
    for distance_along, outgoing_station, has_increasing_station in referents:
        if has_increasing_station is not None:
            sigma = 1.0 if has_increasing_station else -1.0
        stations.append((distance_along, outgoing_station, sigma))

    index = None
    for i, (distance_along, outgoing_station, region_sign) in enumerate(stations):
        if region_sign * (station - outgoing_station) >= 0.0:
            index = i

    if index is None:
        # station precedes the alignment's starting station; extrapolate from the first referent
        distance_along, outgoing_station, region_sign = stations[0]
        return distance_along + region_sign * (station - outgoing_station)

    distance_along, outgoing_station, region_sign = stations[index]
    advance = region_sign * (station - outgoing_station)

    if index + 1 < len(stations):
        next_distance_along, _, _ = stations[index + 1]
        if advance > next_distance_along - distance_along:
            # the station was skipped over by a gap station equation
            return None

    return distance_along + advance
