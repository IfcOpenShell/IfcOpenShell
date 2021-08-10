import os
import bpy
import json


class SelectIfcPatchInput(bpy.types.Operator):
    bl_idname = "bim.select_ifc_patch_input"
    bl_label = "Select IFC Patch Input"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMPatchProperties.ifc_patch_input = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectIfcPatchOutput(bpy.types.Operator):
    bl_idname = "bim.select_ifc_patch_output"
    bl_label = "Select IFC Patch Output"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMPatchProperties.ifc_patch_output = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcPatch(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_patch"
    bl_label = "Execute IFCPatch"
    file_format: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        input_file = context.scene.BIMPatchProperties.ifc_patch_input
        return os.path.isfile(input_file) and "ifc" in os.path.splitext(input_file)[1]

    def execute(self, context):
        import ifcpatch

        ifcpatch.execute(
            {
                "input": context.scene.BIMPatchProperties.ifc_patch_input,
                "output": context.scene.BIMPatchProperties.ifc_patch_output,
                "recipe": context.scene.BIMPatchProperties.ifc_patch_recipes,
                "arguments": json.loads(context.scene.BIMPatchProperties.ifc_patch_args or "[]"),
                "log": os.path.join(context.scene.BIMProperties.data_dir, "process.log"),
            }
        )
        return {"FINISHED"}
