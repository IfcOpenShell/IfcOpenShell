# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type


def remove_products(file: ifcopenshell.file, products: list[ifcopenshell.entity_instance]) -> None:
    """Removes a list of products

    Equivalent to calling :func:`remove_product` on each product, but the
    containment, type and material relationships shared by many of the products
    are rewritten once instead of once per product, so the cost grows linearly
    with the number of products.

    :param products: The elements to remove.
    :return: None

    Example:

    .. code:: python

        walls = [ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall") for _ in range(100)]
        ifcopenshell.api.root.remove_products(model, products=walls)
    """
    products = list(products)
    ifcopenshell.api.spatial.unassign_container(
        file, products=[p for p in products if hasattr(p, "ContainedInStructure")]
    )
    ifcopenshell.api.type.unassign_type(file, related_objects=[p for p in products if p.is_a("IfcObject")])
    ifcopenshell.api.material.unassign_material(file, products=products)
    for product in products:
        ifcopenshell.api.root.remove_product(file, product=product)
