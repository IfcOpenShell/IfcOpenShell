import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data
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
    Data.load(IfcStore.get_file())
    if props.active_task_id == self.ifc_definition_id:
        attribute = context.scene.BIMWorkScheduleProperties.task_attributes.get("Identification")
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

    startfinish_key = "Schedule" + startfinish.capitalize()
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
    setattr(self, startfinish, canonicalise_time(startfinish_datetime))


workschedule_enum = []


def getWorkSchedules(self, context):
    return [(str(k), v["Name"], "") for k, v in Data.work_schedules.items()]


class Task(PropertyGroup):
    name: StringProperty(name="Name", update=updateTaskName)
    identification: StringProperty(name="Identification", update=updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")
    duration: StringProperty(name="Duration")
    start: StringProperty(name="Start", update=updateTaskTimeStart)
    finish: StringProperty(name="Finish", update=updateTaskTimeFinish)
    is_predecessor: BoolProperty(name="Is Predecessor")
    is_successor: BoolProperty(name="Is Successor")


class WorkPlan(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")
    work_schedules: EnumProperty(items=getWorkSchedules, name="Work Schedules")


class BIMWorkScheduleProperties(PropertyGroup):
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")
    active_task_index: IntProperty(name="Active Task Index")
    active_task_id: IntProperty(name="Active Task Id")
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    should_show_times: BoolProperty(name="Should Show Times", default=True)
    active_task_time_id: IntProperty(name="Active Task Id")
    task_time_attributes: CollectionProperty(name="Task Time Attributes", type=Attribute)
    contracted_tasks: StringProperty(name="Contracted Task Items", default="[]")
    is_task_update_enabled: BoolProperty(name="Is Task Update Enabled", default=True)


class BIMTaskTreeProperties(PropertyGroup):
    # This belongs by itself for performance reasons. https://developer.blender.org/T87737
    # In Blender if you add thousands of tasks it makes other property access in the same group really slow.
    tasks: CollectionProperty(name="Tasks", type=Task)


class WorkCalendar(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkCalendarProperties(PropertyGroup):
    work_calendar_attributes: CollectionProperty(name="Work Calendar Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    work_calendars: CollectionProperty(name="Work Calendar", type=WorkCalendar)
    active_work_calendar_index: IntProperty(name="Active Work Calendar Index")
    active_work_calendar_id: IntProperty(name="Active Work Calendar Id")
