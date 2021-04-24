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


class BIMResourceProperties(PropertyGroup):
    resource_attributes: CollectionProperty(name="Resource Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing")
    active_resource_id: IntProperty(name="Active Resource Id")
    active_resource_index: IntProperty(name="Active Resource Id")
    is_nested_resource_update_enabled: BoolProperty(name="Is nested_resource Update Enabled", default=True)
    resources: CollectionProperty(name="Resource", type=Resource)
    is_loaded: BoolProperty(name="Is Editing")
    active_nested_resource_id: IntProperty(name="Active Nested Ressource Id")
    active_nested_resource_index: IntProperty(name="Active Nested Resource Index")
    nested_resource_attributes: CollectionProperty(name="Nested Resource Attributes", type=Attribute)
    contracted_nested_resources: StringProperty(name="Contracted Cost Items", default="[]")
