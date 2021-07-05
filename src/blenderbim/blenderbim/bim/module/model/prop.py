import bpy
import ifcopenshell.util.type
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
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

relating_types_enum = []


def purge():
    global relating_types_enum
    relating_types_enum = []

def getRelatingTypes(self, context):
    global relating_types_enum
    if len(relating_types_enum) < 1:
        elements = IfcStore.get_file().by_type("IfcWallType")
        relating_types_enum.extend((str(e.id()), e.Name, "") for e in elements)
    return relating_types_enum

class BIMModelProperties(PropertyGroup):
    relating_type: EnumProperty(items=getRelatingTypes, name="Relating Type")
