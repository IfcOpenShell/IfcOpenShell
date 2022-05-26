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
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.style as core
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore


class UpdateStyleColours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_colours"
    bl_label = "Update Style Colours"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.update_style_colours(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class UpdateStyleTextures(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_style_textures"
    bl_label = "Update Style Textures"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        representation = ifcopenshell.util.representation.get_representation(
            tool.Ifc.get_entity(context.active_object), "Model", "Body", "MODEL_VIEW"
        )
        if representation:
            core.update_style_textures(
                tool.Ifc, tool.Style, obj=context.active_object.active_material, representation=representation
            )


class RemoveStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_style"
    bl_label = "Remove Style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_style(tool.Ifc, tool.Material, tool.Style, style=tool.Ifc.get().by_id(self.style))


class AddStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_style"
    bl_label = "Add Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class UnlinkStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_style"
    bl_label = "Unlink Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.unlink_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class EnableEditingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_style"
    bl_label = "Enable Editing Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_style(tool.Style, obj=context.active_object.active_material)


class DisableEditingStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_style"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Style"

    def _execute(self, context):
        core.disable_editing_style(tool.Style, obj=context.active_object.active_material)


class EditStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_style"
    bl_label = "Edit Style"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_style(tool.Ifc, tool.Style, obj=context.active_object.active_material)


class DisableEditingStyles(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_styles"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Styles"

    def _execute(self, context):
        core.disable_editing_styles(tool.Style)


class LoadStyles(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_styles"
    bl_label = "Load Styles"
    bl_options = {"REGISTER", "UNDO"}
    style_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.load_styles(tool.Style, style_type=self.style_type)


class SelectByStyle(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_by_style"
    bl_label = "Select By Material"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_by_style(tool.Style, style=tool.Ifc.get().by_id(self.style))
