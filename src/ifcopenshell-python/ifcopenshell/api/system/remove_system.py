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
    def __init__(self, file, system=None):
        """Removes a distribution system

        All the distribution elements within the system are retained.

        :param system: The IfcSystem to remove.
        :type system: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # A completely empty distribution system
            system = ifcopenshell.api.run("system.add_system", model)

            # Delete it.
            ifcopenshell.api.run("system.remove_system", model, system=system)
        """
        self.file = file
        self.settings = {"system": system}

    def execute(self):
        for rel in self.settings["system"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["system"])
