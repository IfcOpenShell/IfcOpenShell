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

from ifcopenshell import entity_instance


def _referent_distance_along(referent: entity_instance) -> float:
    """The distance along the basis curve at which a referent is placed.

    Read from IfcLinearPlacement.RelativePlacement.Location.DistanceAlong. An
    IfcLocalPlacement fallback (semantic-only alignment, or a placement that could not
    yet be expressed relative to a basis curve) carries no DistanceAlong; it is only ever
    used for the starting referent, at distance 0.0 (the global origin).

    Referents nested under an alignment are ordered by increasing DistanceAlong (IFC CT
    4.1.4.4.3), which - for a reverse-stationed alignment - means by decreasing Station.
    Sort on this, never on Pset_Stationing.Station.
    """
    placement = referent.ObjectPlacement
    if placement and placement.is_a("IfcLinearPlacement"):
        return placement.RelativePlacement.Location.DistanceAlong.wrappedValue
    return 0.0
