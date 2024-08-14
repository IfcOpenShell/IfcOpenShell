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
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.pset.data import refresh as refresh_pset
from bpy.types import PropertyGroup
import json
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


def update_active_group_index(self, context):
    refresh_pset()


class ExpandedGroups(StrProperty):
    json_string: StringProperty(name="JSON String", default="[]")


class Group(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    has_children: BoolProperty(name="Has Children", default=False)
    tree_depth: IntProperty(name="Tree Depth")


class BIMGroupProperties(PropertyGroup):
    group_attributes: CollectionProperty(name="Group Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    groups: CollectionProperty(name="Groups", type=Group)
    active_group_index: IntProperty(name="Active Group Index", update=update_active_group_index)
    active_group_id: IntProperty(name="Active Group Id")
