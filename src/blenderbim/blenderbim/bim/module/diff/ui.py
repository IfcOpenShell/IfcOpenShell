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

from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_diff(Panel):
    bl_label = "IFC Diff"
    bl_idname = "BIM_PT_diff"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        bim_properties = scene.DiffProperties

        layout.label(text="IFC Diff Setup:")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_old_file")
        row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_new_file")
        row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(bim_properties, "diff_relationships")

        row = layout.row()
        row.operator("bim.execute_ifc_diff")

        # TODO: show if there ifc diff operation is sucessful
        row = layout.row(align=True)
        row.prop(bim_properties, "diff_json_file")
        row.operator("bim.select_diff_json_file", icon="FILE_FOLDER", text="")
        row.operator("bim.visualise_diff", icon="HIDE_OFF", text="")
