# Ifc4D - IFC scheduling utility
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of Ifc4D.
#
# Ifc4D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc4D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc4D.  If not, see <http://www.gnu.org/licenses/>.


import csv
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import locale
import re


class Csv2Ifc:
    def __init__(self):
        self.csv = None
        self.file = None
        self.tasks = []
        self.work_schedule = None
        self.work_plan = None
        self.is_schedule_of_rates = False
        self.units = {}

    def execute(self):
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self):
        self.parents = {}
        self.headers = {}
        locale.setlocale(locale.LC_ALL, "")  # set the system locale
        with open(self.csv, "r", encoding="ISO-8859-1") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if not row[0]:
                    continue
                if row[0] == "Hierarchy":
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        self.headers[col] = i
                    continue
                task = self.get_row_task(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.tasks.append(task)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(task)
                self.parents[hierarchy_key] = task

    def parse_task_rel(self, task_relationships_str):
        rels = []
        if task_relationships_str:
            for rel_str in task_relationships_str.split(";"):
                rel_parts = re.split(r"(\d+)", rel_str)
                task_1 = rel_parts[1]
                rel_type = rel_parts[2]
                task_2 = rel_parts[3]
                rels.append(
                    {
                        "rel_type": rel_type,
                        "task_1": task_1,
                        "task_2": task_2,
                    }
                )
        return rels

    def get_row_task(self, row):
        hours_per_day = 8
        hierarchy = row[self.headers["Hierarchy"]]
        identification = row[self.headers["Identification"]]
        task_name = row[self.headers["Name"]]

        task_relationships = self.parse_task_rel(row[self.headers["Relationships"]])

        scheduled_start_date = (
            ifcopenshell.util.date.string_to_date(row[self.headers["ScheduleStart"]])
            if row[self.headers["ScheduleStart"]]
            else None
        )
        scheduled_finish_date = (
            ifcopenshell.util.date.string_to_date(row[self.headers["ScheduleFinish"]])
            if row[self.headers["ScheduleFinish"]]
            else None
        )
        scheduled_duration = (
            ifcopenshell.util.date.string_to_duration(row[self.headers["ScheduleDuration"]])
            if row[self.headers["ScheduleDuration"]]
            else None
        )
        actual_start_date = (
            ifcopenshell.util.date.string_to_date(row[self.headers["ActualStart"]])
            if row[self.headers["ActualStart"]]
            else None
        )
        actual_finish_date = (
            ifcopenshell.util.date.string_to_date(row[self.headers["ActualFinish"]])
            if row[self.headers["ActualFinish"]]
            else None
        )
        actual_duration = (
            ifcopenshell.util.date.string_to_duration(row[self.headers["ActualDuration"]])
            if row[self.headers["ActualDuration"]]
            else None
        )

        return {
            "Hierarchy": hierarchy,
            "Identification": identification,
            "Name": task_name,
            "Relationships": task_relationships,
            "ScheduleStart": scheduled_start_date,
            "ScheduleFinish": scheduled_finish_date,
            "ScheduleDuration": scheduled_duration,
            "ActualStart": actual_start_date,
            "ActualFinish": actual_finish_date,
            "ActualDuration": actual_duration,
            "children": [],
        }

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.run("sequence.add_work_plan", self.file)
        self.work_schedule = self.create_work_schedule()
        self.create_tasks(self.tasks)
        self.create_rel_sequences(self.tasks)

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        self.work_plan = self.file.create_entity("IfcWorkPlan")

    def create_tasks(self, tasks, parent=None):
        for task in tasks:
            self.create_task(task, parent)

    def create_rel_sequences(self, tasks=None):
        self.sequence_type_map = {
            "FF": "FINISH_FINISH",
            "FS": "FINISH_START",
            "SF": "START_FINISH",
            "SS": "START_START",
        }
        for task in tasks:
            self.create_rel_sequence(task)

    def create_work_schedule(self):
        return ifcopenshell.api.run("sequence.add_work_schedule", self.file, name="import", work_plan=self.work_plan)

    def create_task(self, task, parent_task=None):
        if parent_task is None:
            task["ifc"] = ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=self.work_schedule)
        else:
            task["ifc"] = ifcopenshell.api.run("sequence.add_task", self.file, parent_task=parent_task)

        ifcopenshell.api.run(
            "sequence.edit_task",
            self.file,
            task=task["ifc"],
            attributes={
                "Name": task["Name"],
                "Identification": task["Identification"],
                # "IsMilestone": task["ScheduleStart"] == task["ScheduleFinish"],
            },
        )
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task["ifc"])
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleStart": task["ScheduleStart"],
                "ScheduleFinish": task["ScheduleFinish"],
                "DurationType": "WORKTIME" if task["ScheduleDuration"] else None,
                "ScheduleDuration": task["ScheduleDuration"],
                "ActualStart": task["ActualStart"],
                "ActualFinish": task["ActualFinish"],
                "ActualDuration": task["ActualDuration"],
            },
        )
        self.create_tasks(task["children"], task["ifc"])

    def get_entity_by_identification(self, tasks, task_identification):
        for task in tasks or []:
            if task["Identification"].replace(".", "").replace(" ", "") == task_identification.replace(" ", ""):
                return task["ifc"]
            else:
                entity = self.get_entity_by_identification(task["children"], task_identification)
                if entity:
                    return entity
        return None

    def create_rel_sequence(self, task=None):
        for rel in task["Relationships"] or []:
            task_1 = self.get_entity_by_identification(self.tasks, rel["task_1"])
            task_2 = self.get_entity_by_identification(self.tasks, rel["task_2"])
            rel_type = self.sequence_type_map[rel["rel_type"]]
            rel_sequence = ifcopenshell.api.run(
                "sequence.assign_sequence",
                self.file,
                related_process=task_2,
                relating_process=task_1,
                sequence_type=rel_type,
            )
            if rel_type:
                ifcopenshell.api.run(
                    "sequence.edit_sequence",
                    self.file,
                    rel_sequence=rel_sequence,
                    attributes={"SequenceType": rel_type},
                )
        self.create_rel_sequences(task["children"])
