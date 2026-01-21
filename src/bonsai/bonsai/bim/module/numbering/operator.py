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
from bonsai.bim.ifc import IfcStore

import json
from bonsai.tool.numbering import Numbering, Settings, LoadSelection, SaveNumber


class UndoOperator:
    @staticmethod
    def execute_with_undo(operator, context, method):
        ifc_file = tool.Ifc.get()
        """Execute a method with undo support."""
        IfcStore.begin_transaction(operator)
        settings = Settings.to_dict(context.scene.BIMNumberingProperties)

        parent_type = LoadSelection.get_parent_type(settings)
        try:
            elements = ifc_file.by_type(parent_type)
        except RuntimeError:
            operator.report({"ERROR"}, f"Parent type {parent_type} not found in {ifc_file.schema} schema.")
            return {"CANCELLED"}

        if settings.get("pset_name") == "Common":
            SaveNumber.get_pset_common_names(elements)

        old_numbers = {SaveNumber.get_id(element): SaveNumber.get_number(element, settings) for element in elements}
        new_numbers = old_numbers.copy()

        result = method(operator, settings, new_numbers)

        operator.transaction_data = {"old_value": old_numbers, "new_value": new_numbers}
        IfcStore.add_transaction_operation(operator)
        IfcStore.end_transaction(operator)

        bpy.context.view_layer.objects.active = bpy.context.active_object

        return result

    @staticmethod
    def rollback(operator, data):
        """Support undo of number assignment"""
        ifc_file = tool.Ifc.get()

        rollback_count = 0
        settings = Settings.to_dict(bpy.context.scene.BIMNumberingProperties)
        for element in ifc_file.by_type(LoadSelection.get_parent_type(settings)):
            old_number = data["old_value"].get(SaveNumber.get_id(element), None)
            rollback_count += int(
                SaveNumber.save_number(ifc_file, element, old_number, settings, data["new_value"]) or 0
            )
        bpy.ops.bim.show_message("EXEC_DEFAULT", message=f"Rollback {rollback_count} numbers.")

    @staticmethod
    def commit(operator, data):
        """Support redo of number assignment"""
        ifc_file = tool.Ifc.get()

        commit_count = 0
        settings = Settings.to_dict(bpy.context.scene.BIMNumberingProperties)
        for obj in bpy.context.scene.objects:
            element = tool.Ifc.get_entity(obj)
            if element is not None and element.is_a(LoadSelection.get_parent_type(settings)):
                new_number = data["new_value"].get(obj.name, None)
                commit_count += int(
                    SaveNumber.save_number(ifc_file, element, new_number, settings, data["old_value"]) or 0
                )
        bpy.ops.bim.show_message("EXEC_DEFAULT", message=f"Commit {commit_count} numbers.")


class AssignNumbers(bpy.types.Operator):
    bl_idname = "bim.assign_numbers"
    bl_label = "Assign numbers"
    bl_description = "Assign numbers to selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return UndoOperator.execute_with_undo(self, context, Numbering.assign_numbers)

    def rollback(self, data):
        UndoOperator.rollback(self, data)

    def commit(self, data):
        UndoOperator.commit(self, data)


class RemoveNumbers(bpy.types.Operator):
    bl_idname = "bim.remove_numbers"
    bl_label = "Remove numbers"
    bl_description = "Remove numbers from selected objects, from the selected attribute or Pset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return UndoOperator.execute_with_undo(self, context, Numbering.remove_numbers)

    def rollback(self, data):
        UndoOperator.rollback(self, data)

    def commit(self, data):
        UndoOperator.commit(self, data)


class ShowMessage(bpy.types.Operator):
    bl_idname = "bim.show_message"
    bl_label = "Show Message"
    bl_description = "Show a message in the info area"
    message: bpy.props.StringProperty()  # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        self.report({"INFO"}, self.message)
        return {"FINISHED"}


class SaveSettings(bpy.types.Operator):
    bl_idname = "bim.save_settings"
    bl_label = "Save Settings"
    bl_description = f"Save the current numbering settings to {Settings.pset_name} of the IFC Project element, under the selected name"

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        ifc_file = tool.Ifc.get()
        return Settings.save_settings(self, props, ifc_file)


class LoadSettings(bpy.types.Operator):
    bl_idname = "bim.load_settings"
    bl_label = "Load Settings"
    bl_description = f"Load the selected numbering settings from {Settings.pset_name} of the IFC Project element"

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        ifc_file = tool.Ifc.get()
        return Settings.load_settings(self, props, ifc_file)


class DeleteSettings(bpy.types.Operator):
    bl_idname = "bim.delete_settings"
    bl_label = "Delete Settings"
    bl_description = f"Delete the selected numbering settings from {Settings.pset_name} of the IFC Project element"

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        return Settings.delete_settings(self, props)


class ClearSettings(bpy.types.Operator):
    bl_idname = "bim.clear_settings"
    bl_label = "Clear Settings"
    bl_description = f"Remove the {Settings.pset_name} Pset and all the saved settings from the IFC Project element"

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        return Settings.clear_settings(self, props)


class ExportSettings(bpy.types.Operator):
    bl_idname = "bim.export_settings"
    bl_label = "Export Settings"
    bl_description = f"Export the current numbering settings to a JSON file"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        with open(self.filepath, "w") as f:
            json.dump(Settings.to_dict(props), f)
        self.report({"INFO"}, f"Exported settings to {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = "settings.json"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ImportSettings(bpy.types.Operator):
    bl_idname = "bim.import_settings"
    bl_label = "Import Settings"
    bl_description = f"Import numbering settings from a JSON file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        with open(self.filepath, "r") as f:
            settings = json.load(f)
            Settings.read_settings(self, settings, props)
        self.report({"INFO"}, f"Imported settings from {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
