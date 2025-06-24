# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
from typing import Optional


def unassign_unit(file: ifcopenshell.file, units: Optional[list[ifcopenshell.entity_instance]] = None) -> None:
    """Unassigns units as default units for the project

    :param units: A list of units to unassign as project defaults.
    :return: None

    Example:

    .. code:: python

        # You need a project before you can assign units.
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")

        # Millimeters and square meters
        length = ifcopenshell.api.unit.add_si_unit(model, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(model, unit_type="AREAUNIT")

        # Make it our default units, if we are doing a metric building
        ifcopenshell.api.unit.assign_unit(model, units=[length, area])

        # Actually, we don't need areas.
        ifcopenshell.api.unit.unassign_unit(model, units=[area])
    """
    unit_assignments = file.by_type("IfcUnitAssignment")
    if not unit_assignments:
        return
    unit_assignment = unit_assignments[0]
    units_set = set(unit_assignment.Units or [])
    units_set = units_set - set(units or [])
    if units_set:
        unit_assignment.Units = list(units_set)
        return
    file.remove(unit_assignment)
