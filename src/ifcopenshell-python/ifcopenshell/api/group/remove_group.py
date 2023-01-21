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
    def __init__(self, file, group=None):
        """Removes a group

        All products assigned to the group will remain, but the relationship to
        the group will be removed.

        :param group: The IfcGroup entity you want to remove
        :type group: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            group = ifcopenshell.api.run("group.add_group", model, Name="Unit 1A")
            ifcopenshell.api.run("group.remove_group", model, group=group)
        """
        self.file = file
        self.settings = {"group": group}

    def execute(self):
        for rel in self.settings["group"].IsGroupedBy or []:
            self.file.remove(rel)
        self.file.remove(self.settings["group"])
