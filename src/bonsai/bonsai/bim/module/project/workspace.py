# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import bonsai.tool as tool
from bpy.types import WorkSpaceTool
from bonsai.bim.module.project.data import LinksData


class ExploreTool(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.explore_tool"
    bl_label = "Explore Tool"
    bl_description = "Fetch data about a linked IFC element"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.explore")
    bl_widget = None
    bl_keymap = (
        ("bim.query_linked_element", {"type": "RIGHTMOUSE", "value": "PRESS"}, None),
        ("bim.explore_hotkey", {"type": "W", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_W")]}),
        ("bim.explore_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.explore_hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.explore_hotkey", {"type": "C", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_C")]}),
        ("bim.explore_hotkey", {"type": "M", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_M")]}),
    )

    def draw_settings(context, layout, ws_tool):
        row = layout.row(align=True)
        row.label(text="Query Object", icon="MOUSE_RMB")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Walk Mode", icon="EVENT_W")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Add Clipping Plane", icon="EVENT_C")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Flip Clipping Plane", icon="EVENT_F")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Set Orbit Center", icon="MOUSE_MMB")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Disable Culling" if LinksData.enable_culling else "Enable Culling", icon="EVENT_C")

        prop = context.scene.MeasureToolSettings
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_M")
        row = layout.row(align=True)
        op = row.operator("bim.explore_hotkey", text="Measure Tool", icon="CON_DISTLIMIT")
        op.hotkey = "S_M"
        row = layout.row(align=True)
        row.prop(prop, "measurement_type", text="Measure Type", expand=True, icon_only=True, emboss=True)


class ExploreHotkey(bpy.types.Operator):
    bl_idname = "bim.explore_hotkey"
    bl_label = "Explore Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def execute(self, context):
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def hotkey_S_W(self):
        bpy.ops.view3d.walk("INVOKE_DEFAULT")

    def hotkey_S_C(self):
        bpy.ops.bim.create_clipping_plane("INVOKE_DEFAULT")

    def hotkey_S_F(self):
        bpy.ops.bim.flip_clipping_plane("INVOKE_DEFAULT")

    def hotkey_A_C(self):
        if LinksData.enable_culling:
            bpy.ops.bim.disable_culling()
        else:
            bpy.ops.bim.enable_culling("INVOKE_DEFAULT")

    def hotkey_S_M(self):
        for obj in tool.Blender.get_selected_objects():
            obj.select_set(False)
        measure_type = bpy.context.scene.MeasureToolSettings.measurement_type
        bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type=measure_type)
