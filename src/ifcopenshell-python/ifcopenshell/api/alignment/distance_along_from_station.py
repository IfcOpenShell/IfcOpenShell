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


def _distance_along_of_referent(referent: entity_instance) -> float:
    placement = referent.ObjectPlacement
    if placement.is_a("IfcLinearPlacement"):
        return placement.RelativePlacement.Location.DistanceAlong.wrappedValue
    # IfcLocalPlacement fallback (e.g. semantic-only alignment, or the placement could not yet
    # be expressed relative to a basis curve) carries no DistanceAlong; it is only ever used for
    # the starting referent, at distance 0.0.
    return 0.0


def distance_along_from_station(file: ifcopenshell.file, alignment: entity_instance, station: float) -> Optional[float]:
    """
    Given a station, returns the distance along the horizontal alignment.

    If the alignment does not have stationing defined with an IfcReferent, the start of the alignment is assumed
    to be at station 0.0. That is, the station is the distance along.

    Station equations (where Pset_Stationing.IncomingStation is set on a referent) are taken into account.
    For each STATION referent nested to the alignment, DistanceAlong (D) and the outgoing station (S, i.e.
    Pset_Stationing.Station) are read off, sorted by DistanceAlong. The requested station is located within
    the segment defined by the last referent whose outgoing station is less than or equal to it, and the
    distance along is computed as D + (station - S) for that referent.

    If the station falls within a gap introduced by a forward (gap) station equation - that is, it was skipped
    over by the equation - there is no distance along that corresponds to it, and None is returned.

    Note that an overlap (backward) station equation causes a range of stations to correspond to two distinct
    distances along the alignment, one on either side of the equation. This implementation returns the distance
    along in the segment following the equation (i.e. the outgoing side).

    :param alignment: the alignment
    :param station: station value
    :return: distance along the horizontal alignment, or None if the station falls inside a station equation gap

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0] # alignment with start station 1+00.00
        dist_along = ifcopenshell.api.alignment.distance_along_from_station(model,alignment=alignment,station=200.0)
        print(dist_along) # 100.00
    """

    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    if referent_nest is None:
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
        return station - start_station

    stations = [
        (
            _distance_along_of_referent(referent),
            ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station"),
        )
        for referent in referent_nest.RelatedObjects
    ]
    stations.sort(key=lambda entry: entry[0])

    index = None
    for i, (distance_along, outgoing_station) in enumerate(stations):
        if outgoing_station <= station:
            index = i

    if index is None:
        # station precedes the alignment's starting station; extrapolate from the first referent
        distance_along, outgoing_station = stations[0]
        return distance_along + (station - outgoing_station)

    distance_along, outgoing_station = stations[index]

    if index + 1 < len(stations):
        next_distance_along, _ = stations[index + 1]
        if station - outgoing_station > next_distance_along - distance_along:
            # the station was skipped over by a forward (gap) station equation
            return None

    return distance_along + (station - outgoing_station)
