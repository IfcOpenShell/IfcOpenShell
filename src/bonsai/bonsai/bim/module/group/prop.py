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
from bonsai.bim.module.pset.data import refresh as refresh_pset
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


def update_active_group_index(self, context):
    refresh_pset()


class Group(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    has_children: BoolProperty(name="Has Children", default=False)
    tree_depth: IntProperty(name="Tree Depth")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int
        is_expanded: bool
        has_children: bool
        tree_depth: int


class BIMGroupProperties(PropertyGroup):
    group_attributes: CollectionProperty(name="Group Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    groups: CollectionProperty(name="Groups", type=Group)
    active_group_index: IntProperty(name="Active Group Index", update=update_active_group_index)
    active_group_id: IntProperty(name="Active Group Id")
    expanded_groups_json: StringProperty(name="JSON String", default="[]")

    if TYPE_CHECKING:
        group_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        is_editing: bool
        groups: bpy.types.bpy_prop_collection_idprop[Group]
        active_group_index: int
        active_group_id: int
        expanded_groups_json: str

    @property
    def active_group(self) -> Union[Group, None]:
        return tool.Blender.get_active_uilist_element(self.groups, self.active_group_index)
