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

import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, resource=None, ifc_class="IfcQuantityCount"):
        """Adds a quantity to a resource

        The quantity of a resource represents the "unit quantity" of that
        resource. For example, labour might be hired on a daily basis (8 hours).
        There are different types of quantities (e.g. volume, count, or time).
        Which quantity is used depends on the type of resource.  Material
        resources may be quantified in terms of length, area, volume, or weight.
        Equipment and labour resources are quantified in terms of time. Products
        resources are quantified in terms of counts.

        This base quantity is then used in other calculations.

        :param resource: The IfcConstructionResource to add a quantity to.
        :type resource: ifcopenshell.entity_instance.entity_instance
        :param ifc_class: The type of quantity to add, chosen from
            IfcQuantityArea (for material), IfcQuantityCount (for products),
            IfcQuantityLength (for material), IfcQuantityTime (for equipment or
            labour), IfcQuantityVolume (for material), and IfcQuantityWeight
            (for material).
        :type ifc_class: str,optional
        :return: The newly created quantity depending on the IFC class
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Add some labour to our crew.
            labour = ifcopenshell.api.run("resource.add_resource", model,
                parent_resource=crew, ifc_class="IfcLaborResource")

            # Labour resource is quantified in terms of time.
            quantity = ifcopenshell.api.run("resource.add_resource_quantity", model,
                resource=labour, ifc_class="IfcQuantityTime")

            # Store the time used in hours
            ifcopenshell.api.run("resource.edit_resource_quantity", model,
                physical_quantity=quantity, attributes={"TimeValue": 8.0})
        """
        self.file = file
        self.settings = {"resource": resource, "ifc_class": ifc_class}

    def execute(self):
        quantity = self.file.create_entity(self.settings["ifc_class"], Name="Unnamed")
        quantity[3] = 0.0
        old_quantity = self.settings["resource"].BaseQuantity
        self.settings["resource"].BaseQuantity = quantity
        if old_quantity:
            ifcopenshell.util.element.remove_deep(self.file, old_quantity)
        return quantity
