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
import ifcopenshell.util.element


def remove_pset(
    file: ifcopenshell.file, product: ifcopenshell.entity_instance, pset: ifcopenshell.entity_instance
) -> None:
    """Removes a property set from a product

    All properties that are part of this property set are also removed.

    :param product: The IfcObject to remove the property set from.
    :type product: ifcopenshell.entity_instance
    :param pset: The IfcPropertySet or IfcElementQuantity to remove.
    :type pset: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's imagine we have a new wall type with a property set.
        wall_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType")
        pset = ifcopenshell.api.pset.add_pset(model, product=wall_type, name="Pset_WallCommon")

        # Remove it!
        ifcopenshell.api.pset.remove_pset(model, product=wall_type, pset=pset)
    """
    settings = {"product": product, "pset": pset}

    to_purge = []
    should_remove_pset = True
    for inverse in file.get_inverse(settings["pset"]):
        if inverse.is_a("IfcRelDefinesByProperties"):
            if not inverse.RelatedObjects or len(inverse.RelatedObjects) == 1:
                to_purge.append(inverse)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["product"])
                inverse.RelatedObjects = related_objects
                should_remove_pset = False
    if should_remove_pset:
        properties = []  # Predefined psets have no properties
        if settings["pset"].is_a("IfcPropertySet"):
            properties = settings["pset"].HasProperties or []
        elif settings["pset"].is_a("IfcQuantitySet"):
            properties = settings["pset"].Quantities or []
        elif settings["pset"].is_a() in ("IfcMaterialProperties", "IfcProfileProperties"):
            properties = settings["pset"].Properties or []
        for prop in properties:
            if file.get_total_inverses(prop) != 1:
                continue
            if prop.is_a("IfcPropertyEnumeratedValue"):
                enumeration = prop.EnumerationReference
                if enumeration and file.get_total_inverses(enumeration) == 1:
                    file.remove(enumeration)
            file.remove(prop)
        # IfcMaterialProperties and IfcProfileProperties don't have OwnerHistory
        history = getattr(settings["pset"], "OwnerHistory", None)
        file.remove(settings["pset"])
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    for element in to_purge:
        history = getattr(element, "OwnerHistory", None)
        file.remove(element)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
