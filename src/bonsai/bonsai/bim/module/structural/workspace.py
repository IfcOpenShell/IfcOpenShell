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
from bpy.types import WorkSpaceTool


class StructuralTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.structural_tool"
    bl_label = "Structural Tool"
    bl_description = "Gives you Structure related superpowers"
    # TODO: replace with structural icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.structural")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.structural_hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        StructuralToolUI.draw(context, layout)


def add_layout_hotkey(layout: bpy.types.UILayout, text: str, hotkey: str, description: str) -> None:
    args = ("structural", layout, text, hotkey, description)
    tool.Blender.add_layout_hotkey_operator(*args)


# NOTES before adding new operators:
# - add scene.BIMStructuralProperties
# - add StructuralData


class StructuralToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        # cls.props = context.scene.BIMStructuralProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        # if not StructuralData.is_loaded:
        #     StructuralData.load()

        cls.draw_type_selection_interface(context)

        if context.active_object and context.selected_objects:
            cls.draw_selected_object_interface(context)
        cls.draw_default_interface()

    @classmethod
    def draw_default_interface(cls):
        add_layout_hotkey(cls.layout, "Placeholder", "S_A", "Placeholder Operator")

    @classmethod
    def draw_selected_object_interface(cls, context):
        pass

    @classmethod
    def draw_type_selection_interface(cls, context):
        pass


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.structural_hotkey"
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
        # self.props = context.scene.BIMStructuralProperties
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        # self.props = context.scene.BIMStructuralProperties
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_A(self):
        pass
