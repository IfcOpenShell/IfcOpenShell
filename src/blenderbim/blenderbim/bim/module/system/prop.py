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


class System(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMSystemProperties(PropertyGroup):
    system_attributes: CollectionProperty(name="System Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    systems: CollectionProperty(name="Systems", type=System)
    active_system_index: IntProperty(name="Active System Index")
    active_system_id: IntProperty(name="Active System Id")
