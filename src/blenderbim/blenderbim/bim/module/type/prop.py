# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell.util.type
from blenderbim.bim.module.type.data import TypeData
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
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


def get_relating_type_class(self, context):
    if not TypeData.is_loaded:
        TypeData.load()
    return TypeData.data["relating_type_classes"]


def get_relating_type(self, context):
    if not TypeData.is_loaded:
        TypeData.load()
    return TypeData.data["relating_types"]


def update_relating_type_class(self, context):
    TypeData.is_loaded = False


class BIMTypeProperties(PropertyGroup):
    is_editing_type: BoolProperty(name="Is Editing Type")
    relating_type_class: EnumProperty(items=get_relating_type_class, name="Relating Type Class", update=update_relating_type_class)
    relating_type: EnumProperty(items=get_relating_type, name="Relating Type")
