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

class BIMSearchProperties(PropertyGroup):
    should_use_regex: BoolProperty(name="Search With Regex", default=False)
    should_ignorecase: BoolProperty(name="Search Ignoring Case", default=True)
    global_id: StringProperty(name="GlobalId")
    ifc_class: StringProperty(name="IFC Class")
    search_attribute_name: StringProperty(name="Search Attribute Name")
    search_attribute_value: StringProperty(name="Search Attribute Value")
    search_pset_name: StringProperty(name="Search Pset Name")
    search_prop_name: StringProperty(name="Search Prop Name")
    search_pset_value: StringProperty(name="Search Pset Value")
