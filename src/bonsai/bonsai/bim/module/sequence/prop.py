# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import isodate
import ifcopenshell.api
import ifcopenshell.util.attribute
import ifcopenshell.util.date
import bonsai.tool as tool
import bonsai.core.sequence as core
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.sequence.data import SequenceData, AnimationColorSchemeData, refresh as refresh_sequence_data
import bonsai.bim.module.resource.data
import bonsai.bim.module.pset.data
from bonsai.bim.prop import StrProperty, Attribute
from dateutil import parser
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def getTaskColumns(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["taskcolumns_enum"]


def getTaskTimeColumns(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["tasktimecolumns_enum"]


def getWorkSchedules(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["work_schedules_enum"]


def getWorkCalendars(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["work_calendars_enum"]


def update_active_task_index(self, context):
    task = tool.Sequence.get_highlighted_task()
    self.highlighted_task_id = task.id() if task else 0
    tool.Sequence.update_task_ICOM(task)
    bonsai.bim.module.pset.data.refresh()
    if self.editing_task_type == "SEQUENCE":
        tool.Sequence.load_task_properties()


def update_active_task_outputs(self, context):
    task = tool.Sequence.get_highlighted_task()
    outputs = tool.Sequence.get_task_outputs(task)
    tool.Sequence.load_task_outputs(outputs)


def update_active_task_resources(self, context):
    task = tool.Sequence.get_highlighted_task()
    resources = tool.Sequence.get_task_resources(task)
    tool.Sequence.load_task_resources(resources)


def update_active_task_inputs(self, context):
    task = tool.Sequence.get_highlighted_task()
    inputs = tool.Sequence.get_task_inputs(task)
    tool.Sequence.load_task_inputs(inputs)


def updateTaskName(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled or self.name == "Unnamed":
        return
    self.file = tool.Ifc.get()
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    SequenceData.load()
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_attributes.get("Name")
        attribute.string_value = self.name


def updateTaskIdentification(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled or self.identification == "XXX":
        return
    self.file = tool.Ifc.get()
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Identification": self.identification}},
    )
    SequenceData.load()
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_attributes.get("Identification")
        attribute.string_value = self.identification


def updateTaskTimeStart(self, context):
    updateTaskTimeDateTime(self, context, "start")


def updateTaskTimeFinish(self, context):
    updateTaskTimeDateTime(self, context, "finish")


def updateTaskTimeDateTime(self, context, startfinish):
    props = context.scene.BIMWorkScheduleProperties

    if not props.is_task_update_enabled:
        return

    def canonicalise_time(time):
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")

    startfinish_value = getattr(self, startfinish)

    if startfinish_value == "-":
        return

    self.file = tool.Ifc.get()

    try:
        startfinish_datetime = parser.isoparse(startfinish_value)
    except:
        try:
            startfinish_datetime = parser.parse(startfinish_value, dayfirst=True, fuzzy=True)
        except:
            setattr(self, startfinish, "-")
            return

    task = self.file.by_id(self.ifc_definition_id)
    if task.TaskTime:
        task_time = task.TaskTime
    else:
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task)
        SequenceData.load()

    startfinish_key = "Schedule" + startfinish.capitalize()
    if SequenceData.data["task_times"][task_time.id()][startfinish_key] == startfinish_datetime:
        canonical_startfinish_value = canonicalise_time(startfinish_datetime)
        if startfinish_value != canonical_startfinish_value:
            setattr(self, startfinish, canonical_startfinish_value)
        return

    ifcopenshell.api.run(
        "sequence.edit_task_time",
        self.file,
        **{"task_time": task_time, "attributes": {startfinish_key: startfinish_datetime}},
    )
    SequenceData.load()
    bpy.ops.bim.load_task_properties()


def updateTaskDuration(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled:
        return

    if self.duration == "-":
        return

    duration = ifcopenshell.util.date.parse_duration(self.duration)
    if not duration:
        self.duration = "-"
        return

    task = tool.Ifc.get().by_id(self.ifc_definition_id)
    if task.TaskTime:
        task_time = task.TaskTime
    else:
        task_time = tool.Ifc.run("sequence.add_task_time", task=task)
    tool.Ifc.run("sequence.edit_task_time", task_time=task_time, attributes={"ScheduleDuration": duration})
    core.load_task_properties(tool.Sequence)
    tool.Sequence.refresh_task_resources()


def get_schedule_predefined_types(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["schedule_predefined_types_enum"]


def update_visualisation_start(self, context):
    update_visualisation_start_finish(self, context, "visualisation_start")


def update_visualisation_finish(self, context):
    update_visualisation_start_finish(self, context, "visualisation_finish")


def update_visualisation_start_finish(self, context, startfinish):
    def canonicalise_time(time):
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")

    startfinish_value = getattr(self, startfinish)
    try:
        startfinish_datetime = parser.isoparse(startfinish_value)
    except:
        try:
            startfinish_datetime = parser.parse(startfinish_value, dayfirst=True, fuzzy=True)
        except:
            setattr(self, startfinish, "-")
            return
    canonical_value = canonicalise_time(startfinish_datetime)
    if startfinish_value != canonical_value:
        setattr(self, startfinish, canonical_value)


def update_color_full(self, context):
    material = bpy.data.materials.get("color_full")
    if material:
        color_full = bpy.context.scene.BIMAnimationProperties.color_full
        inputs = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs
        color = inputs["Base Color"].default_value
        color[0] = color_full.r
        color[1] = color_full.g
        color[2] = color_full.b


def update_color_progress(self, context):
    material = bpy.data.materials.get("color_progress")
    if material:
        color_progress = bpy.context.scene.BIMAnimationProperties.color_progress
        inputs = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs
        color = inputs["Base Color"].default_value
        color[0] = color_progress.r
        color[1] = color_progress.g
        color[2] = color_progress.b


def update_sort_reversed(self, context):
    if context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
        core.load_task_tree(
            tool.Sequence,
            work_schedule=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_work_schedule_id),
        )


def update_filter_by_active_schedule(self, context):
    if context.active_object:
        core.load_product_related_tasks(
            tool.Sequence, product=tool.Ifc.get().by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        )


def switch_options(self, context):
    if self.should_show_visualisation_ui:
        self.should_show_snapshot_ui = False


def switch_options2(self, context):
    if self.should_show_snapshot_ui:
        self.should_show_visualisation_ui = False


def get_saved_color_schemes(self, context):
    if not AnimationColorSchemeData.is_loaded:
        AnimationColorSchemeData.load()
    return AnimationColorSchemeData.data["saved_color_schemes"]


def updateAssignedResourceName(self, context):
    pass


def updateAssignedResourceUsage(self, context):
    if not context.scene.BIMResourceProperties.is_resource_update_enabled:
        return
    if not self.schedule_usage:
        return
    resource = tool.Ifc.get().by_id(self.ifc_definition_id)
    if resource.Usage and resource.Usage.ScheduleUsage == self.schedule_usage:
        return
    tool.Resource.run_edit_resource_time(resource, attributes={"ScheduleUsage": self.schedule_usage})
    tool.Sequence.load_task_properties()
    tool.Resource.load_resource_properties()
    tool.Sequence.refresh_task_resources()
    bonsai.bim.module.resource.data.refresh()
    refresh_sequence_data()
    bonsai.bim.module.pset.data.refresh()


def update_task_bar_list(self, context):
    if not context.scene.BIMWorkScheduleProperties.is_task_update_enabled:
        return
    if self.has_bar_visual:
        tool.Sequence.add_task_bar(self.ifc_definition_id)
    else:
        tool.Sequence.remove_task_bar(self.ifc_definition_id)


class Task(PropertyGroup):
    name: StringProperty(name="Name", update=updateTaskName)
    identification: StringProperty(name="Identification", update=updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_selected: BoolProperty(name="Is Selected")
    is_expanded: BoolProperty(name="Is Expanded")
    has_bar_visual: BoolProperty(name="Show Task Bar Animation", default=False, update=update_task_bar_list)
    level_index: IntProperty(name="Level Index")
    duration: StringProperty(name="Duration", update=updateTaskDuration)
    start: StringProperty(name="Start", update=updateTaskTimeStart)
    finish: StringProperty(name="Finish", update=updateTaskTimeFinish)
    calendar: StringProperty(name="Calendar")
    derived_start: StringProperty(name="Derived Start")
    derived_finish: StringProperty(name="Derived Finish")
    derived_duration: StringProperty(name="Derived Duration")
    derived_calendar: StringProperty(name="Derived Calendar")
    is_predecessor: BoolProperty(name="Is Predecessor")
    is_successor: BoolProperty(name="Is Successor")


class WorkPlan(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class TaskResource(PropertyGroup):
    name: StringProperty(name="Name", update=updateAssignedResourceName)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    schedule_usage: FloatProperty(name="Schedule Usage", update=updateAssignedResourceUsage)


class TaskProduct(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")
    work_schedules: EnumProperty(items=getWorkSchedules, name="Work Schedules")


class ISODuration(PropertyGroup):
    name: StringProperty(name="Name")
    years: IntProperty(name="Years", default=0)
    months: IntProperty(name="Months", default=0)
    days: IntProperty(name="Days", default=0)
    hours: IntProperty(name="Hours", default=0)
    minutes: IntProperty(name="Minutes", default=0)
    seconds: IntProperty(name="Seconds", default=0)


class IFCStatus(PropertyGroup):
    name: StringProperty(name="Name")
    is_visible: BoolProperty(name="Is Visible", default=True, update=lambda x, y: bpy.ops.bim.activate_status_filters())


class BIMStatusProperties(PropertyGroup):
    is_enabled: BoolProperty(name="Is Enabled")
    statuses: CollectionProperty(name="Statuses", type=IFCStatus)


class BIMWorkScheduleProperties(PropertyGroup):
    work_schedule_predefined_types: EnumProperty(
        items=get_schedule_predefined_types, name="Predefined Type", default=None
    )
    object_type: StringProperty(name="Object Type")
    durations_attributes: CollectionProperty(name="Durations Attributes", type=ISODuration)
    work_calendars: EnumProperty(items=getWorkCalendars, name="Work Calendars")
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    editing_task_type: StringProperty(name="Editing Task Type")
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")
    active_task_index: IntProperty(name="Active Task Index", update=update_active_task_index)
    active_task_id: IntProperty(name="Active Task Id")
    highlighted_task_id: IntProperty(name="Highlited Task Id")
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    should_show_visualisation_ui: BoolProperty(name="Should Show Visualisation UI", default=True, update=switch_options)
    should_show_task_bar_selection: BoolProperty(name="Add to task bar", default=False)
    should_show_snapshot_ui: BoolProperty(name="Should Show Snapshot UI", default=False, update=switch_options2)
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    columns: CollectionProperty(name="Columns", type=Attribute)
    active_column_index: IntProperty(name="Active Column Index")
    sort_column: StringProperty(name="Sort Column")
    is_sort_reversed: BoolProperty(name="Is Sort Reversed", update=update_sort_reversed)
    column_types: EnumProperty(
        items=[
            ("IfcTask", "IfcTask", ""),
            ("IfcTaskTime", "IfcTaskTime", ""),
            ("Special", "Special", ""),
        ],
        name="Column Types",
    )
    task_columns: EnumProperty(items=getTaskColumns, name="Task Columns")
    task_time_columns: EnumProperty(items=getTaskTimeColumns, name="Task Time Columns")
    other_columns: EnumProperty(
        items=[
            ("Controls.Calendar", "Calendar", ""),
        ],
        name="Special Columns",
    )
    active_task_time_id: IntProperty(name="Active Task Time Id")
    task_time_attributes: CollectionProperty(name="Task Time Attributes", type=Attribute)
    contracted_tasks: StringProperty(name="Contracted Task Items", default="[]")
    task_bars: StringProperty(name="Checked Task Items", default="[]")
    is_task_update_enabled: BoolProperty(name="Is Task Update Enabled", default=True)
    editing_sequence_type: StringProperty(name="Editing Sequence Type")
    active_sequence_id: IntProperty(name="Active Sequence Id")
    sequence_attributes: CollectionProperty(name="Sequence Attributes", type=Attribute)
    lag_time_attributes: CollectionProperty(name="Time Lag Attributes", type=Attribute)
    visualisation_start: StringProperty(name="Visualisation Start", update=update_visualisation_start)
    visualisation_finish: StringProperty(name="Visualisation Finish", update=update_visualisation_finish)
    speed_multiplier: FloatProperty(name="Speed Multiplier", default=10000)
    speed_animation_duration: StringProperty(name="Speed Animation Duration", default="1 s")
    speed_animation_frames: IntProperty(name="Speed Animation Frames", default=24)
    speed_real_duration: StringProperty(name="Speed Real Duration", default="1 w")
    speed_types: EnumProperty(
        items=[
            ("FRAME_SPEED", "Frame-based", "e.g. 25 frames = 1 real week"),
            ("DURATION_SPEED", "Duration-based", "e.g. 1 video second = 1 real week"),
            ("MULTIPLIER_SPEED", "Multiplier", "e.g. 1000 x real life speed"),
        ],
        name="Speed Type",
        default="FRAME_SPEED",
    )
    task_resources: CollectionProperty(name="Task Resources", type=TaskResource)
    active_task_resource_index: IntProperty(name="Active Task Resource Index")
    task_inputs: CollectionProperty(name="Task Inputs", type=TaskProduct)
    active_task_input_index: IntProperty(name="Active Task Input Index")
    task_outputs: CollectionProperty(name="Task Outputs", type=TaskProduct)
    active_task_output_index: IntProperty(name="Active Task Output Index")
    show_nested_outputs: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_outputs)
    show_nested_resources: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_resources)
    show_nested_inputs: BoolProperty(name="Show Nested Tasks", default=False, update=update_active_task_inputs)
    product_input_tasks: CollectionProperty(name="Product Task Inputs", type=TaskProduct)
    product_output_tasks: CollectionProperty(name="Product Task Outputs", type=TaskProduct)
    active_product_output_task_index: IntProperty(name="Active Product Output Task Index")
    active_product_input_task_index: IntProperty(name="Active Product Input Task Index")
    enable_reorder: BoolProperty(name="Enable Reorder", default=False)
    show_task_operators: BoolProperty(name="Show Task Options", default=True)
    should_show_schedule_baseline_ui: BoolProperty(name="Baselines", default=False)
    filter_by_active_schedule: BoolProperty(
        name="Filter By Active Schedule", default=False, update=update_filter_by_active_schedule
    )


class BIMTaskTreeProperties(PropertyGroup):
    # This belongs by itself for performance reasons. https://developer.blender.org/T87737
    # In Blender if you add many collection items it makes other property access in the same group really slow.
    tasks: CollectionProperty(name="Tasks", type=Task)


class WorkCalendar(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class RecurrenceComponent(PropertyGroup):
    name: StringProperty(name="Name")
    is_specified: BoolProperty(name="Is Specified")


class BIMWorkCalendarProperties(PropertyGroup):
    work_calendar_attributes: CollectionProperty(name="Work Calendar Attributes", type=Attribute)
    work_time_attributes: CollectionProperty(name="Work Time Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    active_work_calendar_id: IntProperty(name="Active Work Calendar Id")
    active_work_time_id: IntProperty(name="Active Work Time Id")
    day_components: CollectionProperty(name="Day Components", type=RecurrenceComponent)
    weekday_components: CollectionProperty(name="Weekday Components", type=RecurrenceComponent)
    month_components: CollectionProperty(name="Month Components", type=RecurrenceComponent)
    position: IntProperty(name="Position")
    interval: IntProperty(name="Recurrence Interval")
    occurrences: IntProperty(name="Occurs N Times")
    recurrence_types: EnumProperty(
        items=[
            ("DAILY", "Daily", "e.g. Every day"),
            ("WEEKLY", "Weekly", "e.g. Every Friday"),
            ("MONTHLY_BY_DAY_OF_MONTH", "Monthly on Specified Date", "e.g. Every 2nd of each Month"),
            ("MONTHLY_BY_POSITION", "Monthly on Specified Weekday", "e.g. Every 1st Friday of each Month"),
            # https://forums.buildingsmart.org/t/what-does-by-day-count-and-by-weekday-count-mean-in-ifcrecurrencetypeenum/3571
            # ("BY_DAY_COUNT", "", ""),
            # ("BY_WEEKDAY_COUNT", "", ""),
            ("YEARLY_BY_DAY_OF_MONTH", "Yearly on Specified Date", "e.g. Every 2nd of October"),
            ("YEARLY_BY_POSITION", "Yearly on Specified Weekday", "e.g. Every 1st Friday of October"),
        ],
        name="Recurrence Types",
    )
    start_time: StringProperty(name="Start Time")
    end_time: StringProperty(name="End Time")


class DatePickerProperties(PropertyGroup):
    display_date: StringProperty(name="Display Date")
    selected_date: StringProperty(name="Selected Date")


class BIMDateTextProperties(PropertyGroup):
    start_frame: IntProperty(name="Start Frame")
    total_frames: IntProperty(name="Total Frames")
    start: StringProperty(name="Start")
    finish: StringProperty(name="Finish")


class BIMTaskTypeColor(PropertyGroup):
    name: StringProperty(name="Name")
    animation_type: StringProperty(name="Type")
    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        default=(1, 0, 0),
        min=0.0,
        max=1.0,
    )


class BIMAnimationProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Loaded", default=False)
    saved_color_schemes: EnumProperty(items=get_saved_color_schemes, name="Saved Colour Schemes")
    active_color_component_outputs_index: IntProperty(name="Active Color Component Index")
    active_color_component_inputs_index: IntProperty(name="Active Color Component Index")
    task_input_colors: CollectionProperty(name="Groups", type=BIMTaskTypeColor)
    task_output_colors: CollectionProperty(name="Groups", type=BIMTaskTypeColor)
    color_full: FloatVectorProperty(
        name="Full Bar",
        subtype="COLOR",
        default=(1.0, 0.0, 0.0),
        min=0.0,
        max=1.0,
        description="color picker",
        update=update_color_full,
    )
    color_progress: FloatVectorProperty(
        name="Progress Bar",
        subtype="COLOR",
        default=(0.0, 1.0, 0.0),
        min=0.0,
        max=1.0,
        description="color picker",
        update=update_color_progress,
    )
    should_show_task_bar_options: BoolProperty(name="Show Task Bar Options", default=False)
