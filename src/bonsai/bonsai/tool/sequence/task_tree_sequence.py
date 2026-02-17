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
import json
import re
import ifcopenshell
import ifcopenshell.util.sequence
import ifcopenshell.util.date
import bonsai.tool as tool
from typing import Optional
from .props_sequence import PropsSequence

class TaskTreeSequence:
    """Mixin class for managing the task tree UI."""

    @classmethod
    def load_task_tree(cls, work_schedule: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_task_tree_props()

        props.tasks.clear()
        schedule_props = tool.Sequence.get_work_schedule_props()
        cls.contracted_tasks = json.loads(schedule_props.contracted_tasks)

        # 1. Get ALL root tasks, as before
        root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
        
        # 2. APPLY FILTER: Pass the root tasks list to our new filtering function
        filtered_root_tasks = cls.get_filtered_tasks(root_tasks)

        # 3. Sort only the tasks that passed the filter
        related_objects_ids = cls.get_sorted_tasks_ids(filtered_root_tasks)
        
        # 4. Create UI elements only for the filtered and sorted tasks
        for related_object_id in related_objects_ids:
            cls.create_new_task_li(related_object_id, 0)

        # 5. AUTOFIX: Detect and fix variance inconsistencies after task reload
        try:
            from .variance_sequence import VarianceSequence
            VarianceSequence.detect_and_fix_variance_inconsistency()
        except Exception as e:
            print(f"[WARNING] Could not run variance autofix: {e}")

    @classmethod
    def get_sorted_tasks_ids(cls, tasks: list[ifcopenshell.entity_instance]) -> list[int]:
        props = tool.Sequence.get_work_schedule_props()

        def get_sort_key(task):
            # Sorting only applies to actual tasks, not the WBS
            # for rel in task.IsNestedBy:
            #     for object in rel.RelatedObjects:
            #         if object.is_a("IfcTask"):
            #             return "0000000000" + (task.Identification or "")
            column_type, name = props.sort_column.split(".")
            if column_type == "IfcTask":
                return task.get_info(task)[name] or ""
            elif column_type == "IfcTaskTime" and task.TaskTime:
                return task.TaskTime.get_info(task)[name] if task.TaskTime.get_info(task)[name] else ""
            return task.Identification or ""

        def natural_sort_key(i, _nsre=re.compile("([0-9]+)")):
            s = sort_keys[i]
            return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

        if props.sort_column:
            sort_keys = {task.id(): get_sort_key(task) for task in tasks}
            related_object_ids = sorted(sort_keys, key=natural_sort_key)
        else:
            related_object_ids = [task.id() for task in tasks]
        if props.is_sort_reversed:
            related_object_ids.reverse()
        return related_object_ids

    @classmethod
    def get_filtered_tasks(cls, tasks: list[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
        """
        Filters a list of tasks (and their children) based on active rules.
        If a parent task doesn't meet the filter, its children won't be shown either.
        """
        props = tool.Sequence.get_work_schedule_props()
        try:
            filter_rules = [r for r in getattr(props, "filters").rules if r.is_active]
        except Exception:
            return tasks

        if not filter_rules:
            return tasks

        filter_logic_is_and = getattr(props.filters, "logic", 'AND') == 'AND'
        
        def get_task_value(task, column_identifier):
            """Enhanced helper function to get the value of a column for a task."""
            if not task or not column_identifier:
                return None
            
            column_name = column_identifier.split('||')[0]

            if column_name == "Special.OutputsCount":
                try:
                    # Get both outputs and inputs for total Element 3D count
                    outputs_count = len(ifcopenshell.util.sequence.get_task_outputs(task, is_deep=False))
                    inputs_count = len(ifcopenshell.util.sequence.get_task_inputs(task, is_deep=False))
                    return outputs_count + inputs_count
                except Exception:
                    return 0

            if column_name in ("Special.VarianceStatus", "Special.VarianceDays"):
                ws_props = tool.Sequence.get_work_schedule_props()
                source_a = ws_props.variance_source_a
                source_b = ws_props.variance_source_b

                if source_a == source_b:
                    return None

                finish_attr_a = f"{source_a.capitalize()}Finish"
                finish_attr_b = f"{source_b.capitalize()}Finish"

                date_a = ifcopenshell.util.sequence.derive_date(task, finish_attr_a, is_latest=True)
                date_b = ifcopenshell.util.sequence.derive_date(task, finish_attr_b, is_latest=True)

                if date_a and date_b:
                    delta = date_b.date() - date_a.date()
                    variance_days = delta.days
                    if column_name == "Special.VarianceDays":
                        return variance_days
                    else:  # VarianceStatus
                        if variance_days > 0:
                            return f"Delayed (+{variance_days}d)"
                        elif variance_days < 0:
                            return f"Ahead ({variance_days}d)"
                        else:
                            return "On Time"
                return "N/A"

            try:
                ifc_class, attr_name = column_name.split('.', 1)
                if ifc_class == "IfcTask":
                    return getattr(task, attr_name, None)
                elif ifc_class == "IfcTaskTime":
                    task_time = getattr(task, "TaskTime", None)
                    return getattr(task_time, attr_name, None) if task_time else None
            except Exception:
                return None
            return None

        def task_matches_filters(task):
            """Checks if a single task meets the set of filters."""
            results = []
            for rule in filter_rules:
                task_value = get_task_value(task, rule.column)
                data_type = getattr(rule, 'data_type', 'string')
                op = rule.operator
                match = False

                if op == 'EMPTY':
                    match = task_value is None or str(task_value).strip() == ""
                elif op == 'NOT_EMPTY':
                    match = task_value is not None and str(task_value).strip() != ""
                else:
                    try:
                        if data_type == 'integer':
                            rule_value = rule.value_integer
                            task_value_num = int(task_value)
                            if op == 'EQUALS': match = task_value_num == rule_value
                            elif op == 'NOT_EQUALS': match = task_value_num != rule_value
                            elif op == 'GREATER': match = task_value_num > rule_value
                            elif op == 'LESS': match = task_value_num < rule_value
                            elif op == 'GTE': match = task_value_num >= rule_value
                            elif op == 'LTE': match = task_value_num <= rule_value
                        elif data_type in ('float', 'real'):
                            rule_value = rule.value_float
                            task_value_num = float(task_value)
                            if op == 'EQUALS': match = task_value_num == rule_value
                            elif op == 'NOT_EQUALS': match = task_value_num != rule_value
                            elif op == 'GREATER': match = task_value_num > rule_value
                            elif op == 'LESS': match = task_value_num < rule_value
                            elif op == 'GTE': match = task_value_num >= rule_value
                            elif op == 'LTE': match = task_value_num <= rule_value
                        elif data_type == 'boolean':
                            rule_value = bool(rule.value_boolean)
                            task_value_bool = bool(task_value)
                            if op == 'EQUALS': match = task_value_bool == rule_value
                            elif op == 'NOT_EQUALS': match = task_value_bool != rule_value
                        elif data_type == 'date':
                            task_date = bonsai.bim.module.sequence.utils.helper_utils.parse_datetime(str(task_value))
                            rule_date = bonsai.bim.module.sequence.utils.helper_utils.parse_datetime(rule.value_string)
                            if task_date and rule_date:
                                if op == 'EQUALS': match = task_date.date() == rule_date.date()
                                elif op == 'NOT_EQUALS': match = task_date.date() != rule_date.date()
                                elif op == 'GREATER': match = task_date > rule_date
                                elif op == 'LESS': match = task_date < rule_date
                                elif op == 'GTE': match = task_date >= rule_date
                                elif op == 'LTE': match = task_date <= rule_date
                        elif data_type == 'variance_status':
                            # Special handling for variance status filtering
                            rule_value = rule.value_variance_status
                            task_value_str = str(task_value) if task_value is not None else ""
                            if op == 'EQUALS': match = rule_value in task_value_str
                            elif op == 'NOT_EQUALS': match = rule_value not in task_value_str
                            elif op == 'CONTAINS': match = rule_value in task_value_str
                            elif op == 'NOT_CONTAINS': match = rule_value not in task_value_str
                        else: # string, enums, etc.
                            rule_value = (rule.value_string or "").lower()
                            task_value_str = (str(task_value) if task_value is not None else "").lower()
                            if op == 'CONTAINS': match = rule_value in task_value_str
                            elif op == 'NOT_CONTAINS': match = rule_value not in task_value_str
                            elif op == 'EQUALS': match = rule_value == task_value_str
                            elif op == 'NOT_EQUALS': match = rule_value != task_value_str
                    except (ValueError, TypeError, AttributeError):
                        match = False
                results.append(match)

            if not results: 
                return True
            return all(results) if filter_logic_is_and else any(results)

        filtered_list = []
        for task in tasks:
            nested_tasks = ifcopenshell.util.sequence.get_nested_tasks(task)
            filtered_children = cls.get_filtered_tasks(nested_tasks) if nested_tasks else []

            if task_matches_filters(task) or len(filtered_children) > 0:
                filtered_list.append(task)
                
        return filtered_list

    @classmethod
    def create_new_task_li(cls, related_object_id: int, level_index: int) -> None:
        task = tool.Ifc.get().by_id(related_object_id)
        props = tool.Sequence.get_task_tree_props()
        new = props.tasks.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in cls.contracted_tasks
        new.level_index = level_index
        if task.IsNestedBy:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cls.get_sorted_tasks_ids(ifcopenshell.util.sequence.get_nested_tasks(task)):
                    cls.create_new_task_li(related_object_id, level_index + 1)

    @classmethod
    def _load_task_date_properties(cls, item, task, date_type_prefix):
        """Helper to load a pair of dates (e.g., ScheduleStart/Finish) for a task item."""
        prop_prefix = date_type_prefix.lower()
        start_attr, finish_attr = f"{date_type_prefix}Start", f"{date_type_prefix}Finish"

        # Map 'schedule' to the old property names for compatibility
        if prop_prefix == "schedule":
            item_start, item_finish = "start", "finish"
        else:
            item_start, item_finish = f"{prop_prefix}_start", f"{prop_prefix}_finish"

        derived_start, derived_finish = f"derived_{item_start}", f"derived_{item_finish}"

        task_time = getattr(task, "TaskTime", None)
        if task_time and (getattr(task_time, start_attr, None) or getattr(task_time, finish_attr, None)):
            start_val = getattr(task_time, start_attr, None)
            finish_val = getattr(task_time, finish_attr, None)
            setattr(item, item_start, ifcopenshell.util.date.canonicalise_time(ifcopenshell.util.date.ifc2datetime(start_val)) if start_val else "-")
            setattr(item, item_finish, ifcopenshell.util.date.canonicalise_time(ifcopenshell.util.date.ifc2datetime(finish_val)) if finish_val else "-")
            setattr(item, derived_start, "")
            setattr(item, derived_finish, "")
        else:
            d_start = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
            d_finish = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)
            setattr(item, derived_start, ifcopenshell.util.date.canonicalise_time(d_start) if d_start else "")
            setattr(item, derived_finish, ifcopenshell.util.date.canonicalise_time(d_finish) if d_finish else "")
            setattr(item, item_start, "-")
            setattr(item, item_finish, "-")

    @classmethod
    def load_task_properties(cls, task: Optional[ifcopenshell.entity_instance] = None) -> None:
        props = tool.Sequence.get_work_schedule_props()
        task_props = tool.Sequence.get_task_tree_props()
        tasks_with_visual_bar = cls.get_task_bar_list()
        props.is_task_update_enabled = False

        for item in task_props.tasks:
            task = tool.Ifc.get().by_id(item.ifc_definition_id)
            item.name = task.Name or "Unnamed"
            item.identification = task.Identification or "XXX"
            item.has_bar_visual = item.ifc_definition_id in tasks_with_visual_bar
            if props.highlighted_task_id:
                item.is_predecessor = props.highlighted_task_id in [
                    rel.RelatedProcess.id() for rel in task.IsPredecessorTo
                ]
                item.is_successor = props.highlighted_task_id in [
                    rel.RelatingProcess.id() for rel in task.IsSuccessorFrom
                ]
            calendar = ifcopenshell.util.sequence.derive_calendar(task)
            if ifcopenshell.util.sequence.get_calendar(task):
                item.calendar = calendar.Name or "Unnamed" if calendar else ""
            else:
                item.calendar = ""
                item.derived_calendar = calendar.Name or "Unnamed" if calendar else ""

            # Load all date pairs using the helper
            cls._load_task_date_properties(item, task, "Schedule")
            cls._load_task_date_properties(item, task, "Actual")
            cls._load_task_date_properties(item, task, "Early")
            cls._load_task_date_properties(item, task, "Late")

            # Duration logic (remains the same, based on Schedule dates)
            task_time = task.TaskTime
            if task_time and task_time.ScheduleDuration:
                item.duration = str(ifcopenshell.util.date.readable_ifc_duration(task_time.ScheduleDuration))
            else:
                derived_start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                derived_finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
                if derived_start and derived_finish:
                    derived_duration = ifcopenshell.util.sequence.count_working_days(
                        derived_start, derived_finish, calendar
                    )
                    item.derived_duration = str(ifcopenshell.util.date.readable_ifc_duration(f"P{derived_duration}D"))
                else:
                    item.derived_duration = ""
                item.duration = "-"

        # After processing all tasks, refresh the Outputs count so UI stays accurate.
        try:
            cls.refresh_task_3d_counts()
        except Exception:
            # Be defensive; never break UI loading if counting fails.
            pass

        props.is_task_update_enabled = True

    @classmethod
    def refresh_task_3d_counts(cls) -> None:
        """
        Recalculates and saves the total count of 3D elements (Inputs + Outputs)
        per task in the UI tree.
        """
        try:
            tprops = tool.Sequence.get_task_tree_props()
            if not hasattr(tprops, "tasks"):
                return
        except Exception:
            return

        try:
            from bonsai import tool as _tool
            import ifcopenshell.util.sequence
        except Exception:
            return

        for item in getattr(tprops, "tasks", []):
            try:
                task = _tool.Ifc.get().by_id(item.ifc_definition_id)
                if not task:
                    if hasattr(item, "outputs_count"):
                        item.outputs_count = 0
                    continue

                # Calculate outputs
                outputs_count = len(ifcopenshell.util.sequence.get_task_outputs(task, is_deep=False))

                # Calculate inputs
                inputs_count = len(ifcopenshell.util.sequence.get_task_inputs(task, is_deep=False))

                # Save the sum in the 'outputs_count' property
                if hasattr(item, "outputs_count"):
                    item.outputs_count = outputs_count + inputs_count

            except Exception:
                if hasattr(item, "outputs_count"):
                    item.outputs_count = 0
                continue

    @classmethod
    def expand_task(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.remove(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def expand_all_tasks(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.contracted_tasks = json.dumps([])

    @classmethod
    def contract_all_tasks(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        tprops = tool.Sequence.get_task_tree_props()
        contracted_tasks = json.loads(props.contracted_tasks)
        for task_item in tprops.tasks:
            if task_item.is_expanded:
                contracted_tasks.append(task_item.ifc_definition_id)
        props.contracted_tasks = json.dumps(contracted_tasks)


    @classmethod
    def contract_task(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.append(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def go_to_task(cls, task):
        props = tool.Sequence.get_work_schedule_props()

        def get_ancestor_ids(task):
            ids = []
            for rel in task.Nests or []:
                ids.append(rel.RelatingObject.id())
                ids.extend(get_ancestor_ids(rel.RelatingObject))
            return ids

        contracted_tasks = json.loads(props.contracted_tasks)
        for ancestor_id in get_ancestor_ids(task):
            if ancestor_id in contracted_tasks:
                contracted_tasks.remove(ancestor_id)
        props.contracted_tasks = json.dumps(contracted_tasks)

        work_schedule = cls.get_active_work_schedule()
        cls.load_task_tree(work_schedule)
        cls.load_task_properties()

        task_props = tool.Sequence.get_task_tree_props()
        expanded_tasks = [item.ifc_definition_id for item in task_props.tasks]
        props.active_task_index = expanded_tasks.index(task.id()) or 0
