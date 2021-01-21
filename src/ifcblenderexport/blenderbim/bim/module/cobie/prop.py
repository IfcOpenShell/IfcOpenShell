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


class COBieProperties(PropertyGroup):
    cobie_ifc_file: StringProperty(default="", name="COBie IFC File")
    cobie_types: StringProperty(default=".COBieType", name="COBie Types")
    cobie_components: StringProperty(default=".COBie", name="COBie Components")
    cobie_json_file: StringProperty(default="", name="COBie JSON File")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
    
