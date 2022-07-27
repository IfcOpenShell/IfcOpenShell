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
from blenderbim.bim.prop import StrProperty, Attribute
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

def update_json(self, context):
    json_string = json.loads(context.scene.ExpandedGroups.json_string)
    json_string.setdefault(self.ifc_definition_id, []) if self.is_expanded else json_string.pop(self.ifc_definition_id, None)
    context.scene.ExpandedGroups.json_string = json.dumps(json_string)
    a="a"

class ExpandedGroups(StrProperty):
    json_string: StringProperty(name="JSON String", update=update_json, default="{}")

class Group(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    selection_query: StringProperty(name="Selection Query")
    is_expanded: BoolProperty(name="Is Expanded", default=False, update=update_json)
    has_children: BoolProperty(name="Has Children", default=False)
    tree_depth: IntProperty(name="Tree Depth")
    json: StringProperty(name="Group Tree", default="")
    
class BIMGroupProperties(PropertyGroup):
    group_attributes: CollectionProperty(name="Group Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_adding: BoolProperty(name="Is Adding", default=False)
    groups: CollectionProperty(name="Groups", type=Group)
    active_group_index: IntProperty(name="Active Group Index")
    active_group_id: IntProperty(name="Active Group Id")
                