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
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.core.patch as core
import blenderbim.bim.handler

try:
    import ifcpatch
except:
    print("IfcPatch not available")


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
        return os.path.isfile(input_file) and "ifc" in os.path.splitext(input_file)[1].lower()

    def execute(self, context):
        props = context.scene.BIMPatchProperties
        if self.use_json_for_args or not props.ifc_patch_args_attr:
            arguments = json.loads(props.ifc_patch_args or "[]")
        else:
            arguments = [arg.get_value() for arg in props.ifc_patch_args_attr]

        output = ifcpatch.execute(
            {
                "input": ifcopenshell.open(props.ifc_patch_input),
                "recipe": props.ifc_patch_recipes,
                "arguments": arguments,
                "log": os.path.join(context.scene.BIMProperties.data_dir, "process.log"),
            }
        )
        ifcpatch.write(output, props.ifc_patch_output)
        return {"FINISHED"}


class UpdateIfcPatchArguments(bpy.types.Operator):
    bl_idname = "bim.update_ifc_patch_arguments"
    bl_label = "Update IFC Patch arguments"
    recipe: bpy.props.StringProperty()

    def execute(self, context):
        if self.recipe == "":
            print("No Recipe Selected. Impossible to load arguments")
            return {"FINISHED"}
        patch_args = context.scene.BIMPatchProperties.ifc_patch_args_attr
        patch_args.clear()
        docs = ifcpatch.extract_docs(self.recipe, "Patcher", "__init__", ("src", "file", "logger", "args"))
        if docs and "inputs" in docs:
            inputs = docs["inputs"]
            for arg_name in inputs:
                arg_info = inputs[arg_name]
                new_attr = patch_args.add()
                new_attr.data_type = {
                    "str": "string",
                    "float": "float",
                    "int": "integer",
                    "bool": "boolean",
                }[arg_info.get("type", "str")]
                new_attr.name = arg_name
                new_attr.set_value(arg_info.get("default", new_attr.get_value_default()))
        return {"FINISHED"}


class RunMigratePatch(bpy.types.Operator):
    bl_idname = "bim.run_migrate_patch"
    bl_label = "Run Migrate Patch"
    infile: bpy.props.StringProperty()
    outfile: bpy.props.StringProperty()
    schema: bpy.props.StringProperty()

    def execute(self, context):
        core.run_migrate_patch(tool.Patch, infile=self.infile, outfile=self.outfile, schema=self.schema)
        try:
            bpy.ops.file.refresh()
        except:
            pass  # Probably running in headless mode
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}
