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


class Usecase:
    def __init__(
        self,
        file,
        product=None,
        ifc_class="IfcBuildingElementProxy",
        predefined_type=None,
    ):
        """Changes the class of a product

        If you ever created a wall then realised it's meant to be something
        else, this function lets you change the IFC class whilst retaining all
        other geometry and relationships.

        This is especially useful when dealing with poorly classified data from
        proprietary software with limited IFC capabilities.

        :param product: The IfcProduct that you want to change the class of.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param ifc_class: The new IFC class you want to change it to.
        :type ifc_class: str,optional
        :param predefined_type: In case you want to change the predefined type
            too. User defined types are also allowed, just type what you want.
        :type predefined_type: str,optional
        :return: The newly modified product.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # We have a wall.
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # Oh, did I say wall? I meant slab.
            slab = ifcopenshell.api.run("root.reassign_class", model, product=wall, ifc_class="IfcSlab")

            # Warning: this will crash since wall doesn't exist any more.
            print(wall) # Kaboom.
        """
        self.file = file
        self.settings = {
            "product": product,
            "ifc_class": ifc_class,
            "predefined_type": predefined_type,
        }

    def execute(self):
        element = ifcopenshell.util.schema.reassign_class(
            self.file, self.settings["product"], self.settings["ifc_class"]
        )
        is_type = element.is_a("IfcTypeProduct")
        if self.settings["predefined_type"] and hasattr(element, "PredefinedType"):
            try:
                element.PredefinedType = self.settings["predefined_type"]
            except:
                # PredefinedType wasn't in the respective enum, assume it's actually USERDEFINED
                # and set .ElementType / .ObjectType to the provided predefined type
                element.PredefinedType = "USERDEFINED"
                if is_type:
                    element.ElementType = self.settings["predefined_type"]
                else:
                    element.ObjectType = self.settings["predefined_type"]

        # reassign classes for occurences connected to the type
        if is_type:
            for occurrence in ifcopenshell.util.element.get_types(element) or []:
                ifc_class = ifcopenshell.util.type.get_applicable_entities(self.settings["ifc_class"])[0]
                ifcopenshell.api.run(
                    "root.reassign_class",
                    self.file,
                    product=occurrence,
                    ifc_class=ifc_class,
                    predefined_type=self.settings["predefined_type"],
                )
        return element
