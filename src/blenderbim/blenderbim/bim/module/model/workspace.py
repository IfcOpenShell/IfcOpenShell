import os
import bpy
from bpy.types import WorkSpaceTool
from blenderbim.bim.ifc import IfcStore


class BimTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"

    bl_idname = "bim.bim_tool"
    bl_label = "BIM Tool"
    bl_description = "Gives you BIM authoring related superpowers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.bim")
    bl_widget = None
    # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
    bl_keymap = (
        # ("bim.wall_tool_op", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        # ("mesh.add_wall", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": []}),
        ("bim.add_type_instance", {"type": "A", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "E")]}),
        ("bim.join_wall", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("join_type", "L")]}),
        ("bim.join_wall", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("join_type", "V")]}),
        ("bim.flip_wall", {"type": "F", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.split_wall", {"type": "S", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "X")]}),
        ("bim.hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "C")]}),
        ("bim.hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "V")]}),
    )

    def draw_settings(context, layout, tool):
        row = layout.row(align=True)
        props = context.scene.BIMTypeProperties
        row.prop(props, "ifc_class", text="")
        row.prop(props, "relating_type", text="")

        row.label(text="", icon="BLANK1")

        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Add", icon="EVENT_A")

        if props.ifc_class == "IfcWallType":
            row.label(text="Extend", icon="EVENT_E")
            row.label(text="Butt", icon="EVENT_T")
            row.label(text="Mitre", icon="EVENT_Y")
            row.label(text="Flip", icon="EVENT_F")
            row.label(text="Split", icon="EVENT_S")

        row.label(text="", icon="EVENT_X")
        row.label(text="", icon="EVENT_C")
        row.label(text="", icon="EVENT_V")
        row.label(text="Align")


class Hotkey(bpy.types.Operator):
    bl_idname = "bim.hotkey"
    bl_label = "Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMTypeProperties
        getattr(self, f"hotkey_{self.hotkey}")()
        return {"FINISHED"}

    def hotkey_C(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="CENTERLINE")
        else:
            bpy.ops.bim.align_product(align_type="CENTERLINE")

    def hotkey_E(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.join_wall(join_type="T")

    def hotkey_V(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="INTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="POSITIVE")

    def hotkey_X(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="EXTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="NEGATIVE")
