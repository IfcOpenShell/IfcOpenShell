# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING, Union


class BIMAttributeProperties(PropertyGroup):
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    is_editing_attributes: BoolProperty(name="Is Editing Attributes")

    if TYPE_CHECKING:
        attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        is_editing_attributes: bool


class ExplorerEntity(PropertyGroup):
    ifc_definition_id: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        ifc_definition_id: int


class BIMExplorerProperties(PropertyGroup):
    def update_is_loaded(self, context: object) -> None:
        if self.is_loaded:
            # Trigger refresh.
            self.ifc_class = self.ifc_class
        else:
            self.property_unset("is_loaded")
            self.property_unset("ifc_class")
            self.entities.clear()
            self.property_unset("active_entity_index")
            self.property_unset("editing_entity_id")
            self.entity_attributes.clear()

    is_loaded: BoolProperty(  # pyright: ignore[reportRedeclaration]
        name="Toggle Explorer UI",
        update=update_is_loaded,
    )

    def get_ifc_class(self, context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
        # TODO: Add more entities.
        classes = [
            "IfcPostalAddress",
            "IfcTelecomAddress",
        ]
        return [(c, c, "") for c in classes]

    def update_ifc_class(self, context: object) -> None:
        tool.Attribute.refresh_uilist_entities()

    ifc_class: EnumProperty(  # pyright: ignore[reportRedeclaration]
        name="IFC Class To Search",
        items=get_ifc_class,
        update=update_ifc_class,
    )
    entities: CollectionProperty(type=ExplorerEntity)  # pyright: ignore[reportRedeclaration]
    active_entity_index: IntProperty()  # pyright: ignore[reportRedeclaration]
    editing_entity_id: IntProperty()  # pyright: ignore[reportRedeclaration]
    entity_attributes: CollectionProperty(type=Attribute)  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        is_loaded: bool
        ifc_class: str
        entities: bpy.types.bpy_prop_collection_idprop[ExplorerEntity]
        active_entity_index: int
        editing_entity_id: int
        entity_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]

    @property
    def active_entity(self) -> Union[ExplorerEntity, None]:
        return tool.Blender.get_active_uilist_element(self.entities, self.active_entity_index)
