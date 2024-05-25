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
import ifcopenshell.util.element


def unassign_group(
    file: ifcopenshell.file, products: list[ifcopenshell.entity_instance], group: ifcopenshell.entity_instance
) -> None:
    """Unassigns products from a group

    If the product isn't assigned to the group, nothing will happen.

    :param products: A list of IfcProduct elements to unassign from the group
    :type products: list[ifcopenshell.entity_instance]
    :param group: The IfcGroup to unassign from
    :type group: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        group = ifcopenshell.api.run("group.add_group", model, name="Furniture")
        furniture = model.by_type("IfcFurniture")
        ifcopenshell.api.run("group.assign_group", model, products=furniture, group=group)

        bad_furniture = furniture[0]
        ifcopenshell.api.run("group.unassign_group", model, products=[bad_furniture], group=group)
    """
    settings = {
        "products": products,
        "group": group,
    }

    if not settings["group"].IsGroupedBy:
        return
    rel = settings["group"].IsGroupedBy[0]
    related_objects = set(rel.RelatedObjects) or set()
    products = set(settings["products"])
    related_objects -= products
    if related_objects:
        rel.RelatedObjects = list(related_objects)
        ifcopenshell.api.run("owner.update_owner_history", file, **{"element": rel})
    else:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
