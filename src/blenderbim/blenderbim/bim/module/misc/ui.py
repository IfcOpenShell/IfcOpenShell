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


class BIM_PT_misc_utilities(bpy.types.Panel):
    bl_idname = "BIM_PT_misc_utilities"
    bl_label = "Miscellaneous"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMMiscProperties

        row = layout.split(factor=0.2, align=True)
        row.prop(props, "override_colour", text="")
        row.operator("bim.set_override_colour")
        row = layout.row()
        row.operator("bim.set_viewport_shadow_from_sun")
        row = layout.row()
        row.operator("bim.snap_spaces_together")
        row = layout.split(factor=0.2, align=True)
        row.prop(props, "total_storeys", text="")
        row.operator("bim.resize_to_storey").total_storeys = props.total_storeys
        row = layout.row()
        row.operator("bim.split_along_edge")
        row = layout.row()
        row.operator("bim.get_connected_system_elements")
        row = layout.row()
        row.operator("bim.draw_system_arrows")
        row = layout.row()
        row.operator("bim.clean_wireframes")

        row = layout.row(align=True)
        row.operator("bim.enable_editing_sketch_extrusion_profile", text="Start Sketching")
        row.operator("bim.edit_sketch_extrusion_profile", text="", icon="FILE_REFRESH")
        row.operator("bim.disable_editing_sketch_extrusion_profile", text="", icon="CANCEL")
