# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool
from bpy.types import WorkSpaceTool
from blenderbim.bim.module.project.data import LinksData


class QueryTool(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.query_tool"
    bl_label = "Query Tool"
    bl_description = "Fetch data about a linked IFC element"
    bl_icon = "ops.generic.select_circle"
    bl_widget = None
    bl_keymap = (
        ("bim.query_linked_element", {"type": "RIGHTMOUSE", "value": "PRESS"}, None),
        ("bim.query_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.query_hotkey", {"type": "C", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_C")]}),
    )

    def draw_settings(context, layout, ws_tool):
        row = layout.row(align=True)
        row.label(text="Query Object", icon="MOUSE_RMB")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Add Clipping Plane", icon="EVENT_C")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Disable Culling" if LinksData.enable_culling else "Enable Culling", icon="EVENT_C")


class QueryHotkey(bpy.types.Operator):
    bl_idname = "bim.query_hotkey"
    bl_label = "Query Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def execute(self, context):
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def hotkey_S_C(self):
        bpy.ops.bim.create_clipping_plane("INVOKE_DEFAULT")

    def hotkey_A_C(self):
        if LinksData.enable_culling:
            bpy.ops.bim.disable_culling()
        else:
            bpy.ops.bim.enable_culling("INVOKE_DEFAULT")
