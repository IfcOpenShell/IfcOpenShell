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


class CsvProperties(PropertyGroup):
    csv_ifc_file: StringProperty(default="", name="CSV IFC File")
    ifc_selector: StringProperty(default="", name="IFC Selector")
    csv_attributes: CollectionProperty(name="CSV Attributes", type=StrProperty)
    csv_delimiter: EnumProperty(
        items=[(";", ";", ""), (",", ",", ""), (".", ".", ""), ("CUSTOM", "Custom", ""),],
        name="IFC CSV Delimiter",
        default=",",
    )
    csv_custom_delimiter: StringProperty(default="", name="Custom Delimiter")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
    
