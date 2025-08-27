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
import bonsai.tool as tool
from bpy.types import WorkSpaceTool
import bpy.ops

from functools import partial

from bonsai.bim.module.numbering.data import NumberingData


class NumberingTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.numbering_tool"
    bl_label = "Numbering Tool"
    bl_description = "Gives you Numbering related superpowers"
    # TODO: replace with numbering icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.numbering")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.assign_numbers", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.remove_numbers", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        NumberingToolUI.draw(context, layout)


class NumberingToolUI:

    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.props = tool.Numbering.get_numbering_props()

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not NumberingData.is_loaded:
            NumberingData.load()

        cls.draw_interface()

    @classmethod
    def draw_interface(cls):
        cls.layout.operator("bim.assign_numbers", text="Assign Numbers", icon="TAG")
        cls.layout.operator("bim.remove_numbers", text="Remove Numbers", icon="X")
