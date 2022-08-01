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


class BIM_PT_authoring(Panel):
    bl_label = "Architectural"
    bl_idname = "BIM_PT_authoring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.join_wall", icon="MOD_SKIN", text="T").join_type = "T"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="L").join_type = "L"
        row.operator("bim.join_wall", icon="MOD_SKIN", text="V").join_type = "V"
        row.operator("bim.join_wall", icon="X", text="").join_type = ""
        row = self.layout.row(align=True)
        row.operator("bim.align_wall", icon="ANCHOR_TOP", text="Ext.").align_type = "EXTERIOR"
        row.operator("bim.align_wall", icon="ANCHOR_CENTER", text="C/L").align_type = "CENTERLINE"
        row.operator("bim.align_wall", icon="ANCHOR_BOTTOM", text="Int.").align_type = "INTERIOR"
        row = self.layout.row(align=True)
        row.operator("bim.flip_wall", icon="ORIENTATION_NORMAL", text="Flip")
        row.operator("bim.split_wall", icon="MOD_PHYSICS", text="Split")
