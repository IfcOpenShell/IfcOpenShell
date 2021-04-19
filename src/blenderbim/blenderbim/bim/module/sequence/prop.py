import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.sequence.data import Data
from blenderbim.bim.prop import StrProperty, Attribute
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
    if self.name == "Unnamed":
        return
    self.file = IfcStore.get_file()
    props = context.scene.BIMWorkScheduleProperties
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Name": self.name}}
    )
    Data.load(IfcStore.get_file())
    if props.active_task_id == self.ifc_definition_id:
        attribute = context.scene.BIMWorkScheduleProperties.task_attributes.get("Name")
        attribute.string_value = self.name


def updateTaskIdentification(self, context):
    if self.identification == "X":
        return
    self.file = IfcStore.get_file()
    props = context.scene.BIMWorkScheduleProperties
    ifcopenshell.api.run(
        "sequence.edit_task",
        self.file,
        **{"task": self.file.by_id(self.ifc_definition_id), "attributes": {"Identification": self.identification}}
    )
    Data.load(IfcStore.get_file())
    if props.active_task_id == self.ifc_definition_id:
        attribute = context.scene.BIMWorkScheduleProperties.task_attributes.get("Identification")
        attribute.string_value = self.identification


class Task(PropertyGroup):
    name: StringProperty(name="Name", update=updateTaskName)
    identification: StringProperty(name="Identification", update=updateTaskIdentification)
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class WorkPlan(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")


class BIMWorkScheduleProperties(PropertyGroup):
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")
    tasks: CollectionProperty(name="Tasks", type=Task)
    active_task_index: IntProperty(name="Active Task Index")
    active_task_id: IntProperty(name="Active Task Id")
    task_attributes: CollectionProperty(name="Task Attributes", type=Attribute)
    contracted_tasks: StringProperty(name="Contracted Task Items", default="[]")


class WorkCalendar(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkCalendarProperties(PropertyGroup):
    work_calendar_attributes: CollectionProperty(name="Work Calendar Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    work_calendars: CollectionProperty(name="Work Calendar", type=WorkCalendar)
    active_work_calendar_index: IntProperty(name="Active Work Calendar Index")
    active_work_calendar_id: IntProperty(name="Active Work Calendar Id")
