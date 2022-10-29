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
import ifcopenshell.api
import blenderbim.bim.helper
import blenderbim.tool as tool


class LoadProfiles(bpy.types.Operator):
    bl_idname = "bim.load_profiles"
    bl_label = "Load Profiles"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMProfileProperties
        props.profiles.clear()

        for profile in tool.Ifc.get().by_type("IfcProfileDef"):
            new = props.profiles.add()
            new.ifc_definition_id = profile.id()
            new.name = profile.ProfileName or "Unnamed"

        props.is_editing = True
        bpy.ops.bim.disable_editing_profile()
        return {"FINISHED"}


class DisableProfileEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_profile_editing_ui"
    bl_label = "Disable Profile Editing UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMProfileProperties.is_editing = False
        return {"FINISHED"}


class RemoveProfileDef(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_profile_def"
    bl_label = "Remove Profile Definition"
    bl_options = {"REGISTER", "UNDO"}
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        ifcopenshell.api.run("profile.remove_profile", tool.Ifc.get(), profile=tool.Ifc.get().by_id(self.profile))
        bpy.ops.bim.load_profiles()
        return {"FINISHED"}


class EnableEditingProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_profile"
    bl_label = "Enable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}
    profile: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMProfileProperties
        props.profile_attributes.clear()
        blenderbim.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.profile), props.profile_attributes)
        props.active_profile_id = self.profile
        return {"FINISHED"}


class DisableEditingProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_profile"
    bl_label = "Disable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMProfileProperties.active_profile_id = 0
        return {"FINISHED"}


class EditProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_profile"
    bl_label = "Edit Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMProfileProperties
        attributes = blenderbim.bim.helper.export_attributes(props.profile_attributes)
        profile = tool.Ifc.get().by_id(props.active_profile_id)
        ifcopenshell.api.run("profile.edit_profile", tool.Ifc.get(), profile=profile, attributes=attributes)
        bpy.ops.bim.load_profiles()
        return {"FINISHED"}
