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
    def __init__(self, file, physical_quantity=None, attributes=None):
        """Edits the attributes of an IFC quantity

        For more information about the attributes and data types of an
        IfC quantity, consult the IFC documentation.

        :param physical_quantity: The IfC quantity entity you want to edit
        :type physical_quantity: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Add some labour to our crew.
            labour = ifcopenshell.api.run("resource.add_resource", model,
                parent_resource=crew, ifc_class="IfcLaborResource")

            # Labour resource is quantified in terms of time.
            ifcopenshell.api.run("resource.add_resource_quantity", model,
                resource=labour, ifc_class="IfcQuantityTime")

            # Store the time used in hours
            ifcopenshell.api.run("resource.edit_resource_quantity", model,
                physical_quantity=time, attributes={"TimeValue": 8.0})
        """
        self.file = file
        self.settings = {"physical_quantity": physical_quantity, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["physical_quantity"], name, value)
