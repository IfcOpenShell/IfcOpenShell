import bpy
import ifcopenshell.api
import ifcopenshell.util.attribute
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data
from ifcopenshell.api.resource.data import Data as ResourceData
from blenderbim.bim.prop import StrProperty, Attribute
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


taskcolumns_enum = []
tasktimecolumns_enum = []


def purge():
    global taskcolumns_enum
    global tasktimecolumns_enum
    taskcolumns_enum = []
    tasktimecolumns_enum = []


def getTaskColumns(self, context):
    global taskcolumns_enum
    if not len(taskcolumns_enum) and IfcStore.get_schema():
        taskcolumns_enum.extend(
            [
                (a.name() + "/" + ifcopenshell.util.attribute.get_primitive_type(a), a.name(), "")
                for a in IfcStore.get_schema().declaration_by_name("IfcTask").all_attributes()
                if ifcopenshell.util.attribute.get_primitive_type(a)
                in ["string", "float", "integer", "boolean", "enum"]
            ]
        )
    return taskcolumns_enum


def getTaskTimeColumns(self, context):
    global tasktimecolumns_enum
    if not len(tasktimecolumns_enum) and IfcStore.get_schema():
        tasktimecolumns_enum.extend(
            [
                (a.name() + "/" + ifcopenshell.util.attribute.get_primitive_type(a), a.name(), "")
                for a in IfcStore.get_schema().declaration_by_name("IfcTaskTime").all_attributes()
                if ifcopenshell.util.attribute.get_primitive_type(a)
                in ["string", "float", "integer", "boolean", "enum"]
            ]
        )
    return tasktimecolumns_enum


def getWorkSchedules(self, context):
    return [(str(k), v["Name"], "") for k, v in Data.work_schedules.items()]


def getWorkCalendars(self, context):
    return [(str(k), v["Name"], "") for k, v in Data.work_calendars.items()]


def updateTaskName(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled or self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}},
    )
    Data.load(IfcStore.get_file())
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_attributes.get("Name")
        attribute.string_value = self.name


def updateTaskIdentification(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled or self.identification == "XXX":
        return
    self.file = IfcStore.get_file()
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Identification": self.identification}},
    )
    Data.load(self.file)
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

    self.file = IfcStore.get_file()

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
        Data.load(IfcStore.get_file())

    startfinish_key = "Schedule" + startfinish.capitalize()
    if Data.task_times[task_time.id()][startfinish_key] == startfinish_datetime:
        canonical_startfinish_value = canonicalise_time(startfinish_datetime)
        if startfinish_value != canonical_startfinish_value:
            setattr(self, startfinish, canonical_startfinish_value)
        return

    ifcopenshell.api.run(
        "sequence.edit_task_time",
        self.file,
        **{"task_time": task_time, "attributes": {startfinish_key: startfinish_datetime}},
    )
    Data.load(IfcStore.get_file())
    bpy.ops.bim.load_task_properties()


def updateTaskDuration(self, context):
    props = context.scene.BIMWorkScheduleProperties
    if not props.is_task_update_enabled:
        return
    self.file = IfcStore.get_file()
    task = self.file.by_id(self.ifc_definition_id)
    if task.TaskTime:
        task_time = task.TaskTime
    else:
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=task)
        Data.load(IfcStore.get_file())
    ifcopenshell.api.run(
        "sequence.edit_task_time",
        self.file,
        **{"task_time": task_time, "attributes": {"ScheduleDuration": self.duration}},
    )
    Data.load(IfcStore.get_file())
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_time_attributes.get("Duration")
        if attribute:
            attribute.string_value = self.duration
    bpy.ops.bim.load_task_properties()


def updateVisualisationStart(self, context):
    updateVisualisationStartFinish(self, context, "visualisation_start")


def updateVisualisationFinish(self, context):
    updateVisualisationStartFinish(self, context, "visualisation_finish")


def updateVisualisationStartFinish(self, context, startfinish):
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


def getResources(self, context):
    self.file = IfcStore.get_file()
    return [(str(k), v["Name"], "") for k, v in ResourceData.resources.items()
    if self.file.by_id(k).Nests and self.file.by_id(k).Nests[0].RelatingObject.HasContext
    ]


class Task(PropertyGroup):
    name: StringProperty(name="Name", update=updateTaskName)
    identification: StringProperty(name="Identification", update=updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_selected: BoolProperty(name="Is Selected")
    is_expanded: BoolProperty(name="Is Expanded")
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


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")
    work_schedules: EnumProperty(items=getWorkSchedules, name="Work Schedules")


class BIMWorkScheduleProperties(PropertyGroup):
    work_calendars: EnumProperty(items=getWorkCalendars, name="Work Calendars")
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    editing_type: StringProperty(name="Editing Type")
    editing_task_type: StringProperty(name="Editing Task Type")
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")
    active_task_index: IntProperty(name="Active Task Index")
    active_task_id: IntProperty(name="Active Task Id")
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    should_show_visualisation_ui: BoolProperty(name="Should Show Visualisation UI", default=False)
    should_show_column_ui: BoolProperty(name="Should Show Column UI", default=False)
    columns: CollectionProperty(name="Columns", type=Attribute)
    active_column_index: IntProperty(name="Active Column Index")
    sort_column: StringProperty(name="Sort Column")
    is_sort_reversed: BoolProperty(name="Is Sort Reversed")
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
    is_task_update_enabled: BoolProperty(name="Is Task Update Enabled", default=True)
    editing_sequence_type: StringProperty(name="Editing Sequence Type")
    active_sequence_id: IntProperty(name="Active Sequence Id")
    sequence_attributes: CollectionProperty(name="Sequence Attributes", type=Attribute)
    time_lag_attributes: CollectionProperty(name="Time Lag Attributes", type=Attribute)
    visualisation_start: StringProperty(name="Visualisation Start", update=updateVisualisationStart)
    visualisation_finish: StringProperty(name="Visualisation Finish", update=updateVisualisationFinish)
    speed_multiplier: FloatProperty(name="Speed Multiplier", default=10000)
    speed_animation_duration: StringProperty(name="Speed Animation Duration", default="PT1S")
    speed_animation_frames: IntProperty(name="Speed Animation Frames", default=24)
    speed_real_duration: StringProperty(name="Speed Real Duration", default="P1W")
    speed_types: EnumProperty(
        items=[
            ("FRAME_SPEED", "Frame-based", "e.g. 25 frames = 1 real week"),
            ("DURATION_SPEED", "Duration-based", "e.g. 1 video second = 1 real week"),
            ("MULTIPLIER_SPEED", "Multiplier", "e.g. 1000 x real life speed"),
        ],
        name="Speed Type",
        default="FRAME_SPEED",
    )
    resources: EnumProperty(items=getResources, name="Resources")


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
    display_date: StringProperty()
    selected_date: StringProperty()
