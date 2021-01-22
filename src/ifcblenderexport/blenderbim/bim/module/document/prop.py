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

class Document(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMDocumentProperties(PropertyGroup):
    document_attributes: CollectionProperty(name="Document Attributes", type=Attribute)
    active_document_id: IntProperty(name="Active Document Id")
    documents: CollectionProperty(name="Documents", type=Document)
    active_document_index: IntProperty(name="Active Document Index")
    is_editing: StringProperty(name="Is Editing")
