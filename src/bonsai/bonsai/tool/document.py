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

import bpy
import ifcopenshell.util.system
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import Any, Union


class Document(bonsai.core.tool.Document):
    @classmethod
    def add_breadcrumb(cls, document: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        new = props.breadcrumbs.add()
        new.name = str(document.id())

    @classmethod
    def clear_breadcrumbs(cls) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        props.breadcrumbs.clear()

    @classmethod
    def clear_document_tree(cls) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        props.documents.clear()

    @classmethod
    def disable_editing_document(cls) -> None:
        bpy.context.scene.BIMDocumentProperties.active_document_id = 0

    @classmethod
    def disable_editing_ui(cls) -> None:
        bpy.context.scene.BIMDocumentProperties.is_editing = False

    @classmethod
    def enable_editing_ui(cls) -> None:
        bpy.context.scene.BIMDocumentProperties.is_editing = True

    @classmethod
    def export_document_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMDocumentProperties.document_attributes)

    @classmethod
    def get_active_breadcrumb(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = bpy.context.scene.BIMDocumentProperties
        if len(props.breadcrumbs):
            return tool.Ifc.get().by_id(int(props.breadcrumbs[-1].name))

    @classmethod
    def import_document_attributes(cls, document: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMDocumentProperties
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
        props = bpy.context.scene.BIMDocumentProperties
        props.documents.clear()
        project = tool.Ifc.get().by_type("IfcProject")[0]
        for rel in project.HasAssociations or []:
            if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument.is_a("IfcDocumentInformation"):
                element = rel.RelatingDocument
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new.name = element.Name or "Unnamed"
                new.is_information = True
                if tool.Ifc.get_schema() == "IFC2X3":
                    new.identification = element.DocumentId or "*"
                else:
                    new.identification = element.Identification or "*"

    @classmethod
    def import_references(cls, document: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        is_ifc2x3 = tool.Ifc.get_schema() == "IFC2X3"
        references = (document.DocumentReference or []) if is_ifc2x3 else document.HasDocumentReferences
        for element in references:
            new = props.documents.add()
            new.ifc_definition_id = element.id()
            # Use Description + Location instead of Name as IFC has a restriction
            # for IfcDocumentReference to have Name only if it has no ReferencedDocument.
            name = " - ".join([x for x in [element.Description, element.Location] if x])
            new.name = name or "Unnamed"
            new.identification = (element.ItemReference if is_ifc2x3 else element.Identification) or "*"
            new.is_information = False

    @classmethod
    def import_subdocuments(cls, document: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        if document.IsPointer:
            for element in document.IsPointer[0].RelatedDocuments or []:
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new.name = element.Name or "Unnamed"
                new.is_information = True
                if tool.Ifc.get_schema() == "IFC2X3":
                    new.identification = element.DocumentId or "*"
                else:
                    new.identification = element.Identification or "*"

    @classmethod
    def is_document_information(cls, document: ifcopenshell.entity_instance) -> bool:
        return document.is_a("IfcDocumentInformation")

    @classmethod
    def remove_latest_breadcrumb(cls) -> None:
        props = bpy.context.scene.BIMDocumentProperties
        if len(props.breadcrumbs):
            props.breadcrumbs.remove(len(props.breadcrumbs) - 1)

    @classmethod
    def set_active_document(cls, document: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMDocumentProperties.active_document_id = document.id()
