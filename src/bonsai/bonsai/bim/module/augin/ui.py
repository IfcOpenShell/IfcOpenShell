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


class BIM_PT_augin(bpy.types.Panel):
    bl_label = "Augin"
    bl_idname = "BIM_PT_augin"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.AuginProperties

        if not props.token:
            row = layout.row()
            row.prop(props, "username")
            row = layout.row()
            row.prop(props, "password")
            row = layout.row()
            row.operator("bim.augin_login")
            return

        row = layout.row()
        row.label(text="Logged in as " + props.username)

        if not context.scene.BIMProperties.ifc_file:
            row = layout.row()
            row.label(text="No IFC Found")
            return

        if props.is_success:
            row = layout.row()
            row.label(text="Upload Successful")
            row = layout.row()
            row.operator("bim.augin_reset")
        else:
            row = layout.row()
            row.prop(props, "project_name")
            row = layout.row()
            row.operator("bim.augin_create_new_model")
