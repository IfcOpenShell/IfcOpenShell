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
import time
import tempfile
import webbrowser
import ifctester
import ifctester.ids
import ifctester.reporter
import ifcopenshell
import blenderbim.tool as tool


class ExecuteIfcTester(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_tester"
    bl_label = "Execute IfcTester"

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcTesterProperties
        return (props.ifc_file or props.should_load_from_memory) and props.specs

    def execute(self, context):
        props = context.scene.IfcTesterProperties

        with tempfile.TemporaryDirectory() as dirpath:
            start = time.time()
            output = os.path.join(dirpath, "{}.html".format(props.specs))

            if props.should_load_from_memory and tool.Ifc.get():
                ifc = tool.Ifc.get()
            else:
                ifc = ifcopenshell.open(props.ifc_file)

            specs = ifctester.ids.open(props.specs)
            print("Finished loading:", time.time() - start)
            start = time.time()
            specs.validate(ifc)
            print("Finished validating:", time.time() - start)
            start = time.time()

            engine = ifctester.reporter.Html(specs)
            engine.report()
            engine.to_file(output)
            webbrowser.open("file://" + output)
        return {"FINISHED"}


class SelectSpecs(bpy.types.Operator):
    bl_idname = "bim.select_specs"
    bl_label = "Select IDS"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ids"
    filter_glob: bpy.props.StringProperty(default="*.ids;*.xml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.IfcTesterProperties.specs = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectIfcTesterIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_ifctester_ifc_file"
    bl_label = "Select IfcTester IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.IfcTesterProperties.ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
