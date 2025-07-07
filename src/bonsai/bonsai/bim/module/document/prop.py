# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.tool as tool
from bonsai.bim.prop import StrProperty, Attribute
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
from bonsai.bim.module.document.data import DocumentData
from typing import TYPE_CHECKING, Union


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


def update_active_document(self, context):
    if (document := self.active_document):
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
        default="INFORMATION"
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
        document_type: str


class DocumentObject(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        name: str
        ifc_definition_id: int


class AssignedDocument(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    description: StringProperty(name="Description", default="")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    location: StringProperty(name="Location", default="")
    document_type: EnumProperty(
        name="Document Type",
        items=[
            ("PROJECT", "Project", "Virtual project root node"),
            ("INFORMATION", "Information", "IfcDocumentInformation"),
            ("REFERENCE", "Reference", "IfcDocumentReference"),
        ],
        default="INFORMATION"
    )

    if TYPE_CHECKING:
        name: str
        identification: str
        ifc_definition_id: int
        location: str
        document_type: str

class BIMDocumentProperties(PropertyGroup):
    document_attributes: CollectionProperty(name="Document Attributes", type=Attribute)
    active_document_id: IntProperty(name="Active Document Id")
    documents: CollectionProperty(name="Documents", type=Document)
    active_document_index: IntProperty(name="Active Document Index", update=update_active_document)
    is_editing: BoolProperty(name="Is Editing", default=False)
    is_document_editing: BoolProperty(name="Is Document Editing", default=False)
    is_object_editing: BoolProperty(name="Is Object Editing", default=False)
    document_objects: CollectionProperty(name="Document Objects", type=DocumentObject)
    active_document_object_index: IntProperty(name="Active Document Object Index")
    assigned_documents: CollectionProperty(name="Assigned Documents", type=AssignedDocument)
    active_assigned_document_index: IntProperty(name="Active Assigned Document Index")
    json_string: StringProperty(name="JSON String", default="[]")

    if TYPE_CHECKING:
        document_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_document_id: int
        documents: bpy.types.bpy_prop_collection_idprop[Document]
        active_document_index: int
        is_editing: bool
        is_document_editing: bool
        is_object_editing: bool
        document_objects: bpy.types.bpy_prop_collection_idprop[DocumentObject]
        active_document_object_index: int
        assigned_documents: bpy.types.bpy_prop_collection_idprop[AssignedDocument]
        active_assigned_document_index: int
        json_string: str

    @property
    def active_document(self) -> Union[Document, None]:
        return tool.Blender.get_active_uilist_element(self.documents, self.active_document_index)
