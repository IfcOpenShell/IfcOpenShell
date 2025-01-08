# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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
from bonsai.bim.module.model.data import AuthoringData
from bpy.types import WorkSpaceTool
import bonsai.core.spatial


class SpatialTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.spatial_tool"
    bl_label = "Spatial Tool"
    bl_description = "Gives you Spatial related superpowers"
    # TODO: replace with spatial icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.spatial")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.spatial_hotkey", {"type": "B", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_B")]}),
        ("bim.spatial_hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.spatial_hotkey", {"type": "B", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_B")]}),
        ("bim.spatial_hotkey", {"type": "V", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_V")]}),
        ("bim.spatial_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.spatial_hotkey", {"type": "G", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_G")]}),
        ("bim.spatial_hotkey", {"type": "H", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_H")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        SpatialToolUI.draw(context, layout)


def add_layout_hotkey(layout: bpy.types.UILayout, text: str, hotkey: str, description: str) -> None:
    args = ("spatial", layout, text, hotkey, description)
    tool.Blender.add_layout_hotkey_operator(*args)


class SpatialToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.model_props = context.scene.BIMModelProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        # if not SpatialData.is_loaded:
        #     SpatialData.load()

        if not AuthoringData.is_loaded:
            AuthoringData.load()

        cls.draw_type_selection_interface(context)
        cls.draw_default_interface(context)

        if context.active_object and context.selected_objects:
            cls.draw_selected_object_interface(context)

        add_layout_hotkey(cls.layout, "Decorate Boundaries", "A_V", bpy.ops.bim.decorate_boundaries.__doc__)

    @classmethod
    def draw_default_interface(cls, context):
        row = cls.layout.row(align=True)
        row.prop(data=cls.model_props, property="rl3", text="RL")
        row = cls.layout.row(align=True)
        op_name = lambda op: op.get_rna_type().name
        if AuthoringData.data["active_class"] == "IfcWall" and context.selected_objects:
            add_layout_hotkey(
                cls.layout,
                op_name(bpy.ops.bim.generate_spaces_from_walls),
                "S_A",
                bpy.ops.bim.generate_spaces_from_walls.__doc__,
            )
        else:
            add_layout_hotkey(
                cls.layout, op_name(bpy.ops.bim.generate_space), "S_A", bpy.ops.bim.generate_space.__doc__
            )
        add_layout_hotkey(
            cls.layout, op_name(bpy.ops.bim.toggle_space_visibility), "S_T", bpy.ops.bim.toggle_space_visibility.__doc__
        )
        add_layout_hotkey(
            cls.layout, op_name(bpy.ops.bim.toggle_hide_spaces), "S_H", bpy.ops.bim.toggle_hide_spaces.__doc__
        )

    @classmethod
    def draw_selected_object_interface(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element and bpy.context.selected_objects and element.is_a("IfcSpace"):
            add_layout_hotkey(cls.layout, "Regen", "S_G", bpy.ops.bim.generate_space.__doc__)

        row = cls.layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_B")
        row.prop(cls.model_props, "boundary_class", text="")
        row.operator("bim.add_boundary", text="Add Boundary")

        add_layout_hotkey(cls.layout, "Boundaries", "A_B", "Load/unload boundaries on selected objects")

    @classmethod
    def draw_type_selection_interface(cls, context):
        pass


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.spatial_hotkey"
    bl_label = "Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_A(self):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element and bpy.context.selected_objects and element.is_a("IfcWall"):
            bpy.ops.bim.generate_spaces_from_walls()
        else:
            try:
                bonsai.core.spatial.generate_space(tool.Ifc, tool.Model, tool.Root, tool.Spatial, tool.Type)
            except bonsai.core.spatial.SpaceGenerationError as e:
                return self.report({"ERROR"}, str(e))

    def hotkey_S_B(self):
        bpy.ops.bim.add_boundary()

    def hotkey_A_B(self):
        if not AuthoringData.is_loaded:
            AuthoringData.load()
        if not bpy.context.selected_objects:
            return
        if AuthoringData.data["has_visible_boundaries"]:
            bpy.ops.bim.hide_boundaries()
        else:
            bpy.ops.bim.show_boundaries()

    def hotkey_A_V(self):
        bpy.ops.bim.decorate_boundaries()

    def hotkey_S_T(self):
        bpy.ops.bim.toggle_space_visibility()

    def hotkey_S_H(self):
        bpy.ops.bim.toggle_hide_spaces()

    def hotkey_S_G(self):
        bpy.ops.bim.generate_space()
