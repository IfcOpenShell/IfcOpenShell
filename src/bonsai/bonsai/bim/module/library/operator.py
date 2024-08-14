# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.library as core


class AddLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_library"
    bl_label = "Add Library"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_library(tool.Ifc)


class RemoveLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_library"
    bl_label = "Remove Library"
    bl_options = {"REGISTER", "UNDO"}
    library: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_library(tool.Ifc, library=tool.Ifc.get().by_id(self.library))


class EnableEditingLibraryReferences(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_library_references"
    bl_label = "Enable Editing Library References"
    bl_options = {"REGISTER", "UNDO"}
    library: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_library_references(tool.Library, library=tool.Ifc.get().by_id(self.library))


class DisableEditingLibraryReferences(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_library_references"
    bl_label = "Disable Editing Library References"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_library_references(tool.Library)


class EnableEditingLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_library"
    bl_label = "Enable Editing Library"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_library(tool.Library)


class DisableEditingLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_library"
    bl_label = "Disable Editing Library"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_library(tool.Library)


class EditLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_library"
    bl_label = "Edit Library"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_library(tool.Ifc, tool.Library)


class AddLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_library_reference"
    bl_label = "Add Library Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_library_reference(tool.Ifc, tool.Library)


class RemoveLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_library_reference"
    bl_label = "Remove Library Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_library_reference(tool.Ifc, tool.Library, reference=tool.Ifc.get().by_id(self.reference))


class EnableEditingLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_library_reference"
    bl_label = "Enable Editing Library Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_library_reference(tool.Library, reference=tool.Ifc.get().by_id(self.reference))


class DisableEditingLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_library_reference"
    bl_label = "Disable Editing Library Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_library_reference(tool.Library)


class EditLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_library_reference"
    bl_label = "Edit Library Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_library_reference(tool.Ifc, tool.Library)


class AssignLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_library_reference"
    bl_label = "Assign Library Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_library_reference(
            tool.Ifc, obj=context.active_object, reference=tool.Ifc.get().by_id(self.reference)
        )


class UnassignLibraryReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_library_reference"
    bl_label = "Unassign Library Reference"
    bl_options = {"REGISTER", "UNDO"}
    reference: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_library_reference(
            tool.Ifc, obj=context.active_object, reference=tool.Ifc.get().by_id(self.reference)
        )
