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


class StructuralAnalysisModel(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMStructuralProperties(PropertyGroup):
    structural_analysis_model_attributes: CollectionProperty(name="Structural Analysis Model Attributes", type=Attribute)
    is_editing: BoolProperty(name="Is Editing", default=False)
    structural_analysis_models: CollectionProperty(name="Structural Analysis Models", type=StructuralAnalysisModel)
    active_structural_analysis_model_index: IntProperty(name="Active Structural Analysis Model Index")
    active_structural_analysis_model_id: IntProperty(name="Active Structural Analysis Model Id")
