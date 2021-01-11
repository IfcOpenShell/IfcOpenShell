import bpy
import blenderbim.bim.module.context.add_context as add_context
import blenderbim.bim.module.context.remove_context as remove_context
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.context.data import Data


class SelectCobieIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_cobie_ifc_file"
    bl_label = "Select COBie IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.cobie_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectCobieJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_cobie_json_file"
    bl_label = "Select COBie JSON File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.cobie_json_file = self.filepath
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

        output_dir = os.path.dirname(bpy.context.scene.BIMProperties.cobie_ifc_file)
        output = os.path.join(output_dir, "output")
        logger = logging.getLogger("IFCtoCOBie")
        fh = logging.FileHandler(os.path.join(output_dir, "cobie.log"))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s : %(levelname)s : %(message)s"))
        logger = logging.getLogger("IFCtoCOBie")
        logger.addHandler(fh)
        selector = ifcopenshell.util.selector.Selector()
        if bpy.context.scene.BIMProperties.cobie_json_file:
            with open(bpy.context.scene.BIMProperties.cobie_json_file, "r") as f:
                custom_data = json.load(f)
        else:
            custom_data = {}
        parser = IfcCobieParser(logger, selector)
        parser.parse(
            bpy.context.scene.BIMProperties.cobie_ifc_file,
            bpy.context.scene.BIMProperties.cobie_types,
            bpy.context.scene.BIMProperties.cobie_components,
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

