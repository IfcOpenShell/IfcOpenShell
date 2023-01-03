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
    def __init__(self, file, condition=None, attributes=None):
        """Edits the attributes of an IfcBoundaryCondition

        For more information about the attributes and data types of an
        IfcBoundaryCondition, consult the IFC documentation.

        :param condition: The IfcBoundaryCondition entity you want to edit
        :type condition: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"condition": condition, "attributes": attributes or {}}

    def execute(self):
        for name, data in self.settings["attributes"].items():
            if data["type"] == "string" or data["type"] == "null":
                value = data["value"]
            elif data["type"] == "IfcBoolean":
                value = self.file.createIfcBoolean(data["value"])
            else:
                value = self.file.create_entity(data["type"], data["value"])
            setattr(self.settings["condition"], name, value)
