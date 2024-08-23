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
import ifcopenshell.api
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.unit as core


class AssignSceneUnits(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_scene_units"
    bl_label = "Assign Scene Units"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.assign_scene_units(tool.Ifc, tool.Unit)


class AssignUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_unit"
    bl_label = "Assign Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class UnassignUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_unit"
    bl_label = "Unassign Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class LoadUnits(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_units"
    bl_label = "Load Units"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open the loaded units"

    def _execute(self, context):
        core.load_units(tool.Unit)


class DisableUnitEditingUI(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_unit_editing_ui"
    bl_label = "Disable Unit Editing UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close the editing units mode"

    def _execute(self, context):
        core.disable_unit_editing_ui(tool.Unit)


class RemoveUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_unit"
    bl_label = "Remove Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class AddConversionBasedUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_conversion_based_unit"
    bl_label = "Add Conversion Based Unit"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_conversion_based_unit(tool.Ifc, tool.Unit, name=self.name)


class AddMonetaryUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_monetary_unit"
    bl_label = "Add Monetary Unit"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_monetary_unit(tool.Ifc, tool.Unit)


class AddSIUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_si_unit"
    bl_label = "Add SI Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_si_unit(tool.Ifc, tool.Unit, unit_type=self.unit_type)


class AddContextDependentUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_context_dependent_unit"
    bl_label = "Add Context Dependent Unit"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    unit_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_context_dependent_unit(tool.Ifc, tool.Unit, unit_type=self.unit_type, name=self.name)


class EnableEditingUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_unit"
    bl_label = "Enable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_unit(tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class DisableEditingUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_unit"
    bl_label = "Disable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_unit(tool.Unit)


class EditUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_unit"
    bl_label = "Edit Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))
