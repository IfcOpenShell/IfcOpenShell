import os
import bpy
import json
import ifcpatch


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
    use_json_for_args: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        input_file = context.scene.BIMPatchProperties.ifc_patch_input
        return os.path.isfile(input_file) and "ifc" in os.path.splitext(input_file)[1]

    def execute(self, context):
        if self.use_json_for_args or not context.scene.BIMPatchProperties.ifc_patch_args_attr:
            arguments = json.loads(context.scene.BIMPatchProperties.ifc_patch_args or "[]")
        else:
            arguments = [arg.get_value() for arg in context.scene.BIMPatchProperties.ifc_patch_args_attr]

        ifcpatch.execute(
            {
                "input": context.scene.BIMPatchProperties.ifc_patch_input,
                "output": context.scene.BIMPatchProperties.ifc_patch_output,
                "recipe": context.scene.BIMPatchProperties.ifc_patch_recipes,
                "arguments": arguments,
                "log": os.path.join(context.scene.BIMProperties.data_dir, "process.log"),
            }
        )
        return {"FINISHED"}


class PopulatePatchArguments(bpy.types.Operator):
    bl_idname = "bim.populate_patch_arguments"
    bl_label = "Update IFC Patch arguments"
    inputs: bpy.props.StringProperty()

    def execute(self, context):
        patch_args = context.scene.BIMPatchProperties.ifc_patch_args_attr
        patch_args.clear()
        for name, _type, default, description in json.loads(self.inputs):
            new_attr = patch_args.add()
            new_attr.data_type = {
                "str": "string",
                "float": "float",
                "int": "integer",
                "bool": "boolean",
            }[_type]
            new_attr.name = name
            if default is not None:
                new_attr.set_value(default)
            new_attr.description = description
        return {"FINISHED"}
