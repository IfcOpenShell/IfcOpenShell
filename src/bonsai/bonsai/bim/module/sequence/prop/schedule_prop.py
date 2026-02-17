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



import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty, StringProperty, EnumProperty,
    BoolProperty, IntProperty, FloatProperty, CollectionProperty
)
from typing import TYPE_CHECKING, Literal, get_args
from . import callbacks_prop as callbacks
from . import enums_prop as enums
from .task_prop import BIMTaskFilterProperties, SavedFilterSet, TaskResource, TaskProduct, WorkPlanEditingType
from bonsai.bim.prop import Attribute, ISODuration


class WorkPlan(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    editing_type: EnumProperty(
        items=[(i, i, "") for i in get_args(WorkPlanEditingType)],
    )
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")
    work_schedules: EnumProperty(items=enums.getWorkSchedules, name="Work Schedules")
    if TYPE_CHECKING:
        work_plan_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: WorkPlanEditingType
        work_plans: bpy.types.bpy_prop_collection_idprop[WorkPlan]
        active_work_plan_index: int
        active_work_plan_id: int
        work_schedules: str


class WorkCalendar(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class RecurrenceComponent(PropertyGroup):
    name: StringProperty(name="Name")
    is_specified: BoolProperty(name="Is Specified")
    if TYPE_CHECKING:
        name: str
        is_specified: bool


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
            ("YEARLY_BY_DAY_OF_MONTH", "Yearly on Specified Date", "e.g. Every 2nd of October"),
            ("YEARLY_BY_POSITION", "Yearly on Specified Weekday", "e.g. Every 1st Friday of October"),
        ],
        name="Recurrence Types",
    )
    start_time: StringProperty(name="Start Time")
    end_time: StringProperty(name="End Time")
    if TYPE_CHECKING:
        work_calendar_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        work_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: str
        active_work_calendar_id: int
        active_work_time_id: int
        day_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        weekday_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        month_components: bpy.types.bpy_prop_collection_idprop[RecurrenceComponent]
        position: int
        interval: int
        occurrences: int
        recurrence_types: str
        start_time: str
        end_time: str

