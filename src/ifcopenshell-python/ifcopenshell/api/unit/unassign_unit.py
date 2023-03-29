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


class Usecase:
    def __init__(self, file, units=None):
        """Unassigns units as default units for the project

        :param units: A list of units to assign as project defaults.
        :type units: list[ifcopenshell.entity_instance.entity_instance],optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # You need a project before you can assign units.
            ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")

            # Millimeters and square meters
            length = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="LENGTHUNIT", prefix="MILLI")
            area = ifcopenshell.api.run("unit.add_si_unit", model, unit_type="AREAUNIT")

            # Make it our default units, if we are doing a metric building
            ifcopenshell.api.run("unit.assign_unit", model, units=[length, area])

            # Actually, we don't need areas.
            ifcopenshell.api.run("unit.unassign_unit", model, units=[area])
        """
        self.file = file
        self.settings = {"units": units}

    def execute(self):
        unit_assignment = self.file.by_type("IfcUnitAssignment")
        if not unit_assignment:
            return
        unit_assignment = unit_assignment[0]
        units = set(unit_assignment.Units or [])
        units = units - set(self.settings["units"])
        if units:
            unit_assignment.Units = list(units)
            return unit_assignment
        self.file.remove(unit_assignment)
