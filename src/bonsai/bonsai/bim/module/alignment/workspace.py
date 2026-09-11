# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2026 Michael Yoder <myoder@desertspringscivil.com>
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
from bpy.types import WorkSpaceTool

import bonsai.tool as tool


class AlignmentTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"
    bl_idname = "bim.alignment_tool"
    bl_label = "Alignment"
    bl_description = "Civil alignment tools — create and edit horizontal alignments using PI method"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.alignment")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap()

    def draw_settings(
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        workspace_tool: bpy.types.WorkSpaceTool,
    ) -> None:
        if context.region.type == "TOOL_HEADER":
            _draw_header(layout)
        else:
            _draw_sidebar(layout)


def _draw_header(layout):
    """Compact icon-only layout for the tool header bar."""
    row = layout.row(align=True)
    row.operator("bim.import_alignment_csv", text="", icon="IMPORT")
    row.operator("align.pick_pi_from_viewport", text="", icon="EYEDROPPER")
    row.separator()
    row.operator("align.recalculate_pis", text="", icon="FILE_REFRESH")


def _draw_sidebar(layout):
    """Expanded layout for the sidebar / N-panel."""
    # -- Horizontal Alignment --
    col = layout.column(align=True)
    col.label(text="Horizontal Alignment", icon="CURVE_DATA")
    col.operator("align.create_alignment_by_pis", icon="ADD")
    col.operator("bim.import_alignment_csv", icon="IMPORT")
    col.separator()
    col.operator("align.pick_pi_from_viewport", icon="EYEDROPPER")
    col.operator("align.enter_pi_edit_mode", text="Edit PIs", icon="EDITMODE_HLT")
    row = col.row(align=True)
    row.operator("align.recalculate_pis", text="Visualize", icon="FILE_REFRESH")
    row.operator("align.clear_pis", text="Clear", icon="TRASH")
    col.separator()
    col.operator("align.add_stationing_referent", icon="EMPTY_AXIS")
    col.operator("align.name_segments", icon="FONT_DATA")
