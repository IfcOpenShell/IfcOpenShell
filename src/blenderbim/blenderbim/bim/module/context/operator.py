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
import blenderbim.core.context as core
import blenderbim.bim.module.context.data
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AddContext(bpy.types.Operator, Operator):
    bl_idname = "bim.add_context"
    bl_label = "Add Subcontext"
    bl_options = {"REGISTER", "UNDO"}
    context_type: bpy.props.StringProperty()
    context_identifier: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()
    parent: bpy.props.IntProperty()



    def _execute(self, context):   
        
        ifc_file = tool.Ifc.get()

        # Check if a IfcGeometricRepresentationSubContext already exists in the file
        for subcontext in ifc_file.by_type("IfcGeometricRepresentationSubContext", include_subtypes=False):
            if (
                subcontext.ContextType == self.context_type
                and subcontext.ContextIdentifier == self.context_identifier
                and subcontext.TargetView == self.target_view
            ):
                self.report({'INFO'}, "Context already exists. Did not add.")
                return {'CANCELLED'}

        # If the context doesn't exist, add it
        core.add_context(
            tool.Ifc,
            context_type=self.context_type,
            context_identifier=self.context_identifier,
            target_view=self.target_view,
            parent=tool.Ifc.get().by_id(self.parent) if self.parent else None,
        )
        self.report({'INFO'}, "Context added.")
        return {'FINISHED'}

    def context_already_exists(ifc_data, context_type, context_identifier, target_view):
        # Check if the context already exists in the loaded IFC data
        for context in ifc_data.by_type("IfcContext"):
            if (
                context.is_a() == context_type
                and context.Name == context_identifier
                and context.Phase == target_view
            ):
                return True
        
        return False



class RemoveContext(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_context"
    bl_label = "Remove Context"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_context(tool.Ifc, context=tool.Ifc.get().by_id(self.context))


class EnableEditingContext(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_context"
    bl_label = "Enable Editing Context"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_context(tool.Context, context=tool.Ifc.get().by_id(self.context))


class DisableEditingContext(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_context"
    bl_label = "Disable Editing Context"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_context(tool.Context)


class EditContext(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_context"
    bl_label = "Edit Context"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_context(tool.Ifc, tool.Context)
