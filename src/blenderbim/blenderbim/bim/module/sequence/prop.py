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
