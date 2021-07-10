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

class BIMQtoProperties(PropertyGroup):
    qto_result: StringProperty(default="", name="Qto Result")
    qto_methods: EnumProperty(
        items=[
            ("HEIGHT", "Height", "Calculate the Z height of an object"),
            ("VOLUME", "Volume", "Calculate the volume of an object"),
            ("FORMWORK", "Formwork", "Calculate the exposed formwork for all bottoms and sides of one or more objects"),
        ],
        name="Qto Methods",
    )
    qto_name: StringProperty(name="Qto Name")
    prop_name: StringProperty(name="Prop Name")
