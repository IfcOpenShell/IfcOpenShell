import bpy
from blenderbim.bim.prop import StrProperty
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


class DiffProperties(PropertyGroup):
    diff_json_file: StringProperty(default="", name="Diff JSON File")
    diff_old_file: StringProperty(default="", name="Diff Old IFC File")
    diff_new_file: StringProperty(default="", name="Diff New IFC File")
    diff_relationships: StringProperty(default="", name="Diff Relationships")
    
