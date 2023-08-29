# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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


def add_work_plan(ifc):
    return ifc.run("sequence.add_work_plan")


def remove_work_plan(ifc, work_plan=None):
    ifc.run("sequence.remove_work_plan", work_plan=work_plan)


def enable_editing_work_plan(sequence, work_plan=None):
    sequence.load_work_plan_attributes(work_plan)
    sequence.enable_editing_work_plan(work_plan)


def disable_editing_work_plan(sequence):
    sequence.disable_editing_work_plan()


def edit_work_plan(ifc, sequence, work_plan=None):
    attributes = sequence.get_work_plan_attributes()
    ifc.run("sequence.edit_work_plan", work_plan=work_plan, attributes=attributes)
    sequence.disable_editing_work_plan()


def edit_work_schedule(ifc, sequence, work_schedule=None):
    attributes = sequence.get_work_schedule_attributes()
    ifc.run("sequence.edit_work_schedule", work_schedule=work_schedule, attributes=attributes)
    sequence.disable_editing_work_schedule()


def enable_editing_work_plan_schedules(sequence, work_plan=None):
    sequence.enable_editing_work_plan_schedules(work_plan)


def add_work_schedule(ifc, sequence, name=None):
    predefined_type, object_type = sequence.get_user_predefined_type()
    return ifc.run("sequence.add_work_schedule", name=name, predefined_type=predefined_type, object_type=object_type)


def remove_work_schedule(ifc, work_schedule=None):
    ifc.run("sequence.remove_work_schedule", work_schedule=work_schedule)


def assign_work_schedule(ifc, work_plan=None, work_schedule=None):
    if work_schedule:
        return ifc.run("aggregate.assign_object", relating_object=work_plan, product=work_schedule)


def unassign_work_schedule(ifc, work_schedule=None):
    ifc.run("aggregate.unassign_object", product=work_schedule)


def enable_editing_work_schedule(sequence, work_schedule=None):
    sequence.load_work_schedule_attributes(work_schedule)
    sequence.enable_editing_work_schedule(work_schedule)


