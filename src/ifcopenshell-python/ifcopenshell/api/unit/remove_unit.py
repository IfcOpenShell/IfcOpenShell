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


class Usecase:
    def __init__(self, file, unit=None):
        """Remove a unit

        Be very careful when a unit is removed, as it may mean that previously
        defined quantities in the model completely lose their meaning.

        :param unit: The unit element to remove
        :type unit: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # What?
            unit = ifcopenshell.api.run("unit.add_context_dependent_unit", model, name="HANDFULS")

            # Yeah maybe not.
            ifcopenshell.api.run("unit.remove_unit", model, unit=unit)
        """
        self.file = file
        self.settings = {"unit": unit}

    def execute(self):
        unit_assignment = ifcopenshell.util.unit.get_unit_assignment(self.file)
        if unit_assignment and self.settings["unit"] in unit_assignment.Units:
            units = list(unit_assignment.Units)
            units.remove(self.settings["unit"])
            if units:
                unit_assignment.Units = units
            else:
                self.file.remove(unit_assignment)
        ifcopenshell.util.element.remove_deep(self.file, self.settings["unit"])
