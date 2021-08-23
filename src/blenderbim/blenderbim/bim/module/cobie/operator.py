
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
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.COBieProperties.cobie_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectCobieJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_cobie_json_file"
    bl_label = "Select COBie JSON File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.COBieProperties.cobie_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcCobie(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_cobie"
    bl_label = "Execute IFCCOBie"
    file_format: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.COBieProperties
        return props.should_load_from_memory or props.cobie_ifc_file

    def execute(self, context):
        from cobie import IfcCobieParser
        props = context.scene.COBieProperties

        if props.should_load_from_memory:
            output_dir = tempfile.gettempdir()
        else:
            output_dir = os.path.dirname(props.cobie_ifc_file)  
        
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

