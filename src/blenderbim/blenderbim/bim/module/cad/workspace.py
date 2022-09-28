# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import blenderbim.bim.module.type.prop as type_prop
from bpy.types import WorkSpaceTool
from blenderbim.bim.module.model.data import AuthoringData


class CadTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"

    bl_idname = "bim.cad_tool"
    bl_label = "CAD Tool"
    bl_description = "Gives you CAD authoring related superpowers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cad")
    bl_widget = None
    # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
    bl_keymap = (
        ("bim.cad_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.cad_hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.cad_hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.cad_hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.cad_hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.cad_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.cad_hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
    )

    def draw_settings(context, layout, tool):
        obj = context.active_object
        if obj and obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.is_profile:
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_Q")
            row.operator("bim.edit_extrusion_profile", text="Save Profile")
            row.operator("bim.disable_editing_extrusion_profile", text="", icon="CANCEL")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.cad_hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.cad_hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_C")
            row.operator("bim.add_ifccircle", text="Circle")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_V")
            row.operator("bim.set_arc_index", text="3-Point Arc")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")
            row.operator("bim.cad_hotkey", text="Offset").hotkey = "S_O"
        else:
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.cad_hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.cad_hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_F")
            row.operator("bim.cad_hotkey", text="Fillet").hotkey = "S_F"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")
            row.operator("bim.cad_hotkey", text="Offset").hotkey = "S_O"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="2-Point Arc", icon="EVENT_C")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_V")
            row.operator("bim.cad_hotkey", text="3-Point Arc").hotkey = "S_V"


class CadHotkey(bpy.types.Operator):
    bl_idname = "bim.cad_hotkey"
    bl_label = "CAD Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    radius: bpy.props.FloatProperty(name="Radius", default=0.1)
    distance: bpy.props.FloatProperty(name="Distance", default=0.1)

    def execute(self, context):
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def draw(self, context):
        if self.hotkey == "S_V":
            if not self.is_profile():
                row = self.layout.row()
                row.prop(self, "resolution")
        elif self.hotkey == "S_F":
            row = self.layout.row()
            row.prop(self, "resolution")
            row = self.layout.row()
            row.prop(self, "radius")
        elif self.hotkey == "S_O":
            row = self.layout.row()
            row.prop(self, "distance")

    def hotkey_S_C(self):
        if self.is_profile():
            bpy.ops.bim.add_ifccircle()
        else:
            bpy.ops.bim.cad_arc_from_2_points()

    def hotkey_S_E(self):
        bpy.ops.bim.cad_trim_extend()

    def hotkey_S_F(self):
        bpy.ops.bim.cad_fillet(resolution=self.resolution, radius=self.radius)

    def hotkey_S_O(self):
        bpy.ops.bim.cad_offset(distance=self.distance)

    def hotkey_S_Q(self):
        bpy.ops.bim.edit_extrusion_profile()

    def hotkey_S_T(self):
        bpy.ops.bim.cad_mitre()

    def hotkey_S_V(self):
        if self.is_profile():
            bpy.ops.bim.set_arc_index()
        else:
            bpy.ops.bim.cad_arc_from_3_points(resolution=self.resolution)

    def is_profile(self):
        obj = bpy.context.active_object
        return obj and obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.is_profile
