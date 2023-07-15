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

import blenderbim.tool as tool
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_cobie(Panel):
    bl_label = "COBie"
    bl_idname = "BIM_PT_cobie"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return tool.Blender.is_tab(context, "FM")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.COBieProperties

        if IfcStore.get_file():
            row = layout.row()
            row.prop(props, "should_load_from_memory")

        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "cobie_ifc_file")
            row.operator("bim.select_cobie_ifc_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        row.prop(props, "cobie_types")
        row = layout.row()
        row.prop(props, "cobie_components")

        row = layout.row(align=True)
        row.prop(props, "cobie_json_file")
        row.operator("bim.select_cobie_json_file", icon="FILE_FOLDER", text="")

        row = layout.row()
        op = row.operator("bim.execute_ifc_cobie", text="CSV")
        op.file_format = "csv"
        op = row.operator("bim.execute_ifc_cobie", text="ODS")
        op.file_format = "ods"
        op = row.operator("bim.execute_ifc_cobie", text="XLSX")
        op.file_format = "xlsx"
