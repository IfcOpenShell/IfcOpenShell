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
import ifcopenshell.guid
import ifcopenshell.util.element


def unassign_pset(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    pset: ifcopenshell.entity_instance,
) -> None:
    """Unassign property set from the provided elements.

    :param products: Elements (or element types) to assign the pset from.
    :param pset: Property set.

    Example:

    .. code:: python

        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.pset.assign_pset(self.file, [element1, element2], pset)

        # Pset is now shared by 2 elements.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element1, element2}

        ifcopenshell.api.pset.unassign_pset(self.file, [element2], pset)
        # Pset was unassigned from element2.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element1}

    """
    is_ifc2x3 = file.schema == "IFC2X3"

    products_occurrences: set[ifcopenshell.entity_instance] = set()
    products_types: set[ifcopenshell.entity_instance] = set()
    for product in products:
        if product.is_a("IfcTypeProduct"):
            products_types.add(product)
        else:
            products_occurrences.add(product)

    # Check occurrences using pset.
    if products_occurrences:
        rels = pset.PropertyDefinitionOf if is_ifc2x3 else pset.DefinesOccurrence
        for rel in rels:
            objs = set(rel.RelatedObjects)
            if not any(p in objs for p in products_occurrences):
                continue
            objs.difference_update(products_occurrences)
            if objs:
                rel.RelatedObjects = list(objs)
            else:
                history = rel.OwnerHistory
                file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)

    for product in products_types:
        psets = list(product.HasPropertySets)
        psets.remove(pset)
        product.HasPropertySets = psets or None
