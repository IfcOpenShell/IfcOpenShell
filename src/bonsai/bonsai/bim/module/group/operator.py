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
import ifcopenshell.api
import ifcopenshell.api.group
import ifcopenshell.util.element
import bonsai.bim.helper
import bonsai.tool as tool
from typing import TYPE_CHECKING, Literal, get_args


class LoadGroups(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        tool.Group.import_groups("IfcGroup")
        tool.Group.enable_group_editing_ui()
        tool.Group.disable_editing_group()
        return {"FINISHED"}


class ToggleGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_group"
    bl_label = "Toggle Group"
    bl_options = {"REGISTER", "UNDO"}

    ifc_definition_id: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]
    group_type: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=[(i, i, "") for i in get_args(tool.Group.GroupType)],
    )
    option: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=[(i, i, "") for i in get_args(tool.Group.ToggleOption)],
    )

    if TYPE_CHECKING:
        ifc_definition_id: int
        group_type: tool.Group.GroupType
        option: tool.Group.ToggleOption

    def _execute(self, context):
        group = tool.Ifc.get().by_id(self.ifc_definition_id)
        tool.Group.toggle_group(group, self.group_type, self.option)
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        tool.Group.disable_group_editing_ui()
        tool.Group.disable_editing_group()
        return {"FINISHED"}


class AddGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add New Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, properties) -> str:
        if properties.group:
            return "Add new subgroup to the active IfcGroup."
        return "Add new IfcGroup."

    def _execute(self, context):
        result = ifcopenshell.api.group.add_group(tool.Ifc.get())
        if self.group:
            group = tool.Ifc.get().by_id(self.group)
            ifcopenshell.api.group.assign_group(tool.Ifc.get(), products=[result], group=group)
            tool.Group.toggle_group(group, "IfcGroup", "EXPAND")
        tool.Group.import_groups("IfcGroup")
        return {"FINISHED"}


class EditGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Group.get_group_props()
        attributes = bonsai.bim.helper.export_attributes(props.group_attributes)
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.group.edit_group(ifc_file, group=ifc_file.by_id(props.active_group_id), attributes=attributes)
        tool.Group.import_groups("IfcGroup")
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.group.remove_group(self.file, group=self.file.by_id(self.group))
        tool.Group.import_groups("IfcGroup")
        tool.Group.update_uilist_index("IfcGroup")
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        props = tool.Group.get_group_props()
        props.group_attributes.clear()
        bonsai.bim.helper.import_attributes(tool.Ifc.get().by_id(self.group), props.group_attributes)
        ifc_file = tool.Ifc.get()
        tool.Group.set_active_group_to_edit(ifc_file.by_id(self.group))
        return {"FINISHED"}


class DisableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_group"
    bl_label = "Disable Editing Group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        tool.Group.disable_editing_group()
        return {"FINISHED"}


class AssignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_group"
    bl_label = "Assign Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Assign the selected objects to the selected group\nALT + CLICK to unassign."
    group: bpy.props.IntProperty(options={"SKIP_SAVE"})
    is_assigning: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        self.is_assigning = not event.alt
        return self.execute(context)

    def _execute(self, context):
        if not self.is_assigning:
            return bpy.ops.bim.unassign_group(group=self.group)
        products = [
            element
            for o in tool.Blender.get_selected_objects(include_active=False)
            if (element := tool.Ifc.get_entity(o))
        ]
        ifcopenshell.api.group.assign_group(tool.Ifc.get(), products=products, group=tool.Ifc.get().by_id(self.group))
        self.report({"INFO"}, f"Assigned {len(products)} objects to group.")


class UnassignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unassign the selected objects from the selected group"
    group: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def _execute(self, context):
        products = [
            element
            for o in tool.Blender.get_selected_objects(include_active=False)
            if (element := tool.Ifc.get_entity(o))
        ]
        if not products:
            return
        ifcopenshell.api.group.unassign_group(tool.Ifc.get(), products=products, group=tool.Ifc.get().by_id(self.group))
        self.report({"INFO"}, f"Unassigned {len(products)} objects from group.")


class SelectGroupElements(bpy.types.Operator):
    bl_idname = "bim.select_group_elements"
    bl_label = "Select Group elements"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Select objects assigned to the selected group and all nested groups\nALT + CLICK to exclude children"
    )
    group: bpy.props.IntProperty()
    is_recursive: bpy.props.BoolProperty(name="Is Recursive", default=True, options={"SKIP_SAVE"})

    def invoke(self, context, event):
        self.is_recursive = not event.alt
        return self.execute(context)

    def execute(self, context):
        tool.Spatial.select_products(
            ifcopenshell.util.element.get_grouped_by(tool.Ifc.get().by_id(self.group), is_recursive=self.is_recursive)
        )
        return {"FINISHED"}


class SetGroupVisibility(bpy.types.Operator):
    bl_idname = "bim.set_group_visibility"
    bl_label = "Set Group Visibility"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()
    should_include_children: bpy.props.BoolProperty(name="Should Include Children", default=True, options={"SKIP_SAVE"})
    mode: bpy.props.StringProperty(name="Mode")

    @classmethod
    def description(cls, context, operator):
        if operator.mode == "HIDE":
            return "Hides the selected group and all children.\n" + "ALT+CLICK to ignore children"
        elif operator.mode == "SHOW":
            return "Shows the selected group and all children.\n" + "ALT+CLICK to ignore children"
        return "Isolate the selected group and all children.\n" + "ALT+CLICK to ignore children"

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.should_include_children = False
        return self.execute(context)

    def execute(self, context):
        if self.mode == "ISOLATE":
            context_override = tool.Blender.get_viewport_context()
            with context.temp_override(**context_override):
                bpy.ops.object.hide_view_set(unselected=True)
                bpy.ops.object.hide_view_set(unselected=False)
            should_hide = False
        else:
            should_hide = self.mode == "HIDE"

        group = tool.Ifc.get().by_id(self.group)
        elements = ifcopenshell.util.element.get_grouped_by(group, is_recursive=self.should_include_children)
        for element in elements:
            if obj := tool.Ifc.get_object(element):
                obj.hide_set(should_hide)
        return {"FINISHED"}
