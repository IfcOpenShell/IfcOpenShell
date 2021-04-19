import bpy
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


class Task(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
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
    is_editing: BoolProperty(name="Is Editing", default=False)
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")
    tasks: CollectionProperty(name="Tasks", type=Task)
    active_task_index: IntProperty(name="Active Task Index")
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
