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

import os
import bpy
import json
import ifcopenshell
import ifcpatch
import bonsai.tool as tool
import bonsai.core.patch as core
import bonsai.bim.handler
from pathlib import Path


class SelectIfcPatchInput(bpy.types.Operator):
    bl_idname = "bim.select_ifc_patch_input"
    bl_label = "Select IFC Patch Input"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifcZIP;*.ifcXML", options={"HIDDEN"})
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
        props = context.scene.BIMPatchProperties
        if props.ifc_patch_recipes == "-":
            cls.poll_message_set("No recipe selected.")
            return False
        if not props.should_load_from_memory and not props.ifc_patch_input:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    def execute(self, context):
        props = context.scene.BIMPatchProperties
        arguments = []
        if props.ifc_patch_args_attr:
            arguments = [arg.get_value() for arg in props.ifc_patch_args_attr]

        if props.should_load_from_memory and tool.Ifc.get():
            input_file = props.ifc_patch_input
            file = tool.Ifc.get()
        else:
            input_file = props.ifc_patch_input
            file = ifcopenshell.open(props.ifc_patch_input)

        # Store this in case the patch recipe resets the Blender session, such as by loading a new project.
        ifc_patch_output = props.ifc_patch_output or props.ifc_patch_input

        output = ifcpatch.execute(
            {
                "input": input_file,
                "file": file,
                "recipe": props.ifc_patch_recipes,
                "arguments": arguments,
                "log": os.path.join(context.scene.BIMProperties.data_dir, "process.log"),
            }
        )
        ifcpatch.write(output, ifc_patch_output)
        self.report({"INFO"}, f"{props.ifc_patch_recipes} patch executed successfully")
        return {"FINISHED"}


class UpdateIfcPatchArguments(bpy.types.Operator):
    bl_idname = "bim.update_ifc_patch_arguments"
    bl_label = "Update IFC Patch Arguments"
    recipe: bpy.props.StringProperty()

    def execute(self, context):
        if self.recipe == "-":
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
                data_type = arg_info.get("type", "str")
                if isinstance(data_type, list):
                    if "file" in data_type:
                        data_type = ["file"]

                    data_type = [dt for dt in data_type if dt != "NoneType"][0]

                new_attr.data_type = {
                    "Literal": "enum",
                    "file": "file",
                    "str": "string",
                    "float": "float",
                    "int": "integer",
                    "bool": "boolean",
                }[data_type]
                new_attr.name = self.pretty_arg_name(arg_name)
                if new_attr.data_type == "enum":
                    new_attr.enum_items = json.dumps(arg_info.get("enum_items", []))
                    new_attr.enum_value = arg_info.get("default", new_attr.get_value_default())
                    continue

                if new_attr.data_type == "file":
                    new_attr.filepath_value.single_file = arg_info.get("default", new_attr.get_value_default())
                    new_attr.filter_glob = arg_info.get("filter_glob", "*.ifc;*.ifczip;*.ifcxml")
                    continue

                new_attr.set_value(arg_info.get("default", new_attr.get_value_default()))
        return {"FINISHED"}

    def pretty_arg_name(self, arg_name: str) -> str:
        words = []

        for word in arg_name.split("_"):
            word = word.strip().capitalize()

            replacements = [("Dir", "Directory"), ("Sql", "SQL")]

            for prev, new in replacements:
                word = word.replace(prev, new)

            words.append(word)

        return " ".join(words)


class RunMigratePatch(bpy.types.Operator):
    bl_idname = "bim.run_migrate_patch"
    bl_label = "Run Migrate Patch"
    infile: bpy.props.StringProperty(name="Input IFC filepath")
    outfile: bpy.props.StringProperty(name="Output IFC filepath")
    schema: bpy.props.StringProperty(name="Target IFC schema")

    @classmethod
    def description(cls, context, properties):
        if not all((properties.infile, properties.outfile, properties.schema)):
            return ""
        return (
            f"Migrate file '{Path(properties.infile).name}' to IFC schema "
            f"{properties.schema} and save as '{Path(properties.outfile).name}'"
        )

    def execute(self, context):
        core.run_migrate_patch(tool.Patch, infile=self.infile, outfile=self.outfile, schema=self.schema)
        try:
            bpy.ops.file.refresh()
        except:
            pass  # Probably running in headless mode
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}
