# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcfm
import logging
import tempfile
import ifcopenshell
import blenderbim.tool as tool


class SelectFMIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_fm_ifc_file"
    bl_label = "Select FM IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    files: bpy.props.CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)

    def execute(self, context):
        props = context.scene.BIMFMProperties
        props.ifc_files.clear()
        dirname = os.path.dirname(self.filepath)
        for f in self.files:
            new = props.ifc_files.add()
            new.name = os.path.join(dirname, f.name)
        props.ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcFM(bpy.types.Operator):
    bl_idname = "bim.execute_ifcfm"
    bl_label = "Execute IfcFM"
    file_format: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(default="*.csv;*.ods;*.xlsx", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMFMProperties
        return props.should_load_from_memory or props.ifc_file

    def invoke(self, context, event):
        props = context.scene.BIMFMProperties
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, f".{props.format}")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        props = context.scene.BIMFMProperties
        ifc_file = tool.Ifc.get()
        filepaths = []
        if not (ifc_file and props.should_load_from_memory):
            if len(props.ifc_files):
                ifc_files = [ifcopenshell.open(f.name) for f in props.ifc_files]
                filepaths = [f.name for f in props.ifc_files]
            else:
                ifc_files = [ifcopenshell.open(props.ifc_file)]
        else:
            ifc_files = [ifc_file]

        for i, ifc_file in enumerate(ifc_files):
            if filepaths:
                dirname = os.path.dirname(self.filepath)
                prefix, _ = os.path.splitext(os.path.basename(filepaths[i]))
                basename = os.path.basename(self.filepath)
                filepath = os.path.join(dirname, f"{prefix}-{basename}")
            else:
                filepath = self.filepath
            parser = ifcfm.Parser(preset=props.engine)
            parser.parse(ifc_file)
            writer = ifcfm.Writer(parser)
            writer.write()
            if props.format == "csv":
                writer.write_csv("tmp/")
            elif props.format == "ods":
                writer.write_ods(filepath)
            elif props.format == "xlsx":
                writer.write_xlsx(filepath)
        return {"FINISHED"}


class SelectFMSpreadsheetFiles(bpy.types.Operator):
    bl_idname = "bim.select_fm_spreadsheet_files"
    bl_label = "Select FM Spreadsheet Files"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.ods;*.xlsx", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    files: bpy.props.CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement)

    def execute(self, context):
        props = context.scene.BIMFMProperties
        props.spreadsheet_files.clear()
        dirname = os.path.dirname(self.filepath)
        for f in self.files:
            new = props.spreadsheet_files.add()
            new.name = os.path.join(dirname, f.name)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcFMFederate(bpy.types.Operator):
    bl_idname = "bim.execute_ifcfm_federate"
    bl_label = "Execute IfcFM"
    file_format: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(default="*.ods;*.xlsx", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMFMProperties
        return props.spreadsheet_files

    def invoke(self, context, event):
        props = context.scene.BIMFMProperties
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, f".{props.format}")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        props = context.scene.BIMFMProperties
        parser = ifcfm.Parser(preset=props.engine)
        parser.federate([f.name for f in props.spreadsheet_files])
        writer = ifcfm.Writer(parser)
        writer.write()
        if props.format == "ods":
            writer.write_ods(self.filepath)
        elif props.format == "xlsx":
            writer.write_xlsx(self.filepath)
        return {"FINISHED"}
