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

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.system


def assign_system(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    system: ifcopenshell.entity_instance,
) -> None:
    """Assigns distribution elements to a system

    Note that it is not necessary to assign distribution ports to a system.

    :param products: The list of IfcDistributionElements to assign to the system.
    :type products: list[ifcopenshell.entity_instance]
    :param system: The IfcSystem you want to assign the element to.
    :type system: ifcopenshell.entity_instance
    :return: The IfcRelAssignsToGroup relationship
        or `None` if `products` was empty list.
    :rtype: [ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        # A completely empty distribution system
        system = ifcopenshell.api.run("system.add_system", model)

        # Create a duct
        duct = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")

        # This duct is part of the system
        ifcopenshell.api.run("system.assign_system", model, products=[duct], system=system)
    """
    settings = {
        "products": products,
        "system": system,
    }

    system = settings["system"]
    products = settings["products"]

    if not all(ifcopenshell.util.system.is_assignable(failed_product := product, system) for product in products):
        raise TypeError(f"You cannot assign an {failed_product.is_a()} to an {system.is_a()}")

    rel = ifcopenshell.api.run("group.assign_group", file, products=products, group=system)
    return rel
