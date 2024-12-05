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

import bpy
import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search
from bonsai.bim.helper import draw_attributes


class BIM_PT_patch(bpy.types.Panel):
    bl_label = "Patch"
    bl_idname = "BIM_PT_patch"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = scene.BIMPatchProperties
        row = layout.row()
        prop_with_search(row, props, "ifc_patch_recipes")

        if tool.Ifc.get():
            row = self.layout.row()
            row.prop(props, "should_load_from_memory")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "ifc_patch_input")
            row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        if tool.Patch.does_patch_has_output(props.ifc_patch_recipes):
            row = layout.row(align=True)
            row.prop(props, "ifc_patch_output")
            row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        if props.ifc_patch_args_attr:
            draw_attributes(props.ifc_patch_args_attr, layout)
        op = layout.operator("bim.execute_ifc_patch")
