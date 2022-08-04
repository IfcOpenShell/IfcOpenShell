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
from blenderbim.bim.prop import StrProperty
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

class Relationships(PropertyGroup):
    relationship: EnumProperty(
        name="Relationship",
        items=[(r,r,r) for r in ["type", "property", "container", "aggregate", "classification"]],
    )

class DiffProperties(PropertyGroup):
    diff_json_file: StringProperty(default="", name="Diff JSON File")
    diff_old_file: StringProperty(default="", name="Diff Old IFC File")
    diff_new_file: StringProperty(default="", name="Diff New IFC File")
    diff_relationships: CollectionProperty(type=Relationships, name="Diff Relationships")
    diff_filter_elements: StringProperty(default="", name="Diff Filter")
    diff_result: StringProperty(default="", name="Diff Result")
