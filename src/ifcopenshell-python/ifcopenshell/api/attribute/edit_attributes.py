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
from typing import Any, Union
from types import EllipsisType


def edit_attributes(file: ifcopenshell.file, product: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edit the attributes of a product

    All IFC entities have attributes. Normally they can be edited directly,
    by simply assigning a new value to them. In some scenarios, you may wish
    to also ensure that ownership history is updated. This function provides
    that convenience.

    The method will maintain consistency for PredefinedType attribute
    based on whether ElementType/ObjectType and whether occurrence is typed:

    - PredefinedType and ObjectType to be `None` if occurrence is typed
    - PredefinedType to be "NOTDEFINED" if ElementType/ObjectType is None
    - PredefinedType to be "USERDEFINED" if ElementType/ObjectType is not None

    :param product: The product you want to edit. This may be any rooted IFC
        entity.
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.attribute.edit_attributes(model,
            product=element, attributes={"Name": "Waldo"})
    """

    def getattr_safe(element: ifcopenshell.entity_instance, attr: str) -> Union[Any, EllipsisType]:
        """Return attribute value or Ellipsis if attribute doesn't exist.

        Useful as an alternative to hasattr - hasattr under the hood just does
        getattr but doesn't return a value. That helps reduce times IFC is accessed.
        """
        return getattr(element, attr, ...)

    for name, value in attributes.items():
        setattr(product, name, value)

    if (predefined_type := getattr_safe(product, "PredefinedType")) is not ...:
        if (element_type := getattr_safe(product, "ElementType")) is not ...:
            if element_type is None and predefined_type == "USERDEFINED":
                product.PredefinedType = "NOTDEFINED"
            elif element_type and predefined_type != "USERDEFINED":
                product.PredefinedType = "USERDEFINED"

        elif (object_type := getattr_safe(product, "ObjectType")) is not ...:
            relating_type = ifcopenshell.util.element.get_type(product)
            # Allow for None due to https://github.com/buildingSMART/IFC4.3.x-development/issues/818
            if relating_type and relating_type.PredefinedType not in ("NOTDEFINED", None):
                product.ObjectType = None
                product.PredefinedType = None
            elif object_type is None and predefined_type == "USERDEFINED":
                product.PredefinedType = "NOTDEFINED"
            elif object_type and predefined_type != "USERDEFINED":
                product.PredefinedType = "USERDEFINED"

    if hasattr(product, "OwnerHistory"):
        ifcopenshell.api.owner.update_owner_history(file, **{"element": product})
