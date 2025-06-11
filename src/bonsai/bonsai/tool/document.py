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
import bpy
import ifcopenshell.util.system
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.document.prop import BIMDocumentProperties


class Document(bonsai.core.tool.Document):
    @classmethod
    def get_document_props(cls) -> BIMDocumentProperties:
        return bpy.context.scene.BIMDocumentProperties

    @classmethod
    def add_breadcrumb(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        new = props.breadcrumbs.add()
        new.name = str(document.id())

    @classmethod
    def clear_breadcrumbs(cls) -> None:
        props = cls.get_document_props()
        props.breadcrumbs.clear()

    @classmethod
    def clear_document_tree(cls) -> None:
        props = cls.get_document_props()
        props.documents.clear()

    @classmethod
    def disable_editing_document(cls) -> None:
        props = cls.get_document_props()
        props.active_document_id = 0

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
    def get_active_breadcrumb(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = cls.get_document_props()
        if len(props.breadcrumbs):
            return tool.Ifc.get().by_id(int(props.breadcrumbs[-1].name))

    @classmethod
    def import_document_attributes(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        props.document_attributes.clear()

        def callback(attr_name: str, _, data: dict[str, Any]) -> Union[bool, None]:
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
        bonsai.bim.helper.import_attributes2(document, props.document_attributes, callback=import_callback)

    @classmethod
    def import_project_documents(cls) -> None:
        props = cls.get_document_props()
        props.documents.clear()
        project = tool.Ifc.get().by_type("IfcProject")[0]
        for rel in project.HasAssociations or []:
            if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument.is_a("IfcDocumentInformation"):
                element = rel.RelatingDocument
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new["name"] = element.Name or "Unnamed"
                new.is_information = True
                new["identification"] = cls.get_document_information_id(element)

    @classmethod
    def import_references(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        is_ifc2x3 = tool.Ifc.get_schema() == "IFC2X3"
        references = cls.get_document_references(document)
        for element in references:
            new = props.documents.add()
            new.ifc_definition_id = element.id()
            # Use Description + Location instead of Name as IFC has a restriction
            # for IfcDocumentReference to have Name only if it has no ReferencedDocument.
            name = " - ".join([x for x in [element.Description, element.Location] if x])
            new["name"] = name or "Unnamed"
            new["identification"] = cls.get_external_reference_id(element)
            new.is_information = False

    @classmethod
    def import_subdocuments(cls, document: ifcopenshell.entity_instance) -> None:
        props = cls.get_document_props()
        if document.IsPointer:
            for element in document.IsPointer[0].RelatedDocuments or []:
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new["name"] = element.Name or "Unnamed"
                new.is_information = True
                new["identification"] = cls.get_document_information_id(element) or "*"

    @classmethod
    def is_document_information(cls, document: ifcopenshell.entity_instance) -> bool:
        return document.is_a("IfcDocumentInformation")

    @classmethod
    def remove_latest_breadcrumb(cls) -> None:
        props = cls.get_document_props()
        if len(props.breadcrumbs):
            props.breadcrumbs.remove(len(props.breadcrumbs) - 1)

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
        """Get IfcDocumentReference.ReferencedDocuments, compatible with IFC2X3."""
        if document.file.schema == "IFC2X3":
            return document.DocumentReferences or ()
        return document.HasDocumentReferences
