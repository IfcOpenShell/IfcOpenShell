# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.module.brick.data import BrickschemaData, BrickschemaReferencesData
from blenderbim.bim.prop import StrProperty, Attribute
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
from blenderbim.tool.brick import BrickStore

def update_active_brick_index(self, context):
    BrickschemaData.is_loaded = False


def get_libraries(self, context):
    if not BrickschemaReferencesData.is_loaded:
        BrickschemaReferencesData.load()
    return BrickschemaReferencesData.data["libraries"]


def get_namespaces(self, context):
    return BrickStore.namespaces


def get_brick_equipment_classes(self, context):
    if not BrickschemaData.is_loaded:
        BrickschemaData.load()
    return BrickschemaData.data["brick_equipment_classes"]


def get_brick_roots(self, context):
    return [("System", "System", ""),
            ("Location", "Location", ""),
            ("Equipment", "Equipment", ""),
            ("Point", "Point", "")
        ]
            

class Brick(PropertyGroup):
    name: StringProperty(name="Name")
    label: StringProperty(name="Label")
    uri: StringProperty(name="URI")
    total_items: IntProperty(name="Total Items")


class BIMBrickProperties(PropertyGroup):
    active_brick_class: StringProperty(name="Active Brick Class")
    brick_breadcrumbs: CollectionProperty(name="Brick Breadcrumbs", type=StrProperty)
    bricks: CollectionProperty(name="Bricks", type=Brick)
    active_brick_index: IntProperty(name="Active Brick Index", update=update_active_brick_index)
    libraries: EnumProperty(name="Libraries", items=get_libraries)
    namespace: EnumProperty(name="Namespace", items=get_namespaces)
    brick_equipment_class: EnumProperty(name="Brick Equipment Class", items=get_brick_equipment_classes)
    brick_settings_toggled: BoolProperty(name="Brick Settings Toggled", default=False)
    new_brick_label: StringProperty(name="New Brick Label")
    new_brick_namespace_alias: StringProperty(name="New Brick Namespace Alias")
    new_brick_namespace_uri: StringProperty(name="New Brick Namespace URI")
    brick_list_root: EnumProperty(name="Brick List Root", items=get_brick_roots)