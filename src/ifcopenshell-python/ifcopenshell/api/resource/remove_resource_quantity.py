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


def remove_resource_quantity(file: ifcopenshell.file, resource: ifcopenshell.entity_instance) -> None:
    """Removes the base quantity of a resource

    :param resource: The IfcConstructionResource to remove the quantity from.
    :return: None

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Add some labour to our crew.
        labour = ifcopenshell.api.resource.add_resource(model,
            parent_resource=crew, ifc_class="IfcLaborResource")

        # Labour resource is quantified in terms of time.
        ifcopenshell.api.resource.add_resource_quantity(model,
            resource=labour, ifc_class="IfcQuantityTime")

        # Let's say we only want to store the resource but no quantities,
        # let's clean up our mess and remove the quantity.
        ifcopenshell.api.resource.remove_resource_quantity(model, resource=labour)
    """
    old_quantity = resource.BaseQuantity
    resource.BaseQuantity = None
    if old_quantity:
        ifcopenshell.util.element.remove_deep(file, old_quantity)
