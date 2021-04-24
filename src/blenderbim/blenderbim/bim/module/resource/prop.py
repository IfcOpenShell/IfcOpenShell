import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data
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




class Resource(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_children: BoolProperty(name="Has Children")
    is_expanded: BoolProperty(name="Is Expanded")
    level_index: IntProperty(name="Level Index")

class BIMResourceTreeProperties(PropertyGroup):
    nested_resources: CollectionProperty(name="nested_resources", type=Resource)

class BIMResourceProperties(PropertyGroup):
    resource_attributes: CollectionProperty(name="Resource Attributes", type=Attribute)
    is_editing: StringProperty(name="Is Editing")
    active_resource_index: IntProperty(name="Active Resource Index")
    active_resource_id: IntProperty(name="Active Resource Id")
    active_nested_resource_index: IntProperty(name="Active nested_resource Index")
    active_nested_resource_id: IntProperty(name="Active nested_resource Id")
    nested_resource_attributes: CollectionProperty(name="nested_resource Attributes", type=Attribute)
    contracted_nested_resources: StringProperty(name="Contracted nested_resource Items", default="[]")
    is_nested_resource_update_enabled: BoolProperty(name="Is nested_resource Update Enabled", default=True)
    resources: CollectionProperty(name="Resource", type=Resource)
    is_loaded: BoolProperty(name="Is Editing")
