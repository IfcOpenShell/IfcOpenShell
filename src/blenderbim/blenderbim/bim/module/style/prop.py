import bpy
from blenderbim.bim.ifc import IfcStore
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

class BIMStyleProperties(PropertyGroup):
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    is_editing_attributes: BoolProperty(name="Is Editing Attributes")
