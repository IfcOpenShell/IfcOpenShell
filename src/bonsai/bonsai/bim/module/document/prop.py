from typing import TYPE_CHECKING, Literal, Union

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

import bonsai.tool as tool
from bonsai.bim.module.document.data import DocumentData, refresh
from bonsai.bim.prop import Attribute


def update_document_name(self: "Document", context: bpy.types.Context) -> None:
    if not self.ifc_definition_id:
        return
    tool.Ifc.get().by_id(self.ifc_definition_id).Name = self.name


def update_document_identification(self: "Document", context: bpy.types.Context) -> None:
    if not self.ifc_definition_id:
        return
    document = tool.Ifc.get().by_id(self.ifc_definition_id)
    if document.is_a("IfcDocumentInformation"):
        tool.Document.set_document_information_id(document, self.identification)
    else:
        tool.Document.set_external_reference_id(document, self.identification)


def update_active_document_index(self, context):
    refresh()
    if document := self.active_document:
        if document.ifc_definition_id:
            DocumentData.load_document_objects_into_props(document.ifc_definition_id)


class Document(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    description: StringProperty(name="Description")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    location: StringProperty(name="Location", default="")
    tree_depth: IntProperty(name="Tree Depth", default=0)
    has_children: BoolProperty(name="Has Children", default=False)
    is_expanded: BoolProperty(name="Is Expanded", default=False)
    document_type: EnumProperty(
        name="Document Type",
        items=[
            ("PROJECT", "Project", "Virtual project root node"),
            ("INFORMATION", "Information", "IfcDocumentInformation"),
            ("REFERENCE", "Reference", "IfcDocumentReference"),
        ],
        default="INFORMATION",
    )

    if TYPE_CHECKING:
        name: str
        identification: str
        description: str
        ifc_definition_id: int
        location: str
        tree_depth: int
        has_children: bool
        is_expanded: bool
        document_type: Literal["PROJECT", "INFORMATION", "REFERENCE"]


class DocumentObject(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class BIMDocumentProperties(PropertyGroup):
    document_attributes: CollectionProperty(name="Document Attributes", type=Attribute)
    active_document_id: IntProperty(name="Active Document Id")
    documents: CollectionProperty(name="Documents", type=Document)
    active_document_index: IntProperty(name="Active Document Index", update=update_active_document_index)
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_object_editing: BoolProperty(name="Is Object Editing", default=False)
    document_objects: CollectionProperty(name="Document Objects", type=DocumentObject)
    active_document_object_index: IntProperty(name="Active Document Object Index")
    json_string: StringProperty(name="JSON String", default="[]")

    if TYPE_CHECKING:
        document_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_document_id: int
        documents: bpy.types.bpy_prop_collection_idprop[Document]
        active_document_index: int
        is_editing: bool
        is_object_editing: bool
        document_objects: bpy.types.bpy_prop_collection_idprop[DocumentObject]
        active_document_object_index: int
        json_string: str

    @property
    def active_document(self) -> Union[Document, None]:
        return tool.Blender.get_active_uilist_element(self.documents, self.active_document_index)
