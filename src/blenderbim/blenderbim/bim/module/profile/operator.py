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
import blenderbim.bim.module.model.profile as model_profile
from blenderbim.bim.module.model.slab import DecorationsHandler


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
            new.ifc_class = profile.is_a()

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


class EnableEditingProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_profile"
    bl_label = "Enable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        props = context.scene.BIMProfileProperties
        props.profile_attributes.clear()
        blenderbim.bim.helper.import_attributes2(tool.Ifc.get().by_id(self.profile), props.profile_attributes)
        props.active_profile_id = self.profile


class DisableEditingProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_profile"
    bl_label = "Disable Editing Profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMProfileProperties.active_profile_id = 0
        bpy.ops.bim.disable_editing_arbitrary_profile()
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
        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)
        bpy.ops.bim.load_profiles()


class AddProfileDef(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_profile_def"
    bl_label = "Add Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMProfileProperties
        profile_class = props.profile_classes
        if profile_class == "IfcArbitraryClosedProfileDef":
            points = [(0, 0), (0.1, 0), (0.1, 0.1), (0, 0.1), (0, 0)]
            profile = ifcopenshell.api.run("profile.add_arbitrary_profile", tool.Ifc.get(), profile=points)
        else:
            profile = ifcopenshell.api.run("profile.add_parameterized_profile", tool.Ifc.get(), ifc_class=profile_class)
        profile.ProfileName = "New Profile"
        bpy.ops.bim.load_profiles()


class EnableEditingArbitraryProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_arbitrary_profile"
    bl_label = "Enable Editing Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in context.selected_objects:
            obj.select_set(False)
        props = context.scene.BIMProfileProperties
        profile = tool.Ifc.get().by_id(props.active_profile_id)
        obj = tool.Model.import_profile(profile)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        DecorationsHandler.install(context)
        bpy.ops.wm.tool_set_by_id(name="bim.cad_tool")


class DisableEditingArbitraryProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_arbitrary_profile"
    bl_label = "Disable Editing Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        if obj and obj.data and obj.data.BIMMeshProperties.is_profile:
            DecorationsHandler.uninstall()
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.data.objects.remove(obj)


class EditArbitraryProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_arbitrary_profile"
    bl_label = "Edit Arbitrary Profile"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMProfileProperties
        old_profile = tool.Ifc.get().by_id(props.active_profile_id)

        obj = context.active_object

        DecorationsHandler.uninstall()
        bpy.ops.object.mode_set(mode="OBJECT")

        profile = tool.Model.export_profile(obj)
        if not profile:
            def msg(self, context):
                self.layout.label(text="INVALID PROFILE: " + indices[1])

            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            DecorationsHandler.install(context)
            bpy.ops.object.mode_set(mode="EDIT")
            return

        bpy.data.objects.remove(obj)
        profile.ProfileType = old_profile.ProfileType
        profile.ProfileName = old_profile.ProfileName
        for inverse in tool.Ifc.get().get_inverse(old_profile):
            ifcopenshell.util.element.replace_attribute(inverse, old_profile, profile)
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_profile)
        bpy.ops.bim.load_profiles()
        props.active_profile_id = profile.id()

        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)
