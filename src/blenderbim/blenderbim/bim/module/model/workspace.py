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
        ("bim.hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.join_wall", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("join_type", "L")]}),
        ("bim.join_wall", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("join_type", "V")]}),
        ("bim.flip_wall", {"type": "F", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.split_wall", {"type": "S", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
        ("bim.hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_O")]}),
    )

    def draw_settings(context, layout, tool):
        row = layout.row(align=True)
        props = context.scene.BIMTypeProperties
        row.prop(props, "ifc_class", text="")
        row.prop(props, "relating_type", text="")

        row.label(text="", icon="BLANK1")

        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Add Type Instance", icon="EVENT_A")

        if props.ifc_class == "IfcWallType":
            row = layout.row(align=True)
            row.label(text="Join")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Extend", icon="EVENT_E")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Butt", icon="EVENT_T")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Mitre", icon="EVENT_Y")

            row = layout.row(align=True)
            row.label(text="Wall Tools")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Flip", icon="EVENT_F")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Split", icon="EVENT_S")
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Opening", icon="EVENT_O")

        if props.ifc_class == "IfcSlabType":
            row = layout.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="Opening", icon="EVENT_O")

        row = layout.row(align=True)
        row.label(text="Align")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Exterior", icon="EVENT_X")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Centerline", icon="EVENT_C")
        row = layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Align Interior", icon="EVENT_V")
        row = layout.row(align=True)

        row = layout.row(align=True)
        row.label(text="", icon="EVENT_ALT")
        row.label(text="Opening", icon="EVENT_O")


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

    def hotkey_S_C(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="CENTERLINE")
        else:
            bpy.ops.bim.align_product(align_type="CENTERLINE")

    def hotkey_S_E(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.join_wall(join_type="T")

    def hotkey_S_V(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="INTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="POSITIVE")

    def hotkey_S_X(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.align_wall(align_type="EXTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="NEGATIVE")

    def hotkey_S_O(self):
        if self.props.ifc_class == "IfcWallType":
            bpy.ops.bim.add_wall_opening()
        elif self.props.ifc_class == "IfcSlabType":
            bpy.ops.bim.add_slab_opening()

    def hotkey_A_O(self):
        bpy.ops.bim.toggle_opening_visibility()
