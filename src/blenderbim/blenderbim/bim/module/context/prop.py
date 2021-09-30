import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.context.data import ContextData
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


class BIMContextProperties(PropertyGroup):
    contexts: EnumProperty(items=[("Model", "Model", ""), ("Plan", "Plan", "")], name="Contexts")
    subcontexts: EnumProperty(
        items=[
            ("Annotation", "Annotation", ""),
            ("Axis", "Axis", ""),
            ("Box", "Box", ""),
            ("FootPrint", "FootPrint", ""),
            ("Reference", "Reference", ""),
            ("Body", "Body", ""),
            ("Clearance", "Clearance", ""),
            ("CoG", "CoG", ""),
            ("Profile", "Profile", ""),
            ("SurveyPoints", "SurveyPoints", ""),
            ("Lighting", "Lighting", ""),
        ],
        name="Subcontexts",
    )
    target_views: EnumProperty(
        items=[
            ("GRAPH_VIEW", "GRAPH_VIEW", ""),
            ("SKETCH_VIEW", "SKETCH_VIEW", ""),
            ("MODEL_VIEW", "MODEL_VIEW", ""),
            ("PLAN_VIEW", "PLAN_VIEW", ""),
            ("REFLECTED_PLAN_VIEW", "REFLECTED_PLAN_VIEW", ""),
            ("SECTION_VIEW", "SECTION_VIEW", ""),
            ("ELEVATION_VIEW", "ELEVATION_VIEW", ""),
            ("USERDEFINED", "USERDEFINED", ""),
            ("NOTDEFINED", "NOTDEFINED", ""),
        ],
        name="Target Views",
    )
