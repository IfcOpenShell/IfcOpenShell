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
from bonsai.bim.prop import StrProperty, BIMFilterGroup
from bonsai.bim.module.diff.data import DiffData
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


def update_diff_json_file(self, context):
    DiffData.data["diff_json"] = DiffData.diff_json()


class Relationships(PropertyGroup):
    relationship: EnumProperty(
        name="Relationship",
        items=[(r, r.capitalize(), r) for r in ["type", "property", "container", "aggregate", "classification"]],
    )


class DiffProperties(PropertyGroup):
    diff_json_file: StringProperty(default="", name="JSON Output", update=update_diff_json_file)
    old_file: StringProperty(default="", name="Old IFC File")
    new_file: StringProperty(default="", name="New IFC File")
    diff_relationships: CollectionProperty(type=Relationships, name="Relationships")
    filter_groups: CollectionProperty(type=BIMFilterGroup, name="Filter Groups")
    should_load_changed_elements: BoolProperty(name="Load Changed Elements", default=True)
    active_file: EnumProperty(
        items=[
            ("NONE", "N/A", ""),
            ("OLD", "Old", ""),
            ("NEW", "New", ""),
        ],
        name="Active File",
        default="NEW",
    )
