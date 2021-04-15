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


class CostItem(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")


class BIMCostProperties(PropertyGroup):
    cost_schedule_attributes: CollectionProperty(name="Cost Schedule Attributes", type=Attribute)
    active_cost_schedule_id: IntProperty(name="Active Cost Schedule Id")
    cost_items: CollectionProperty(name="Work Calendar", type=CostItem)
    active_cost_item_index: IntProperty(name="Active Cost Item Index")
    contracted_cost_items: StringProperty(name="Contracted Cost Items", default="[]")
