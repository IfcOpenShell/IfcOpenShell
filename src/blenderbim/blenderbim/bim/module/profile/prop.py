import bpy
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.attribute
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

class Profile(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMProfileProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    profiles: CollectionProperty(name="Profiles", type=Profile)
    active_profile_index: IntProperty(name="Active Profile Index")
    active_profile_id: IntProperty(name="Active Profile Id")
    profile_attributes: CollectionProperty(name="Profile Attributes", type=Attribute)
