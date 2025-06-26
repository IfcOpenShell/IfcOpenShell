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

import bpy
import bonsai.tool as tool
import bonsai.core.context as core


class AddContext(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_context"
    bl_label = "Add Subcontext"
    bl_options = {"REGISTER", "UNDO"}
    context_type: bpy.props.StringProperty()
    context_identifier: bpy.props.StringProperty()
    target_view: bpy.props.StringProperty()
    parent: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_context(
            tool.Ifc,
            context_type=self.context_type,
            context_identifier=self.context_identifier,
            target_view=self.target_view,
            parent=tool.Ifc.get().by_id(self.parent) if self.parent else None,
        )


class RemoveContext(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_context"
    bl_label = "Remove Context"
    bl_description = (
        "Remove representation context. Any representation geometry that is assigned to the context is also removed. "
        "If a context is removed, then any subcontexts are also removed"
    )
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_context(tool.Ifc, context=tool.Ifc.get().by_id(self.context))


class EnableEditingContext(bpy.types.Operator):
    bl_idname = "bim.enable_editing_context"
    bl_label = "Enable Editing Context"
    bl_options = {"REGISTER", "UNDO"}
    context: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_context(tool.Context, context=tool.Ifc.get().by_id(self.context))
        return {"FINISHED"}


class DisableEditingContext(bpy.types.Operator):
    bl_idname = "bim.disable_editing_context"
    bl_label = "Disable Editing Context"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_context(tool.Context)
        return {"FINISHED"}


class EditContext(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_context"
    bl_label = "Edit Context"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_context(tool.Ifc, tool.Context)
