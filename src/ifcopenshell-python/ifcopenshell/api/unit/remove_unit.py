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

import ifcopenshell.util.unit
import ifcopenshell.util.element


def remove_unit(file: ifcopenshell.file, unit: ifcopenshell.entity_instance) -> None:
    """Remove a unit

    Be very careful when a unit is removed, as it may mean that previously
    defined quantities in the model completely lose their meaning.

    :param unit: The unit element to remove
    :return: None

    Example:

    .. code:: python

        # What?
        unit = ifcopenshell.api.unit.add_context_dependent_unit(model, name="HANDFULS")

        # Yeah maybe not.
        ifcopenshell.api.unit.remove_unit(model, unit=unit)
    """
    unit_assignment = ifcopenshell.util.unit.get_unit_assignment(file)
    if unit_assignment and unit in unit_assignment.Units:
        units = list(unit_assignment.Units)
        units.remove(unit)
        if units:
            unit_assignment.Units = units
        else:
            file.remove(unit_assignment)
    ifcopenshell.util.element.remove_deep(file, unit)
