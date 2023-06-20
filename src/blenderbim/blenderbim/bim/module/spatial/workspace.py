# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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
import blenderbim.tool as tool
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.model.data import AuthoringData
from bpy.types import WorkSpaceTool
from blenderbim.bim.ifc import IfcStore
import blenderbim.bim.handler


# declaring it here to avoid circular import problems
class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


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
        ("bim.spatial_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        SpatialToolUI.draw(context, layout)


def add_layout_hotkey(layout, text, hotkey, description):
    args = ["spatial", layout, text, hotkey, description]
    tool.Blender.add_layout_hotkey_operator(*args)


# NOTES before adding new operators:
# - add scene.BIMSpatialProperties
# - add SpatialData


class SpatialToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        # cls.props = context.scene.BIMSpatialProperties
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

    @classmethod
    def draw_default_interface(cls, context):
        row = cls.layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_A")
        if context.selected_objects:
            row.operator("bim.generate_spaces_from_walls")
        else:
            row.operator("bim.generate_space")
        row = cls.layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_T")
        row.operator("bim.toggle_space_visibility")

    @classmethod
    def draw_selected_object_interface(cls, context):
        row = cls.layout.row(align=True)
        row.label(text="", icon="EVENT_SHIFT")
        row.label(text="", icon="EVENT_B")
        row.prop(cls.model_props, "boundary_class", text="")
        row.operator("bim.add_boundary", text="Add Boundary")

        add_layout_hotkey(cls.layout, "Boundaries", "A_B", "Toggle boundaries")

    @classmethod
    def draw_type_selection_interface(cls, context):
        pass


class Hotkey(bpy.types.Operator, Operator):
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
        # self.props = context.scene.BIMSpatialProperties
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        # self.props = context.scene.BIMSpatialProperties
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_A(self):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element and bpy.context.selected_objects and element.is_a("IfcWall"):
            bpy.ops.bim.generate_spaces_from_walls()
        else:
            bpy.ops.bim.generate_space()

    def hotkey_S_B(self):
        bpy.ops.bim.add_boundary()

    def hotkey_A_B(self):
        if not bpy.context.selected_objects:
            return
        if AuthoringData.data["has_visible_boundaries"]:
            bpy.ops.bim.hide_boundaries()
        else:
            bpy.ops.bim.show_boundaries()

    def hotkey_S_T(self):
        bpy.ops.bim.toggle_space_visibility()
