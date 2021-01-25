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


class Layer(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMLayerProperties(PropertyGroup):
    layer_attributes: CollectionProperty(name="Layer Attributes", type=Attribute)
    active_layer_id: IntProperty(name="Active Layer Id")
    layers: CollectionProperty(name="Layers", type=Layer)
    active_layer_index: IntProperty(name="Active Layer Index")
    is_editing: BoolProperty(name="Is Editing", default=False)
