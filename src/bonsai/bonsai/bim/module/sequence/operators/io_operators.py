# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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

# Description: Operators for importing and exporting data from external formats.

import bpy
import time
from dateutil import parser
from bpy_extras.io_utils import ImportHelper, ExportHelper
import bonsai.tool as tool
import bonsai.core.sequence as core

# --- Operators ---

class ImportWorkScheduleCSV(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_work_schedule_csv"
    bl_label = "Import Work Schedule CSV"
    bl_description = "Import work schedule from the provided .csv file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.csv4d2ifc import Csv2Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        csv2ifc = Csv2Ifc()
        csv2ifc.csv = self.filepath
        csv2ifc.file = self.file
        csv2ifc.execute()
        # === Ensure Start/Finish columns are visible after import ===
        try:
            import bonsai.core.sequence as core
            props = tool.Sequence.get_work_schedule_props()
            existing = {c.name for c in getattr(props, "columns", [])}
            # These map to headers "Start" and "Finish" in the UI
            if "IfcTaskTime.ScheduleStart" not in existing:
                core.add_task_column(tool.Sequence, "IfcTaskTime", "ScheduleStart", "string")
            if "IfcTaskTime.ScheduleFinish" not in existing:
                core.add_task_column(tool.Sequence, "IfcTaskTime", "ScheduleFinish", "string")
        except Exception as e:
            print("Auto-add Start/Finish columns after CSV import failed:", e)
        # Default sort by Identification ascending after import
        try:
            props = tool.Sequence.get_work_schedule_props()
            props.sort_column = "IfcTask.Identification"
            props.is_sort_reversed = False
            import bonsai.core.sequence as core
            core.load_task_tree(tool.Ifc, tool.Sequence)
        except Exception:
            pass
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))

class ImportP6(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_p6"
    bl_label = "Import P6"
    bl_description = "Import provided .xml P6 file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.p62ifc import P62Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        p62ifc = P62Ifc()
        p62ifc.xml = self.filepath
        p62ifc.file = self.file
        p62ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p62ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))

class ImportP6XER(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_p6xer"
    bl_label = "Import P6 XER"
    bl_description = "Import provided .xer P6 file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xer"
    filter_glob: bpy.props.StringProperty(default="*.xer", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.p6xer2ifc import P6XER2Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        p6xer2ifc = P6XER2Ifc()
        p6xer2ifc.xer = self.filepath
        p6xer2ifc.file = self.file
        p6xer2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p6xer2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))

class ImportPP(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_pp"
    bl_label = "Import Powerproject .pp"
    bl_description = "Import provided .pp file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".pp"
    filter_glob: bpy.props.StringProperty(default="*.pp", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.pp2ifc import PP2Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        pp2ifc = PP2Ifc()
        pp2ifc.pp = self.filepath
        pp2ifc.file = self.file
        pp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        pp2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))

class ImportMSP(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_msp"
    bl_label = "Import MSP"
    bl_description = "Import provided .xml MSP file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.msp2ifc import MSP2Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        msp2ifc = MSP2Ifc()
        msp2ifc.xml = self.filepath
        msp2ifc.file = self.file
        msp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        msp2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))

class ExportMSP(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_msp"
    bl_label = "Export MSP"
    bl_description = "Export work schedule as .xml MSP file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def execute(self, context):
        from ifc4d.ifc2msp import Ifc2Msp

        self.file = tool.Ifc.get()
        start = time.time()
        ifc2msp = Ifc2Msp()
        ifc2msp.work_schedule = self.file.by_type("IfcWorkSchedule")[0]
        ifc2msp.xml = bpy.path.ensure_ext(self.filepath, ".xml")
        ifc2msp.file = self.file
        ifc2msp.holiday_start_date = parser.parse(self.holiday_start_date).date()
        ifc2msp.holiday_finish_date = parser.parse(self.holiday_finish_date).date()
        ifc2msp.execute()
        self.report({"INFO"}, "Export finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}

class ExportP6(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_p6"
    bl_label = "Export P6"
    bl_description = "Export work schedule as .xml P6 file."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def execute(self, context):
        from ifc4d.ifc2p6 import Ifc2P6

        self.file = tool.Ifc.get()
        start = time.time()
        ifc2p6 = Ifc2P6()
        ifc2p6.xml = bpy.path.ensure_ext(self.filepath, ".xml")
        ifc2p6.file = self.file
        ifc2p6.holiday_start_date = parser.parse(self.holiday_start_date).date()
        ifc2p6.holiday_finish_date = parser.parse(self.holiday_finish_date).date()
        ifc2p6.execute()
        self.report({"INFO"}, "Export finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}
    