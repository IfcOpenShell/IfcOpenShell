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
from blenderbim.bim.module.brick.data import BrickschemaData
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


def update_active_brick_index(self, context):
    BrickschemaData.is_loaded = False


class Brick(PropertyGroup):
    name: StringProperty(name="Name")
    uri: StringProperty(name="URI")
    total_items: IntProperty(name="Total Items")


class BIMBrickProperties(PropertyGroup):
    active_brick_class: StringProperty(name="Active Brick Class")
    brick_breadcrumbs: CollectionProperty(name="Brick Breadcrumbs", type=StrProperty)
    bricks: CollectionProperty(name="Bricks", type=Brick)
    active_brick_index: IntProperty(name="Active Brick Index", update=update_active_brick_index)
