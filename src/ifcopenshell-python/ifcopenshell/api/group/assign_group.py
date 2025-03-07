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
from typing import Union


def assign_group(
    file: ifcopenshell.file, products: list[ifcopenshell.entity_instance], group: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns products to a group

    If a product is already assigned to the group, it will not be assigned
    twice.

    :param products: A list of IfcProduct elements to assign to the group
    :param group: The IfcGroup to assign the products to
    :return: The IfcRelAssignsToGroup relationship
        or `None` if `products` was empty list.

    Example:

    .. code:: python

        group = ifcopenshell.api.group.add_group(model, name="Furniture")
        ifcopenshell.api.group.assign_group(model,
            products=model.by_type("IfcFurniture"), group=group)
    """
    if not products:
        return

    is_grouped_by: tuple[ifcopenshell.entity_instance, ...]
    if not (is_grouped_by := group.IsGroupedBy):
        return file.create_entity(
            "IfcRelAssignsToGroup",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": products,
                "RelatingGroup": group,
            },
        )
    rel = is_grouped_by[0]
    related_objects = set(rel.RelatedObjects) or set()
    products_set = set(products)
    if products_set.issubset(related_objects):
        return rel
    rel.RelatedObjects = list(related_objects | products_set)
    ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
    return rel
