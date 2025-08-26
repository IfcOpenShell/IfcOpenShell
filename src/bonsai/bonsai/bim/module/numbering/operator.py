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
import functools as ft
from .util import Settings, LoadSelection, NumberFormatting, SaveNumber, Storeys, ObjectGeometry, get_id

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
            operator.report({'ERROR'}, f"Parent type {parent_type} not found in {ifc_file.schema} schema.")
            return {'CANCELLED'}

        if settings.get("pset_name") == "Common":
            SaveNumber.get_pset_common_names(elements)

        old_numbers = {get_id(element): SaveNumber.get_number(element, settings) for element in elements}
        new_numbers = old_numbers.copy()

        result = method(settings, new_numbers)

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
            old_number = data["old_value"].get(get_id(element), None)
            rollback_count += int(SaveNumber.save_number(ifc_file, element, old_number, settings, data["new_value"]) or 0)
        bpy.ops.bonsai.show_message('EXEC_DEFAULT', message=f"Rollback {rollback_count} numbers.")
    
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
                commit_count += int(SaveNumber.save_number(ifc_file, element, new_number, settings, data["old_value"]) or 0)
        bpy.ops.bonsai.show_message('EXEC_DEFAULT', message=f"Commit {commit_count} numbers.")
  
class AssignNumbers(bpy.types.Operator):
    bl_idname = "bim.assign_numbers"
    bl_label = "Assign numbers"
    bl_description = "Assign numbers to selected objects"
    bl_options = {"REGISTER", "UNDO"}

    def number_elements(elements, ifc_file, settings, elements_locations = None, elements_dimensions = None, storeys = None, numbers_cache = {}, storeys_numbers={}, report=None, remove_count=None):
        """Number elements in the IFC file with the provided settings. If element locations or dimensions are specified, these are used for sorting.
        Providing numbers_cache, a dictionary with element-> currently saved number, speeds up execution.
        If storeys_numbers is provided, as a dictionary storey->number, this is used for assigning storey numbers."""
        if report is None:
            def report(report_type, message):
                if report_type == {"INFO"}:
                    print("INFO: ", message)
                if report_type == {"WARNING"}:
                    raise Exception(message)
        if storeys is None:
            storeys = []

        number_count = 0

        if elements_dimensions:
            elements.sort(key=ft.cmp_to_key(lambda a, b: ObjectGeometry.cmp_within_precision(elements_dimensions[a], elements_dimensions[b], settings, use_dir=False)))
        if elements_locations:
            elements.sort(key=ft.cmp_to_key(lambda a, b: ObjectGeometry.cmp_within_precision(elements_locations[a], elements_locations[b], settings)))

        selected_types = LoadSelection.get_selected_types(settings)

        if not selected_types:
            selected_types = list(set(element.is_a() for element in elements))

        elements_by_type = [[element for element in elements if element.is_a() == ifc_type] for ifc_type in selected_types]

        failed_types = set()
        for (element_number, element) in enumerate(elements):

            type_index = selected_types.index(element.is_a())
            type_elements = elements_by_type[type_index]
            type_number = type_elements.index(element)
            type_name = selected_types[type_index][3:]

            if storeys:
                storey_number = Storeys.get_storey_number(element, storeys, settings, storeys_numbers)
                if storey_number is None and "{S}" in settings.get("format"):
                    if report is not None:
                        report({'WARNING'}, f"Element {getattr(element, 'Name', '')} of type {element.is_a()} with ID {get_id(element)} is not contained in any storey.")
                    else:
                        raise Exception(f"Element {getattr(element, 'Name', '')} of type {element.is_a()} with ID {get_id(element)} is not contained in any storey.")
            else:
                storey_number = None
            
            number = NumberFormatting.format_number(settings, (element_number, type_number, storey_number), (len(elements), len(type_elements), len(storeys)), type_name)
            count = SaveNumber.save_number(ifc_file, element, number, settings, numbers_cache)
            if count is None:
                report({'WARNING'}, f"Failed to save number for element {getattr(element, 'Name', '')} of type {element.is_a()} with ID {get_id(element)}.")
                failed_types.add(element.is_a())
            else:
                number_count += count

        if failed_types:
            report({'WARNING'}, f"Failed to renumber the following types: {failed_types}")

        if settings.get("remove_toggle") and remove_count is not None:
            report({'INFO'}, f"Renumbered {number_count} objects, removed number from {remove_count} objects.")
        else:
            report({'INFO'}, f"Renumbered {number_count} objects.")

        return {'FINISHED'}, number_count

    def assign_numbers(self, settings, numbers_cache):
        """Assign numbers to selected objects based on their IFC type and location."""
        ifc_file = tool.Ifc.get()

        remove_count = 0

        if settings.get("remove_toggle"):
            for obj in bpy.context.scene.objects:
                if (settings.get("selected_toggle") and obj not in bpy.context.selected_objects) or \
                (settings.get("visible_toggle") and not obj.visible_get()):
                    element = tool.Ifc.get_entity(obj)
                    if element is not None and element.is_a(LoadSelection.get_parent_type(settings)):
                        count_diff = SaveNumber.remove_number(ifc_file, element, settings, numbers_cache)
                        remove_count += count_diff

        objects = LoadSelection.load_selected_objects(settings)

        if not objects:
            self.report({'WARNING'}, f"No objects selected or available for numbering, removed {remove_count} existing numbers.")
            return {'CANCELLED'}
        
        selected_types = LoadSelection.get_selected_types(settings)
        possible_types = [tupl[0] for tupl in LoadSelection.possible_types]
        
        selected_elements = []
        elements_locations = {}
        elements_dimensions = {}
        for obj in objects: 
            element = tool.Ifc.get_entity(obj)
            if element is None:
                continue
            if element.is_a() in selected_types:
                selected_elements.append(element)
                elements_locations[element] = ObjectGeometry.get_object_location(obj, settings)
                elements_dimensions[element] = ObjectGeometry.get_object_dimensions(obj)
            elif settings.get("remove_toggle") and element.is_a() in possible_types:
                remove_count += SaveNumber.remove_number(ifc_file, element, settings, numbers_cache)
        
        if not selected_elements:
            self.report({'WARNING'}, f"No elements selected or available for numbering, removed {remove_count} existing numbers.")

        storeys = Storeys.get_storeys(settings)
        res, _= AssignNumbers.number_elements(selected_elements, 
                                                    ifc_file, settings, 
                                                    elements_locations, 
                                                    elements_dimensions,  
                                                    storeys, 
                                                    numbers_cache,
                                                    report = self.report,
                                                    remove_count=remove_count)

        if settings.get("check_duplicates_toggle"):
            numbers = []
            for obj in bpy.context.scene.objects:
                element = tool.Ifc.get_entity(obj)
                if element is None or not element.is_a(LoadSelection.get_parent_type(settings)):
                    continue
                number = SaveNumber.get_number(element, settings, numbers_cache)
                if number in numbers:
                    self.report({'WARNING'}, f"The model contains duplicate numbers")
                    return {'FINISHED'}
                if number is not None:
                    numbers.append(number)

        return res

    def execute(self, context):
        return UndoOperator.execute_with_undo(self, context, self.assign_numbers)

    def rollback(self, data):
        UndoOperator.rollback(self, data)
    
    def commit(self, data):
        UndoOperator.commit(self, data)

