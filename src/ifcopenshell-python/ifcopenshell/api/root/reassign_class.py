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
import ifcopenshell.util.type
import ifcopenshell.util.schema
import ifcopenshell.util.element
from typing import Optional


def reassign_class(
    file: ifcopenshell.file,
    product: ifcopenshell.entity_instance,
    ifc_class: str = "IfcBuildingElementProxy",
    predefined_type: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    """Changes the class of a product

    If you ever created a wall then realised it's meant to be something
    else, this function lets you change the IFC class whilst retaining all
    other geometry and relationships.

    This is especially useful when dealing with poorly classified data from
    proprietary software with limited IFC capabilities.

    If you are reassigning a type, the occurrence classes are also
    reassigned to maintain validity.

    Vice versa, if you are reassigning an occurrence, the type is also
    reassigned in IFC4 and up. In IFC2X3, this may not occur if the type
    cannot be unambiguously derived, so you are required to manually check
    this.

    :param product: The IfcProduct that you want to change the class of.
    :type product: ifcopenshell.entity_instance
    :param ifc_class: The new IFC class you want to change it to.
    :type ifc_class: str,optional
    :param predefined_type: In case you want to change the predefined type
        too. User defined types are also allowed, just type what you want.
    :type predefined_type: str,optional
    :return: The newly modified product.
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # We have a wall.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Oh, did I say wall? I meant slab.
        slab = ifcopenshell.api.root.reassign_class(model, product=wall, ifc_class="IfcSlab")

        # Warning: this will crash since wall doesn't exist any more.
        print(wall) # Kaboom.
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "product": product,
        "ifc_class": ifc_class,
        "predefined_type": predefined_type,
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        element = self.reassign_class(self.settings["product"], self.settings["ifc_class"])

        if element.is_a("IfcTypeProduct"):
            for occurrence in ifcopenshell.util.element.get_types(element) or []:
                ifc_class = ifcopenshell.util.type.get_applicable_entities(self.settings["ifc_class"])[0]
                self.reassign_class(occurrence, ifc_class)
        else:
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type:
                ifc_class = ifcopenshell.util.type.get_applicable_types(self.settings["ifc_class"])
                if ifc_class and len(ifc_class) == 1:
                    element_type = self.reassign_class(element_type, ifc_class[0])
                ifc_class = element.is_a()
                for occurrence in ifcopenshell.util.element.get_types(element_type) or []:
                    if occurrence == element:
                        continue
                    self.reassign_class(occurrence, ifc_class)
        return element

    def reassign_class(self, element, ifc_class):
        element = ifcopenshell.util.schema.reassign_class(self.file, element, ifc_class)
        if self.settings["predefined_type"] and hasattr(element, "PredefinedType"):
            try:
                element.PredefinedType = self.settings["predefined_type"]
            except:
                # PredefinedType wasn't in the respective enum, assume it's actually USERDEFINED
                # and set .ElementType / .ObjectType to the provided predefined type
                element.PredefinedType = "USERDEFINED"
                if element.is_a("IfcTypeProduct"):
                    element.ElementType = self.settings["predefined_type"]
                else:
                    element.ObjectType = self.settings["predefined_type"]

        return element
