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
        attribute = context.scene.CsvProperties.csv_attributes.add()
        return {"FINISHED"}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.CsvProperties.csv_attributes.remove(self.index)
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

        props = context.scene.CsvProperties
        self.filepath = bpy.path.ensure_ext(self.filepath, ".csv")
        if props.should_load_from_memory:
            ifc_file = IfcStore.get_file()
        else:
            ifc_file = ifcopenshell.open(props.csv_ifc_file)
        selector = ifcopenshell.util.selector.Selector()
        results = selector.parse(ifc_file, props.ifc_selector)
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.attributes = [a.name for a in props.csv_attributes]
        ifc_csv.selector = selector
        if props.csv_delimiter == "CUSTOM":
            ifc_csv.delimiter = props.csv_custom_delimiter
        else:
            ifc_csv.delimiter = props.csv_delimiter
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
        ifc_csv.Import(context.scene.CsvProperties.csv_ifc_file)
        return {"FINISHED"}


class EyedropIfcCsv(bpy.types.Operator):
    bl_idname = "bim.eyedrop_ifccsv"
    bl_label = "Query Selected Items"

    def execute(self, context):
        global_ids = []
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            if hasattr(obj, "BIMObjectProperties") and obj.BIMObjectProperties.ifc_definition_id:
                global_ids.append("#" + self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId)
        context.scene.CsvProperties.ifc_selector = "|".join(global_ids)
        return {"FINISHED"}


class SelectCsvIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_csv_ifc_file"
    bl_label = "Select CSV IFC File"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")


    def execute(self, context):
        context.scene.CsvProperties.csv_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
