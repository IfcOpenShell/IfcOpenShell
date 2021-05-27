import bpy
from bpy.types import WorkSpaceTool


class WallTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"

    bl_idname = "bim.wall_tool"
    bl_label = "Wall Tool"
    bl_description = "Gives you wall related superpowers"
    bl_icon = "ops.generic.select_circle"
    bl_widget = None
    # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
    bl_keymap = (
        # ("bim.wall_tool_op", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        # ("mesh.add_wall", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": []}),
        ("bim.add_wall", {"type": "A", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.join_wall", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("join_type", "T")]}),
        ("bim.join_wall", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("join_type", "L")]}),
        ("bim.join_wall", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("join_type", "V")]}),
        ("bim.flip_wall", {"type": "F", "value": "PRESS", "shift": True}, {"properties": []}),
        ("bim.split_wall", {"type": "S", "value": "PRESS", "shift": True}, {"properties": []}),
        (
            "bim.align_wall",
            {"type": "X", "value": "PRESS", "shift": True},
            {"properties": [("align_type", "EXTERIOR")]},
        ),
        (
            "bim.align_wall",
            {"type": "C", "value": "PRESS", "shift": True},
            {"properties": [("align_type", "CENTERLINE")]},
        ),
        (
            "bim.align_wall",
            {"type": "V", "value": "PRESS", "shift": True},
            {"properties": [("align_type", "INTERIOR")]},
        ),
    )

    def draw_settings(context, layout, tool):
        props = context.scene.BIMModelProperties
        row = layout.row(align=True)
        row.prop(props, "relating_type", text="")

        row.label(text="", icon="BLANK1")

        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="Add", icon="EVENT_A")
        row.label(text="Extend", icon="EVENT_E")
        row.label(text="Butt", icon="EVENT_T")
        row.label(text="Mitre", icon="EVENT_Y")
        row.label(text="Flip", icon="EVENT_F")
        row.label(text="Split", icon="EVENT_S")
        row.label(text="", icon="EVENT_X")
        row.label(text="", icon="EVENT_C")
        row.label(text="", icon="EVENT_V")
        row.label(text="Align")
