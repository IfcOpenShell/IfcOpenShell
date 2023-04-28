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
    def __init__(self, file, element=None, attributes=None):
        """Edits the attributes of an IfcMaterial

        For more information about the attributes and data types of an
        IfcMaterial, consult the IFC documentation.

        :param element: The IfcMaterial entity you want to edit
        :type element: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")
            ifcopenshell.api.run("material.edit_assigned_material", model,
                element=concrete, attributes={"Description": "40MPA concrete with broom finish"})
        """
        self.file = file
        self.settings = {"element": element, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["element"], name, value)