class RemoveNumbers(bpy.types.Operator):
    bl_idname = "bim.remove_numbers"
    bl_label = "Remove numbers"
    bl_description = "Remove numbers from selected objects, from the selected attribute or Pset"
    bl_options = {"REGISTER", "UNDO"}

    def remove_numbers(self, settings, numbers_cache):
        """Remove numbers from selected objects"""
        ifc_file = tool.Ifc.get()
        
        remove_count = 0

        objects = bpy.context.selected_objects if settings.get("selected_toggle") else bpy.context.scene.objects
        if settings.get("visible_toggle"):
            objects = [obj for obj in objects if obj.visible_get()]

        if not objects:
            self.report({'WARNING'}, f"No objects selected or available for removal.")
            return {'CANCELLED'}
            
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if element is not None and element.is_a(LoadSelection.get_parent_type(settings)):
                remove_count += SaveNumber.remove_number(ifc_file, element, settings, numbers_cache)
                numbers_cache[get_id(element)] = None

        if remove_count == 0:
            self.report({'WARNING'}, f"No elements selected or available for removal.")
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"Removed {remove_count} existing numbers.")
        return {'FINISHED'}
        
    def execute(self, context):
        return UndoOperator.execute_with_undo(self, context, self.remove_numbers)

    def rollback(self, data):
        UndoOperator.rollback(self, data)
    
    def commit(self, data):
        UndoOperator.commit(self, data)

class ShowMessage(bpy.types.Operator):
    bl_idname = "bim.show_message"
    bl_label = "Show Message"
    bl_description = "Show a message in the info area"
    message: bpy.props.StringProperty() # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

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
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        with open(self.filepath, 'w') as f:
            json.dump(Settings.settings_dict(props), f)
        self.report({'INFO'}, f"Exported settings to {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = "settings.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ImportSettings(bpy.types.Operator):
    bl_idname = "bim.import_settings"
    bl_label = "Import Settings"
    bl_description = f"Import numbering settings from a JSON file"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        props = context.scene.BIMNumberingProperties
        with open(self.filepath, 'r') as f:
            settings = json.load(f)
            Settings.read_settings(self, settings, props)
        self.report({'INFO'}, f"Imported settings from {self.filepath}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
