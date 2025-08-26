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
import ifcopenshell.util.element


def unassign_group(
    file: ifcopenshell.file, products: list[ifcopenshell.entity_instance], group: ifcopenshell.entity_instance
) -> None:
    """Unassigns products from a group

    If the product isn't assigned to the group, nothing will happen.

    :param products: A list of IfcProduct elements to unassign from the group
    :param group: The IfcGroup to unassign from
    :return: None

    Example:

    .. code:: python

        group = ifcopenshell.api.group.add_group(model, name="Furniture")
        furniture = model.by_type("IfcFurniture")
        ifcopenshell.api.group.assign_group(model, products=furniture, group=group)

        bad_furniture = furniture[0]
        ifcopenshell.api.group.unassign_group(model, products=[bad_furniture], group=group)
    """
    if not group.IsGroupedBy:
        return
    rel = group.IsGroupedBy[0]
    related_objects = set(rel.RelatedObjects) or set()
    products_set = set(products)
    related_objects -= products_set
    if related_objects:
        rel.RelatedObjects = list(related_objects)
        ifcopenshell.api.owner.update_owner_history(file, element=rel)
    else:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
