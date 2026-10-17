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

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
import ifcopenshell
from bpy.types import Panel, UIList

import bonsai.tool as tool
from bonsai.bim.helper import draw_attributes, prop_with_search
from bonsai.bim.module.group.data import GroupsData, ObjectGroupsData

if TYPE_CHECKING:
    from bonsai.bim.module.group.prop import BIMGroupProperties, Group


class BIM_PT_groups(Panel):
    bl_label = "Groups"
    bl_idname = "BIM_PT_groups"
    bl_options = {"HIDE_HEADER"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_groups"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not GroupsData.is_loaded:
            GroupsData.load()
        self.props = tool.Group.get_group_props()
        assert self.layout

        row = self.layout.row(align=True)
        row.label(text=f"{GroupsData.data['total_groups']} Groups Found", icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_group", text="", icon="ADD").group = 0
            row.operator("bim.disable_group_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_groups", text="", icon="IMPORT")

        if not self.props.is_editing:
            return

        # What the list shows: kinds of group, and whether Bonsai's own groups are included.
        row = self.layout.row(align=True)
        row.prop(self.props, "group_kinds", expand=True, icon_only=True)
        row.separator()
        row.prop(self.props, "should_show_internal", text="", icon="FILTER")

        group = self.props.active_group
        group_id = group.ifc_definition_id if group else 0

        # Every kind of group gets the same buttons; the operators route systems, zones and structural groups.
        actions = tool.Group.get_group_actions(tool.Ifc.get().by_id(group_id)) if group_id else set()

        row = self.layout.row()
        row.template_list("BIM_UL_groups", "", self.props, "groups", self.props, "active_group_index")
        if group_id:
            col = row.column(align=True)
            if "ADD_CHILD" in actions:
                col.operator("bim.add_group", text="", icon="ADD").group = group_id
            if "REMOVE" in actions:
                col.operator("bim.remove_group", text="", icon="X").group = group_id
            col.separator()
            col.operator("bim.enable_editing_group", text="", icon="GREASEPENCIL").group = group_id

        if group_id:
            row = self.layout.row(align=True)
            row.label(text="Contents")
            row.operator("bim.select_group_elements", text="", icon="RESTRICT_SELECT_OFF").group = group_id
            tool.Group.draw_visibility_buttons(row, group_id)

        if "ASSIGN" in actions:
            self.draw_selection_row(context, tool.Ifc.get().by_id(group_id))

        if self.props.active_group_id:
            draw_attributes(self.props.group_attributes, self.layout)
            row = self.layout.row(align=True)
            row.operator("bim.edit_group", text="Save Group", icon="CHECKMARK")
            row.operator("bim.disable_editing_group", text="", icon="CANCEL")

    def draw_selection_row(self, context: bpy.types.Context, group: ifcopenshell.entity_instance) -> None:
        # Gray out what wouldn't do anything: systems and zones only take some classes.
        selected = [e for o in context.selected_objects if (e := tool.Ifc.get_entity(o))]
        assignable = tool.Group.get_assignable(group, selected)
        members = {o for rel in group.IsGroupedBy or [] for o in rel.RelatedObjects}
        text = f"{len(context.selected_objects)} Selected"
        if len(assignable) < len(selected):
            text += f" ({len(assignable)} can join)"
        row = self.layout.row(align=True)
        row.label(text=f"{text} →")
        sub = row.row(align=True)
        sub.enabled = bool(assignable)
        sub.operator("bim.assign_group", text="", icon="KEYFRAME_HLT").group = group.id()
        sub = row.row(align=True)
        sub.enabled = any(e in members for e in selected)
        sub.operator("bim.unassign_group", text="", icon="KEYFRAME").group = group.id()


class BIM_PT_object_groups(Panel):
    bl_label = "Groups"
    bl_idname = "BIM_PT_object_groups"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object):
            return False
        props = tool.Blender.get_object_bim_props(obj)
        return tool.Ifc.get() and props.ifc_definition_id

    def draw(self, context):
        if not ObjectGroupsData.is_loaded:
            ObjectGroupsData.load()
        assert self.layout
        self.props = tool.Group.get_group_props()
        groups = ObjectGroupsData.data["groups"]

        row = self.layout.row(align=True)
        if self.props.is_editing_object_groups:
            prop_with_search(row, self.props, "object_group", text="")
            col = row.column(align=True)
            group = tool.Ifc.get_entity_by_id(int(self.props.object_group or 0))
            col.enabled = bool(group)
            if group and group.is_a("IfcSystem"):
                # Systems and zones only accept certain classes, which bim.assign_system checks.
                col.operator("bim.assign_system", text="", icon="CHECKMARK").system = group.id()
            else:
                col.operator("bim.assign_group", text="", icon="CHECKMARK").group = group.id() if group else 0
            row.operator("bim.disable_editing_object_groups", text="", icon="CANCEL")
        else:
            if not groups:
                text = "No Groups"
            elif len(groups) == 1:
                text = "1 Group"
            else:
                text = f"{len(groups)} Groups"
            if total_hidden := ObjectGroupsData.data["total_hidden"]:
                text += f" ({total_hidden} hidden)"
            row.label(text=text, icon="OUTLINER")
            row.prop(self.props, "should_show_internal", text="", icon="FILTER")
            row.operator("bim.enable_editing_object_groups", text="", icon="GREASEPENCIL")
            row.operator("bim.add_group_to_selected", text="", icon="ADD")

        for group in groups:
            row = self.layout.row(align=True)
            row.label(text=group["name"], icon=group["icon"])
            row.operator("bim.select_group_elements", text="", icon="RESTRICT_SELECT_OFF").group = group["id"]
            op = row.operator("bim.unassign_group", text="", icon="X")
            op.group = group["id"]


class BIM_UL_groups(UIList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_filter_show = True

    def draw_filter(self, context, layout):
        row = layout.row()
        row.prop(tool.Group.get_group_props(), "group_filter", text="", icon="VIEWZOOM")

    def filter_items(self, context: bpy.types.Context, data: BIMGroupProperties, propname: str):
        items = getattr(data, propname)
        filter_name = data.group_filter.strip().lower()
        if not filter_name:
            return [], []
        # Show matching groups along with the groups they are nested in.
        flags = [0] * len(items)
        ancestors: list[int] = []
        for index, item in enumerate(items):
            del ancestors[item.tree_depth :]
            if filter_name in item.name.lower():
                flags[index] = self.bitflag_filter_item
                for ancestor in ancestors:
                    flags[ancestor] = self.bitflag_filter_item
            ancestors.append(index)
        return flags, []

    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data: BIMGroupProperties,
        item: Group,
        icon,
        active_data,
        active_propname,
        index: int,
    ) -> None:
        if item:
            row = layout.row(align=True)
            for i in range(0, item.tree_depth):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                op = row.operator(
                    "bim.toggle_group", icon="TRIA_DOWN" if item.is_expanded else "TRIA_RIGHT", text="", emboss=False
                )
                op.group_type = "IfcGroup"
                op.ifc_definition_id = item.ifc_definition_id
                op.option = "COLLAPSE" if item.is_expanded else "EXPAND"
            row.prop(item, "name", text="", emboss=False, icon=item.icon)
