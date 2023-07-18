# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.bim.helper
import blenderbim.tool as tool
from bpy.types import Panel, UIList
from blenderbim.bim.module.profile.data import ProfileData
from blenderbim.bim.module.profile.prop import generate_thumbnail_for_active_profile


class BIM_PT_profiles(Panel):
    bl_label = "Profiles"
    bl_idname = "BIM_PT_profiles"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_geometry"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ProfileData.is_loaded:
            ProfileData.load()
        self.props = context.scene.BIMProfileProperties

        active_profile = None
        if self.props.is_editing and self.props.profiles and self.props.active_profile_index < len(self.props.profiles):
            preview_collection = ProfileData.preview_collection
            box = self.layout.box()
            active_profile = self.props.profiles[self.props.active_profile_index]
            profile_id = active_profile.ifc_definition_id
            profile_id_str = str(profile_id)
            if profile_id_str in preview_collection:
                preview_image = preview_collection[profile_id_str]
            else:
                preview_image = preview_collection.new(profile_id_str)
                generate_thumbnail_for_active_profile()

            box.template_icon(icon_value=preview_image.icon_id, scale=5)

        row = self.layout.row(align=True)
        row.label(text=f"{ProfileData.data['total_profiles']} Named Profiles Found", icon="SNAP_GRID")
        if self.props.is_editing:
            row.operator("bim.disable_profile_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_profiles", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "profile_classes", text="")
        row.operator("bim.add_profile_def", text="", icon="ADD")

        self.layout.template_list(
            "BIM_UL_profiles",
            "",
            self.props,
            "profiles",
            self.props,
            "active_profile_index",
        )
        if active_profile and active_profile.ifc_class == "IfcArbitraryClosedProfileDef":
            if self.props.active_arbitrary_profile_id:
                row = self.layout.row(align=True)
                row.operator("bim.edit_arbitrary_profile", text="Save Arbitrary Profile", icon="CHECKMARK")
                row.operator("bim.disable_editing_arbitrary_profile", text="", icon="CANCEL")
            else:
                row = self.layout.row()
                row.operator("bim.enable_editing_arbitrary_profile", text="Edit Arbitrary Profile", icon="GREASEPENCIL")

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
            row.label(text=item.ifc_class)

            if props.active_profile_id == item.ifc_definition_id:
                row.operator("bim.edit_profile", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_profile", text="", icon="CANCEL")
            elif props.active_profile_id:
                row.operator("bim.remove_profile_def", text="", icon="X").profile = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_profile", text="", icon="GREASEPENCIL")
                op.profile = item.ifc_definition_id
                row.operator("bim.remove_profile_def", text="", icon="X").profile = item.ifc_definition_id
