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

from __future__ import annotations
import bpy
from typing import Any
import ifcopenshell
import ifcopenshell.util.sequence
import ifcopenshell.util.date
import bonsai.tool as tool

class GanttChartSequence:
    """Mixin class for generating and displaying the web-based Gantt chart."""

    @classmethod
    def create_tasks_json(cls, work_schedule: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
            sequence_type_map = {
                None: "FS",
                "START_START": "SS",
                "START_FINISH": "SF",
                "FINISH_START": "FS",
                "FINISH_FINISH": "FF",
                "USERDEFINED": "FS",
                "NOTDEFINED": "FS",
            }
            is_baseline = False
            if work_schedule.PredefinedType == "BASELINE":
                is_baseline = True
                relating_work_schedule = work_schedule.IsDeclaredBy[0].RelatingObject
                work_schedule = relating_work_schedule
            tasks_json = []
            for task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
                if is_baseline:
                    cls.create_new_task_json(task, tasks_json, sequence_type_map, baseline_schedule=work_schedule)
                else:
                    cls.create_new_task_json(task, tasks_json, sequence_type_map)
            return tasks_json

    @classmethod
    def create_new_task_json(cls, task, json, type_map=None, baseline_schedule=None):
            task_time = task.TaskTime
            resources = ifcopenshell.util.sequence.get_task_resources(task, is_deep=False)

            string_resources = ""
            resources_usage = ""
            for resource in resources:
                string_resources += resource.Name + ", "
                resources_usage += str(resource.Usage.ScheduleUsage) + ", " if resource.Usage else "-, "

            schedule_start = task_time.ScheduleStart if task_time else ""
            schedule_finish = task_time.ScheduleFinish if task_time else ""

            baseline_task = None
            if baseline_schedule:
                for rel in task.Declares:
                    for baseline_task in rel.RelatedObjects:
                        if baseline_schedule.id() == ifcopenshell.util.sequence.get_task_work_schedule(baseline_task).id():
                            baseline_task = task
                            break

            if baseline_task and baseline_task.TaskTime:
                compare_start = baseline_task.TaskTime.ScheduleStart
                compare_finish = baseline_task.TaskTime.ScheduleFinish
            else:
                compare_start = schedule_start
                compare_finish = schedule_finish
            task_name = task.Name or "Unnamed"
            task_name = task_name.replace("\n", "")
            data = {
                "pID": task.id(),
                "pName": task_name,
                "pCaption": task_name,
                "pStart": schedule_start,
                "pEnd": schedule_finish,
                "pPlanStart": compare_start,
                "pPlanEnd": compare_finish,
                "pMile": 1 if task.IsMilestone else 0,
                "pRes": string_resources,
                "pComp": 0,
                "pGroup": 1 if task.IsNestedBy else 0,
                "pParent": task.Nests[0].RelatingObject.id() if task.Nests else 0,
                "pOpen": 1,
                "pCost": 1,
                "ifcduration": (
                    str(ifcopenshell.util.date.ifc2datetime(task_time.ScheduleDuration))
                    if (task_time and task_time.ScheduleDuration)
                    else ""
                ),
                "resourceUsage": resources_usage,
            }
            if task_time and task_time.IsCritical:
                data["pClass"] = "gtaskred"
            elif data["pGroup"]:
                data["pClass"] = "ggroupblack"
            elif data["pMile"]:
                data["pClass"] = "gmilestone"
            else:
                data["pClass"] = "gtaskblue"

            data["pDepend"] = ",".join(
                [f"{rel.RelatingProcess.id()}{type_map[rel.SequenceType]}" for rel in task.IsSuccessorFrom or []]
            )
            json.append(data)
            for nested_task in ifcopenshell.util.sequence.get_nested_tasks(task):
                cls.create_new_task_json(nested_task, json, type_map, baseline_schedule)

    @classmethod
    def generate_gantt_browser_chart(
            cls, task_json: list[dict[str, Any]], work_schedule: ifcopenshell.entity_instance
        ) -> None:
            if not bpy.context.scene.WebProperties.is_connected:
                bpy.ops.bim.connect_websocket_server(page="sequencing")
            gantt_data = {"tasks": task_json, "work_schedule": work_schedule.get_info(recursive=True)}
            tool.Web.send_webui_data(data=gantt_data, data_key="gantt_data", event="gantt_data")