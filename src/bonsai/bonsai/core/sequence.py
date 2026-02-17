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
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_work_plan(ifc: type[tool.Ifc]) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_plan")


def remove_work_plan(ifc: type[tool.Ifc], work_plan: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_plan", work_plan=work_plan)


def enable_editing_work_plan(sequence: type[tool.Sequence], work_plan: ifcopenshell.entity_instance) -> None:
    sequence.load_work_plan_attributes(work_plan)
    sequence.enable_editing_work_plan(work_plan)


def disable_editing_work_plan(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_work_plan()


def edit_work_plan(ifc: type[tool.Ifc], sequence: type[tool.Sequence], work_plan: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_work_plan_attributes()
    ifc.run("sequence.edit_work_plan", work_plan=work_plan, attributes=attributes)
    sequence.disable_editing_work_plan()


def edit_work_schedule(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance
) -> None:
    try:
        # Validate that the work_schedule exists before editing
        if not work_schedule or not hasattr(work_schedule, 'is_a'):
            print("ERROR: WorkSchedule is invalid or doesn't exist")
            return
            
        # Get ID for debug
        schedule_id = work_schedule.id()
        schedule_name = getattr(work_schedule, 'Name', 'Unnamed')
        print(f"DEBUG: Editing WorkSchedule ID {schedule_id} - Name: {schedule_name}")
        
        # Get attributes
        attributes = sequence.get_work_schedule_attributes()
        print(f"DEBUG: Attributes to update: {attributes}")
        
        # Validate that we have valid attributes
        if not attributes:
            print("WARNING: No attributes to update")
            sequence.disable_editing_work_schedule()
            return
            
        # Execute the edit
        ifc.run("sequence.edit_work_schedule", work_schedule=work_schedule, attributes=attributes)
        
        # Verify that the work_schedule still exists after editing
        try:
            # Try to access the work_schedule to verify that it was not deleted
            test_id = work_schedule.id()
            test_name = getattr(work_schedule, 'Name', 'Unnamed')
            print(f"DEBUG: WorkSchedule still exists after edit - ID {test_id} - Name: {test_name}")
        except:
            print("ERROR: WorkSchedule was deleted during edit operation!")
            sequence.disable_editing_work_schedule()
            return

        # SMART SOLUTION: Preserve original schedule instead of resetting automatically
        try:
            # Refresh ALL schedule-related data
            from bonsai.bim.module.sequence.data import SequenceData, WorkScheduleData
            SequenceData.load()
            WorkScheduleData.load()
            
            props = sequence.get_work_schedule_props()
            current_active_id = props.active_work_schedule_id
            
            # CRITICAL: Only reset if NO other schedules are available
            # Instead of resetting automatically, look for a fallback schedule
            ifc_file = tool.Ifc.get()
            all_schedules = ifc_file.by_type("IfcWorkSchedule")
            
            if all_schedules:
                # If schedules are available, prefer originals over copies
                original_schedules = [ws for ws in all_schedules 
                                    if not (ws.Name and ws.Name.startswith("Copy of "))]
                
                if original_schedules:
                    # Use the first original schedule found
                    fallback_id = original_schedules[0].id()
                    props.active_work_schedule_id = fallback_id
                    props.editing_type = "TASKS"
                    print(f"[INFO] EDIT_WORK_SCHEDULE: Preserving original schedule ID {fallback_id} - '{original_schedules[0].Name}'")
                elif all_schedules:
                    # If there are no originals, use any available schedule
                    fallback_id = all_schedules[0].id()
                    props.active_work_schedule_id = fallback_id
                    props.editing_type = "TASKS"
                    print(f"[INFO] EDIT_WORK_SCHEDULE: Using available schedule ID {fallback_id} - '{all_schedules[0].Name}'")
                else:
                    # Only reset if there are really no schedules
                    props.active_work_schedule_id = 0
                    props.editing_type = ""
                    print("[INFO] EDIT_WORK_SCHEDULE: No schedules available, resetting")
            else:
                # Only reset if there are really no schedules
                props.active_work_schedule_id = 0
                props.editing_type = ""
                print("[INFO] EDIT_WORK_SCHEDULE: No schedules available, resetting")
            
            # Force UI update
            import bpy
            for area in bpy.context.screen.areas:
                if area.type in ['PROPERTIES', 'OUTLINER']:
                    area.tag_redraw()
            
            print(f"INFO: WorkSchedule {work_schedule.id()} - UI reset completed successfully")
            
        except Exception as refresh_error:
            print(f"WARNING: Failed to reset UI after edit: {refresh_error}")
            sequence.disable_editing_work_schedule()
            
    except Exception as e:
        print(f"ERROR in edit_work_schedule: {e}")
        import traceback
        traceback.print_exc()
        sequence.disable_editing_work_schedule()


def enable_editing_work_plan_schedules(
    sequence: type[tool.Sequence], work_plan: Optional[ifcopenshell.entity_instance] = None
) -> None:
    sequence.enable_editing_work_plan_schedules(work_plan)


def add_work_schedule(ifc: type[tool.Ifc], sequence: type[tool.Sequence], name: str) -> ifcopenshell.entity_instance:
    res = sequence.get_user_predefined_type()
    if not isinstance(res, tuple) or len(res) != 2:
        # User cancelled or UI not available: use defaults
        predefined_type, object_type = "NOTDEFINED", ""
    else:
        predefined_type, object_type = res
    return ifc.run("sequence.add_work_schedule", name=name, predefined_type=predefined_type, object_type=object_type)



def remove_work_schedule(ifc: type[tool.Ifc], work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_schedule", work_schedule=work_schedule)


def copy_work_schedule(sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.copy_work_schedule(work_schedule)


def assign_work_schedule(
    ifc: type[tool.Ifc], work_plan: ifcopenshell.entity_instance, work_schedule: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    if work_schedule:
        return ifc.run("aggregate.assign_object", relating_object=work_plan, products=[work_schedule])


def unassign_work_schedule(ifc: type[tool.Ifc], work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("aggregate.unassign_object", products=[work_schedule])


def enable_editing_work_schedule(sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.load_work_schedule_attributes(work_schedule)
    sequence.enable_editing_work_schedule(work_schedule)


def enable_editing_work_schedule_tasks(
    sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance
) -> None:
    # Only set active schedule, DO NOT load task tree immediately
    # The operator will handle the correct sequence: callback → load_task_tree → restore
    sequence.enable_editing_work_schedule_tasks(work_schedule)


def load_task_tree(sequence: type[tool.Sequence], work_schedule) -> None:
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_task(sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    sequence.expand_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_all_tasks(sequence: type[tool.Sequence]) -> None:
    sequence.expand_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_task(sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    sequence.contract_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_all_tasks(sequence: type[tool.Sequence]) -> None:
    sequence.contract_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def remove_task(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()
    sequence.disable_selecting_deleted_task()


def load_task_properties(sequence: type[tool.Sequence]) -> None:
    sequence.load_task_properties()


def disable_editing_work_schedule(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_work_schedule()


def add_summary_task(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance
) -> None:
    ifc.run("sequence.add_task", work_schedule=work_schedule)
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def add_task(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], parent_task: Optional[ifcopenshell.entity_instance] = None
) -> None:
    ifc.run("sequence.add_task", parent_task=parent_task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def enable_editing_task_attributes(sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    sequence.load_task_attributes(task)
    sequence.enable_editing_task_attributes(task)


def _auto_sync_task_predefined_type(task_id: int, predefined_type: str) -> None:
    """
    Synchronizes the PredefinedType with the task's DEFAULT ColorType AND FORCES UI REDRAW.
    """
    try:
        import bpy
        import bonsai.tool as tool
        from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager

        # 1. Find the task in UI properties (task_pg)
        tprops = tool.Sequence.get_task_tree_props()
        task_pg = next((t for t in tprops.tasks if t.ifc_definition_id == task_id), None)

        if task_pg:
            # 2. Call central logic to update the data
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(bpy.context, task_pg)
            print(f"[INFO] Auto-Sync: Task {task_id} updated to DEFAULT ColorType '{predefined_type}'.")

            # 3. THE KEY PART! Force Properties UI redraw.
            # Blender doesn't always detect changes in nested collections, so we force it.
            for window in bpy.context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()

    except Exception as e:
        print(f"[ERROR] ERROR in _auto_sync_task_predefined_type: {e}")


def edit_task(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    """Edits a task, reloads data, and triggers DEFAULT ColorType synchronization."""
    attributes = sequence.get_task_attributes()
    old_predefined = getattr(task, "PredefinedType", "NOTDEFINED") or "NOTDEFINED"

    # 1. Save changes to the IFC file
    ifc.run("sequence.edit_task", task=task, attributes=attributes)

    # 2. Reload data from IFC so cache is updated
    from bonsai.bim.module.sequence.data import SequenceData
    SequenceData.load() # Complete reload to ensure consistency
    sequence.load_task_properties(task=task)

    # 3. Trigger synchronization if PredefinedType changed
    new_predefined = attributes.get("PredefinedType", old_predefined)
    if new_predefined != old_predefined:
        _auto_sync_task_predefined_type(task.id(), new_predefined)

    sequence.disable_editing_task()


def copy_task_attribute(ifc: type[tool.Ifc], sequence: type[tool.Sequence], attribute_name: str) -> None:
    for task in sequence.get_checked_tasks():
        ifc.run(
            "sequence.edit_task",
            task=task,
            attributes={attribute_name: sequence.get_task_attribute_value(attribute_name)},
        )
        sequence.load_task_properties(task)


def duplicate_task(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.duplicate_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def disable_editing_task(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_task()


def enable_editing_task_time(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance
) -> None:
    task_time = sequence.get_task_time(task)
    if task_time is None:
        task_time = ifc.run("sequence.add_task_time", task=task)
    sequence.load_task_time_attributes(task_time)
    sequence.enable_editing_task_time(task)


def edit_task_time(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], resource, task_time: ifcopenshell.entity_instance
) -> None:
    attributes = sequence.get_task_time_attributes()
    # TODO: nasty loop goes on when calendar props are messed up
    ifc.run("sequence.edit_task_time", task_time=task_time, attributes=attributes)
    task = sequence.get_active_task()
    sequence.load_task_properties(task=task)
    sequence.disable_editing_task_time()
    resource.load_resource_properties()


def assign_predecessor(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def unassign_predecessor(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance
) -> None:
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def assign_successor(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def unassign_successor(ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def assign_products(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    spatial: type[tool.Spatial],
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def unassign_products(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    spatial: type[tool.Spatial],
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def assign_input_products(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    spatial: type[tool.Spatial],
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def unassign_input_products(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    spatial: type[tool.Spatial],
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def assign_resource(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], resource_tool, task: ifcopenshell.entity_instance
) -> None:
    resource = resource_tool.get_highlighted_resource()
    sub_resource = ifc.run(
        "resource.add_resource",
        parent_resource=resource,
        ifc_class=resource.is_a(),
        name="{}/{}".format(resource.Name or "Unnamed", task.Name or ""),
    )
    ifc.run("sequence.assign_process", relating_process=task, related_object=sub_resource)
    sequence.load_task_resources(task)
    resource_tool.load_resources()


def unassign_resource(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    resource_tool,
    task: ifcopenshell.entity_instance,
    resource: ifcopenshell.entity_instance,
) -> None:
    ifc.run("sequence.unassign_process", relating_process=task, related_object=resource)
    ifc.run("resource.remove_resource", resource=resource)
    sequence.load_task_resources(task)
    resource_tool.load_resources()


def remove_work_calendar(ifc: type[tool.Ifc], work_calendar: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_calendar", work_calendar=work_calendar)


def add_work_calendar(ifc: type[tool.Ifc]) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_calendar")


def edit_work_calendar(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], work_calendar: ifcopenshell.entity_instance
) -> None:
    attributes = sequence.get_work_calendar_attributes()
    ifc.run("sequence.edit_work_calendar", work_calendar=work_calendar, attributes=attributes)
    sequence.disable_editing_work_calendar()
    sequence.load_task_properties()


def enable_editing_work_calendar(sequence: type[tool.Sequence], work_calendar: ifcopenshell.entity_instance) -> None:
    sequence.load_work_calendar_attributes(work_calendar)
    sequence.enable_editing_work_calendar(work_calendar)


def disable_editing_work_calendar(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_work_calendar()


def enable_editing_work_calendar_times(
    sequence: type[tool.Sequence], work_calendar: ifcopenshell.entity_instance
) -> None:
    sequence.enable_editing_work_calendar_times(work_calendar)


def add_work_time(
    ifc: type[tool.Ifc], work_calendar: ifcopenshell.entity_instance, time_type: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_time", work_calendar=work_calendar, time_type=time_type)


def enable_editing_work_time(sequence: type[tool.Sequence], work_time: ifcopenshell.entity_instance) -> None:
    sequence.load_work_time_attributes(work_time)
    sequence.enable_editing_work_time(work_time)


def disable_editing_work_time(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_work_time()


def remove_work_time(ifc: type[tool.Ifc], work_time=None) -> None:
    ifc.run("sequence.remove_work_time", work_time=work_time)


def edit_work_time(ifc: type[tool.Ifc], sequence: type[tool.Sequence]) -> None:
    work_time = sequence.get_active_work_time()
    ifc.run("sequence.edit_work_time", work_time=work_time, attributes=sequence.get_work_time_attributes())
    recurrence_pattern = work_time.RecurrencePattern
    if recurrence_pattern:
        ifc.run(
            "sequence.edit_recurrence_pattern",
            recurrence_pattern=recurrence_pattern,
            attributes=sequence.get_recurrence_pattern_attributes(recurrence_pattern),
        )
    sequence.disable_editing_work_time()


def assign_recurrence_pattern(
    ifc: type[tool.Ifc], work_time: ifcopenshell.entity_instance, recurrence_type: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.assign_recurrence_pattern", parent=work_time, recurrence_type=recurrence_type)


def unassign_recurrence_pattern(ifc: type[tool.Ifc], recurrence_pattern: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.unassign_recurrence_pattern", recurrence_pattern=recurrence_pattern)


def add_time_period(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], recurrence_pattern: ifcopenshell.entity_instance
) -> None:
    start_time, end_time = sequence.get_recurrence_pattern_times()
    ifc.run("sequence.add_time_period", recurrence_pattern=recurrence_pattern, start_time=start_time, end_time=end_time)
    sequence.reset_time_period()


def remove_time_period(ifc: type[tool.Ifc], time_period: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_time_period", time_period=time_period)


def enable_editing_task_calendar(sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> None:
    sequence.enable_editing_task_calendar(task)


def edit_task_calendar(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    task: ifcopenshell.entity_instance,
    work_calendar: ifcopenshell.entity_instance,
) -> None:
    ifc.run("control.assign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def remove_task_calendar(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    task: ifcopenshell.entity_instance,
    work_calendar: ifcopenshell.entity_instance,
) -> None:
    ifc.run("control.unassign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def enable_editing_task_sequence(sequence: type[tool.Sequence]) -> None:
    sequence.enable_editing_task_sequence()
    sequence.load_task_properties()


def disable_editing_task_time(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_task_time()


def enable_editing_sequence_attributes(
    sequence: type[tool.Sequence], rel_sequence: ifcopenshell.entity_instance
) -> None:
    sequence.enable_editing_rel_sequence_attributes(rel_sequence)
    sequence.load_rel_sequence_attributes(rel_sequence)


def enable_editing_sequence_lag_time(
    sequence: type[tool.Sequence], rel_sequence: ifcopenshell.entity_instance, lag_time: ifcopenshell.entity_instance
) -> None:
    sequence.load_lag_time_attributes(lag_time)
    sequence.enable_editing_sequence_lag_time(rel_sequence)


def unassign_lag_time(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], rel_sequence: ifcopenshell.entity_instance
) -> None:
    ifc.run("sequence.unassign_lag_time", rel_sequence=rel_sequence)
    sequence.load_task_properties()


def assign_lag_time(ifc: type[tool.Ifc], rel_sequence: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.assign_lag_time", rel_sequence=rel_sequence, lag_value="P1D")


def edit_sequence_attributes(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], rel_sequence: ifcopenshell.entity_instance
) -> None:
    attributes = sequence.get_rel_sequence_attributes()
    ifc.run("sequence.edit_sequence", rel_sequence=rel_sequence, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def edit_sequence_lag_time(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], lag_time: ifcopenshell.entity_instance
) -> None:
    attributes = sequence.get_lag_time_attributes()
    ifc.run("sequence.edit_lag_time", lag_time=lag_time, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def disable_editing_rel_sequence(sequence: type[tool.Sequence]) -> None:
    sequence.disable_editing_rel_sequence()


def select_task_outputs(
    sequence: type[tool.Sequence], spatial: type[tool.Spatial], task: ifcopenshell.entity_instance
) -> None:
    spatial.select_products(products=sequence.get_task_outputs(task))


def select_task_inputs(
    sequence: type[tool.Sequence], spatial: type[tool.Spatial], task: ifcopenshell.entity_instance
) -> None:
    spatial.select_products(products=sequence.get_task_inputs(task))


def select_work_schedule_products(
    sequence: type[tool.Sequence], spatial: type[tool.Spatial], work_schedule: ifcopenshell.entity_instance
) -> None:
    products = sequence.get_work_schedule_products(work_schedule)
    spatial.select_products(products)


def select_unassigned_work_schedule_products(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], spatial: type[tool.Spatial]
) -> None:
    spatial.deselect_objects()
    products = ifc.get().by_type("IfcElement")
    work_schedule = sequence.get_active_work_schedule()
    schedule_products = sequence.get_work_schedule_products(work_schedule)
    selection = [product for product in products if product not in schedule_products]
    spatial.select_products(selection)


def recalculate_schedule(ifc: type[tool.Ifc], work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.recalculate_schedule", work_schedule=work_schedule)


def add_task_column(sequence: type[tool.Sequence], column_type: str, name: str, data_type: str) -> None:
    sequence.add_task_column(column_type, name, data_type)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def remove_task_column(sequence: type[tool.Sequence], name: str) -> None:
    sequence.remove_task_column(name)


def set_task_sort_column(sequence: type[tool.Sequence], column: str) -> None:
    sequence.set_task_sort_column(column)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def calculate_task_duration(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance
) -> None:
    ifc.run("sequence.calculate_task_duration", task=task)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def load_animation_color_scheme(
    sequence: type[tool.Sequence], scheme: Union[ifcopenshell.entity_instance, None]
) -> None:
    sequence.load_animation_color_scheme(scheme)


def go_to_task(sequence: type[tool.Sequence], task: ifcopenshell.entity_instance) -> Union[None, str]:
    work_schedule = sequence.get_work_schedule(task)
    is_work_schedule_active = sequence.is_work_schedule_active(work_schedule)
    if is_work_schedule_active:
        sequence.go_to_task(task)
    else:
        return "Work schedule is not active"


def guess_date_range(sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance) -> None:
    start, finish = sequence.guess_date_range(work_schedule)
    sequence.update_visualisation_date(start, finish)


def setup_default_task_columns(sequence: type[tool.Sequence]) -> None:
    sequence.setup_default_task_columns()



def add_task_bars(sequence: "type[tool.Sequence]") -> set[str]:
    """Generates the visual bars for the selected tasks.

    - Synchronizes `has_bar_visual` from the tree with `props.task_bars` (JSON).
    - Calls `sequence.refresh_task_bars()` to create/delete bars in the viewport.
    - Returns {'FINISHED'} to maintain operator-style semantics.
    """
    # Update has_bar_visual synchronization with task_bars
    task_tree = sequence.get_task_tree_props()
    selected_tasks = []

    for task in getattr(task_tree, "tasks", []):
        try:
            tid = int(task.ifc_definition_id)
        except Exception:
            continue

        if getattr(task, "has_bar_visual", False):
            selected_tasks.append(tid)
            sequence.add_task_bar(tid)
        else:
            sequence.remove_task_bar(tid)

    # Generate/update visual bars
    sequence.refresh_task_bars()

    return {"FINISHED"}



def load_default_animation_color_scheme(sequence: type[tool.Sequence]) -> None:
    sequence.load_default_animation_color_scheme()



def visualise_work_schedule_date_range(
    sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance
) -> None:
    """
    Creates 4D animation using ONLY the Animation Color Schemes system.
    No fallback to old system - if no ColorTypes exist, creates DEFAULT.
    
    Process:
    1. Clears previous animations
    2. Calculates time configuration
    3. Verifies/creates DEFAULT group if necessary
    4. Generates frames with state information
    5. Applies animation with ColorTypes
    6. Adds additional elements (timeline, bars)
    """

    # Clear any previous animation
    sequence.clear_objects_animation(include_blender_objects=False)

    # Get time configuration (dates, frames, speed)
    settings = sequence.get_animation_settings()
    if not settings:
        print("[ERROR] Error: Could not calculate animation configuration")
        return


    # NEW: Validate date range
    import ifcopenshell.util.sequence
    all_tasks = []
    for root_task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
        all_tasks.extend(ifcopenshell.util.sequence.get_all_nested_tasks(root_task))

    # Check for out-of-range tasks
    out_of_range_count = 0
    earliest_task_date = None
    latest_task_date = None
    
    for task in all_tasks:
        start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
        finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
        
        if start and finish:
            if not earliest_task_date or start < earliest_task_date:
                earliest_task_date = start
            if not latest_task_date or finish > latest_task_date:
                latest_task_date = finish
                
            if finish < settings["start"] or start > settings["finish"]:
                out_of_range_count += 1
    
    # Warn if there are discrepancies
    if earliest_task_date and earliest_task_date < settings["start"]:
        print(f"[WARNING] Warning: Earliest task starts {(settings['start'] - earliest_task_date).days} days before visualization range")
    if latest_task_date and latest_task_date > settings["finish"]:
        print(f"[WARNING] Warning: Latest task ends {(latest_task_date - settings['finish']).days} days after visualization range")
    if out_of_range_count > 0:
        print(f"[WARNING] {out_of_range_count} tasks are completely outside the visualization range")
    # Get animation properties
    animation_props = sequence.get_animation_props()

    # If no groups configured, create and use DEFAULT
    if not animation_props.animation_group_stack:
        print("[WARNING] No ColorType groups configured")
        print("   Creating DEFAULT group automatically...")

        # Create DEFAULT group with basic ColorTypes
        sequence.create_default_ColorType_group()

        # Add DEFAULT to the animation stack
        item = animation_props.animation_group_stack.add()
        item.group = "DEFAULT"
        item.enabled = True

        print("[INFO] DEFAULT group added to the stack")

    # Generate frame information with states
    print(f"[INFO] Processing schedule tasks...")
    product_frames = sequence.get_animation_product_frames_enhanced(
        work_schedule, settings
    )

    if not product_frames:
        print("[WARNING] No products found to animate")
        return

    print(f"[INFO] {len(product_frames)} products found")

    # ALWAYS use ColorType system (no fallback)
    print(f"[INFO] Applying animation with Animation Color Schemes...")
    sequence.animate_objects_with_ColorTypes(settings, product_frames)

    # Add additional elements
    sequence.add_text_animation_handler(settings)  # Timeline with date
    add_task_bars(sequence)  # Gantt bars (optional)
    sequence.set_object_shading()  # Configure view for colors

    print(f"[INFO] Animation created: {settings['total_frames']:.0f} frames")
    print(f"   From: {settings['start'].strftime('%Y-%m-%d')}")
    print(f"   To: {settings['finish'].strftime('%Y-%m-%d')}")

def visualise_work_schedule_date(sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance) -> None:
    """Visualizes the schedule state at a specific date.
    CORRECTION: Processes ALL visible elements, not just active ones."""
    # Clear keyframes and previous visual states is crucial for clean snapshot.
    sequence.clear_objects_animation(include_blender_objects=True)

    # Parse the visualization date
    props = sequence.get_work_schedule_props()
    date_text = props.visualisation_start
    if not date_text:
        return
    try:
        from dateutil import parser
        current_date = parser.parse(date_text, yearfirst=True, fuzzy=True)
    except Exception:
        return

    # Process ALL states up to current date
    product_states = sequence.process_construction_state(work_schedule, current_date)

    # Apply snapshot with correct ColorTypes
    sequence.show_snapshot(product_states)

    # Ensure colors are visible
    sequence.set_object_shading()


def load_product_related_tasks(
    sequence: type[tool.Sequence], product: ifcopenshell.entity_instance
) -> Union[list[ifcopenshell.entity_instance], str]:
    filter_by_schedule = sequence.is_filter_by_active_schedule()
    if filter_by_schedule:
        work_schedule = sequence.get_active_work_schedule()
        if work_schedule:
            task_inputs, task_ouputs = sequence.get_tasks_for_product(product, work_schedule)
        else:
            return "No active work schedule."
    else:
        task_inputs, task_ouputs = sequence.get_tasks_for_product(product)
    sequence.load_product_related_tasks(task_inputs, task_ouputs)
    return task_inputs + task_ouputs


def reorder_task_nesting(
    ifc: type[tool.Ifc], sequence: type[tool.Sequence], task: ifcopenshell.entity_instance, new_index: int
) -> Union[None, str]:
    is_sorting_enabled = sequence.is_sorting_enabled()
    is_sort_reversed = sequence.is_sort_reversed()
    if is_sorting_enabled or is_sort_reversed:
        return "Remove manual sorting"
    else:
        ifc.run("nest.reorder_nesting", item=task, new_index=new_index)
        work_schedule = sequence.get_active_work_schedule()
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def create_baseline(
    ifc: type[tool.Ifc],
    sequence: type[tool.Sequence],
    work_schedule: ifcopenshell.entity_instance,
    name: Optional[str] = None,
) -> None:
    ifc.run("sequence.create_baseline", work_schedule=work_schedule, name=name)


def clear_previous_animation(sequence: type[tool.Sequence]) -> None:
    sequence.clear_objects_animation(include_blender_objects=False)


def add_animation_camera(sequence: type[tool.Sequence]) -> None:
    sequence.add_animation_camera()


def save_animation_color_scheme(sequence: type[tool.Sequence], name: str) -> None:
    sequence.save_animation_color_scheme(name)


def generate_gantt_chart(sequence: type[tool.Sequence], work_schedule: ifcopenshell.entity_instance) -> None:
    """Generates the task data and sends it to the web UI for Gantt chart rendering."""
    json_data = sequence.create_tasks_json(work_schedule)
    sequence.generate_gantt_browser_chart(json_data, work_schedule)


def save_ColorTypes_to_ifc_core(ifc_file: "ifcopenshell.file", work_schedule: "ifcopenshell.entity_instance", ColorType_data: dict) -> None:
    """
    (Core) Saves 4D ColorTypes configuration to an IfcPropertySet associated with the active IfcWorkSchedule.
    """
    import json
    import ifcopenshell.api
    from datetime import datetime

    pset_name = "Pset_Bonsai4DColorTypeConfig"
    prop_name = "ColorTypeDataJSON"

    # 1. Serialize all configuration to a JSON string
    ColorType_json = json.dumps(ColorType_data, ensure_ascii=False, indent=2)

    # 2. Create properties that will go in the Pset
    try:
        properties_to_add = {
            prop_name: ifc_file.create_entity(
                "IfcPropertySingleValue",
                Name=prop_name,
                NominalValue=ifc_file.create_entity("IfcText", ColorType_json),
            ),
            "Version": ifc_file.create_entity(
                "IfcPropertySingleValue",
                Name="Version",
                NominalValue=ifc_file.create_entity("IfcLabel", "1.0"),
            ),
            "LastModified": ifc_file.create_entity(
                "IfcPropertySingleValue",
                Name="LastModified",
                NominalValue=ifc_file.create_entity("IfcText", datetime.now().isoformat()),
            ),
        }

        # 3. Use ifcopenshell API to create or edit Pset robustly
        ifcopenshell.api.run(
            "pset.edit_pset",
            ifc_file,
            product=work_schedule,
            name=pset_name,
            properties=properties_to_add,
        )
    except Exception:
        # Robust fallback: use simple values instead of entities
        ifcopenshell.api.run(
            "pset.edit_pset",
            ifc_file,
            product=work_schedule,
            name=pset_name,
            properties={
                prop_name: ColorType_json,
                "Version": "1.0",
                "LastModified": datetime.now().isoformat(),
            },
        )
    print(f"Bonsai INFO: 4D ColorTypes automatically saved to WorkSchedule Pset '{pset_name}'.")


def load_ColorTypes_from_ifc_core(work_schedule: "ifcopenshell.entity_instance") -> dict | None:
    """
    (Core) Loads 4D ColorTypes configuration from the IfcPropertySet associated with the IfcWorkSchedule.
    """
    import json

    pset_name = "Pset_Bonsai4DColorTypeConfig"
    prop_name = "ColorTypeDataJSON"

    if not getattr(work_schedule, "IsDefinedBy", None):
        return None

    for rel in work_schedule.IsDefinedBy:
        # Ensure the relationship is for properties
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue

        pset = rel.RelatingPropertySet
        if getattr(pset, "Name", None) == pset_name:
            for prop in getattr(pset, "HasProperties", []) or []:
                if getattr(prop, "Name", None) == prop_name and prop.is_a("IfcPropertySingleValue"):
                    try:
                        nominal = getattr(prop, "NominalValue", None)
                        # Robust handling of the nominal value (wrappedValue or direct value)
                        if hasattr(nominal, "wrappedValue"):
                            raw = nominal.wrappedValue
                        else:
                            raw = nominal
                        data = json.loads(raw) if isinstance(raw, str) else None
                        if isinstance(data, dict):
                            print(f"Bonsai INFO: 4D ColorTypes loaded from IFC for WorkSchedule '{getattr(work_schedule, 'Name', '')}'.")
                            return data
                    except Exception as e:
                        print(f"Bonsai ERROR: Could not decode ColorTypes JSON from IFC: {e}")
                        return None
    return None

def refresh_task_output_counts(SequenceTool, work_schedule=None):
    """
    Safely recalculates the 'Outputs' counters per task.
    This is a shim to avoid AttributeError if the real logic lives in tool.Sequence.
    """
    try:
        ws = work_schedule or SequenceTool.get_active_work_schedule()
    except Exception:
        ws = None
    try:
        # If the tool already has the native method, use it
        if hasattr(SequenceTool, "refresh_task_output_counts"):
            if ws is not None:
                SequenceTool.refresh_task_output_counts(ws)
            else:
                SequenceTool.refresh_task_output_counts()
        else:
            # Reasonable fallback: reload tree and properties
            if ws is not None:
                SequenceTool.load_task_tree(ws)
            SequenceTool.load_task_properties()
    except Exception as e:
        print(f"Bonsai WARNING: refresh_task_output_counts shim failed: {e}")
