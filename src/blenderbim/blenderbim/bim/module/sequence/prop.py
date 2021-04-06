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


class BIMTaskProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing", default=False)
    tasks: CollectionProperty(name="Tasks", type=Task)
    active_task_index: IntProperty(name="Active Task Index")


class WorkPlan(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkPlanProperties(PropertyGroup):
    work_plan_attributes: CollectionProperty(name="Work Plan Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    work_plans: CollectionProperty(name="Work Plans", type=WorkPlan)
    active_work_plan_index: IntProperty(name="Active Work Plan Index")
    active_work_plan_id: IntProperty(name="Active Work Plan Id")


class WorkSchedule(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMWorkScheduleProperties(PropertyGroup):
    work_schedule_attributes: CollectionProperty(name="Work Schedule Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    work_schedules: CollectionProperty(name="Work Schedules", type=WorkSchedule)
    active_work_schedule_index: IntProperty(name="Active Work Schedules Index")
    active_work_schedule_id: IntProperty(name="Active Work Schedules Id")