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

import ifcopenshell.api.owner
import ifcopenshell.util.element
from typing import Any


def edit_attributes(file: ifcopenshell.file, product: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edit the attributes of a product

    All IFC entities have attributes. Normally they can be edited directly,
    by simply assigning a new value to them. In some scenarios, you may wish
    to also ensure that ownership history is updated. This function provides
    that convenience.

    :param product: The product you want to edit. This may be any rooted IFC
        entity.
    :type product: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.attribute.edit_attributes(model,
            product=element, attributes={"Name": "Waldo"})
    """
    settings = {"product": product, "attributes": attributes or {}}

    for name, value in settings["attributes"].items():
        setattr(settings["product"], name, value)
    if hasattr(settings["product"], "PredefinedType"):
        if hasattr(settings["product"], "ElementType"):
            if settings["product"].ElementType is None and settings["product"].PredefinedType == "USERDEFINED":
                settings["product"].PredefinedType = "NOTDEFINED"
            elif settings["product"].ElementType and settings["product"].PredefinedType != "USERDEFINED":
                settings["product"].PredefinedType = "USERDEFINED"
        elif hasattr(settings["product"], "ObjectType"):
            relating_type = ifcopenshell.util.element.get_type(settings["product"])
            # Allow for None due to https://github.com/buildingSMART/IFC4.3.x-development/issues/818
            if relating_type and relating_type.PredefinedType not in ("NOTDEFINED", None):
                settings["product"].ObjectType = None
                settings["product"].PredefinedType = None
            elif settings["product"].ObjectType is None and settings["product"].PredefinedType == "USERDEFINED":
                settings["product"].PredefinedType = "NOTDEFINED"
            elif settings["product"].ObjectType and settings["product"].PredefinedType != "USERDEFINED":
                settings["product"].PredefinedType = "USERDEFINED"
    if hasattr(settings["product"], "OwnerHistory"):
        ifcopenshell.api.owner.update_owner_history(file, **{"element": settings["product"]})
