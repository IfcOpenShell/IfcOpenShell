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


class BIMGeometryProperties(PropertyGroup):
    # Revit workaround
    should_use_presentation_style_assignment: BoolProperty(name="Force Presentation Style Assignment", default=False)
    # RIB iTwo, DESITE BIM workaround
    should_force_faceted_brep: BoolProperty(name="Force Faceted Breps", default=False)
    # Navisworks workaround
    should_force_triangulation: BoolProperty(name="Force Triangulation", default=False)
