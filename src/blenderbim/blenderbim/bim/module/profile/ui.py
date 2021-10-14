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

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.profile.data import Data


class BIM_PT_profiles(Panel):
    bl_label = "IFC Profiles"
    bl_idname = "BIM_PT_profiles"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        view_setting = context.preferences.addons["blenderbim"].preferences.module_visibility
        file = IfcStore.get_file()
        if not file:
            return False
        return view_setting in ["Admin"]

    def draw(self, context):
        self.file = IfcStore.get_file()
        if not Data.is_loaded:
            Data.load(self.file)
        self.props = context.scene.BIMProfileProperties

        row = self.layout.row(align=True)
        row.label(text="{} Profiles Found".format(len(Data.profiles)), icon="SNAP_GRID")
        if self.props.is_editing:
            row.operator("bim.disable_profile_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_profiles", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            return

        self.layout.template_list(
            "BIM_UL_profiles",
            "",
            self.props,
            "profiles",
            self.props,
            "active_profile_index",
        )

        if self.props.active_profile_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        blenderbim.bim.helper.draw_attributes(self.props.profile_attributes, self.layout)


class BIM_UL_profiles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMProfileProperties
        if item:
            row = layout.row(align=True)
            row.label(text=item.name or "Unnamed")

            if props.active_profile_id == item.ifc_definition_id:
                row.operator("bim.edit_profile", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_profile", text="", icon="CANCEL")
            elif props.active_profile_id:
                row.operator("bim.remove_profile_def", text="", icon="X").profile = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_profile", text="", icon="GREASEPENCIL")
                op.profile = item.ifc_definition_id
                row.operator("bim.remove_profile_def", text="", icon="X").profile = item.ifc_definition_id
