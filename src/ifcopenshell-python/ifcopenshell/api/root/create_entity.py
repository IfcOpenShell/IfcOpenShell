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


class Usecase:
    def __init__(self, file, ifc_class="IfcBuildingElementProxy", predefined_type=None, name=None):
        """Create a new rooted product

        This is a critical function used to create almost any rooted product or
        product type. If you want to create walls, spaces, buildings, wall
        types, and so on, use this function.

        Just specify the class you want to create, as well as the predefined
        type and name. It will handle the storage of the predefined type and
        check whether the predefined type is built-in or custom. It will also
        generate a valid GlobalId and store ownership history. It will also
        handle some edge cases for default validity where users might forget to
        populate some mandatory attributes. For example, doors must define an
        operation type but many people forget.

        :param ifc_class: Any rooted IFC class.
        :type ifc_class: str,optional
        :param predefined_type: Any built-in or user-defined predefined type that
            is applicable to that IFC class. For user-defined predefined types
            just enter in any value and the API will handle it automatically.
        :type predefined_type: str,optional
        :param name: The name of the new element.
        :type name: str,optional
        :return: The newly created element based on the specified IFC class.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # We have a project.
            ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")

            # We have a building.
            ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")

            # We have a wall.
            ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # We have a wall type.
            ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType")
        """
        self.file = file
        self.settings = {
            "ifc_class": ifc_class,
            "predefined_type": predefined_type,
            "name": name,
        }

    def execute(self):
        element = self.file.create_entity(
            self.settings["ifc_class"],
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
            }
        )
        element.Name = self.settings["name"] or None
        if self.settings["predefined_type"]:
            if hasattr(element, "PredefinedType"):
                try:
                    element.PredefinedType = self.settings["predefined_type"]
                except:
                    element.PredefinedType = "USERDEFINED"
                    if hasattr(element, "ObjectType"):
                        element.ObjectType = self.settings["predefined_type"]
                    elif hasattr(element, "ElementType"):
                        element.ElementType = self.settings["predefined_type"]
                    elif hasattr(element, "ProcessType"):
                        element.ProcessType = self.settings["predefined_type"]
            elif hasattr(element, "ObjectType"):
                element.ObjectType = self.settings["predefined_type"]
        if self.file.schema == "IFC2X3":
            self.handle_2x3_defaults(element)
        elif self.file.schema == "IFC4":
            self.handle_4_defaults(element)
        return element

    def handle_2x3_defaults(self, element):
        if element.is_a("IfcElementType"):
            if hasattr(element, "PredefinedType") and not element.PredefinedType:
                element.PredefinedType = "NOTDEFINED"

        if element.is_a("IfcSpatialStructureElement"):
            element.CompositionType = "ELEMENT"
        elif element.is_a("IfcRoof"):
            element.ShapeType = "NOTDEFINED"
        elif element.is_a("IfcFurnitureType"):
            element.AssemblyPlace = "NOTDEFINED"
        elif element.is_a("IfcDoorStyle") or element.is_a("IfcWindowStyle"):
            element.OperationType = "NOTDEFINED"
            element.ConstructionType = "NOTDEFINED"
            element.ParameterTakesPrecedence = False
            element.Sizeable = False

    def handle_4_defaults(self, element):
        if element.is_a("IfcElementType"):
            if hasattr(element, "PredefinedType") and not element.PredefinedType:
                element.PredefinedType = "NOTDEFINED"

        if element.is_a("IfcDoorStyle") or element.is_a("IfcWindowStyle"):
            element.OperationType = "NOTDEFINED"
            element.ConstructionType = "NOTDEFINED"
            element.ParameterTakesPrecedence = False
            element.Sizeable = False
        elif element.is_a("IfcDoorType"):
            element.OperationType = "NOTDEFINED"
        elif element.is_a("IfcWindowType"):
            element.PartitioningType = "NOTDEFINED"
        elif element.is_a("IfcFurnitureType"):
            element.AssemblyPlace = "NOTDEFINED"
