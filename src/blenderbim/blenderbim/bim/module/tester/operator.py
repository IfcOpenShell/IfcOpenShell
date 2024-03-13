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
import blenderbim.bim.handler
from pathlib import Path


class ExecuteIfcTester(bpy.types.Operator, tool.Ifc.Operator):
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
            output = Path(os.path.join(dirpath, "{}.html".format(props.specs)))

            filepath = None
            if props.should_load_from_memory and tool.Ifc.get():
                ifc = tool.Ifc.get()
                filepath = tool.Ifc.get_path()
            else:
                ifc = ifcopenshell.open(props.ifc_file)
                filepath = props.ifc_file

            specs = ifctester.ids.open(props.specs)
            print("Finished loading:", time.time() - start)
            start = time.time()
            specs.validate(ifc, filepath=filepath)

            print("Finished validating:", time.time() - start)
            start = time.time()

            if props.generate_html_report:
                engine = ifctester.reporter.Html(specs)
                engine.report()
                output_path = output.as_posix()
                engine.to_file(output_path)
                webbrowser.open(f"file://{output_path}")

            if props.generate_ods_report:
                engine = ifctester.reporter.Ods(specs)
                engine.report()
                output_path = output.with_suffix(".ods").as_posix()
                engine.to_file(output_path)

            report = None
            report = ifctester.reporter.Json(specs).report()["specifications"]
            if report:
                tool.Tester.specs = specs
                tool.Tester.report = report
            props.specifications.clear()
            for spec in report:
                print(spec)
                new_spec = props.specifications.add()
                new_spec.name = spec["name"]
                new_spec.description = spec["description"]
                new_spec.status = spec["status"]

        blenderbim.bim.handler.refresh_ui_data()
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


class SelectRequirement(bpy.types.Operator):
    bl_idname = "bim.select_requirement"
    bl_label = "Select Specification"
    bl_options = {"REGISTER", "UNDO"}
    spec_index: bpy.props.IntProperty()
    req_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.IfcTesterProperties
        report = tool.Tester.report
        props.old_index = self.spec_index
        failed_entities = report[self.spec_index]["requirements"][self.req_index]["failed_entities"]
        props.n_entities = len(failed_entities)
        props.has_entities = True if props.n_entities > 0 else False
        props.failed_entities.clear()

        for e in failed_entities:
            new_entity = props.failed_entities.add()
            new_entity.ifc_id = e["id"]
            new_entity.element = f'{e["class"]} | {e["name"]}'
            new_entity.reason = e["reason"]

        if props.flag:
            area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
            area.spaces[0].shading.color_type = "OBJECT"
            area.spaces[0].shading.show_xray = True
            failed_ids = [e["id"] for e in failed_entities]
            for obj in context.scene.objects:
                if obj.BIMObjectProperties.ifc_definition_id in failed_ids:
                    obj.color = (1, 0, 0, 1)
                else:
                    obj.color = (1, 1, 1, 1)

        return {"FINISHED"}


class SelectFailedEntities(bpy.types.Operator):
    bl_idname = "bim.select_failed_entities"
    bl_label = "Select Failed Entities"
    bl_options = {"REGISTER", "UNDO"}
    spec_index: bpy.props.IntProperty()
    req_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.IfcTesterProperties
        report = tool.Tester.report
        props.old_index = self.spec_index
        failed_entities = report[self.spec_index]["requirements"][self.req_index]["failed_entities"]
        props.n_entities = len(failed_entities)
        props.has_entities = True if props.n_entities > 0 else False

        failed_ids = [e["id"] for e in failed_entities]
        for obj in context.scene.objects:
            if obj.BIMObjectProperties.ifc_definition_id in failed_ids:
                obj.select_set(True)
            else:
                obj.select_set(False)

        return {"FINISHED"}


class SelectEntity(bpy.types.Operator):
    bl_idname = "bim.select_entity"
    bl_label = "Select Entity"
    bl_options = {"REGISTER", "UNDO"}
    ifc_id: bpy.props.IntProperty()

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        for obj in context.scene.objects:
            if obj.BIMObjectProperties.ifc_definition_id == self.ifc_id:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
        return {"FINISHED"}


class ExportBcf(bpy.types.Operator):
    bl_idname = "bim.export_bcf"
    bl_label = "Export BCF"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.bcf", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bcf_reporter = ifctester.reporter.Bcf(tool.Tester.specs)
        bcf_reporter.report()
        bcf_reporter.to_file(self.filepath)
        self.report({"INFO"}, "Finished exporting!")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
