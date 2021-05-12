import bpy
from blenderbim.bim.prop import StrProperty
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


class LibraryElement(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_declared: BoolProperty(name="Is Declared", default=False)


class BIMProjectProperties(PropertyGroup):
    is_authoring: BoolProperty(name="Enable Authoring Mode", default=True)
    active_library_element: StringProperty(name="Enable Authoring Mode", default="")
    library_breadcrumb: CollectionProperty(name="Library Breadcrumb", type=StrProperty)
    library_elements: CollectionProperty(name="Library Elements", type=LibraryElement)
    active_library_element_index: IntProperty(name="Active Library Element Index")
