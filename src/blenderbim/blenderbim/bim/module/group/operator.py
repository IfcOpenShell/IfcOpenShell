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
import ifcopenshell.util.attribute
import ifcopenshell.api
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.util.selector import Selector
import json
from blenderbim.bim.module.group.data import GroupsData
from blenderbim.bim.module.group.prop import BIMGroupProperties, Group
import blenderbim.core.group as core


class LoadGroups(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_groups(tool.Ifc, tool.Group, context.scene.BIMGroupProperties,
                         json.loads(context.scene.ExpandedGroups.json_string))
        return {"FINISHED"}


class ToggleGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_group"
    bl_label = "Toggle Group"
    bl_options = {"REGISTER", "UNDO"}
    ifc_definition_id: bpy.props.IntProperty()
    index: bpy.props.IntProperty()
    option: bpy.props.StringProperty(name="Expand or Collapse")

    def _execute(self, context):
        expanded_groups = set(json.loads(context.scene.ExpandedGroups.json_string))
        if self.option == "Expand":
            expanded_groups.add(self.ifc_definition_id)
        elif self.ifc_definition_id in expanded_groups:
            expanded_groups.remove(self.ifc_definition_id)
        context.scene.ExpandedGroups.json_string = json.dumps(list(expanded_groups))
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        context.scene.BIMGroupProperties.is_editing = False
        context.scene.BIMGroupProperties.active_group_id = 0
        return {"FINISHED"}


class AddGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add New Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        if not GroupsData.is_loaded:
            GroupsData.load()
        core.add_group(self.group, tool.Ifc, tool.Group, tool.Loader)
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_group(self.group, tool.Ifc, tool.Group)
        return {"FINISHED"}


class AssignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_group"
    bl_label = "Assign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def _execute(self, context):
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        core.assign_group(self.group, products, tool.Group, tool.Ifc)
        return {"FINISHED"}


class UnassignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    product: bpy.props.StringProperty()
    group: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        products = [bpy.data.objects.get(self.product)] if self.product else context.selected_objects
        core.unassign_group(self.group, products, tool.Group, tool.Ifc)
        return {"FINISHED"}


class SelectGroupObject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_group_object"
    bl_label = "Select Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_group_object_by_id(context, tool.Ifc, tool.Group, self.group)
        return {"FINISHED"}


class UpdateGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_group"
    bl_label = "Update Group"
    bl_options = {"REGISTER", "UNDO"}
    query: bpy.props.StringProperty()
    group_id: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        group = self.file.by_id(self.group_id)
        query = self.query

        new_products = Selector.parse(self.file, query)
        ifcopenshell.api.run(
            "group.update_group_products",
            self.file,
            **{
                "group": group,
                "products": new_products,
            }
        )
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class SelectGroupElements(bpy.types.Operator):
    bl_idname = "bim.select_group_elements"
    bl_label = "Select Group elements"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return bool(tool.Ifc.get() and context.active_object)

    def execute(self, context):
        elements = tool.Drawing.get_group_elements(tool.Ifc.get().by_id(self.group))
        tool.Spatial.select_products(elements)
        return {"FINISHED"}
