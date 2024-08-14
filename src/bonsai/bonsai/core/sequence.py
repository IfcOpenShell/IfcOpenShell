# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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


def add_work_plan(ifc: tool.Ifc) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_plan")


def remove_work_plan(ifc: tool.Ifc, work_plan: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_plan", work_plan=work_plan)


def enable_editing_work_plan(sequence: tool.Sequence, work_plan: ifcopenshell.entity_instance) -> None:
    sequence.load_work_plan_attributes(work_plan)
    sequence.enable_editing_work_plan(work_plan)


def disable_editing_work_plan(sequence: tool.Sequence) -> None:
    sequence.disable_editing_work_plan()


def edit_work_plan(ifc: tool.Ifc, sequence: tool.Sequence, work_plan: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_work_plan_attributes()
    ifc.run("sequence.edit_work_plan", work_plan=work_plan, attributes=attributes)
    sequence.disable_editing_work_plan()


def edit_work_schedule(ifc: tool.Ifc, sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_work_schedule_attributes()
    ifc.run("sequence.edit_work_schedule", work_schedule=work_schedule, attributes=attributes)
    sequence.disable_editing_work_schedule()


def enable_editing_work_plan_schedules(
    sequence: tool.Sequence, work_plan: Optional[ifcopenshell.entity_instance] = None
) -> None:
    sequence.enable_editing_work_plan_schedules(work_plan)


def add_work_schedule(ifc: tool.Ifc, sequence: tool.Sequence, name: str) -> ifcopenshell.entity_instance:
    predefined_type, object_type = sequence.get_user_predefined_type()
    return ifc.run("sequence.add_work_schedule", name=name, predefined_type=predefined_type, object_type=object_type)


def remove_work_schedule(ifc: tool.Ifc, work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_schedule", work_schedule=work_schedule)


def assign_work_schedule(
    ifc: tool.Ifc, work_plan: ifcopenshell.entity_instance, work_schedule: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, None]:
    if work_schedule:
        return ifc.run("aggregate.assign_object", relating_object=work_plan, products=[work_schedule])


def unassign_work_schedule(ifc: tool.Ifc, work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("aggregate.unassign_object", products=[work_schedule])


def enable_editing_work_schedule(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.load_work_schedule_attributes(work_schedule)
    sequence.enable_editing_work_schedule(work_schedule)


def enable_editing_work_schedule_tasks(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.enable_editing_work_schedule_tasks(work_schedule)
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def load_task_tree(sequence: tool.Sequence, work_schedule) -> None:
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_task(sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    sequence.expand_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_all_tasks(sequence: tool.Sequence) -> None:
    sequence.expand_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_task(sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    sequence.contract_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_all_tasks(sequence: tool.Sequence) -> None:
    sequence.contract_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def remove_task(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()
    sequence.disable_selecting_deleted_task()


def load_task_properties(sequence: tool.Sequence) -> None:
    sequence.load_task_properties()


def disable_editing_work_schedule(sequence: tool.Sequence) -> None:
    sequence.disable_editing_work_schedule()


def add_summary_task(ifc: tool.Ifc, sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.add_task", work_schedule=work_schedule)
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def add_task(
    ifc: tool.Ifc, sequence: tool.Sequence, parent_task: Optional[ifcopenshell.entity_instance] = None
) -> None:
    ifc.run("sequence.add_task", parent_task=parent_task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def enable_editing_task_attributes(sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    sequence.load_task_attributes(task)
    sequence.enable_editing_task_attributes(task)


def edit_task(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_task_attributes()
    ifc.run("sequence.edit_task", task=task, attributes=attributes)
    sequence.load_task_properties(task=task)
    sequence.disable_editing_task()


def copy_task_attribute(ifc: tool.Ifc, sequence: tool.Sequence, attribute_name: str) -> None:
    for task in sequence.get_checked_tasks():
        ifc.run(
            "sequence.edit_task",
            task=task,
            attributes={attribute_name: sequence.get_task_attribute_value(attribute_name)},
        )
        sequence.load_task_properties(task)


def duplicate_task(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.duplicate_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def disable_editing_task(sequence: tool.Sequence) -> None:
    sequence.disable_editing_task()


def enable_editing_task_time(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    task_time = sequence.get_task_time(task)
    if task_time is None:
        task_time = ifc.run("sequence.add_task_time", task=task)
    sequence.load_task_time_attributes(task_time)
    sequence.enable_editing_task_time(task)


def edit_task_time(ifc: tool.Ifc, sequence: tool.Sequence, resource, task_time: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_task_time_attributes()
    # TODO: nasty loop goes on when calendar props are messed up
    ifc.run("sequence.edit_task_time", task_time=task_time, attributes=attributes)
    task = sequence.get_active_task()
    sequence.load_task_properties(task=task)
    sequence.disable_editing_task_time()
    resource.load_resource_properties()


def assign_predecessor(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def unassign_predecessor(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def assign_successor(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def unassign_successor(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def assign_products(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    spatial: tool.Spatial,
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def unassign_products(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    spatial: tool.Spatial,
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def assign_input_products(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    spatial: tool.Spatial,
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def unassign_input_products(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    spatial: tool.Spatial,
    task: ifcopenshell.entity_instance,
    products: Optional[list[ifcopenshell.entity_instance]] = None,
) -> None:
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def assign_resource(ifc: tool.Ifc, sequence: tool.Sequence, resource_tool, task: ifcopenshell.entity_instance) -> None:
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
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    resource_tool,
    task: ifcopenshell.entity_instance,
    resource: ifcopenshell.entity_instance,
) -> None:
    ifc.run("sequence.unassign_process", relating_process=task, related_object=resource)
    ifc.run("resource.remove_resource", resource=resource)
    sequence.load_task_resources(task)
    resource_tool.load_resources()


def remove_work_calendar(ifc: tool.Ifc, work_calendar: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_work_calendar", work_calendar=work_calendar)


def add_work_calendar(ifc: tool.Ifc) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_calendar")


def edit_work_calendar(ifc: tool.Ifc, sequence: tool.Sequence, work_calendar: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_work_calendar_attributes()
    ifc.run("sequence.edit_work_calendar", work_calendar=work_calendar, attributes=attributes)
    sequence.disable_editing_work_calendar()
    sequence.load_task_properties()


def enable_editing_work_calendar(sequence: tool.Sequence, work_calendar: ifcopenshell.entity_instance) -> None:
    sequence.load_work_calendar_attributes(work_calendar)
    sequence.enable_editing_work_calendar(work_calendar)


def disable_editing_work_calendar(sequence: tool.Sequence) -> None:
    sequence.disable_editing_work_calendar()


def enable_editing_work_calendar_times(sequence: tool.Sequence, work_calendar: ifcopenshell.entity_instance) -> None:
    sequence.enable_editing_work_calendar_times(work_calendar)


def add_work_time(
    ifc: tool.Ifc, work_calendar: ifcopenshell.entity_instance, time_type: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.add_work_time", work_calendar=work_calendar, time_type=time_type)


def enable_editing_work_time(sequence: tool.Sequence, work_time: ifcopenshell.entity_instance) -> None:
    sequence.load_work_time_attributes(work_time)
    sequence.enable_editing_work_time(work_time)


def disable_editing_work_time(sequence: tool.Sequence) -> None:
    sequence.disable_editing_work_time()


def remove_work_time(ifc: tool.Ifc, work_time=None) -> None:
    ifc.run("sequence.remove_work_time", work_time=work_time)


def edit_work_time(ifc: tool.Ifc, sequence: tool.Sequence) -> None:
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
    ifc: tool.Ifc, work_time: ifcopenshell.entity_instance, recurrence_type: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    return ifc.run("sequence.assign_recurrence_pattern", parent=work_time, recurrence_type=recurrence_type)


def unassign_recurrence_pattern(ifc: tool.Ifc, recurrence_pattern: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.unassign_recurrence_pattern", recurrence_pattern=recurrence_pattern)


def add_time_period(ifc: tool.Ifc, sequence: tool.Sequence, recurrence_pattern: ifcopenshell.entity_instance) -> None:
    start_time, end_time = sequence.get_recurrence_pattern_times()
    ifc.run("sequence.add_time_period", recurrence_pattern=recurrence_pattern, start_time=start_time, end_time=end_time)
    sequence.reset_time_period()


def remove_time_period(ifc: tool.Ifc, time_period: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.remove_time_period", time_period=time_period)


def enable_editing_task_calendar(sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    sequence.enable_editing_task_calendar(task)


def edit_task_calendar(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    task: ifcopenshell.entity_instance,
    work_calendar: ifcopenshell.entity_instance,
) -> None:
    ifc.run("control.assign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def remove_task_calendar(
    ifc: tool.Ifc,
    sequence: tool.Sequence,
    task: ifcopenshell.entity_instance,
    work_calendar: ifcopenshell.entity_instance,
) -> None:
    ifc.run("control.unassign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def enable_editing_task_sequence(sequence: tool.Sequence) -> None:
    sequence.enable_editing_task_sequence()
    sequence.load_task_properties()


def disable_editing_task_time(sequence: tool.Sequence) -> None:
    sequence.disable_editing_task_time()


def enable_editing_sequence_attributes(sequence: tool.Sequence, rel_sequence: ifcopenshell.entity_instance) -> None:
    sequence.enable_editing_rel_sequence_attributes(rel_sequence)
    sequence.load_rel_sequence_attributes(rel_sequence)


def enable_editing_sequence_lag_time(
    sequence: tool.Sequence, rel_sequence: ifcopenshell.entity_instance, lag_time: ifcopenshell.entity_instance
) -> None:
    sequence.load_lag_time_attributes(lag_time)
    sequence.enable_editing_sequence_lag_time(rel_sequence)


def unassign_lag_time(ifc: tool.Ifc, sequence: tool.Sequence, rel_sequence: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.unassign_lag_time", rel_sequence=rel_sequence)
    sequence.load_task_properties()


def assign_lag_time(ifc: tool.Ifc, rel_sequence: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.assign_lag_time", rel_sequence=rel_sequence, lag_value="P1D")


def edit_sequence_attributes(
    ifc: tool.Ifc, sequence: tool.Sequence, rel_sequence: ifcopenshell.entity_instance
) -> None:
    attributes = sequence.get_rel_sequence_attributes()
    ifc.run("sequence.edit_sequence", rel_sequence=rel_sequence, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def edit_sequence_lag_time(ifc: tool.Ifc, sequence: tool.Sequence, lag_time: ifcopenshell.entity_instance) -> None:
    attributes = sequence.get_lag_time_attributes()
    ifc.run("sequence.edit_lag_time", lag_time=lag_time, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def disable_editing_rel_sequence(sequence: tool.Sequence) -> None:
    sequence.disable_editing_rel_sequence()


def select_task_outputs(sequence: tool.Sequence, spatial: tool.Spatial, task: ifcopenshell.entity_instance) -> None:
    spatial.select_products(products=sequence.get_task_outputs(task))


def select_task_inputs(sequence: tool.Sequence, spatial: tool.Spatial, task: ifcopenshell.entity_instance) -> None:
    spatial.select_products(products=sequence.get_task_inputs(task))


def select_work_schedule_products(
    sequence: tool.Sequence, spatial: tool.Spatial, work_schedule: ifcopenshell.entity_instance
) -> None:
    products = sequence.get_work_schedule_products(work_schedule)
    spatial.select_products(products)


def select_unassigned_work_schedule_products(ifc: tool.Ifc, sequence: tool.Sequence, spatial: tool.Spatial) -> None:
    spatial.deselect_objects()
    products = ifc.get().by_type("IfcElement")
    work_schedule = sequence.get_active_work_schedule()
    schedule_products = sequence.get_work_schedule_products(work_schedule)
    selection = [product for product in products if product not in schedule_products]
    spatial.select_products(selection)


def recalculate_schedule(ifc: tool.Ifc, work_schedule: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.recalculate_schedule", work_schedule=work_schedule)


def add_task_column(sequence: tool.Sequence, column_type: str, name: str, data_type: str) -> None:
    sequence.add_task_column(column_type, name, data_type)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def remove_task_column(sequence: tool.Sequence, name: str) -> None:
    sequence.remove_task_column(name)


def set_task_sort_column(sequence: tool.Sequence, column: str) -> None:
    sequence.set_task_sort_column(column)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def calculate_task_duration(ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> None:
    ifc.run("sequence.calculate_task_duration", task=task)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def load_animation_color_scheme(sequence: tool.Sequence, scheme: Union[ifcopenshell.entity_instance, None]) -> None:
    sequence.load_animation_color_scheme(scheme)


def go_to_task(sequence: tool.Sequence, task: ifcopenshell.entity_instance) -> Union[None, str]:
    work_schedule = sequence.get_work_schedule(task)
    is_work_schedule_active = sequence.is_work_schedule_active(work_schedule)
    if is_work_schedule_active:
        sequence.go_to_task(task)
    else:
        return "Work schedule is not active"


def guess_date_range(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    start, finish = sequence.guess_date_range(work_schedule)
    sequence.update_visualisation_date(start, finish)


def setup_default_task_columns(sequence: tool.Sequence) -> None:
    sequence.setup_default_task_columns()


def add_task_bars(sequence: tool.Sequence) -> None:
    tasks = sequence.get_animation_bar_tasks()
    if tasks:
        sequence.create_bars(tasks)


def load_default_animation_color_scheme(sequence: tool.Sequence) -> None:
    sequence.load_default_animation_color_scheme()


def visualise_work_schedule_date_range(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.clear_objects_animation(include_blender_objects=False)
    settings = sequence.get_animation_settings()
    if settings:
        product_frames = sequence.get_animation_product_frames(work_schedule, settings)
        if not sequence.has_animation_colors():
            sequence.load_default_animation_color_scheme()
        load_animation_color_scheme(sequence, scheme=sequence.get_animation_color_scheme())
        sequence.animate_objects(settings, product_frames, "date_range")
        sequence.add_text_animation_handler(settings)
        add_task_bars(sequence)
        sequence.set_object_shading()


def visualise_work_schedule_date(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    sequence.clear_objects_animation(include_blender_objects=False)
    start_date = sequence.get_start_date()
    product_states = sequence.process_construction_state(work_schedule, start_date)
    sequence.show_snapshot(product_states)
    sequence.set_object_shading()


def generate_gantt_chart(sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance) -> None:
    json = sequence.create_tasks_json(work_schedule)
    sequence.generate_gantt_browser_chart(json, work_schedule)


def load_product_related_tasks(
    sequence: tool.Sequence, product: ifcopenshell.entity_instance
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
    ifc: tool.Ifc, sequence: tool.Sequence, task: ifcopenshell.entity_instance, new_index: int
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
    ifc: tool.Ifc, sequence: tool.Sequence, work_schedule: ifcopenshell.entity_instance, name: Optional[str] = None
) -> None:
    ifc.run("sequence.create_baseline", work_schedule=work_schedule, name=name)


def clear_previous_animation(sequence: tool.Sequence) -> None:
    sequence.clear_objects_animation(include_blender_objects=False)


def add_animation_camera(sequence: tool.Sequence) -> None:
    sequence.add_animation_camera()


def save_animation_color_scheme(sequence: tool.Sequence, name: str) -> None:
    sequence.save_animation_color_scheme(name)
