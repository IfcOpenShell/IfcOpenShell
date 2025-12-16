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
        ("bim.explore_hotkey", {"type": "S", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_S")]}),
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

        prop = tool.Project.get_measure_tool_settings()
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_M")
        row = layout.row(align=True)
        op = row.operator("bim.explore_hotkey", text="Measure Tool", icon="CON_DISTLIMIT")
        op.hotkey = "S_M"
        row = layout.row(align=True)
        row.prop(prop, "measurement_type", text="Measure Type", expand=True, icon_only=True, emboss=True)
        row = layout.row(align=True)
        op = row.operator("bim.clear_measurement", text="", icon="X")

        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_S")
        row = layout.row(align=True)
        op = row.operator("bim.explore_hotkey", text="Image Scaling Tool", icon="IMAGE_PLANE")
        op.hotkey = "S_S"
        op.description = "Scale Image Annotation. Allows to scale an IfcReferenceImage. Select image, select tool. Check lower left corner instructions to select two points and provide real distance between them"


class ExploreHotkey(bpy.types.Operator):
    bl_idname = "bim.explore_hotkey"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
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
        measure_type = tool.Project.get_measure_tool_settings().measurement_type
        if measure_type == "FACE_AREA":
            bpy.ops.bim.measure_face_area_tool("INVOKE_DEFAULT")
        else:
            bpy.ops.bim.measure_tool("INVOKE_DEFAULT", measure_type=measure_type)

    def hotkey_S_S(self):
        active_obj = bpy.context.active_object
        selected_objects = tool.Blender.get_selected_objects()
        element = tool.Ifc.get_entity(active_obj) if active_obj else None

        if (
            not active_obj
            or not element
            or not element.is_a("IfcAnnotation")
            or len(selected_objects) != 1
            or not tool.Drawing.is_annotation_object_type(element, "IMAGE")
        ):
            self.report({"ERROR"}, "Please select one image annotation first.")
            return

        bpy.ops.bim.image_scaling_tool("INVOKE_DEFAULT")
