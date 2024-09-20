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
import ifcopenshell.api.owner
import ifcopenshell.api.pset
import ifcopenshell.guid
import ifcopenshell.util.element


def unshare_pset(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    pset: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance]:
    """Copy a shared pset as linked only to the provided elements.

    Note that method will create a copy of the pset for each element provided.

    :param products: Elements (or element types) to link the pset to.
    :param pset: Shared property set.
    :return: List of copied property sets.

    Example:

    .. code:: python

        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.pset.assign_pset(self.file, [element1, element2], pset)

        # Pset is now shared by 2 elements.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element1, element2}

        new_psets = ifcopenshell.api.pset.unshare_pset(self.file, [element2], pset)

        # element2 was unassigned from the original pset.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element1}
        new_pset = new_psets[0]

        # New pset was created and was assigned to element2.
        assert new_pset != pset
        assert ifcopenshell.util.element.get_elements_by_pset(new_pset) == {element2}
    """

    if not products:
        raise Exception("No products provided.")

    # If pset has no other elements besides the provided products,
    # then we skip the first product, so it won't get additional pset copy
    # leaving the original pset orphaned.
    pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
    products_original = products

    if set(products) == pset_elements:
        products = products[1:]

    if not products:
        raise Exception(f"Provided product is the only element to which pset is assigned: {products_original[0]}.")

    products_occurrences: set[ifcopenshell.entity_instance] = set()
    products_types: set[ifcopenshell.entity_instance] = set()
    for product in products:
        if product.is_a("IfcTypeProduct"):
            products_types.add(product)
        else:
            products_occurrences.add(product)

    ifcopenshell.api.pset.unassign_pset(file, products, pset)

    pset_copies: list[ifcopenshell.entity_instance] = []
    for product in products:
        # No need to consider about profile/material properties since
        # they are assigned to 1 element directly and therefore cannot be shared.
        # Don't copy_deep to keep it light - edit_pset supports unsharing shared props.
        pset_copy = ifcopenshell.util.element.copy(file, pset)
        pset_copies.append(pset_copy)
        ifcopenshell.api.pset.assign_pset(file, [product], pset_copy)

    return pset_copies
