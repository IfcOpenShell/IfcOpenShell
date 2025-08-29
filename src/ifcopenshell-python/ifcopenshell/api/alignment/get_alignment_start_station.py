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


def get_alignment_start_station(file: ifcopenshell.file, alignment: entity_instance) -> float:
    """
    Returns the start station of the alignment. The starting station is defined by the first nested IfcReferent.
    This is interpreted to mean the first IfcReferent with an occurance of Pset_Stationing.Station,
    otherwise returns 0.0.
    """

    if not alignment.is_a("IfcAlignment"):
        raise TypeError(f"Expected entity type to be IfcAlignment, instead received {alignment.is_a()}")

    start_station = 0.0

    parent_alignment = ifcopenshell.api.alignment.get_parent_alignment(alignment)
    if parent_alignment:
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, parent_alignment)
    else:
        components = ifcopenshell.util.element.get_components(alignment)
        for c in components:
            if c.is_a("IfcReferent"):
                start_station = ifcopenshell.util.element.get_pset(c, name="Pset_Stationing", prop="Station")
                if not start_station == None:
                    break

    return start_station
