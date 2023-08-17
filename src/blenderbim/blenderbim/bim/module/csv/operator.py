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

import os
import bpy
import json
import ifccsv
import logging
import tempfile
import webbrowser
import ifcopenshell
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.handler import purge_module_data


class AddCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.add_csv_attribute"
    bl_label = "Add CSV Attribute"
    bl_description = "Add a new IFC Attribute to the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        attribute = context.scene.CsvProperties.csv_attributes.add()
        return {"FINISHED"}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.CsvProperties.csv_attributes.remove(self.index)
        return {"FINISHED"}


class RemoveAllCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.remove_all_csv_attributes"
    bl_label = "Remove all CSV Attributes"
    bl_description = "Remove all IFC Attributes from the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.CsvProperties.csv_attributes.clear()
        return {"FINISHED"}


class ImportCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.import_csv_attributes"
    bl_label = "Import CSV Template"
    bl_description = "Import a json template for CSV export"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        csv_props = context.scene.CsvProperties
        csv_json = json.load(open(self.filepath))

        expression = csv_json.get("expression", "")
        if expression:
            csv_props.ifc_selector = expression

        attributes = csv_json.get("attributes", [])
        if attributes:
            csv_props.csv_attributes.clear()
            for attribute in attributes:
                csv_props.csv_attributes.add().name = attribute

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.export_csv_attributes"
    bl_label = "Export CSV Template"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save a json template for CSV export"
    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        csv_props = context.scene.CsvProperties

        csv_template = {}
        expression = csv_props.ifc_selector
        if expression:
            csv_template["expression"] = expression

        csv_attributes = []
        for attribute in csv_props.csv_attributes:
            attribute_name = attribute.name
            csv_attributes.append(attribute_name)
        if csv_attributes:
            csv_template["attributes"] = csv_attributes

        with open(self.filepath, "w") as outfile:
            json.dump(csv_template, outfile)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.export_ifccsv"
    bl_label = "Export IFC"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        props = context.scene.CsvProperties
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, f".{props.format}")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        props = context.scene.CsvProperties
        self.filepath = bpy.path.ensure_ext(self.filepath, f".{props.format}")
        if props.should_load_from_memory:
            ifc_file = IfcStore.get_file()
        else:
            ifc_file = ifcopenshell.open(props.csv_ifc_file)
        results = ifcopenshell.util.selector.filter_elements(ifc_file, props.ifc_selector)
        ifc_csv = ifccsv.IfcCsv()
        attributes = [a.name for a in props.csv_attributes]
        sep = props.csv_custom_delimiter if props.csv_delimiter == "CUSTOM" else props.csv_delimiter
        ifc_csv.export(
            ifc_file,
            results,
            attributes,
            output=self.filepath,
            format=props.format,
            delimiter=sep,
            null=props.null_value,
        )
        return {"FINISHED"}


class ImportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.import_ifccsv"
    bl_label = "Import CSV to IFC"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        props = context.scene.CsvProperties
        if props.should_load_from_memory:
            ifc_file = IfcStore.get_file()
        else:
            ifc_file = ifcopenshell.open(props.csv_ifc_file)
        ifc_csv = ifccsv.IfcCsv()
        sep = props.csv_custom_delimiter if props.csv_delimiter == "CUSTOM" else props.csv_delimiter
        ifc_csv.Import(ifc_file, self.filepath, delimiter=sep, null=props.null_value)
        if not props.should_load_from_memory:
            ifc_file.write(props.csv_ifc_file)
        purge_module_data()
        return {"FINISHED"}


class EyedropIfcCsv(bpy.types.Operator):
    bl_idname = "bim.eyedrop_ifccsv"
    bl_label = "Query Selected Items"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global_ids = []
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                global_id = getattr(element, "GlobalId", None)
                if global_id:
                    global_ids.append(global_id)
        context.scene.CsvProperties.ifc_selector = ",".join(global_ids)
        return {"FINISHED"}


class SelectCsvIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_csv_ifc_file"
    bl_label = "Select CSV IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.CsvProperties.csv_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
