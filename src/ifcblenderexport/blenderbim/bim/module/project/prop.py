import bpy
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


class BIMProjectProperties(PropertyGroup):
    is_authoring: BoolProperty(name="Enable Authoring Mode", default=True)
