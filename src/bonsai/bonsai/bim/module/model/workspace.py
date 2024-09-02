# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import sys
import bpy
import bpy.utils.previews
import bonsai.tool as tool
import bonsai.core.model as core
from bonsai.bim.module.model.wall import DumbWallJoiner
from bonsai.bim.helper import prop_with_search
from bpy.types import WorkSpaceTool
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.system.data import PortData
from bonsai.bim.module.model.prop import get_ifc_class

custom_icon_previews = None


def load_custom_icons():
    global custom_icon_previews
    icons_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "icons")
    custom_icon_previews = bpy.utils.previews.new()
    for entry in os.scandir(icons_dir):
        if entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            custom_icon_previews.load(name.upper(), entry.path, "IMAGE")


def unload_custom_icons():
    global custom_icon_previews
    if custom_icon_previews:
        bpy.utils.previews.remove(custom_icon_previews)
        custom_icon_previews = None


class BimTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.bim_tool"
    bl_label = "BIM Tool"
    bl_description = "Create and edit elements by construction class"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.bim")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        # ("bim.wall_tool_op", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        # ("mesh.add_wall", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": []}),
        # ("bim.sync_modeling", {"type": 'MOUSEMOVE', "value": 'ANY'}, {"properties": []}),
        ("bim.hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.hotkey", {"type": "B", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_B")]}),
        ("bim.hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.hotkey", {"type": "G", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_G")]}),
        ("bim.hotkey", {"type": "K", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_K")]}),
        ("bim.hotkey", {"type": "M", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_M")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.hotkey", {"type": "P", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_P")]}),
        ("bim.hotkey", {"type": "L", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_L")]}),
        ("bim.hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.hotkey", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
        ("bim.hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
        ("bim.hotkey", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Y")]}),
        ("bim.hotkey", {"type": "D", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_D")]}),
        ("bim.hotkey", {"type": "E", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_E")]}),
        ("bim.hotkey", {"type": "O", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_O")]}),
        ("bim.hotkey", {"type": "P", "value": "PRESS", "ctrl": True}, {"properties": [("hotkey", "C_P")]}),
        ("bim.hotkey", {"type": "P", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_P")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        BimToolUI.draw(context, layout, ifc_element_type="all")


class WallTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.wall_tool"
    bl_label = "Wall Tool"
    bl_description = "Create and edit walls"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.wall")
    bl_widget = None
    ifc_element_type = "IfcWallType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class SlabTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.slab_tool"
    bl_label = "Slab Tool"
    bl_description = "Create and edit slabs"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.slab")
    bl_widget = None
    ifc_element_type = "IfcSlabType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class DoorTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.door_tool"
    bl_label = "Door Tool"
    bl_description = "Create and edit doors"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.door")
    bl_widget = None
    ifc_element_type = "IfcDoorType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class WindowTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.window_tool"
    bl_label = "Window Tool"
    bl_description = "Create and edit windows"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.window")
    bl_widget = None
    ifc_element_type = "IfcWindowType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class ColumnTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.column_tool"
    bl_label = "Column Tool"
    bl_description = "Create and edit columns"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.column")
    bl_widget = None
    ifc_element_type = "IfcColumnType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class BeamTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.beam_tool"
    bl_label = "Beam Tool"
    bl_description = "Create and edit beams"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.beam")
    bl_widget = None
    ifc_element_type = "IfcBeamType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class DuctTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.duct_tool"
    bl_label = "Duct Tool"
    bl_description = "Create and edit ducks"  # No, not a typo.
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.duct")
    bl_widget = None
    ifc_element_type = "IfcDuctSegmentType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class CableCarrierTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.cable_carrier_tool"
    bl_label = "Cable Carrier Tool"
    bl_description = "Create and edit cable carriers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cablecarrier")
    bl_widget = None
    ifc_element_type = "IfcCableCarrierSegmentType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class PipeTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.pipe_tool"
    bl_label = "Pipe Tool"
    bl_description = "Create and edit pipes"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.pipe")
    bl_widget = None
    ifc_element_type = "IfcPipeSegmentType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


class CableTool(BimTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.cable_tool"
    bl_label = "Cable Tool"
    bl_description = "Create and edit cables"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.cable")
    bl_widget = None
    ifc_element_type = "IfcCableSegmentType"

    @classmethod
    def draw_settings(cls, context, layout, ws_tool):
        BimToolUI.draw(context, layout, ifc_element_type=cls.ifc_element_type)


MODIFIERS = {
    "A": ("EVENT_ALT", "OPTION" if sys.platform == "Darwin" else "ALT"),
    "C": ("EVENT_CTRL", "CTRL"),
    "S": ("EVENT_SHIFT", "⇧"),
}


def add_layout_hotkey_operator(layout, text, hotkey, description, ui_context=""):
    modifier, key = hotkey.split("_")

    try:
        custom_icon = custom_icon_previews[text.upper().replace(" ", "_")].icon_id
    except KeyError:
        custom_icon = custom_icon_previews["IFC"].icon_id

    modifier_icon, modifier_str = MODIFIERS[modifier]

    if ui_context == "TOOL_HEADER":
        op = layout.operator("bim.hotkey", text="", icon_value=custom_icon)
    else:
        row = layout.row(align=True)
        op = row.operator("bim.hotkey", text=text, icon_value=custom_icon)
        row.label(text="", icon=modifier_icon)
        row.label(text="", icon=f"EVENT_{key}")

    hotkey_description = f"Hotkey: {modifier_str} {key}"
    if description:
        description += "\n\n"
    description += hotkey_description

    op.hotkey = hotkey
    op.description = description
    return op


class BimToolUI:
    @classmethod
    def draw(cls, context, layout, ifc_element_type=None):
        cls.layout = layout
        cls.props = context.scene.BIMModelProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not PortData.is_loaded:
            PortData.load()

        if not AuthoringData.is_loaded:
            AuthoringData.load(ifc_element_type)
        elif ifc_element_type == "all" and AuthoringData.data["ifc_element_type"] is not None:
            AuthoringData.load("all")
        elif AuthoringData.data["ifc_element_type"] != ifc_element_type:
            AuthoringData.load(ifc_element_type)

        if context.region.type == "TOOL_HEADER":
            cls.draw_container(context)
            cls.draw_type_selection_interface(context)
            if context.active_object and context.selected_objects:
                cls.draw_edit_object_header_interface(context)

        elif context.region.type in ("UI", "WINDOW"):
            cls.draw_container(context)
            cls.draw_thumbnail()
            cls.draw_type_selection_interface(context)
            if context.active_object and context.selected_objects:
                cls.draw_edit_object_panel_interface(context)

        if not context.selected_objects:
            cls.draw_create_object_interface()

    @classmethod
    def draw_create_object_interface(cls):
        if not AuthoringData.data["relating_type_id"]:
            return
        if cls.props.ifc_class == "IfcWallType":
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="rl1", text="RL")

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="extrusion_depth", text="Height")

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="length", text="Length")

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle")
        elif cls.props.ifc_class in ("IfcSlabType", "IfcRampType", "IfcRoofType"):
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle")
        elif cls.props.ifc_class in ("IfcColumnType", "IfcBeamType", "IfcMemberType"):
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="cardinal_point", text="Axis")

            row = cls.layout.row(align=True)
            label = "Height" if cls.props.ifc_class == "IfcColumn" else "Length"
            row.prop(data=cls.props, property="extrusion_depth", text=label)
        elif cls.props.ifc_class in ("IfcDoorType", "IfcDoorStyle"):
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="rl1", text="RL")
        elif cls.props.ifc_class in (
            "IfcWindowType",
            "IfcWindowStyle",
            "IfcDoorType",
            "IfcDoorStyle",
            "IfcDuctSegmentType",
            "IfcPipeSegmentType",
            "IfcCableCarrierSegmentType",
            "IfcCableSegmentType",
        ):
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="rl2", text="RL")
        elif cls.props.ifc_class in ("IfcSpaceType"):
            add_layout_hotkey_operator(cls.layout, "Generate", "S_G", bpy.ops.bim.generate_space.__doc__)
        else:
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="rl_mode", text="RL")

    @classmethod
    def draw_edit_object_panel_interface(cls, context):
        ui_context = str(context.region.type)
        if AuthoringData.data["active_material_usage"] == "LAYER2":
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="extrusion_depth", text="Height:")
            op = row.operator("bim.change_extrusion_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="length", text="Length:")
            op = row.operator("bim.change_layer_length", icon="FILE_REFRESH", text="")
            op.length = cls.props.length

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle:")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

            cls.layout.separator()

            add_layout_hotkey_operator(cls.layout, "Regen", "S_G", bpy.ops.bim.recalculate_wall.__doc__, ui_context)

            cls.layout.separator()

            add_layout_hotkey_operator(
                cls.layout,
                "Extend",
                "S_E",
                "Extends/reduces element to 3D cursor",
                ui_context,
            )
            add_layout_hotkey_operator(
                cls.layout,
                "Butt",
                "S_T",
                "Intersects two non-parallel elements to a butt corner junction",
                ui_context,
            )
            add_layout_hotkey_operator(
                cls.layout,
                "Mitre",
                "S_Y",
                "Intersects two non-parallel elements to a mitred corner junction",
                ui_context,
            )

            row = cls.layout.row(align=True)
            row.operator(
                "bim.unjoin_walls", text="Unjoin Walls", icon_value=custom_icon_previews["UNJOIN_WALLS"].icon_id
            )
            cls.layout.separator()

            add_layout_hotkey_operator(cls.layout, "Merge", "S_M", bpy.ops.bim.merge_wall.__doc__, ui_context)
            add_layout_hotkey_operator(cls.layout, "Split", "S_K", bpy.ops.bim.split_wall.__doc__, ui_context)
            add_layout_hotkey_operator(cls.layout, "Rotate 90", "S_R", bpy.ops.bim.rotate_90.__doc__, ui_context)
            add_layout_hotkey_operator(cls.layout, "Flip", "S_F", bpy.ops.bim.flip_wall.__doc__, ui_context)

            # row.operator("bim.unjoin_walls", icon="X", text="")

        elif AuthoringData.data["active_material_usage"] == "LAYER3":
            if len(context.selected_objects) == 1:
                add_layout_hotkey_operator(cls.layout, "Edit Profile", "S_E", "", ui_context)
            elif "LAYER2" in AuthoringData.data["selected_material_usages"]:
                add_layout_hotkey_operator(cls.layout, "Extend Wall To Slab", "S_E", "", ui_context)

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

        elif AuthoringData.data["active_material_usage"] == "PROFILE":
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="cardinal_point", text="Axis")
            op = row.operator("bim.change_cardinal_point", icon="FILE_REFRESH", text="")
            op.cardinal_point = int(cls.props.cardinal_point)

            row = cls.layout.row(align=True)
            label = (
                "Height" if AuthoringData.data["active_class"] in ("IfcColumn", "IfcColumnStandardCase") else "Length"
            )
            row.prop(data=cls.props, property="extrusion_depth", text=label)
            op = row.operator("bim.change_profile_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

            add_layout_hotkey_operator(
                cls.layout,
                "Extend",
                "S_E",
                "",
                ui_context,
            )
            add_layout_hotkey_operator(cls.layout, "Flip", "S_F", bpy.ops.bim.flip_object.__doc__, ui_context)

            if AuthoringData.data["active_class"] in (
                "IfcCableCarrierSegment",
                "IfcCableSegment",
                "IfcDuctSegment",
                "IfcPipeSegment",
            ):

                add_layout_hotkey_operator(cls.layout, "Add Fitting", "S_Y", "", ui_context)
                cls.layout.operator("bim.mep_add_bend")
                cls.layout.operator("bim.mep_add_transition")
                cls.layout.operator("bim.mep_add_obstruction")

            else:
                add_layout_hotkey_operator(
                    cls.layout,
                    "Edit Axis",
                    "A_E",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(
                    cls.layout,
                    "Butt",
                    "S_T",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(
                    cls.layout,
                    "Mitre",
                    "S_Y",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(cls.layout, "Rotate 90", "S_R", bpy.ops.bim.rotate_90.__doc__, ui_context)
                add_layout_hotkey_operator(
                    cls.layout, "Regen", "S_G", bpy.ops.bim.recalculate_profile.__doc__, ui_context
                )
            row.operator("bim.extend_profile", icon="X", text="").join_type = ""

        elif (
            tool.Model.is_parametric_railing_active() and not context.active_object.BIMRailingProperties.is_editing_path
        ):
            # NOTE: should be above "active_representation_type" = "SweptSolid" check
            # because it could be a SweptSolid too
            row = cls.layout.row(align=True)
            row.label(text="", icon="EVENT_TAB")
            row.operator("bim.enable_editing_railing_path", text="Edit Railing Path")

        elif AuthoringData.data["active_class"] in (
            "IfcWindow",
            "IfcWindowStandardCase",
            "IfcDoor",
            "IfcDoorStandardCase",
        ):
            if AuthoringData.data["active_class"] in ("IfcWindow", "IfcWindowStandardCase"):
                row = cls.layout.row(align=True)
                row.prop(data=cls.props, property="rl2", text="RL")
            elif AuthoringData.data["active_class"] in ("IfcDoor", "IfcDoorStandardCase"):
                row = cls.layout.row(align=True)
                row.prop(data=cls.props, property="rl1", text="RL")

            add_layout_hotkey_operator(cls.layout, "Regen", "S_G", bpy.ops.bim.recalculate_fill.__doc__, ui_context)
            add_layout_hotkey_operator(cls.layout, "Flip", "S_F", "", ui_context)

        elif AuthoringData.data["active_representation_type"] == "SweptSolid":
            if not tool.Model.is_parametric_window_active() and not tool.Model.is_parametric_door_active():
                add_layout_hotkey_operator(cls.layout, "Edit Profile", "S_E", "", ui_context)

        elif AuthoringData.data["active_class"] in ("IfcSpace",):
            add_layout_hotkey_operator(cls.layout, "Regen", "S_G", bpy.ops.bim.generate_space.__doc__, ui_context)

        elif tool.Model.is_parametric_roof_active() and not context.active_object.BIMRoofProperties.is_editing_path:
            row = cls.layout.row(align=True)
            row.label(text="", icon="EVENT_TAB")
            row.operator("bim.enable_editing_roof_path", text="Edit Roof Path")

        if context.region.type != "TOOL_HEADER" and PortData.data["total_ports"] > 0:
            add_layout_hotkey_operator(
                cls.layout, "Regen MEP", "S_G", bpy.ops.bim.regenerate_distribution_element.__doc__, ui_context
            )
            cls.layout.operator("bim.mep_connect_elements")

        row = cls.layout.row(align=True)
        if len(context.selected_objects) > 1:
            row.operator("bim.add_opening", text="Apply Void", icon_value=custom_icon_previews["VOID"].icon_id)
        else:
            row.operator(
                "bim.add_potential_opening", text="Add Void", icon_value=custom_icon_previews["ADD_VOID"].icon_id
            )
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="EVENT_O")

        if AuthoringData.data["is_voidable_element"]:
            if AuthoringData.data["has_visible_openings"]:
                row = cls.layout.row(align=True)
                row.operator("bim.edit_openings", icon="CHECKMARK", text="")
                row.operator("bim.hide_openings", icon="CANCEL", text="")

        if AuthoringData.data["active_class"] in ("IfcOpeningElement",):
            row.operator("bim.edit_openings", icon="CHECKMARK", text="")
            row.operator("bim.hide_openings", icon="CANCEL", text="")
            if len(context.selected_objects) == 2:
                row = cls.layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_L")
                row.operator("bim.clone_opening", text="Clone Opening")

        cls.layout.row(align=True).label(text="Align")
        add_layout_hotkey_operator(cls.layout, "Exterior", "S_X", "", ui_context)
        add_layout_hotkey_operator(cls.layout, "Centerline", "S_C", "", ui_context)
        add_layout_hotkey_operator(cls.layout, "Interior", "S_V", "", ui_context)
        add_layout_hotkey_operator(cls.layout, "Mirror", "S_M", bpy.ops.bim.mirror_elements.__doc__, ui_context)

        cls.layout.row(align=True).label(text="Mode")
        add_layout_hotkey_operator(cls.layout, "Void", "A_O", "Toggle openings", ui_context)
        add_layout_hotkey_operator(cls.layout, "Decomposition", "A_D", "Select decomposition", ui_context)

        cls.layout.row(align=True).label(text="Aggregation")
        add_layout_hotkey_operator(cls.layout, "Assign", "C_P", bpy.ops.bim.aggregate_assign_object.__doc__, ui_context)
        add_layout_hotkey_operator(
            cls.layout, "Unassign", "A_P", bpy.ops.bim.aggregate_unassign_object.__doc__, ui_context
        )

        cls.layout.row(align=True).label(text="Qto")
        add_layout_hotkey_operator(
            cls.layout, "Perform Quantity Take-off", "S_Q", bpy.ops.bim.perform_quantity_take_off.__doc__, ui_context
        )

    @classmethod
    def draw_edit_object_header_interface(cls, context):
        ui_context = str(context.region.type)
        if AuthoringData.data["active_material_usage"] == "LAYER2":
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="extrusion_depth", text="Height:")
            op = row.operator("bim.change_extrusion_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="length", text="Length:")
            op = row.operator("bim.change_layer_length", icon="FILE_REFRESH", text="")
            op.length = cls.props.length

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle:")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

            row = cls.layout.row()
            add_layout_hotkey_operator(row, "Regen", "S_G", bpy.ops.bim.recalculate_wall.__doc__, ui_context)

            row = cls.layout.row(align=True)
            add_layout_hotkey_operator(
                row,
                "Extend",
                "S_E",
                "Extends/reduces element to 3D cursor",
                ui_context,
            )
            add_layout_hotkey_operator(
                row,
                "Butt",
                "S_T",
                "Intersects two non-parallel elements to a butt corner junction",
                ui_context,
            )
            add_layout_hotkey_operator(
                row,
                "Mitre",
                "S_Y",
                "Intersects two non-parallel elements to a mitred corner junction",
                ui_context,
            )
            row.operator("bim.unjoin_walls", text="", icon_value=custom_icon_previews["UNJOIN_WALLS"].icon_id)

            row = cls.layout.row(align=True)
            add_layout_hotkey_operator(row, "Merge", "S_M", bpy.ops.bim.merge_wall.__doc__, ui_context)
            add_layout_hotkey_operator(row, "Split", "S_K", bpy.ops.bim.split_wall.__doc__, ui_context)
            add_layout_hotkey_operator(row, "Rotate 90", "S_R", bpy.ops.bim.rotate_90.__doc__, ui_context)
            add_layout_hotkey_operator(row, "Flip", "S_F", bpy.ops.bim.flip_wall.__doc__, ui_context)

        elif AuthoringData.data["active_material_usage"] == "LAYER3":
            if len(context.selected_objects) == 1:
                add_layout_hotkey_operator(cls.layout, "Edit Profile", "S_E", "", ui_context)
            elif "LAYER2" in AuthoringData.data["selected_material_usages"]:
                add_layout_hotkey_operator(cls.layout, "Extend Wall To Slab", "S_E", "", ui_context)

            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="x_angle", text="Angle")
            op = row.operator("bim.change_extrusion_x_angle", icon="FILE_REFRESH", text="")
            op.x_angle = cls.props.x_angle

        elif AuthoringData.data["active_material_usage"] == "PROFILE":
            row = cls.layout.row(align=True)
            row.prop(data=cls.props, property="cardinal_point", text="Axis")
            op = row.operator("bim.change_cardinal_point", icon="FILE_REFRESH", text="")
            op.cardinal_point = int(cls.props.cardinal_point)

            row = cls.layout.row(align=True)
            label = (
                "Height" if AuthoringData.data["active_class"] in ("IfcColumn", "IfcColumnStandardCase") else "Length"
            )
            row.prop(data=cls.props, property="extrusion_depth", text=label)
            op = row.operator("bim.change_profile_depth", icon="FILE_REFRESH", text="")
            op.depth = cls.props.extrusion_depth

            add_layout_hotkey_operator(
                cls.layout,
                "Extend",
                "S_E",
                "",
                ui_context,
            )
            add_layout_hotkey_operator(cls.layout, "Flip", "S_F", bpy.ops.bim.flip_object.__doc__, ui_context)

            if AuthoringData.data["active_class"] in (
                "IfcCableCarrierSegment",
                "IfcCableSegment",
                "IfcDuctSegment",
                "IfcPipeSegment",
            ):

                add_layout_hotkey_operator(cls.layout, "Add Fitting", "S_Y", "", ui_context)
                if context.region.type != "TOOL_HEADER":
                    cls.layout.operator("bim.mep_add_bend")
                    cls.layout.operator("bim.mep_add_transition")
                    cls.layout.operator("bim.mep_add_obstruction")

            else:
                add_layout_hotkey_operator(
                    cls.layout,
                    "Edit Axis",
                    "A_E",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(
                    cls.layout,
                    "Butt",
                    "S_T",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(
                    cls.layout,
                    "Mitre",
                    "S_Y",
                    "",
                    ui_context,
                )
                add_layout_hotkey_operator(cls.layout, "Rotate 90", "S_R", bpy.ops.bim.rotate_90.__doc__, ui_context)
                add_layout_hotkey_operator(
                    cls.layout, "Regen", "S_G", bpy.ops.bim.recalculate_profile.__doc__, ui_context
                )
            row.operator("bim.extend_profile", icon="X", text="").join_type = ""

        elif (
            tool.Model.is_parametric_railing_active() and not context.active_object.BIMRailingProperties.is_editing_path
        ):
            # NOTE: should be above "active_representation_type" = "SweptSolid" check
            # because it could be a SweptSolid too
            row = cls.layout.row(align=True)
            row.label(text="", icon="EVENT_TAB")
            row.operator("bim.enable_editing_railing_path", text="Edit Railing Path")

        elif AuthoringData.data["active_class"] in (
            "IfcWindow",
            "IfcWindowStandardCase",
            "IfcDoor",
            "IfcDoorStandardCase",
        ):
            if AuthoringData.data["active_class"] in ("IfcWindow", "IfcWindowStandardCase"):
                row = cls.layout.row(align=True)
                row.prop(data=cls.props, property="rl2", text="RL")
            elif AuthoringData.data["active_class"] in ("IfcDoor", "IfcDoorStandardCase"):
                row = cls.layout.row(align=True)
                row.prop(data=cls.props, property="rl1", text="RL")

            add_layout_hotkey_operator(cls.layout, "Regen", "S_G", bpy.ops.bim.recalculate_fill.__doc__, ui_context)
            add_layout_hotkey_operator(cls.layout, "Flip", "S_F", "", ui_context)

        elif AuthoringData.data["active_representation_type"] == "SweptSolid":
            if not tool.Model.is_parametric_window_active() and not tool.Model.is_parametric_door_active():
                add_layout_hotkey_operator(cls.layout, "Edit Profile", "S_E", "", ui_context)

        elif AuthoringData.data["active_class"] in ("IfcSpace",):
            add_layout_hotkey_operator(cls.layout, "Regen", "S_G", bpy.ops.bim.generate_space.__doc__, ui_context)

        elif tool.Model.is_parametric_roof_active() and not context.active_object.BIMRoofProperties.is_editing_path:
            row = cls.layout.row(align=True)
            row.label(text="", icon="EVENT_TAB")
            row.operator("bim.enable_editing_roof_path", text="Edit Roof Path")

        if context.region.type != "TOOL_HEADER" and PortData.data["total_ports"] > 0:
            add_layout_hotkey_operator(
                cls.layout, "Regen MEP", "S_G", bpy.ops.bim.regenerate_distribution_element.__doc__, ui_context
            )
            cls.layout.operator("bim.mep_connect_elements")

        row = cls.layout.row(align=True)
        if len(context.selected_objects) > 1:
            row.operator("bim.add_opening", text="", icon_value=custom_icon_previews["VOID"].icon_id)
        else:
            row.operator("bim.add_potential_opening", text="", icon_value=custom_icon_previews["ADD_VOID"].icon_id)

        if AuthoringData.data["is_voidable_element"]:
            if AuthoringData.data["has_visible_openings"]:
                row = cls.layout.row(align=True)
                row.operator("bim.edit_openings", icon="CHECKMARK", text="")
                row.operator("bim.hide_openings", icon="CANCEL", text="")

        if AuthoringData.data["active_class"] in ("IfcOpeningElement",):
            row.operator("bim.edit_openings", icon="CHECKMARK", text="")
            row.operator("bim.hide_openings", icon="CANCEL", text="")
            if len(context.selected_objects) == 2:
                row = cls.layout.row(align=True)
                row.label(text="", icon="EVENT_SHIFT")
                row.label(text="", icon="EVENT_L")
                row.operator("bim.clone_opening", text="Clone Opening")

        row = cls.layout.row(align=True)
        add_layout_hotkey_operator(row, "Exterior", "S_X", "", ui_context)
        add_layout_hotkey_operator(row, "Centerline", "S_C", "", ui_context)
        add_layout_hotkey_operator(row, "Interior", "S_V", "", ui_context)
        add_layout_hotkey_operator(row, "Mirror", "S_M", bpy.ops.bim.mirror_elements.__doc__, ui_context)

        row = cls.layout.row(align=True)
        add_layout_hotkey_operator(row, "Void", "A_O", "Toggle openings", ui_context)
        add_layout_hotkey_operator(row, "Decomposition", "A_D", "Select decomposition", ui_context)

        row = cls.layout.row(align=True)
        add_layout_hotkey_operator(row, "Assign", "C_P", bpy.ops.bim.aggregate_assign_object.__doc__, ui_context)
        add_layout_hotkey_operator(row, "Unassign", "A_P", bpy.ops.bim.aggregate_unassign_object.__doc__, ui_context)

        row = cls.layout.row()
        add_layout_hotkey_operator(
            row, "Perform Quantity Take-off", "S_Q", bpy.ops.bim.perform_quantity_take_off.__doc__, ui_context
        )

    @classmethod
    def draw_container(cls, context):
        text = AuthoringData.data["default_container"]
        if context.region.type == "UI":
            text = f"Container: {text}"

        cls.layout.row(align=True).label(text=text, icon="OUTLINER_COLLECTION")

    @classmethod
    def draw_type_selection_interface(cls, context):
        # shared by both sidebar and header
        ui_context = str(context.region.type)
        row = cls.layout.row(align=True)
        if AuthoringData.data["ifc_classes"]:
            if ui_context == "UI":
                text = "Add"
            else:
                text = ""
            if not AuthoringData.data["ifc_element_type"]:
                prop_with_search(row, cls.props, "ifc_class", text="")

            row = cls.layout.row(align=True)
            if AuthoringData.data["relating_type_id"]:
                prop_with_search(row, cls.props, "relating_type_id", text="")
                row.operator("bim.add_constr_type_instance", text=text, icon_value=custom_icon_previews["ADD"].icon_id)

            else:
                row.label(text="No Construction Type", icon="FILE_3D")
            row.operator("bim.launch_type_manager", icon=tool.Blender.TYPE_MANAGER_ICON, text="")
        else:
            if AuthoringData.data["ifc_element_type"]:
                row.label(text=f"No {AuthoringData.data['ifc_element_type']} Found", icon="ERROR")
                row = cls.layout.row()
                row.prop(cls.props, "type_name")
                row = cls.layout.row(align=True)
                op = row.operator(
                    "bim.add_default_type",
                    icon_value=custom_icon_previews["ADD_TYPE"].icon_id,
                    text=f"Create {AuthoringData.data['ifc_element_type']}",
                )
                op.ifc_element_type = AuthoringData.data["ifc_element_type"]
                row.operator("bim.launch_type_manager", icon=tool.Blender.TYPE_MANAGER_ICON, text="")
            else:
                row.label(text="No Element Types Found", icon="ERROR")
                row.operator("bim.launch_type_manager", icon=tool.Blender.TYPE_MANAGER_ICON, text="Launch Type Manager")

    @classmethod
    def draw_thumbnail(cls):
        if AuthoringData.data["ifc_classes"]:
            if cls.props.ifc_class:
                box = cls.layout.box()
                if AuthoringData.data["type_thumbnail"]:
                    box.template_icon(icon_value=AuthoringData.data["type_thumbnail"], scale=5)
                else:
                    op = box.operator("bim.load_type_thumbnails", text="Load Thumbnails", icon="FILE_REFRESH")
                    op.ifc_class = cls.props.ifc_class


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.hotkey"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    x: bpy.props.FloatProperty(name="X", default=0.5)
    y: bpy.props.FloatProperty(name="Y", default=0.5)
    z: bpy.props.FloatProperty(name="Z", default=0.5)

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
        self.props = context.scene.BIMModelProperties
        self.has_ifc_class = True

        self.active_class = None
        self.active_material_usage = None
        element = tool.Ifc.get_entity(context.active_object)
        if element:
            self.active_class = element.is_a()
            self.active_material_usage = tool.Model.get_usage_type(element)

        if get_ifc_class(None, None):
            try:
                self.has_ifc_class = bool(self.props.ifc_class)
            except:
                pass
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        self.props = context.scene.BIMModelProperties
        self.x = self.props.x
        self.y = self.props.y
        self.z = self.props.z
        return self.execute(context)

    def draw(self, context):
        if self.hotkey == "S_O":
            row = self.layout.row()
            row.prop(self, "x")
            row = self.layout.row()
            row.prop(self, "y")
            row = self.layout.row()
            row.prop(self, "z")

    def hotkey_S_A(self):
        bpy.ops.bim.add_constr_type_instance()

    def hotkey_S_Q(self):
        if not bpy.context.selected_objects:
            return

        bpy.ops.bim.perform_quantity_take_off()

    def hotkey_C_P(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.aggregate_assign_object()

    def hotkey_A_P(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.aggregate_unassign_object()

    def hotkey_S_C(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            if bpy.ops.bim.align_wall.poll():
                bpy.ops.bim.align_wall(align_type="CENTERLINE")
        else:
            bpy.ops.bim.align_product(align_type="CENTERLINE")

    def hotkey_S_E(self):
        if not bpy.context.selected_objects:
            return

        # NOTE: placing it before the other operations because railing can also be SweptSolid
        # and it might conflict with one of the conditions below
        if (
            tool.Model.is_parametric_railing_active()
            and not bpy.context.active_object.BIMRailingProperties.is_editing_path
        ):
            bpy.ops.bim.enable_editing_railing_path()
            return

        elif tool.Model.is_parametric_roof_active() and not bpy.context.active_object.BIMRoofProperties.is_editing_path:
            # undo the unselection done above because roof has no usage type
            bpy.ops.bim.enable_editing_roof_path()
            return

        elif tool.Model.is_parametric_window_active() or tool.Model.is_parametric_door_active():
            return

        selected_usages = {}
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                obj.select_set(False)
                continue
            usage = tool.Model.get_usage_type(element)
            if not usage:
                representation = tool.Geometry.get_active_representation(obj)
                representation = tool.Geometry.resolve_mapped_representation(representation)
                if representation and representation.RepresentationType == "SweptSolid":
                    usage = "SWEPTSOLID"
                else:
                    obj.select_set(False)
                    continue
            selected_usages.setdefault(usage, []).append(obj)

        if len(bpy.context.selected_objects) == 1:
            if self.active_material_usage == "LAYER3":
                # Edit LAYER3 profile
                if bpy.context.active_object and bpy.context.active_object.mode == "OBJECT":
                    bpy.ops.bim.enable_editing_extrusion_profile()
            elif self.active_material_usage == "LAYER2":
                # Extend LAYER2 to cursor
                core.extend_walls(
                    tool.Ifc,
                    tool.Blender,
                    tool.Geometry,
                    DumbWallJoiner(),
                    tool.Model,
                    bpy.context.scene.cursor.location,
                )
            elif self.active_material_usage == "PROFILE":
                # Extend PROFILE to cursor
                bpy.ops.bim.extend_profile(join_type="T")
            else:
                # Edit SWEPTSOLID profile (assuming single profile for now)
                bpy.ops.bim.enable_editing_extrusion_profile()

        elif self.active_material_usage == "LAYER2" and selected_usages.get("PROFILE", []):
            # Extend PROFILEs to LAYER2
            [o.select_set(False) for o in selected_usages.get("LAYER3", [])]
            [o.select_set(False) for o in selected_usages.get("LAYER2", []) if o != bpy.context.active_object]
            bpy.ops.bim.extend_profile(join_type="T")

        elif self.active_material_usage == "LAYER3" and selected_usages.get("LAYER2", []):
            # Extend LAYER2s to LAYER3
            [o.select_set(False) for o in selected_usages.get("PROFILE", [])]
            [o.select_set(False) for o in selected_usages.get("LAYER3", []) if o != bpy.context.active_object]
            try:
                core.join_walls_TZ(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
            except core.RequireAtLeastTwoLayeredElements as e:
                self.report({"ERROR"}, str(e))

        elif self.active_material_usage == "LAYER2":
            # Extend LAYER2s to LAYER2
            [o.select_set(False) for o in selected_usages.get("LAYER3", [])]
            [o.select_set(False) for o in selected_usages.get("PROFILE", [])]
            try:
                core.join_walls_TZ(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model)
            except core.RequireAtLeastTwoLayeredElements as e:
                self.report({"ERROR"}, str(e))

        elif self.active_material_usage == "PROFILE":
            # Extend PROFILEs to PROFILE
            [o.select_set(False) for o in selected_usages.get("LAYER3", [])]
            [o.select_set(False) for o in selected_usages.get("LAYER2", [])]
            bpy.ops.bim.extend_profile(join_type="T")

    def hotkey_S_F(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.flip_wall()
        elif self.active_class in ("IfcWindow", "IfcWindowStandardCase", "IfcDoor", "IfcDoorStandardCase"):
            bpy.ops.bim.flip_fill()
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.flip_object(flip_local_axes="XZ")

    def hotkey_S_G(self):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not bpy.context.selected_objects:
            if self.props.ifc_class == "IfcSpaceType":
                bpy.ops.bim.generate_space()
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.recalculate_wall()
        elif tool.System.get_ports(element):
            bpy.ops.bim.regenerate_distribution_element()
        elif self.active_material_usage == "PROFILE":
            if self.active_class not in (
                "IfcCableCarrierSegment",
                "IfcCableSegment",
                "IfcDuctSegment",
                "IfcPipeSegment",
            ):
                bpy.ops.bim.recalculate_profile()
        elif self.active_class in ("IfcWindow", "IfcWindowStandardCase", "IfcDoor", "IfcDoorStandardCase"):
            bpy.ops.bim.recalculate_fill()
        elif self.active_class in ("IfcSpace"):
            bpy.ops.bim.generate_space()

    def hotkey_S_M(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.merge_wall()
        else:
            if len(bpy.context.selected_objects) == 1:
                self.report(
                    {"ERROR"},
                    "At least two objects must be selected: an object to be mirrored, and a mirror axis as the active object.",
                )
            else:
                bpy.ops.bim.mirror_elements()

    def hotkey_S_R(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.active_class in ("IfcColumn", "IfcColumnStandardCase"):
            bpy.ops.bim.rotate_90(axis="Z")
        elif self.active_class in ("IfcBeam", "IfcBeamStandardCase", "IfcMember", "IfcMemberStandardCase"):
            bpy.ops.bim.rotate_90(axis="Y")

    def hotkey_S_K(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.split_wall()

    def hotkey_S_T(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            try:
                core.join_walls_LV(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model, join_type="L")
            except core.RequireTwoWallsError as e:
                self.report({"ERROR"}, str(e))
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.extend_profile(join_type="L")

    def hotkey_S_V(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            bpy.ops.bim.align_wall(align_type="INTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="POSITIVE")

    def hotkey_S_X(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            if bpy.ops.bim.align_wall.poll():
                bpy.ops.bim.align_wall(align_type="EXTERIOR")
        else:
            bpy.ops.bim.align_product(align_type="NEGATIVE")

    def hotkey_S_Y(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "LAYER2":
            try:
                core.join_walls_LV(tool.Ifc, tool.Blender, tool.Geometry, DumbWallJoiner(), tool.Model, join_type="V")
            except core.RequireTwoWallsError as e:
                self.report({"ERROR"}, str(e))
        elif self.active_class in ("IfcDuctSegment", "IfcPipeSegment", "IfcCableCarrierSegment", "IfcCableSegment"):
            bpy.ops.bim.fit_flow_segments()
        elif self.active_material_usage == "PROFILE":
            bpy.ops.bim.extend_profile(join_type="V")

    def hotkey_S_B(self):
        bpy.ops.bim.add_boundary()

    def hotkey_S_O(self):
        if len(bpy.context.selected_objects) == 2:
            bpy.ops.bim.add_opening()
        else:
            bpy.ops.bim.add_potential_opening(x=self.x, y=self.y, z=self.z)
            self.props.x = self.x
            self.props.y = self.y
            self.props.z = self.z

    def hotkey_S_P(self):
        mode = bpy.context.mode
        current_tool = bpy.context.workspace.tools.from_space_view3d_mode(mode)
        if current_tool.idname == "bim.wall_tool":
            bpy.ops.bim.draw_polyline_wall("INVOKE_DEFAULT")

    def hotkey_S_L(self):
        if AuthoringData.data["active_class"] in ("IfcOpeningElement",):
            if len(bpy.context.selected_objects) == 2:
                bpy.ops.bim.clone_opening()

    def hotkey_A_D(self):
        if not bpy.context.selected_objects:
            return
        bpy.ops.bim.select_decomposition()

    def hotkey_A_E(self):
        if not bpy.context.selected_objects:
            return
        if self.active_material_usage == "PROFILE":
            bpy.ops.bim.enable_editing_extrusion_axis()

    def hotkey_A_O(self):
        if not bpy.context.selected_objects:
            return
        if AuthoringData.data["has_visible_openings"]:
            bpy.ops.bim.edit_openings()
        else:
            bpy.ops.bim.show_openings()


LIST_OF_TOOLS = [cls.bl_idname for cls in (BimTool.__subclasses__() + [BimTool])]
TOOLS_TO_CLASSES_MAP = {cls.bl_idname: cls.ifc_element_type for cls in BimTool.__subclasses__()}
