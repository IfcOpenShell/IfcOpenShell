# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy

class BIM_PT_radiance_exporter(bpy.types.Panel):
    """Creates a Panel in the render properties window"""
    bl_label = "Radiance Exporter"
    bl_idname = "BIM_PT_radiance_exporter"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_services"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        props = scene.radiance_exporter_properties
        
        row = layout.row()
        row.prop(props, "ifc_file_name")

        row = layout.row()
        row.prop(props, "json_file_path")
        
        row = layout.row()
        row.label(text="Resolution")
        row.prop(props, "radiance_resolution_x", text="X")
        
        row = layout.row()
        row.label(text="")
        row.prop(props, "radiance_resolution_y", text="Y")
        
        row = layout.row()
        row.prop(props, "radiance_quality")
        
        row = layout.row()
        row.prop(props, "radiance_detail")
        
        row = layout.row()
        row.prop(props, "radiance_variability")
        
        row = layout.row()
        row.operator("export_scene.radiance", text="Export to OBJ")

        row = layout.row()
        row.operator("render_scene.radiance", text="Radiance Render")