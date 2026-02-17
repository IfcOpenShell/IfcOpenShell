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
import ifcopenshell.api.root
import ifcopenshell.api.sequence
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
                if not row or not row[0]:
                    continue
                if row[0] == "Hierarchy":
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        self.headers[col] = i
                    continue
                task = self.get_row_task(row)
                hierarchy_key = int(float(row[0]))
                if hierarchy_key == 1:
                    self.tasks.append(task)
                else:
                    if hierarchy_key - 1 in self.parents:
                        self.parents[hierarchy_key - 1]["children"].append(task)
                self.parents[hierarchy_key] = task

    def parse_task_rel(self, task_relationships_str):
        rels = []
        if task_relationships_str:
            for rel_str in task_relationships_str.split(";"):
                rel_str = rel_str.strip()
                match = re.search(r"([A-Z]{2})", rel_str)
                if not match:
                    continue

                rel_type = match.group(1)
                parts = rel_str.split(rel_type)
                task_1 = parts[0]
                remaining_part = parts[1]

                lag_match = re.match(r"([+\-]\w+)(.*)", remaining_part)
                if lag_match:
                    lag = lag_match.group(1)
                    task_2 = lag_match.group(2)
                else:
                    lag = None
                    task_2 = remaining_part
                
                if task_1 and task_2 and rel_type:
                    rels.append({
                        "rel_type": rel_type,
                        "task_1": task_1,
                        "task_2": task_2,
                        "lag": lag
                    })
        return rels

    def get_row_task(self, row):
        task_relationships = self.parse_task_rel(row[self.headers.get("Relationships", -1)] if "Relationships" in self.headers else "")

        def get_date(col_name):
            if col_name in self.headers and row[self.headers[col_name]]:
                return ifcopenshell.util.date.string_to_date(row[self.headers[col_name]])
            return None

        def get_duration(col_name):
            if col_name in self.headers and row[self.headers[col_name]]:
                return ifcopenshell.util.date.string_to_duration(row[self.headers[col_name]])
            return None
        
        def get_bool(col_name):
            if col_name in self.headers and row[self.headers[col_name]]:
                return row[self.headers[col_name]].upper() == 'TRUE'
            return False

        def get_float(col_name):
            if col_name in self.headers and row[self.headers[col_name]]:
                try:
                    return float(row[self.headers[col_name]])
                except (ValueError, TypeError):
                    return None
            return None

        return {
            "Hierarchy": row[self.headers["Hierarchy"]],
            "Identification": row[self.headers["Identification"]],
            "Name": row[self.headers["Name"]],
            "Relationships": task_relationships,
            "ScheduleStart": get_date("ScheduleStart"),
            "ScheduleFinish": get_date("ScheduleFinish"),
            "ScheduleDuration": get_duration("ScheduleDuration"),
            "ActualStart": get_date("ActualStart"),
            "ActualFinish": get_date("ActualFinish"),
            "ActualDuration": get_duration("ActualDuration"),
            "EarlyStart": get_date("EarlyStart"),
            "EarlyFinish": get_date("EarlyFinish"),
            "LateStart": get_date("LateStart"),
            "LateFinish": get_date("LateFinish"),
            "IsCritical": get_bool("IsCritical"),
            "Completion": get_float("Completion"),
            "children": [],
        }

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)
        self.work_schedule = self.create_work_schedule()
        self.create_tasks(self.tasks)

        self.sequence_type_map = {
            "FF": "FINISH_FINISH",
            "FS": "FINISH_START",
            "SF": "START_FINISH",
            "SS": "START_START",
        }
        all_tasks = self.get_all_tasks_flat()
        for task in all_tasks:
            self.create_relationships_for_task(task)

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        self.work_plan = self.file.create_entity("IfcWorkPlan")

    def create_tasks(self, tasks, parent=None):
        for task in tasks:
            self.create_task(task, parent)

    def create_work_schedule(self):
        return ifcopenshell.api.sequence.add_work_schedule(self.file, name="import", work_plan=self.work_plan)

    def create_task(self, task, parent_task=None):
        if parent_task is None:
            task["ifc"] = ifcopenshell.api.sequence.add_task(self.file, work_schedule=self.work_schedule)
        else:
            task["ifc"] = ifcopenshell.api.sequence.add_task(self.file, parent_task=parent_task)

        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=task["ifc"],
            attributes={
                "Name": task["Name"],
                "Identification": task["Identification"],
            },
        )
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=task["ifc"])
        
        ifcopenshell.api.sequence.edit_task_time(
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
                "EarlyStart": task["EarlyStart"],
                "EarlyFinish": task["EarlyFinish"],
                "LateStart": task["LateStart"],
                "LateFinish": task["LateFinish"],
                "IsCritical": task["IsCritical"],
                "Completion": task["Completion"],
            },
        )
        self.create_tasks(task["children"], task["ifc"])

    def get_all_tasks_flat(self, tasks=None):
        if tasks is None:
            tasks = self.tasks
        flat_list = []
        for task in tasks:
            flat_list.append(task)
            flat_list.extend(self.get_all_tasks_flat(task["children"]))
        return flat_list

    def get_entity_by_identification(self, task_id):
        all_tasks = self.get_all_tasks_flat()
        for task in all_tasks:
            if task["Identification"].replace(".", "").replace(" ", "") == task_id.replace(".", "").replace(" ", ""):
                return task.get("ifc")
        return None

    def create_relationships_for_task(self, task):
        for rel in task.get("Relationships", []) or []:
            task_1_ifc = self.get_entity_by_identification(rel.get("task_1"))
            task_2_ifc = self.get_entity_by_identification(rel.get("task_2"))
            if not task_1_ifc or not task_2_ifc:
                continue

            time_lag = None
            if rel.get("lag"):
                try:
                    duration_str = rel["lag"].replace("+", "")
                    duration = ifcopenshell.util.date.string_to_duration(duration_str)
                    time_lag = self.file.create_entity(
                        "IfcLagTime",
                        LagValue=duration,
                        DurationType="WORKTIME"
                    )
                except Exception as e:
                    print(f"Advertencia: No se pudo analizar el tiempo de retraso '{rel['lag']}': {e}")
                    pass

            rel_type = self.sequence_type_map.get(rel.get("rel_type"))
            if rel_type:
                ifcopenshell.api.sequence.assign_sequence(
                    self.file,
                    related_process=task_2_ifc,
                    relating_process=task_1_ifc,
                    sequence_type=rel_type
                )

