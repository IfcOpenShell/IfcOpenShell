import bpy
import os
import logging
import ifcopenshell
import json
import webbrowser
import tempfile
from blenderbim.bim.ifc import IfcStore


class SelectCobieIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_cobie_ifc_file"
    bl_label = "Select COBie IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.COBieProperties.cobie_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectCobieJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_cobie_json_file"
    bl_label = "Select COBie JSON File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.COBieProperties.cobie_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcCobie(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_cobie"
    bl_label = "Execute IFCCOBie"
    file_format: bpy.props.StringProperty()

    def execute(self, context):
        from cobie import IfcCobieParser
        props = bpy.context.scene.COBieProperties
        
        output_dir = os.path.dirname(props.cobie_ifc_file)
        
        if props.should_load_from_memory:
            output_dir = tempfile.gettempdir()
        
        output = os.path.join(output_dir, "output")
        logger = logging.getLogger("IFCtoCOBie")
        fh = logging.FileHandler(os.path.join(output_dir, "cobie.log"))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))
        logger = logging.getLogger("IFCtoCOBie")
        logger.addHandler(fh)
        selector = ifcopenshell.util.selector.Selector()
        if props.cobie_json_file:
            with open(props.cobie_json_file, "r") as f:
                custom_data = json.load(f)
        else:
            custom_data = {}
        parser = IfcCobieParser(logger, selector)

        ifc_file = IfcStore.get_file()
        
        if not (ifc_file and props.should_load_from_memory):
            ifc_file = props.cobie_ifc_file
        
        parser.parse(
            ifc_file,
            props.cobie_types,
            props.cobie_components,
            custom_data,
        )
        if self.file_format == "xlsx":
            from cobie import CobieXlsWriter

            writer = CobieXlsWriter(parser, output)
            writer.write()
            webbrowser.open("file://" + output + "." + self.file_format)
        elif self.file_format == "ods":
            from cobie import CobieOdsWriter

            writer = CobieOdsWriter(parser, output)
            writer.write()
            webbrowser.open("file://" + output + "." + self.file_format)
        else:
            from cobie import CobieCsvWriter

            writer = CobieCsvWriter(parser, output_dir)
            writer.write()
            webbrowser.open("file://" + output_dir)
        webbrowser.open("file://" + output_dir + "/cobie.log")
        return {"FINISHED"}

