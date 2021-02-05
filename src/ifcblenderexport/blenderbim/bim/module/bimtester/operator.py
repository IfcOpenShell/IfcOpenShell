import os
import bpy
import tempfile
import webbrowser
import ifcopenshell
import bimtester
import bimtester.run
import bimtester.reports
from pathlib import Path
from itertools import cycle
from blenderbim.bim.ifc import IfcStore


class ExecuteBIMTester(bpy.types.Operator):
    bl_idname = "bim.execute_bim_tester"
    bl_label = "Execute BIMTester"

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
                "steps": props.steps
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
        filename = os.path.join(
            bpy.context.scene.BimTesterProperties.features_dir,
            bpy.context.scene.BimTesterProperties.features_file + ".feature",
        )
        cwd = os.getcwd()
        os.chdir(bpy.context.scene.BimTesterProperties.features_dir)
        bimtester.clean.TestPurger().purge()
        os.chdir(cwd)
        return {"FINISHED"}


class SelectFeature(bpy.types.Operator):
    bl_idname = "bim.select_feature"
    bl_label = "Select Feature"
    filename_ext = ".feature"
    filter_glob: bpy.props.StringProperty(default="*.feature", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BimTesterProperties.feature = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSteps(bpy.types.Operator):
    bl_idname = "bim.select_steps"
    bl_label = "Select Steps"
    filename_ext = ".py"
    filter_glob: bpy.props.StringProperty(default="*.py", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BimTesterProperties.steps = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectBIMTesterIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_bimtester_ifc_file"
    bl_label = "Select BIMTester IFC File"
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
        for obj in bpy.context.selected_objects:
            lines.append(
                " * The element {} should not exist because {}".format(
                    self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId,
                    bpy.context.scene.BimTesterProperties.qa_reject_element_reason,
                )
            )
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class ApproveClass(bpy.types.Operator):
    bl_idname = "bim.approve_class"
    bl_label = "Approve Class"

    def execute(self, context):
        lines = []
        self.file = IfcStore.get_file()
        for obj in bpy.context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            lines.append(" * The element {} is an {}".format(element.GlobalId, element.is_a()))
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class RejectClass(bpy.types.Operator):
    bl_idname = "bim.reject_class"
    bl_label = "Reject Class"

    def execute(self, context):
        lines = []
        self.file = IfcStore.get_file()
        for obj in bpy.context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            lines.append(
                " * The element {} is an {}".format(
                    self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId,
                    bpy.context.scene.BimTesterProperties.audit_ifc_class,
                )
            )
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class SelectAudited(bpy.types.Operator):
    bl_idname = "bim.select_audited"
    bl_label = "Select Audited"

    def execute(self, context):
        audited_global_ids = []
        self.file = IfcStore.get_file()
        for filename in Path(bpy.context.scene.BimTesterProperties.features_dir).glob("*.feature"):
            with open(filename, "r") as feature_file:
                lines = feature_file.readlines()
                for line in lines:
                    words = line.strip().split()
                    for word in words:
                        if self.is_a_global_id(word):
                            audited_global_ids.append(word)
        for obj in bpy.context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId in audited_global_ids:
                obj.select_set(True)
        return {"FINISHED"}

    def is_a_global_id(self, word):
        return word[0] in ["0", "1", "2", "3"] and len(word) == 22


class QAHelper:
    @classmethod
    def append_to_scenario(cls, lines):
        filename = os.path.join(
            bpy.context.scene.BimTesterProperties.features_dir,
            bpy.context.scene.BimTesterProperties.features_file + ".feature",
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
                        and bpy.context.scene.BimTesterProperties.scenario == source_line.strip()[len("Scenario: ") :]
                    ):
                        is_in_scenario = True
                    elif is_in_scenario:
                        for line in lines:
                            destination.write(line + "\n")
                        is_in_scenario = False
                    destination.write(source_line)
        os.remove(filename + "~")


colour_list = [
    (0.651, 0.81, 0.892, 1),
    (0.121, 0.471, 0.706, 1),
    (0.699, 0.876, 0.54, 1),
    (0.199, 0.629, 0.174, 1),
    (0.983, 0.605, 0.602, 1),
    (0.89, 0.101, 0.112, 1),
    (0.989, 0.751, 0.427, 1),
    (0.986, 0.497, 0.1, 1),
    (0.792, 0.699, 0.839, 1),
    (0.414, 0.239, 0.603, 1),
    (0.993, 0.999, 0.6, 1),
    (0.693, 0.349, 0.157, 1),
]