class BIMWorkScheduleProperties(PropertyGroup):
    work_schedule_predefined_types: EnumProperty(
        items=enums.get_schedule_predefined_types, name="Predefined Type", default=None, update=callbacks.update_work_schedule_predefined_type
    )
    object_type: StringProperty(name="Object Type")
    durations_attributes: CollectionProperty(name="Durations Attributes", type=ISODuration)
    work_calendars: EnumProperty(items=enums.getWorkCalendars, name="Work Calendars")
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    editing_task_type: StringProperty(name="Editing Task Type")
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id", update=callbacks.update_active_work_schedule_id)
    active_task_index: IntProperty(name="Active Task Index", update=callbacks.update_active_task_index)
    active_task_id: IntProperty(name="Active Task Id")
    highlighted_task_id: IntProperty(name="Highlited Task Id")
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    should_show_visualisation_ui: BoolProperty(name="Should Show Visualisation UI", default=True, update=callbacks.switch_options)
    should_show_task_bar_selection: BoolProperty(name="Add to task bar", default=False)
    should_show_snapshot_ui: BoolProperty(name="Should Show Snapshot UI", default=False, update=callbacks.switch_options2)
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    columns: CollectionProperty(name="Columns", type=Attribute)
    active_column_index: IntProperty(name="Active Column Index")
    sort_column: StringProperty(name="Sort Column")
    is_sort_reversed: BoolProperty(name="Is Sort Reversed", update=callbacks.update_sort_reversed)
    column_types: EnumProperty(
        items=[
            ("IfcTask", "IfcTask", ""),
            ("IfcTaskTime", "IfcTaskTime", ""),
            ("Special", "Special", ""),
        ],
        name="Column Types",
    )
    task_columns: EnumProperty(items=enums.getTaskColumns, name="Task Columns")
    task_time_columns: EnumProperty(items=enums.getTaskTimeColumns, name="Task Time Columns")
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
    date_source_type: EnumProperty(
        name="Date Source",
        description="Choose which set of dates to use for animation and snapshots",
        items=[
            ('SCHEDULE', "Schedule", "Use ScheduleStart and ScheduleFinish dates"),
            ('ACTUAL', "Actual", "Use ActualStart and ActualFinish dates"),
            ('EARLY', "Early", "Use EarlyStart and EarlyFinish dates"),
            ('LATE', "Late", "Use LateStart and LateFinish dates"),
        ],
        default='SCHEDULE'
    )
    last_lookahead_window: StringProperty(
        name="Last Lookahead Window",
        description="Stores the last selected lookahead time window to allow re-applying it automatically.",
        default=""
    )
    sequence_attributes: CollectionProperty(name="Sequence Attributes", type=Attribute)
    lag_time_attributes: CollectionProperty(name="Time Lag Attributes", type=Attribute)
    visualisation_start: StringProperty(name="Visualisation Start", update=callbacks.update_visualisation_start)
    visualisation_finish: StringProperty(name="Visualisation Finish", update=callbacks.update_visualisation_finish)
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
    show_saved_colortypes_section: BoolProperty(name="Show Saved colortypes", default=True)
    show_nested_outputs: BoolProperty(name="Show Nested Tasks", default=False, update=callbacks.update_active_task_outputs)
    show_nested_resources: BoolProperty(name="Show Nested Tasks", default=False, update=callbacks.update_active_task_resources)
    show_nested_inputs: BoolProperty(name="Show Nested Tasks", default=False, update=callbacks.update_active_task_inputs)
    product_input_tasks: CollectionProperty(name="Product Task Inputs", type=TaskProduct)
    product_output_tasks: CollectionProperty(name="Product Task Outputs", type=TaskProduct)
    active_product_output_task_index: IntProperty(name="Active Product Output Task Index")
    active_product_input_task_index: IntProperty(name="Active Product Input Task Index")
    enable_reorder: BoolProperty(name="Enable Reorder", default=False)
    show_task_operators: BoolProperty(name="Show Task Options", default=True)
    should_show_schedule_baseline_ui: BoolProperty(name="Baselines", default=False)
    should_select_3d_on_task_click: BoolProperty(
        name="Select 3D on Task Click",
        description="Automatically select 3D elements when a task is selected in the list",
        default=True
    )
    filter_by_active_schedule: BoolProperty(
        name="Filter By Active Schedule", default=False, update=callbacks.update_filter_by_active_schedule
    )
    # New property to show selected tasks count
    selected_tasks_count: IntProperty(name="Selected Tasks Count", default=0)

   
    # Property that will contain the filter configuration
    filters: PointerProperty(type=BIMTaskFilterProperties)

    saved_filter_sets: CollectionProperty(type=SavedFilterSet)
    active_saved_filter_set_index: IntProperty()
    variance_source_a: EnumProperty(
        name="Compare",
        items=enums.get_date_source_items,
        default=0,
        description="The baseline date set for comparison",
        update=callbacks.update_variance_calculation,
    )
    variance_source_b: EnumProperty(
        name="With",
        items=enums.get_date_source_items, 
        default=1,
        description="The date set to compare against the baseline",
        update=callbacks.update_variance_calculation,
    )
    
    # --- START COLUMN NAVIGATION PROPERTIES ---
    column_start_index: IntProperty(
        name="Column Start Index",
        description="Starting index for visible columns",
        default=0,
        min=0
    )
    columns_per_view: IntProperty(
        name="Columns Per View", 
        description="Maximum number of columns to display at once",
        default=5,
        min=1,
        max=20
    )
    # --- END COLUMN NAVIGATION PROPERTIES ---

    
    if TYPE_CHECKING:
        saved_filter_sets: bpy.types.bpy_prop_collection_idprop[SavedFilterSet]
        active_saved_filter_set_index: int
        work_schedule_predefined_types: str
        object_type: str
        durations_attributes: bpy.types.bpy_prop_collection_idprop[ISODuration]
        work_calendars: str
        work_schedule_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        editing_type: str
        editing_task_type: str
        active_work_schedule_index: int
        active_work_schedule_id: int
        active_task_index: int
        active_task_id: int
        last_lookahead_window: str
        date_source_type: str
        highlighted_task_id: int
        task_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        should_show_visualisation_ui: bool
        should_show_task_bar_selection: bool
        should_show_snapshot_ui: bool
        should_show_column_ui: bool
        columns: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_column_index: int
        sort_column: str
        is_sort_reversed: bool
        column_types: str
        task_columns: str
        task_time_columns: str
        other_columns: str
        active_task_time_id: int
        task_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        contracted_tasks: str
        task_bars: str
        is_task_update_enabled: bool
        editing_sequence_type: str
        active_sequence_id: int
        sequence_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        lag_time_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        visualisation_start: str
        visualisation_finish: str
        speed_multiplier: float
        speed_animation_duration: str
        speed_animation_frames: int
        speed_real_duration: str
        speed_types: str
        task_resources: bpy.types.bpy_prop_collection_idprop[TaskResource]
        active_task_resource_index: int
        task_inputs: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_task_input_index: int
        task_outputs: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_task_output_index: int
        show_nested_outputs: bool
        show_nested_resources: bool
        show_nested_inputs: bool
        product_input_tasks: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        product_output_tasks: bpy.types.bpy_prop_collection_idprop[TaskProduct]
        active_product_output_task_index: int
        active_product_input_task_index: int
        enable_reorder: bool
        show_task_operators: bool
        should_show_schedule_baseline_ui: bool
        filter_by_active_schedule: bool
        selected_tasks_count: int
        filters: 'BIMTaskFilterProperties'
        variance_source_a: str
        variance_source_b: str






