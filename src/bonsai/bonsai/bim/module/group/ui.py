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

        if (group := self.props.active_group) and (group_id := group.ifc_definition_id):
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"
            row.operator("bim.select_group_elements", text="", icon="RESTRICT_SELECT_OFF").group = group_id
            tool.Group.draw_visibility_buttons(row, group_id)
            row.operator("bim.assign_group", text="", icon="KEYFRAME_HLT").group = group_id
            row.operator("bim.unassign_group", text="", icon="KEYFRAME").group = group_id
            row.operator("bim.enable_editing_group", text="", icon="GREASEPENCIL").group = group_id
            row.operator("bim.add_group", text="", icon="ADD").group = group_id
            row.operator("bim.remove_group", text="", icon="X").group = group_id

        self.layout.template_list("BIM_UL_groups", "", self.props, "groups", self.props, "active_group_index")

        if self.props.active_group_id:
            draw_attributes(self.props.group_attributes, self.layout)
            row = self.layout.row(align=True)
            row.operator("bim.edit_group", text="Save Group", icon="CHECKMARK")
            row.operator("bim.disable_editing_group", text="", icon="CANCEL")


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
            prop_with_search(row, self.props, "object_group", text="", icon="OUTLINER")
            col = row.column(align=True)
            col.enabled = bool(self.props.object_group)
            op = col.operator("bim.assign_group", text="", icon="CHECKMARK")
            op.group = int(self.props.object_group or 0)
            row.operator("bim.disable_editing_object_groups", text="", icon="CANCEL")
        else:
            if not groups:
                row.label(text="No Groups", icon="OUTLINER")
            elif len(groups) == 1:
                row.label(text="1 Group", icon="OUTLINER")
            else:
                row.label(text=f"{len(groups)} Groups", icon="OUTLINER")
            row.operator("bim.enable_editing_object_groups", text="", icon="GREASEPENCIL")
            row.operator("bim.add_group_to_selected", text="", icon="ADD")

        for group in groups:
            row = self.layout.row(align=True)
            row.label(text=group["name"])
            row.operator("bim.select_group_elements", text="", icon="RESTRICT_SELECT_OFF").group = group["id"]
            op = row.operator("bim.unassign_group", text="", icon="X")
            op.group = group["id"]


class BIM_UL_groups(UIList):
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
            row.prop(item, "name", text="", emboss=False)
