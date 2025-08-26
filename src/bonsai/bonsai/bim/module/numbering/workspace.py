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


class NumberingTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.numbering_tool"
    bl_label = "Numbering Tool"
    bl_description = "Assign or remove numbers from elements"
    # TODO: replace with numbering icon
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.numbering")
    bl_widget = None

    @classmethod
    def draw_settings(context, layout, ws_tool):
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
        
        pass
