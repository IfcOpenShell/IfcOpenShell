# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel


class BIM_PT_cityjson_converter(Panel):
    bl_label = "CityJSON"
    bl_idname = "BIM_PT_ifccityjson"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.ifccityjson_properties

        row = layout.row(align=True)
        row.prop(props, "input")
        row = layout.row(align=True)
        row.operator("bim.find_cityjson_lod")
        row = layout.row(align=True)
        row.prop(props, "output")
        row = layout.row(align=True)
        row.prop(props, "name")
        row = layout.row(align=True)
        row.prop(props, "split_lod")
        row.prop(props, "load_after_convert")
        row = layout.row(align=True)
        row.prop(props, "lod")
        if not props.is_lod_found:
            row.enabled = False
        row = layout.row(align=True)
        row.operator("bim.convert_cityjson2ifc")
