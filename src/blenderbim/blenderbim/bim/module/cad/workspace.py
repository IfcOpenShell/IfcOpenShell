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
from blenderbim.bim.ifc import IfcStore
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
        ("bim.cad_hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.cad_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.cad_hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.cad_fillet", {"type": "F", "value": "PRESS", "shift": True}, {"properties": []}),
        # Enable Mesh Tools add-on to get this amazing tool
        ("mesh.offset_edges", {"type": "O", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.cad_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
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
            row.operator("bim.hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_C")
            row.operator("bim.add_ifccircle", text="Circle")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_V")
            row.operator("bim.set_arc_index", text="3-Point Arc")
        else:
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_E")
            row.operator("bim.hotkey", text="Extend").hotkey = "S_E"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_T")
            row.operator("bim.hotkey", text="Mitre").hotkey = "S_T"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_F")
            row.operator("bim.hotkey", text="Fillet").hotkey = "S_F"

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Offset", icon="EVENT_O")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="2-Point Arc", icon="EVENT_C")

            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="3-Point Arc", icon="EVENT_V")


class CadHotkey(bpy.types.Operator):
    bl_idname = "bim.cad_hotkey"
    bl_label = "CAD Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMModelProperties
        self.has_ifc_class = True
        try:
            self.has_ifc_class = bool(self.props.ifc_class)
        except:
            pass
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def hotkey_S_C(self):
        if self.is_profile():
            bpy.ops.bim.add_ifccircle()
        else:
            bpy.ops.bim.cad_arc_from_2_points()

    def hotkey_S_E(self):
        bpy.ops.bim.cad_trim_extend()

    def hotkey_S_Q(self):
        bpy.ops.bim.edit_extrusion_profile()

    def hotkey_S_T(self):
        bpy.ops.bim.cad_mitre()

    def hotkey_S_V(self):
        if self.is_profile():
            bpy.ops.bim.set_arc_index()
        else:
            bpy.ops.bim.cad_arc_from_3_points()

    def is_profile(self):
        obj = bpy.context.active_object
        return obj and obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.is_profile
