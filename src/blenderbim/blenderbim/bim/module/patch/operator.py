import os
import bpy
import json
from .helper import extract_docs


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


class PopulatePatchArguments(bpy.types.Operator):
    bl_idname = "bim.populate_patch_arguments"
    bl_label = "Update IFC Patch arguments"
    TYPE_BINDINGS = {
        "str": "string",
    
    }
    recipe: bpy.props.StringProperty()

    def execute(self, context):
        import importlib
        import ifcpatch

        patch_args = context.scene.BIMPatchProperties.ifc_patch_args_attr
        patch_args.clear()
        recipe = self.recipe
        spec = importlib.util.spec_from_file_location(recipe, f"{ifcpatch.__path__[0]}/recipes/{recipe}.py")
        patcher = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(patcher)
            try:
                docs = extract_docs(patcher.Patcher, boilerplate_args=("src", "file", "logger", "args"))
                if "inputs" in docs:
                    for arg_name in docs["inputs"]:
                        arg_info = docs["inputs"][arg_name]
                        new_attr = patch_args.add()
                        new_attr.data_type = self.TYPE_BINDINGS[arg_info["type"]]
                        new_attr.name = arg_name
                        if new_attr.data_type == "string":
                            new_attr.string_value = arg_info.get("default", "")
                        elif new_attr.data_type == "float":
                            new_attr.float_value = arg_info.get("default", 0)
                        elif new_attr.data_type == "integer":
                            new_attr.int_value = arg_info.get("default", 0)
                        elif new_attr.data_type == "boolean":
                            new_attr.bool_value = arg_info.get("default", False)

                        new_attr.description =arg_info.get("description", "")

            except AttributeError as e:
                print(e)
        except ModuleNotFoundError as e:
            print("Error : " + str(e) + "in " + str(patcher))    
        return {"FINISHED"}
