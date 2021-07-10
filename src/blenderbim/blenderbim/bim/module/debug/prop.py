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


class BIMDebugProperties(PropertyGroup):
    step_id: IntProperty(name="STEP ID")
    number_of_polygons: IntProperty(name="Number of Polygons")
    active_step_id: IntProperty(name="STEP ID")
    step_id_breadcrumb: CollectionProperty(name="STEP ID Breadcrumb", type=StrProperty)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    inverse_attributes: CollectionProperty(name="Inverse Attributes", type=Attribute)
    inverse_references: CollectionProperty(name="Inverse References", type=Attribute)