def enable_editing_work_schedule_tasks(sequence, work_schedule=None):
    sequence.enable_editing_work_schedule_tasks(work_schedule)
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def load_task_tree(sequence, work_schedule):
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_task(sequence, task=None):
    sequence.expand_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def expand_all_tasks(sequence):
    sequence.expand_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_task(sequence, task=None):
    sequence.contract_task(task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def contract_all_tasks(sequence):
    sequence.contract_all_tasks()
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def remove_task(ifc, sequence, task=None):
    ifc.run("sequence.remove_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()
    sequence.disable_selecting_deleted_task()


def load_task_properties(sequence):
    sequence.load_task_properties()


def disable_editing_work_schedule(sequence):
    sequence.disable_editing_work_schedule()


def add_summary_task(ifc, sequence, work_schedule=None):
    ifc.run("sequence.add_task", work_schedule=work_schedule)
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def add_task(ifc, sequence, parent_task=None):
    ifc.run("sequence.add_task", parent_task=parent_task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def enable_editing_task(sequence, task=None):
    sequence.enable_editing_task(task)


def enable_editing_task_attributes(sequence, task=None):
    sequence.load_task_attributes(task)
    sequence.enable_editing_task_attributes(task)


def edit_task(ifc, sequence, task=None):
    attributes = sequence.get_task_attributes()
    ifc.run("sequence.edit_task", task=task, attributes=attributes)
    sequence.load_task_properties(task=task)
    sequence.disable_editing_task()


def copy_task_attribute(ifc, sequence, attribute_name=None):
    for task in sequence.get_checked_tasks():
        ifc.run(
            "sequence.edit_task",
            task=task,
            attributes={attribute_name: sequence.get_task_attribute_value(attribute_name)},
        )
        sequence.load_task_properties(task)


def duplicate_task(ifc, sequence, task=None):
    ifc.run("sequence.duplicate_task", task=task)
    work_schedule = sequence.get_active_work_schedule()
    sequence.load_task_tree(work_schedule)
    sequence.load_task_properties()


def disable_editing_task(sequence):
    sequence.disable_editing_task()


def enable_editing_task_time(ifc, sequence, task=None):
    task_time = sequence.get_task_time(task)
    if task_time is None:
        task_time = ifc.run("sequence.add_task_time", task=task)
    sequence.load_task_time_attributes(task_time)
    sequence.enable_editing_task_time(task)


def edit_task_time(ifc, sequence, task_time=None):
    attributes = sequence.get_task_time_attributes()
    # TODO: nasty loop goes on when calendar props are messed up
    ifc.run("sequence.edit_task_time", task_time=task_time, attributes=attributes)
    task = sequence.get_active_task()
    sequence.load_task_properties(task=task)
    sequence.disable_editing_task_time()
    sequence.load_resources()


def assign_predecessor(ifc, sequence, task=None):
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def unassign_predecessor(ifc, sequence, task=None):
    predecessor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=task, related_process=predecessor_task)
    sequence.load_task_properties()


def assign_successor(ifc, sequence, task=None):
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.assign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def unassign_successor(ifc, sequence, task=None):
    successor_task = sequence.get_highlighted_task()
    ifc.run("sequence.unassign_sequence", relating_process=successor_task, related_process=task)
    sequence.load_task_properties()


def assign_products(ifc, sequence, spatial, task=None, products=None):
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def unassign_products(ifc, sequence, spatial, task=None, products=None):
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_product", relating_product=product, related_object=task)
    outputs = sequence.get_task_outputs(task)
    sequence.load_task_outputs(outputs)


def assign_input_products(ifc, sequence, spatial, task=None, products=None):
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.assign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def unassign_input_products(ifc, sequence, spatial, task=None, products=None):
    for product in products or spatial.get_selected_products() or []:
        ifc.run("sequence.unassign_process", relating_process=task, related_object=product)
    inputs = sequence.get_task_inputs(task)
    sequence.load_task_inputs(inputs)


def assign_resource(ifc, sequence, task=None):
    resource = sequence.get_selected_resource()
    sub_resource = ifc.run(
        "resource.add_resource",
        parent_resource=resource,
        ifc_class=resource.is_a(),
        name="{}/{}".format(resource.Name or "Unnamed", task.Name or ""),
    )
    ifc.run("sequence.assign_process", relating_process=task, related_object=sub_resource)
    resources = sequence.get_task_resources(task)
    sequence.load_task_resources(resources)
    sequence.load_resources()


def unassign_resource(ifc, sequence, task=None, resource=None):
    ifc.run("sequence.unassign_process", relating_process=task, related_object=resource)
    ifc.run("resource.remove_resource", resource=resource)
    resources = sequence.get_task_resources(task)
    sequence.load_task_resources(resources)
    sequence.load_resources()


def remove_work_calendar(ifc, work_calendar=None):
    ifc.run("sequence.remove_work_calendar", work_calendar=work_calendar)


def add_work_calendar(ifc):
    return ifc.run("sequence.add_work_calendar")


def edit_work_calendar(ifc, sequence, work_calendar=None):
    attributes = sequence.get_work_calendar_attributes()
    ifc.run("sequence.edit_work_calendar", work_calendar=work_calendar, attributes=attributes)
    sequence.disable_editing_work_calendar()
    sequence.load_task_properties()


def enable_editing_work_calendar(sequence, work_calendar=None):
    sequence.load_work_calendar_attributes(work_calendar)
    sequence.enable_editing_work_calendar(work_calendar)


def disable_editing_work_calendar(sequence):
    sequence.disable_editing_work_calendar()


def enable_editing_work_calendar_times(sequence, work_calendar=None):
    sequence.enable_editing_work_calendar_times(work_calendar)


def add_work_time(ifc, work_calendar=None, time_type=None):
    return ifc.run("sequence.add_work_time", work_calendar=work_calendar, time_type=time_type)


def enable_editing_work_time(sequence, work_time=None):
    sequence.load_work_time_attributes(work_time)
    sequence.enable_editing_work_time(work_time)


def disable_editing_work_time(sequence):
    sequence.disable_editing_work_time()


def remove_work_time(ifc, work_time=None):
    ifc.run("sequence.remove_work_time", work_time=work_time)


def edit_work_time(ifc, sequence):
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


def assign_recurrence_pattern(ifc, work_time=None, recurrence_type=None):
    return ifc.run("sequence.assign_recurrence_pattern", parent=work_time, recurrence_type=recurrence_type)


def unassign_recurrence_pattern(ifc, recurrence_pattern=None):
    ifc.run("sequence.unassign_recurrence_pattern", recurrence_pattern=recurrence_pattern)


def add_time_period(ifc, sequence, recurrence_pattern=None):
    start_time, end_time = sequence.get_recurrence_pattern_times()
    ifc.run("sequence.add_time_period", recurrence_pattern=recurrence_pattern, start_time=start_time, end_time=end_time)
    sequence.reset_time_period()


def remove_time_period(ifc, time_period=None):
    ifc.run("sequence.remove_time_period", time_period=time_period)


def enable_editing_task_calendar(sequence, task=None):
    sequence.enable_editing_task_calendar(task)


def edit_task_calendar(ifc, sequence, task=None, work_calendar=None):
    ifc.run("control.assign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def remove_task_calendar(ifc, sequence, task=None, work_calendar=None):
    ifc.run("control.unassign_control", relating_control=work_calendar, related_object=task)
    ifc.run("sequence.cascade_schedule", task=task)
    sequence.load_task_properties()


def enable_editing_task_sequence(sequence):
    sequence.enable_editing_task_sequence()
    sequence.load_task_properties()


def disable_editing_task_time(sequence):
    sequence.disable_editing_task_time()


def enable_editing_sequence_attributes(sequence, rel_sequence=None):
    sequence.enable_editing_rel_sequence_attributes(rel_sequence)
    sequence.load_rel_sequence_attributes(rel_sequence)


def enable_editing_sequence_lag_time(sequence, rel_sequence=None, lag_time=None):
    sequence.load_lag_time_attributes(lag_time)
    sequence.enable_editing_sequence_lag_time(rel_sequence)


def unassign_lag_time(ifc, sequence, rel_sequence=None):
    ifc.run("sequence.unassign_lag_time", rel_sequence=rel_sequence)
    sequence.load_task_properties()


def assign_lag_time(ifc, rel_sequence=None):
    ifc.run("sequence.assign_lag_time", rel_sequence=rel_sequence, lag_value="P1D")


def edit_sequence_attributes(ifc, sequence, rel_sequence=None):
    attributes = sequence.get_rel_sequence_attributes()
    ifc.run("sequence.edit_sequence", rel_sequence=rel_sequence, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def edit_sequence_lag_time(ifc, sequence, lag_time=None):
    attributes = sequence.get_lag_time_attributes()
    ifc.run("sequence.edit_lag_time", lag_time=lag_time, attributes=attributes)
    sequence.disable_editing_rel_sequence()
    sequence.load_task_properties()


def disable_editing_rel_sequence(sequence):
    sequence.disable_editing_rel_sequence()


def select_task_outputs(sequence, spatial, task=None):
    spatial.select_products(products=sequence.get_task_outputs(task))


def select_task_inputs(sequence, spatial, task=None):
    spatial.select_products(products=sequence.get_task_inputs(task))


def select_work_schedule_products(sequence, spatial, work_schedule=None):
    products = sequence.get_work_schedule_products(work_schedule)
    spatial.select_products(products)


def select_unassigned_work_schedule_products(ifc, sequence, spatial):
    spatial.deselect_objects()
    products = ifc.get().by_type("IfcElement")
    work_schedule = sequence.get_active_work_schedule()
    schedule_products = sequence.get_work_schedule_products(work_schedule)
    selection = [product for product in products if product not in schedule_products]
    spatial.select_products(selection)


def recalculate_schedule(ifc, work_schedule=None):
    ifc.run("sequence.recalculate_schedule", work_schedule=work_schedule)


def add_task_column(sequence, column_type=None, name=None, data_type=None):
    sequence.add_task_column(column_type, name, data_type)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def remove_task_column(sequence, name=None):
    sequence.remove_task_column(name)


def set_task_sort_column(sequence, column=None):
    sequence.set_task_sort_column(column)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def calculate_task_duration(ifc, sequence, task=None):
    ifc.run("sequence.calculate_task_duration", task=task)
    work_schedule = sequence.get_active_work_schedule()
    if work_schedule:
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def load_animation_color_scheme(sequence, scheme):
    sequence.load_animation_color_scheme(scheme)


def go_to_task(sequence, task=None):
    work_schedule = sequence.get_work_schedule(task)
    is_work_schedule_active = sequence.is_work_schedule_active(work_schedule)
    if is_work_schedule_active:
        sequence.go_to_task(task)
    else:
        return "Work schedule is not active"


def highlight_product_related_task(sequence, spatial, product_type=None):
    products = spatial.get_selected_products()
    if products:
        if product_type == "Output":
            tasks = sequence.find_related_output_tasks(products[0])
        elif product_type == "Input":
            tasks = sequence.find_related_input_tasks(products[0])
        for task in tasks:
            work_schedule = sequence.get_work_schedule(task)
            is_work_schedule_active = sequence.is_work_schedule_active(work_schedule)
            if is_work_schedule_active:
                sequence.go_to_task(task)


def guess_date_range(sequence, work_schedule=None):
    start, finish = sequence.guess_date_range(work_schedule)
    sequence.update_visualisation_date(start, finish)


def setup_default_task_columns(sequence):
    sequence.setup_default_task_columns()


def add_task_bars(sequence):
    tasks = sequence.get_animation_bar_tasks()
    if tasks:
        sequence.create_bars(tasks)


def load_default_animation_color_scheme(sequence):
    sequence.load_default_animation_color_scheme()


def visualise_work_schedule_date_range(sequence, work_schedule=None):
    sequence.clear_objects_animation(include_blender_objects=False)
    settings = sequence.get_animation_settings()
    if settings:
        product_frames = sequence.get_animation_product_frames(work_schedule, settings)
        if not sequence.has_animation_colors():
            sequence.load_default_animation_color_scheme()
        sequence.animate_objects(settings, product_frames, "date_range")
        sequence.add_text_animation_handler(settings)
        add_task_bars(sequence)
        sequence.set_object_shading()


def visualise_work_schedule_date(sequence, work_schedule=None):
    sequence.clear_objects_animation(include_blender_objects=False)
    start_date = sequence.get_start_date()
    product_states = sequence.process_construction_state(work_schedule, start_date)
    sequence.show_snapshot(product_states)
    sequence.set_object_shading()


def generate_gantt_chart(sequence, work_schedule):
    json = sequence.create_tasks_json(work_schedule)
    sequence.generate_gantt_browser_chart(json, work_schedule)


def load_product_related_tasks(sequence, product=None):
    filter_by_schedule = sequence.is_filter_by_active_schedule()
    if filter_by_schedule:
        work_schedule = sequence.get_active_work_schedule()
        if work_schedule:
            task_inputs, task_ouputs = sequence.get_tasks_for_product(product, work_schedule)
        else:
            return "No active work schedule"
    else:
        task_inputs, task_ouputs = sequence.get_tasks_for_product(product)
    sequence.load_product_related_tasks(task_inputs, task_ouputs)


def reorder_task_nesting(ifc, sequence, task, new_index):
    is_sorting_enabled = sequence.is_sorting_enabled()
    is_sort_reversed = sequence.is_sort_reversed()
    if is_sorting_enabled or is_sort_reversed:
        return "Remove manual sorting"
    else:
        ifc.run("nest.reorder_nesting", item=task, new_index=new_index)
        work_schedule = sequence.get_active_work_schedule()
        sequence.load_task_tree(work_schedule)
        sequence.load_task_properties()


def create_baseline(ifc, sequence, work_schedule, name):
    ifc.run("sequence.create_baseline", work_schedule=work_schedule, name=name)


def clear_previous_animation(sequence):
    sequence.clear_objects_animation(include_blender_objects=False)


def add_animation_camera(sequence):
    sequence.add_animation_camera()


def save_animation_color_scheme(sequence, name):
    sequence.save_animation_color_scheme(name)
