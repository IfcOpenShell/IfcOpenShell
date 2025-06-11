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
import ifcopenshell.util.element
import ifcopenshell.util.type
from bonsai.bim.module.type.data import TypeData
import bonsai.tool as tool
from typing import TYPE_CHECKING, Union
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


def get_relating_type_class(self: "BIMTypeProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not TypeData.is_loaded:
        TypeData.load()
    return TypeData.data["relating_type_classes"]


def get_relating_type(self: "BIMTypeProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    if not TypeData.is_loaded:
        TypeData.load()
    return TypeData.data["relating_types"]


def update_relating_type_class(self: "BIMTypeProperties", context: bpy.types.Context) -> None:
    TypeData.is_loaded = False


def update_relating_type_from_object(self: "BIMTypeProperties", context: bpy.types.Context) -> None:
    if self.relating_type_object is None:
        return
    element = tool.Ifc.get_entity(self.relating_type_object)
    if not element:
        return
    element_type = ifcopenshell.util.element.get_type(element)
    if not element_type:
        return
    self.relating_type = str(element_type.id())
    bpy.ops.bim.assign_type()


def is_object_class_applicable(self: "BIMTypeProperties", obj: bpy.types.Object) -> bool:
    if not TypeData.is_loaded:
        TypeData.load()
    element = tool.Ifc.get_entity(obj)
    if not element:
        return False
    element_type = ifcopenshell.util.element.get_type(element)
    if element_type is None:
        return False
    return str(element_type.is_a()) in (r_t_c[0] for r_t_c in TypeData.data["relating_type_classes"])


class BIMTypeProperties(PropertyGroup):
    is_editing_type: BoolProperty(name="Is Editing Type")
    relating_type_class: EnumProperty(
        items=get_relating_type_class,
        name="Relating Type Class",
        update=update_relating_type_class,
    )
    relating_type: EnumProperty(items=get_relating_type, name="Relating Type")
    relating_type_object: PointerProperty(
        type=bpy.types.Object,
        name="Copy Type",
        update=update_relating_type_from_object,
        poll=is_object_class_applicable,
    )

    if TYPE_CHECKING:
        is_editing_type: bool
        relating_type_class: str
        relating_type: str
        relating_type_object: Union[bpy.types.Object, None]
