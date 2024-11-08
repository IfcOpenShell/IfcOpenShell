# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy.types


class BIM_PT_covetool(bpy.types.Panel):
    bl_label = "cove.tool"
    bl_idname = "BIM_PT_covetool"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.CoveToolProperties

        if not props.token:
            row = layout.row()
            row.prop(props, "username")
            row = layout.row()
            row.prop(props, "password")
            row = layout.row()
            row.operator("bim.covetool_login")
            return

        layout.template_list("BIM_UL_covetool_projects", "", props, "projects", props, "active_project_index")

        row = layout.row()
        row.operator("bim.covetool_run_analysis")

        prop_names = [
            "si_units",
            "building_height",
            "roof_area",
            "floor_area",
            "skylight_area",
            "wall_area_e",
            "wall_area_ne",
            "wall_area_n",
            "wall_area_nw",
            "wall_area_w",
            "wall_area_sw",
            "wall_area_s",
            "wall_area_se",
            "window_area_e",
            "window_area_ne",
            "window_area_n",
            "window_area_nw",
            "window_area_w",
            "window_area_sw",
            "window_area_s",
            "window_area_se",
        ]
        for prop_name in prop_names:
            row = layout.row()
            row.prop(props.simple_analysis, prop_name)

        row = layout.row()
        row.operator("bim.covetool_run_simple_analysis")


class BIM_UL_covetool_projects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)
