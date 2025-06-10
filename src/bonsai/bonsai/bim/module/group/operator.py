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
import json


class LoadGroups(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_groups"
    bl_label = "Load Groups"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        self.props = tool.Blender.get_group_props()
        self.expanded_groups = json.loads(self.props.expanded_groups_json)
        self.props.groups.clear()

        groups = [
            group for group in tool.Ifc.get().by_type("IfcGroup", include_subtypes=False) if not group.HasAssignments
        ]
        sorted_groups = sorted(groups, key=lambda group: group.Name or "Unnamed")

        for group in sorted_groups:
            self.load_group(group)

        self.props.is_editing = True
        bpy.ops.bim.disable_editing_group()
        return {"FINISHED"}

    def load_group(self, group, tree_depth=0):
        new = self.props.groups.add()
        new.ifc_definition_id = group.id()
        new.name = group.Name or "Unnamed"
        new.tree_depth = tree_depth
        new.has_children = False
        new.is_expanded = group.id() in self.expanded_groups

        related_groups = [
            related_object
            for rel in group.IsGroupedBy or []
            for related_object in rel.RelatedObjects
            if related_object.is_a("IfcGroup")
        ]
        sorted_related_groups = sorted(related_groups, key=lambda group: group.Name or "Unnamed")

        for related_group in sorted_related_groups:
            new.has_children = True
            if not new.is_expanded:
                return
            self.load_group(related_group, tree_depth=tree_depth + 1)


class ToggleGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_group"
    bl_label = "Toggle Group"
    bl_options = {"REGISTER", "UNDO"}
    ifc_definition_id: bpy.props.IntProperty()
    index: bpy.props.IntProperty()
    option: bpy.props.StringProperty(name="Expand or Collapse")

    def _execute(self, context):
        props = tool.Blender.get_group_props()
        expanded_groups = set(json.loads(props.expanded_groups_json))
        if self.option == "Expand":
            expanded_groups.add(self.ifc_definition_id)
        elif self.ifc_definition_id in expanded_groups:
            expanded_groups.remove(self.ifc_definition_id)
        props.expanded_groups_json = json.dumps(list(expanded_groups))
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class DisableGroupEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_group_editing_ui"
    bl_label = "Disable Group Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Blender.get_group_props()
        props.is_editing = False
        props.active_group_id = 0
        return {"FINISHED"}


class AddGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_group"
    bl_label = "Add New Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        result = ifcopenshell.api.group.add_group(tool.Ifc.get())
        if self.group:
            ifcopenshell.api.group.assign_group(
                tool.Ifc.get(), products=[result], group=tool.Ifc.get().by_id(self.group)
            )
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EditGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_group"
    bl_label = "Edit Group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Blender.get_group_props()
        attributes = bonsai.bim.helper.export_attributes(props.group_attributes)
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.group.edit_group(ifc_file, group=ifc_file.by_id(props.active_group_id), attributes=attributes)
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class RemoveGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = tool.Ifc.get()
        ifcopenshell.api.group.remove_group(self.file, group=self.file.by_id(self.group))
        bpy.ops.bim.load_groups()
        return {"FINISHED"}


class EnableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_group"
    bl_label = "Enable Editing Group"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.IntProperty()

    def _execute(self, context):
        props = tool.Blender.get_group_props()
        props.group_attributes.clear()
        bonsai.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.group), props.group_attributes)
        props.active_group_id = self.group
        return {"FINISHED"}


class DisableEditingGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_group"
    bl_label = "Disable Editing Group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Blender.get_group_props()
        props.active_group_id = 0
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


class UnassignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unassign the selected objects from the selected group"
    group: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def _execute(self, context):
        products = [
            tool.Ifc.get_entity(o)
            for o in tool.Blender.get_selected_objects(include_active=False)
            if tool.Ifc.get_entity(o)
        ]
        if not products:
            return
        ifcopenshell.api.group.unassign_group(tool.Ifc.get(), products=products, group=tool.Ifc.get().by_id(self.group))


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
