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
import tempfile
import webbrowser

try:
    import bimtester
    import bimtester.run
    import bimtester.reports
except:
    print("Failed to load BIMTester. Try disabling other add-ons, in particular Blender-OSM. See bug #1318.")

from pathlib import Path
from blenderbim.bim.ifc import IfcStore


class ExecuteBIMTester(bpy.types.Operator):
    bl_idname = "bim.execute_bim_tester"
    bl_label = "Execute BIMTester"

    @classmethod
    def poll(cls, context):
        props = context.scene.BimTesterProperties
        return (props.ifc_file or props.should_load_from_memory) and props.feature

    def execute(self, context):
        props = context.scene.BimTesterProperties

        with tempfile.TemporaryDirectory() as dirpath:
            report = os.path.join(dirpath, "{}.html".format(props.feature))
            args = {
                "action": "run",
                "advanced_arguments": "",
                "console": False,
                "feature": props.feature,
                "ifc": props.ifc_file,
                "path": "",
                "report": report,
                "schema_file": "",
                "schema_name": "",
                "lang": "en",
                "steps": props.steps,
            }
            use_stored_ifc = props.should_load_from_memory and IfcStore.get_file()
            runner = bimtester.run.TestRunner(args["ifc"], ifc=IfcStore.get_file() if use_stored_ifc else None)
            report_json = runner.run(args)
            bimtester.reports.ReportGenerator().generate(report_json, args["report"])
            webbrowser.open("file://" + report)
        return {"FINISHED"}


class BIMTesterPurge(bpy.types.Operator):
    bl_idname = "bim.bim_tester_purge"
    bl_label = "Purge Tests"

    def execute(self, context):
        cwd = os.getcwd()
        os.chdir(context.scene.BimTesterProperties.features_dir)
        bimtester.clean.TestPurger().purge()
        os.chdir(cwd)
        return {"FINISHED"}


class SelectFeature(bpy.types.Operator):
    bl_idname = "bim.select_feature"
    bl_label = "Select Feature / IDS"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".feature"
    filter_glob: bpy.props.StringProperty(default="*.feature;*.xml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BimTesterProperties.feature = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSteps(bpy.types.Operator):
    bl_idname = "bim.select_steps"
    bl_label = "Select Steps"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default="*.py", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BimTesterProperties.steps = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBIMTesterIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_bimtester_ifc_file"
    bl_label = "Select BIMTester IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BimTesterProperties.ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class RejectElement(bpy.types.Operator):
    bl_idname = "bim.reject_element"
    bl_label = "Reject Element"

    def execute(self, context):
        lines = []
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            lines.append(
                " * The element {} should not exist because {}".format(
                    self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId,
                    context.scene.BimTesterProperties.qa_reject_element_reason,
                )
            )
        QAHelper.append_to_scenario(lines, context)
        return {"FINISHED"}


class ApproveClass(bpy.types.Operator):
    bl_idname = "bim.approve_class"
    bl_label = "Approve Class"

    def execute(self, context):
        lines = []
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            lines.append(" * The element {} is an {}".format(element.GlobalId, element.is_a()))
        QAHelper.append_to_scenario(lines, context)
        return {"FINISHED"}


class RejectClass(bpy.types.Operator):
    bl_idname = "bim.reject_class"
    bl_label = "Reject Class"

    def execute(self, context):
        lines = []
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            lines.append(
                " * The element {} is an {}".format(
                    self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId,
                    context.scene.BimTesterProperties.audit_ifc_class,
                )
            )
        QAHelper.append_to_scenario(lines, context)
        return {"FINISHED"}


class SelectAudited(bpy.types.Operator):
    bl_idname = "bim.select_audited"
    bl_label = "Select Audited"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        audited_global_ids = []
        self.file = IfcStore.get_file()
        for filename in Path(context.scene.BimTesterProperties.features_dir).glob("*.feature"):
            with open(filename, "r") as feature_file:
                lines = feature_file.readlines()
                for line in lines:
                    words = line.strip().split()
                    for word in words:
                        if self.is_a_global_id(word):
                            audited_global_ids.append(word)
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId in audited_global_ids:
                obj.select_set(True)
        return {"FINISHED"}

    def is_a_global_id(self, word):
        return word[0] in ["0", "1", "2", "3"] and len(word) == 22


class QAHelper:
    @classmethod
    def append_to_scenario(cls, lines, context):
        filename = os.path.join(
            context.scene.BimTesterProperties.features_dir,
            context.scene.BimTesterProperties.features_file + ".feature",
        )
        if os.path.exists(filename + "~"):
            os.remove(filename + "~")
        os.rename(filename, filename + "~")
        with open(filename, "w") as destination:
            with open(filename + "~", "r") as source:
                is_in_scenario = False
                for source_line in source:
                    if (
                        "Scenario: " in source_line
                        and context.scene.BimTesterProperties.scenario == source_line.strip()[len("Scenario: ") :]
                    ):
                        is_in_scenario = True
                    elif is_in_scenario:
                        for line in lines:
                            destination.write(line + "\n")
                        is_in_scenario = False
                    destination.write(source_line)
        os.remove(filename + "~")
