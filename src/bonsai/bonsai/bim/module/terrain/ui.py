# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.tool as tool
from bonsai.bim.module.terrain.data import TerrainData
from bonsai.bim.module.terrain.operator import get_active_terrain


class BIM_PT_terrain_contours(bpy.types.Panel):
    bl_label = "Contours"
    bl_idname = "BIM_PT_terrain_contours"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_parametric_geometry"

    @classmethod
    def poll(cls, context):
        return get_active_terrain(context) is not None

    def draw(self, context):
        if not TerrainData.is_loaded:
            TerrainData.load()

        props = tool.Terrain.get_terrain_props()
        layout = self.layout

        if TerrainData.data["interval"]:
            box = layout.box()
            row = box.row()
            row.label(text=f"Every {TerrainData.data['interval']}", icon="IPO_LINEAR")
            if TerrainData.data["index_interval"]:
                row.label(text=f"Index every {TerrainData.data['index_interval']}")
            box.label(text=f"{TerrainData.data['total_contours']} contours")
            row = box.row(align=True)
            row.operator("bim.update_contours", icon="FILE_REFRESH")
            row.operator("bim.remove_contours", icon="X", text="")

        layout.prop(props, "contour_interval")
        layout.prop(props, "contour_index_interval")
        text = "Regenerate With These Settings" if TerrainData.data["interval"] else "Generate Contours"
        layout.operator("bim.generate_contours", icon="MOD_WAVE", text=text)
