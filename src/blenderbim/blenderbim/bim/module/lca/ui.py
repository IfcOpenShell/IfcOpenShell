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
from bpy.types import Panel


class BIM_PT_lca(Panel):
    bl_label = "BIM Life Cycle Assessment"
    bl_idname = "BIM_PT_lca"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        props = context.scene.BIMLCAProperties
        if props.is_connected:
            row = self.layout.row()
            row.prop(props, "product_systems", text="")
            row = self.layout.row()
            row.prop(props, "amount", text="")
            row = self.layout.row()
            row.operator("bim.calculate_lca")
        else:
            row = self.layout.row()
            row.operator("bim.connect_openlca")
