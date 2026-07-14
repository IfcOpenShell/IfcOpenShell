# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Union

import bpy
import ifcopenshell.util.system
from natsort import natsorted

import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.document.prop import BIMDocumentProperties


class Document(bonsai.core.tool.Document):
    @classmethod
    def get_document_props(cls) -> BIMDocumentProperties:
        return bpy.context.scene.BIMDocumentProperties

    @classmethod
    def clear_document_tree(cls) -> None:
        props = cls.get_document_props()
        props.documents.clear()

    @classmethod
    def disable_editing_document(cls) -> None:
        props = cls.get_document_props()
        props.active_document_id = 0

    @classmethod
    def disable_object_editing_ui(cls) -> None:
        props = cls.get_document_props()
        props.is_object_editing = False

    @classmethod
    def disable_editing_ui(cls) -> None:
        props = cls.get_document_props()
        props.is_editing = False

    @classmethod
    def enable_editing_ui(cls) -> None:
        props = cls.get_document_props()
        props.is_editing = True

    @classmethod
    def export_document_attributes(cls) -> dict[str, Any]:
        props = cls.get_document_props()
        return bonsai.bim.helper.export_attributes(props.document_attributes)

    @classmethod
    def import_document_attributes(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        props.document_attributes.clear()

        def callback(attr_name: str, attr_value: Any, data: dict[str, Any]) -> Union[bool, None]:
            if attr_name == "Location" and attr_value is None:
                data[attr_name] = ""
                return True
            if attr_name != "Name":
                return None  # Proceed normally

            current_value = data[attr_name]
            # If Name is already filled, display it so user would be able to correct invalid IFC.
            if current_value is not None:
                return None

            # Skip import since IFC restricts Name to be filled
            # for IfcDocumentReference with ReferencedDocument.
            return False

        import_callback = callback if document.is_a("IfcDocumentReference") else None
        bonsai.bim.helper.import_attributes(document, props.document_attributes, callback=import_callback)

    @classmethod
    def import_project_documents(cls) -> None:
        props = cls.get_document_props()
        props.documents.clear()
        file = tool.Ifc.get()
        try:
            expanded_documents = json.loads(props.json_string)
        except (AttributeError, json.JSONDecodeError):
            expanded_documents = []

        project = file.by_type("IfcProject")[0] if file.by_type("IfcProject") else None
        if not project:
            return

        document_children = {}

        for rel in file.by_type("IfcDocumentInformationRelationship"):
            parent_id = rel.RelatingDocument.id()
            if parent_id not in document_children:
                document_children[parent_id] = []

            for child in rel.RelatedDocuments:
                document_children[parent_id].append(child)

        is_ifc2x3 = file.schema == "IFC2X3"

        if is_ifc2x3:
            for ref in file.by_type("IfcDocumentReference"):
                if ref.ReferenceToDocument:
                    parent = ref.ReferenceToDocument[0]
                    parent_id = parent.id()
                    if parent_id not in document_children:
                        document_children[parent_id] = []
                    document_children[parent_id].append(ref)
        else:
            for ref in file.by_type("IfcDocumentReference"):
                if ref.ReferencedDocument:
                    parent = ref.ReferencedDocument
                    parent_id = parent.id()
                    if parent_id not in document_children:
                        document_children[parent_id] = []
                    document_children[parent_id].append(ref)

        root_documents = []
        for rel in project.HasAssociations or []:
            if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument.is_a("IfcDocumentInformation"):
                is_child = False
                for children in document_children.values():
                    if rel.RelatingDocument in children:
                        is_child = True
                        break

                if not is_child:
                    root_documents.append(rel.RelatingDocument)

        root = props.documents.add()
        root.ifc_definition_id = -project.id()
        root.document_type = "PROJECT"
        root.name = f"Project Documents ({project.Name or 'Unnamed Project'})"
        root.identification = ""
        root.location = ""
        root.tree_depth = 0
        root.has_children = bool(root_documents)

        root_id = -project.id()

        root.is_expanded = root_id not in expanded_documents

        if root.is_expanded:
            root_documents = natsorted(
                root_documents, key=lambda doc: (cls.get_document_information_id(doc) or "", doc.Name or "")
            )

            for doc in root_documents:
                cls._process_document(doc, props, document_children, expanded_documents, 1)

    @classmethod
    def _process_document(cls, document, props, document_children, expanded_documents, depth):
        new = props.documents.add()
        new.ifc_definition_id = document.id()
        new.document_type = "INFORMATION" if document.is_a("IfcDocumentInformation") else "REFERENCE"
        new.tree_depth = depth

        new.name = document.Name or ""
        new.identification = (
            cls.get_document_information_id(document)
            if new.document_type == "INFORMATION"
            else cls.get_external_reference_id(document)
        )
        new.identification = new.identification or ""
        new.description = document.Description or ""
        new.location = document.Location or ""

        if new.document_type == "INFORMATION":
            new.name = document.Name or "Unnamed"

        elif new.document_type == "REFERENCE":
            file = document.file
            if file.schema == "IFC2X3":
                if document.ReferenceToDocument and not new.name:
                    new.name = document.ReferenceToDocument[0].Name or ""
            else:
                if document.ReferencedDocument and not new.name:
                    new.name = document.ReferencedDocument.Name or ""

        doc_id = document.id()
        has_children = doc_id in document_children and bool(document_children[doc_id])
        new.has_children = has_children
        new.is_expanded = doc_id in expanded_documents

        if has_children and new.is_expanded:
            children = document_children[doc_id]

            info_children = natsorted(
                [d for d in children if d.is_a("IfcDocumentInformation")],
                key=lambda doc: (cls.get_document_information_id(doc) or "", doc.Name or ""),
            )

            ref_children = natsorted(
                [d for d in children if not d.is_a("IfcDocumentInformation")],
                key=lambda doc: (cls.get_external_reference_id(doc) or "", doc.Description or doc.Name or ""),
            )

            for child in info_children + ref_children:
                cls._process_document(child, props, document_children, expanded_documents, depth + 1)

    @classmethod
    def is_document_information(cls, document: ifcopenshell.entity_instance) -> bool:
        return document.is_a("IfcDocumentInformation")

    @classmethod
    def set_active_document(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        props.active_document_id = document.id()

    @classmethod
    def get_document_information_id(cls, document: ifcopenshell.entity_instance) -> Union[str, None]:
        """Get IfcDocumentInformation.DocumentId/Identification, compatible with IFC2X3."""
        return document[0]

    @classmethod
    def set_document_information_id(cls, document: ifcopenshell.entity_instance, value: Union[str, None]) -> None:
        """Set IfcDocumentInformation.DocumentId/Identification, compatible with IFC2X3."""
        document[0] = value

    @classmethod
    def get_external_reference_id(cls, reference: ifcopenshell.entity_instance) -> Union[str, None]:
        """Get IfcExternalReference.ItemReference/Identification, compatible with IFC2X3."""
        return reference[1]

    @classmethod
    def set_external_reference_id(cls, reference: ifcopenshell.entity_instance, value: Union[str, None]) -> None:
        """Set IfcExternalReference.ItemReference/Identification, compatible with IFC2X3."""
        reference[1] = value

    @classmethod
    def get_document_references(
        cls, document: ifcopenshell.entity_instance
    ) -> tuple[ifcopenshell.entity_instance, ...]:
        # TODO: migrate to util.document and replace all instances
        """Get IfcDocumentReference.ReferencedDocuments, compatible with IFC2X3."""
        if document.file.schema == "IFC2X3":
            return document.DocumentReferences or ()
        return document.HasDocumentReferences

    @classmethod
    def get_reference_document(cls, reference: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance | None:
        # TODO: migrate to util.document and replace all instances
        if reference.file.schema == "IFC2X3":
            reference_to_document = reference.ReferenceToDocument
            return reference_to_document[0] if reference_to_document else None
        return reference.ReferencedDocument

    @classmethod
    def clear_active_document(cls) -> None:
        props = cls.get_document_props()
        props.active_document_id = 0

    @classmethod
    def clear_document_attributes(cls) -> None:
        props = cls.get_document_props()
        props.document_attributes.clear()

    @classmethod
    def expand_document(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        try:
            expanded_docs = json.loads(props.json_string)
        except (AttributeError, json.JSONDecodeError):
            expanded_docs = []

        if document.id() not in expanded_docs:
            expanded_docs.append(document.id())
            props.json_string = json.dumps(expanded_docs)

    @classmethod
    def get_default_parent_for_information(cls) -> Union[ifcopenshell.entity_instance, None]:
        file = tool.Ifc.get()
        projects = file.by_type("IfcProject")
        return projects[0] if projects else None

    @classmethod
    def get_selected_document_information(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = cls.get_document_props()

        if props.active_document and props.active_document.document_type == "INFORMATION":
            file = tool.Ifc.get()
            return file.by_id(props.active_document.ifc_definition_id)
        return None

    @classmethod
    def refresh_document_data(cls) -> None:
        import bonsai.bim.module.document.data as document_data

        document_data.DocumentData.is_loaded = False
        document_data.DocumentData.load()

    @classmethod
    def load_document_objects_into_props(cls, document_id: int) -> None:
        import bonsai.bim.module.document.data as document_data

        document_data.DocumentData.load_document_objects_into_props(document_id)

    @classmethod
    def update_document_objects(cls, document_id: Union[int, None] = None) -> None:
        cls.refresh_document_data()

        if document_id is None:
            props = cls.get_document_props()
            if props.active_document and props.active_document.ifc_definition_id > 0:
                document_id = props.active_document.ifc_definition_id

        if document_id:
            cls.load_document_objects_into_props(document_id)
