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


class Group(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMGroupProperties(PropertyGroup):
    group_attributes: CollectionProperty(name="Group Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    groups: CollectionProperty(name="Groups", type=Group)
    active_group_index: IntProperty(name="Active Group Index")
    active_group_id: IntProperty(name="Active Group Id")
