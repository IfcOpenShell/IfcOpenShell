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


class BIMCostProperties(PropertyGroup):
    cost_schedule_attributes: CollectionProperty(name="Cost Schedule Attributes", type=Attribute)
    active_cost_schedule_id: IntProperty(name="Active Cost Schedule Id")
