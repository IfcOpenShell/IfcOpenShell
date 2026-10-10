# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from typing import TYPE_CHECKING

import bpy
from bpy.types import Panel, UIList

import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.linked_reference.prop import BIMLinkedReferenceProperties, LinkedReferenceLink


class BIM_PT_linked_references(Panel):
    bl_label = "Linked References"
    bl_idname = "BIM_PT_linked_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    def draw(self, context):
        assert self.layout
        props = tool.LinkedReference.get_props()

        row = self.layout.row(align=True)
        row.operator("bim.link_reference", icon="LINKED")

        if not props.references:
            return

        index = props.active_reference_index
        if 0 <= index < len(props.references):
            link = props.references[index]
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"
            if link.is_loaded:
                row.operator("bim.select_linked_reference_handle", text="", icon="OBJECT_DATA").reference_index = index
                row.operator("bim.refresh_linked_reference", text="", icon="FILE_REFRESH").reference_index = index
                row.operator("bim.unload_linked_reference", text="", icon="UNLINKED").reference_index = index
            else:
                row.operator("bim.load_linked_reference", text="", icon="LINKED").reference_index = index
            row.operator("bim.unlink_reference", text="", icon="X").reference_index = index

        self.layout.template_list("BIM_UL_linked_references", "", props, "references", props, "active_reference_index")

        row = self.layout.row(align=True)
        row.prop(props, "auto_refresh")
        if props.auto_refresh:
            row.prop(props, "auto_refresh_interval")


class BIM_UL_linked_references(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: "BIMLinkedReferenceProperties",
        item: "LinkedReferenceLink",
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        row.label(text=item.filepath)
        if item.is_loaded:
            anchor = tool.LinkedReference.get_anchor(item)
            hidden = bool(anchor and anchor.hide_viewport)
            op = row.operator(
                "bim.toggle_linked_reference_visibility",
                text="",
                icon="HIDE_ON" if hidden else "HIDE_OFF",
                emboss=False,
            )
            op.reference_index = index
