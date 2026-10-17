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

from typing import TYPE_CHECKING, get_args

import bpy
import ifcopenshell.api.group
import ifcopenshell.util.element

import bonsai.bim.helper
import bonsai.tool as tool
from bonsai.bim.module.group.data import ObjectGroupsData


def run_routed(operator: bpy.types.Operator, routed_operator, **kwargs) -> set[str]:
    """Run the operator that handles a kind of group (e.g. bim.assign_system) from a Groups operator.

    Blender raises an error an operator reports as a RuntimeError when it's called from Python, so pass
    the message on as this operator's own report rather than as a traceback.
    """
    try:
        return routed_operator(**kwargs)
    except RuntimeError as error:
        operator.report({"ERROR"}, str(error).removeprefix("Error: ").strip())
        return {"CANCELLED"}


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

    ifc_definition_id: bpy.props.IntProperty()
    group_type: bpy.props.EnumProperty(
        items=[(i, i, "") for i in get_args(tool.Group.GroupType)],
    )
    option: bpy.props.EnumProperty(
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
    name: bpy.props.StringProperty(name="Name", default="Unnamed", options={"SKIP_SAVE"})

    @classmethod
    def description(cls, context, properties) -> str:
        if properties.group:
            return "Add new subgroup to the active IfcGroup."
        return "Add new IfcGroup."

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        if self.is_adding_subsystem():
            self.layout.prop(tool.System.get_system_props(), "system_class", text="Class")
        self.layout.prop(self, "name")

    def is_adding_subsystem(self) -> bool:
        return bool(self.group) and tool.Group.get_kind(tool.Ifc.get().by_id(self.group)) == "SYSTEM"

    def _execute(self, context):
        if self.is_adding_subsystem():
            # A child of a system is a subsystem, added like the Systems panel does.
            run_routed(self, bpy.ops.bim.add_system, parent_system_id=self.group, name=self.name)
        else:
            result = ifcopenshell.api.group.add_group(tool.Ifc.get(), name=self.name)
            if self.group:
                ifcopenshell.api.group.assign_group(
                    tool.Ifc.get(), products=[result], group=tool.Ifc.get().by_id(self.group)
                )
        if self.group:
            tool.Group.toggle_group(tool.Ifc.get().by_id(self.group), "IfcGroup", "EXPAND")
        tool.Group.import_groups("IfcGroup")
        return {"FINISHED"}


class AddGroupToSelected(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_group_to_selected"
    bl_label = "Add Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new IfcGroup and assign the selected objects to it"
    name: bpy.props.StringProperty(name="Name", default="Unnamed", options={"SKIP_SAVE"})
    allow_duplicate: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE", "HIDDEN"})

    def invoke(self, context, event):
        if self.allow_duplicate:
            return context.window_manager.invoke_confirm(
                self,
                event,
                title="Duplicate Group Name",
                message=f'A group named "{self.name}" already exists. Add another one?',
                confirm_text="Add Group",
            )
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not self.allow_duplicate and any(g.Name == self.name for g in tool.Group.get_user_groups()):
            # Ask again from a confirmation popup, which runs this operator anew.
            bpy.ops.bim.add_group_to_selected("INVOKE_DEFAULT", name=self.name, allow_duplicate=True)
            return
        group = ifcopenshell.api.group.add_group(ifc_file, name=self.name)
        products = [
            element
            for o in tool.Blender.get_selected_objects(include_active=False)
            if (element := tool.Ifc.get_entity(o))
        ]
        if products:
            ifcopenshell.api.group.assign_group(ifc_file, products=products, group=group)
        tool.Group.import_groups("IfcGroup")
        tool.Blender.update_all_properties_editors(context)
        # Groups include systems, whose membership the viewport decorations depend on.
        tool.Blender.update_all_viewports(context)
        self.report({"INFO"}, f"Added group with {len(products)} objects.")


class EnableEditingObjectGroups(bpy.types.Operator):
    bl_idname = "bim.enable_editing_object_groups"
    bl_label = "Assign to Existing Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Pick an existing group, or a system or zone the active object can join, to assign the selected objects to"
    )

    @classmethod
    def poll(cls, context):
        if not ObjectGroupsData.is_loaded:
            ObjectGroupsData.load()
        if not ObjectGroupsData.data["group_items"]:
            cls.poll_message_set("No groups, or systems or zones this object can join. Add a group first.")
            return False
        return True

    def execute(self, context):
        tool.Group.get_group_props().is_editing_object_groups = True
        return {"FINISHED"}


class DisableEditingObjectGroups(bpy.types.Operator):
    bl_idname = "bim.disable_editing_object_groups"
    bl_label = "Cancel"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tool.Group.get_group_props().is_editing_object_groups = False
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
        group = self.file.by_id(self.group)
        # Remove other kinds of group the way their own panels do, so those panels stay up to date.
        if group.is_a("IfcStructuralAnalysisModel"):
            run_routed(self, bpy.ops.bim.remove_structural_analysis_model, structural_analysis_model=self.group)
        elif group.is_a("IfcStructuralLoadCase"):
            run_routed(self, bpy.ops.bim.remove_structural_load_case, load_case=self.group)
        elif group.is_a("IfcStructuralLoadGroup"):
            run_routed(self, bpy.ops.bim.remove_structural_load_group, load_group=self.group)
        elif group.is_a("IfcZone"):
            run_routed(self, bpy.ops.bim.remove_zone, zone=self.group)
        elif group.is_a("IfcSystem"):
            run_routed(self, bpy.ops.bim.remove_system, system=self.group)
        else:
            ifcopenshell.api.group.remove_group(self.file, group=group)
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
        ifc_file = tool.Ifc.get()
        group = ifc_file.by_id(self.group)
        # Systems, zones and structural analysis models only accept some classes, which their operators check.
        if group.is_a("IfcStructuralAnalysisModel"):
            return run_routed(self, bpy.ops.bim.assign_structural_analysis_model, structural_analysis_model=self.group)
        if group.is_a("IfcSystem"):
            return run_routed(self, bpy.ops.bim.assign_system, system=self.group)
        products = [
            element
            for o in tool.Blender.get_selected_objects(include_active=False)
            if (element := tool.Ifc.get_entity(o))
        ]
        relocated_annotations = self.unassign_from_previous_drawing(ifc_file, group, products)
        ifcopenshell.api.group.assign_group(ifc_file, products=products, group=group)
        self.relocate_annotations_to_drawing(relocated_annotations, group)
        tool.Group.get_group_props().is_editing_object_groups = False
        tool.Blender.update_all_properties_editors(context)
        # Groups include systems, whose membership the viewport decorations depend on.
        tool.Blender.update_all_viewports(context)
        self.report({"INFO"}, f"Assigned {len(products)} objects to group.")

    def unassign_from_previous_drawing(self, ifc_file, group, products) -> list[ifcopenshell.entity_instance]:
        """Assigning an annotation to a group that represents a drawing means the
        annotation should belong to that drawing only, so it needs to leave
        whichever drawing it was previously part of, instead of ending up
        visible in both at once.
        """
        new_drawing = tool.Drawing.get_group_drawing(group)
        if not new_drawing:
            return []
        relocated = []
        for product in products:
            if not product.is_a("IfcAnnotation") or product.ObjectType == "DRAWING":
                continue
            old_drawing = tool.Drawing.get_annotation_drawing(product)
            if not old_drawing or old_drawing.id() == new_drawing.id():
                continue
            if old_group := tool.Drawing.get_drawing_group(old_drawing):
                ifcopenshell.api.group.unassign_group(ifc_file, products=[product], group=old_group)
            relocated.append(product)
        return relocated

    def relocate_annotations_to_drawing(self, products, group) -> None:
        """Move the relocated annotations into the new drawing's collection and
        depth, now that they have actually been assigned to its group.
        """
        if not products:
            return
        new_drawing = tool.Drawing.get_group_drawing(group)
        new_camera = tool.Ifc.get_object(new_drawing) or tool.Drawing.import_drawing(new_drawing)
        for product in products:
            if obj := tool.Ifc.get_object(product):
                tool.Drawing.ensure_annotation_in_drawing_plane(obj, camera=new_camera)
                tool.Collector.assign(obj)


class UnassignGroup(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_group"
    bl_label = "Unassign Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unassign the selected objects from the selected group"
    group: bpy.props.IntProperty(options={"SKIP_SAVE"})

    def _execute(self, context):
        if tool.Ifc.get().by_id(self.group).is_a("IfcStructuralAnalysisModel"):
            return run_routed(
                self, bpy.ops.bim.unassign_structural_analysis_model, structural_analysis_model=self.group
            )
        products = [
            element
            for o in tool.Blender.get_selected_objects(include_active=False)
            if (element := tool.Ifc.get_entity(o))
        ]
        if not products:
            return
        ifcopenshell.api.group.unassign_group(tool.Ifc.get(), products=products, group=tool.Ifc.get().by_id(self.group))
        tool.Blender.update_all_properties_editors(context)
        # Groups include systems, whose membership the viewport decorations depend on.
        tool.Blender.update_all_viewports(context)
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
