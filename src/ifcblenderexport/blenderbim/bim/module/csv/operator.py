import bpy
import ifccsv
import ifcopenshell
import os
import logging
import json
import webbrowser
import tempfile
from blenderbim.bim.ifc import IfcStore



class AddCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.add_csv_attribute"
    bl_label = "Add CSV Attribute"

    def execute(self, context):
        attribute = bpy.context.scene.CsvProperties.csv_attributes.add()
        return {"FINISHED"}

class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.CsvProperties.csv_attributes.remove(self.index)
        return {"FINISHED"}

class ExportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.export_ifccsv"
    bl_label = "Export IFC to CSV"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        self.filepath = bpy.path.ensure_ext(self.filepath, ".csv")
        ifc_file = ifcopenshell.open(bpy.context.scene.CsvProperties.csv_ifc_file)
        selector = ifcopenshell.util.selector.Selector()
        results = selector.parse(ifc_file, bpy.context.scene.CsvProperties.ifc_selector)
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.attributes = [a.name for a in bpy.context.scene.CsvProperties.csv_attributes]
        ifc_csv.selector = selector
        if bpy.context.scene.CsvProperties.csv_delimiter == "CUSTOM":
            ifc_csv.delimiter = bpy.context.scene.CsvProperties.csv_custom_delimiter
        else:
            ifc_csv.delimiter = bpy.context.scene.CsvProperties.csv_delimiter
        ifc_csv.export(ifc_file, results)
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

        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.Import(bpy.context.scene.CsvProperties.csv_ifc_file)
        return {"FINISHED"}

class EyedropIfcCsv(bpy.types.Operator):
    bl_idname = "bim.eyedrop_ifccsv"
    bl_label = "Query Selected Items"

    def execute(self, context):
        global_ids = []
        for obj in bpy.context.selected_objects:
            if hasattr(obj, "BIMObjectProperties") and obj.BIMObjectProperties.attributes.get("GlobalId"):
                global_ids.append("#" + obj.BIMObjectProperties.attributes.get("GlobalId").string_value)
        bpy.context.scene.CsvProperties.ifc_selector = "|".join(global_ids)
        return {"FINISHED"}

