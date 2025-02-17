# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import bpy
import bonsai.bim.helper
import bonsai.tool as tool
from bpy.types import Panel, UIList
from bonsai.bim.module.profile.data import ProfileData
from bonsai.bim.module.profile.prop import generate_thumbnail_for_active_profile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.profile.prop import BIMProfileProperties, Profile


class BIM_PT_profiles(Panel):
    bl_label = "Profiles"
    bl_idname = "BIM_PT_profiles"
    bl_options = {"HIDE_HEADER"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_profiles"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ProfileData.is_loaded:
            ProfileData.load()
        self.props = tool.Profile.get_profile_props()

        active_profile = None
        if self.props.is_editing and (active_profile := tool.Profile.get_active_profile_ui()):
            preview_collection = ProfileData.preview_collection
            box = self.layout.box()
            profile_id = active_profile.ifc_definition_id

            if profile_id in ProfileData.failed_previews:
                box.label(text="Failed to load preview (invalid profile).", icon="ERROR")
            else:
                profile_id_str = str(profile_id)
                if profile_id_str in preview_collection:
                    preview_image = preview_collection[profile_id_str]
                else:
                    preview_image = preview_collection.new(profile_id_str)
                    generate_thumbnail_for_active_profile()

                box.template_icon(icon_value=preview_image.icon_id, scale=5)

        row = self.layout.row(align=True)
        row.label(text=f"{ProfileData.data['total_profiles']} Named Profiles", icon="ITALIC")
        if self.props.is_editing:
            row.operator("bim.disable_profile_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_profiles", text="", icon="IMPORT")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        if self.props.profile_classes == "IfcArbitraryClosedProfileDef":
            split = row.split(factor=0.5, align=True)
            row = split.row(align=True)
            row.prop(self.props, "profile_classes", text="")
            row = split.row(align=True)
            row.prop(self.props, "object_to_profile", text="")
        else:
            row.prop(self.props, "profile_classes", text="")
        row.operator("bim.add_profile_def", text="", icon="ADD")

        if active_profile:
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"

            is_editable = active_profile.ifc_class in (
                "IfcArbitraryClosedProfileDef",
                "IfcArbitraryProfileDefWithVoids",
                "IfcCompositeProfileDef",
            )
            if self.props.active_profile_id == active_profile.ifc_definition_id:
                row.operator("bim.edit_profile", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_profile", text="", icon="CANCEL")
            elif self.props.active_arbitrary_profile_id:
                row.operator("bim.edit_arbitrary_profile", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_arbitrary_profile", text="", icon="CANCEL")
            else:
                row.operator("bim.duplicate_profile_def", icon="DUPLICATE", text="")
                row.operator("bim.select_by_profile", icon="RESTRICT_SELECT_OFF", text="")
                if is_editable:
                    row.operator("bim.enable_editing_arbitrary_profile", text="", icon="ITALIC")
                op = row.operator("bim.enable_editing_profile", text="", icon="GREASEPENCIL")
                op.profile = active_profile.ifc_definition_id
                row.operator("bim.remove_profile_def", text="", icon="X").profile = active_profile.ifc_definition_id

        self.layout.template_list(
            "BIM_UL_profiles",
            "",
            self.props,
            "profiles",
            self.props,
            "active_profile_index",
        )

        row = self.layout.row()
        row.prop(self.props, "is_filtering_material_profiles", text="Filter Material Profiles")

        if active_profile:
            users_of_profile = ProfileData.data["active_profile_users"]
            self.layout.label(icon="INFO", text=f"Profile has {users_of_profile} inverse relationship(s) in project")

        if self.props.active_profile_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        bonsai.bim.helper.draw_attributes(self.props.profile_attributes, self.layout)


class BIM_UL_profiles(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMProfileProperties,
        item: Profile,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False)
            row.label(text=item.ifc_class)
