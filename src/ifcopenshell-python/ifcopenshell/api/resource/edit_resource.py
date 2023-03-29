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
    def __init__(self, file, resource=None, attributes=None):
        """Edits the attributes of an IfcResource

        For more information about the attributes and data types of an
        IfcResource, consult the IFC documentation.

        :param resource: The IfcResource entity you want to edit
        :type resource: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Change the name of the resource to "Zone A Crew"
            ifcopenshell.api.run("resource.edit_resource", model, resource=resource, attributes={"Name": "Foo"})
        """
        self.file = file
        self.settings = {"resource": resource, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["resource"], name, value)
