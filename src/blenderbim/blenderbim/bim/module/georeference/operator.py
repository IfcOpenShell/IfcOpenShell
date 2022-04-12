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
import blenderbim.tool as tool
import blenderbim.core.georeference as core
import blenderbim.bim.handler

class AddGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_georeferencing"
    bl_label = "Add Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new georeference"

    def _execute(self, context):
        core.add_georeferencing(tool.Ifc)
        
class EnableEditingGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_georeferencing"
    bl_label = "Enable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing georeferencing"
    
    def _execute(self, context):
        core.enable_editing_georeferencing(tool.Georeference)

class RemoveGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_georeferencing"
    bl_label = "Remove Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the georeferencing"
    
    def _execute(self, context):
        core.remove_georeferencing(tool.Ifc)
        
class EditGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_georeferencing"
    bl_label = "Edit Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the georeferencing"
    
    def _execute(self, context):
        core.edit_georeferencing(tool.Ifc, tool.Georeference)
    
class DisableEditingGeoreferencing(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_georeferencing"
    bl_label = "Disable Editing Georeferencing"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close editing panel"

    def _execute(self, context):
        core.disable_editing_georeferencing(tool.Georeference)

class SetIfcGridNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_ifc_grid_north"
    bl_label = "Set IFC Grid North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Set IFC grid north"
    
    def _execute(self, context):
        core.set_ifc_grid_north()

class SetBlenderGridNorth(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_blender_grid_north"
    bl_label = "Set Blender Grid North"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Set Blender grif north"
    
    def _execute(self, context):
        core.set_blender_grid_north()



