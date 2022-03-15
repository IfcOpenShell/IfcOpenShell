# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell.util.system
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.bim import import_ifc


class Document(blenderbim.core.tool.Document):
    @classmethod
    def add_breadcrumb(cls, document):
        props = bpy.context.scene.BIMDocumentProperties
        new = props.breadcrumbs.add()
        new.name = str(document.id())

    @classmethod
    def clear_breadcrumbs(cls):
        props = bpy.context.scene.BIMDocumentProperties
        props.breadcrumbs.clear()

    @classmethod
    def clear_document_tree(cls):
        props = bpy.context.scene.BIMDocumentProperties
        props.documents.clear()

    @classmethod
    def disable_editing_document(cls):
        bpy.context.scene.BIMDocumentProperties.active_document_id = 0

    @classmethod
    def disable_editing_ui(cls):
        bpy.context.scene.BIMDocumentProperties.is_editing = False

    @classmethod
    def enable_editing_ui(cls):
        bpy.context.scene.BIMDocumentProperties.is_editing = True

    @classmethod
    def export_document_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMDocumentProperties.document_attributes)

    @classmethod
    def get_active_breadcrumb(cls):
        props = bpy.context.scene.BIMDocumentProperties
        if len(props.breadcrumbs):
            return tool.Ifc.get().by_id(int(props.breadcrumbs[-1].name))

    @classmethod
    def import_document_attributes(cls, document):
        props = bpy.context.scene.BIMDocumentProperties
        props.document_attributes.clear()
        blenderbim.bim.helper.import_attributes2(document, props.document_attributes)

    @classmethod
    def import_project_documents(cls):
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
    def import_references(cls, document):
        props = bpy.context.scene.BIMDocumentProperties
        if tool.Ifc.get_schema() == "IFC2X3":
            for element in document.DocumentReferences or []:
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new.name = element.Name or "Unnamed"
                new.identification = element.ItemReference or "*"
                new.is_information = False
        else:
            for element in document.HasDocumentReferences:
                new = props.documents.add()
                new.ifc_definition_id = element.id()
                new.name = element.Name or "Unnamed"
                new.identification = element.Identification or "*"
                new.is_information = False

    @classmethod
    def import_subdocuments(cls, document):
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
    def is_document_information(cls, document):
        return document.is_a("IfcDocumentInformation")

    @classmethod
    def remove_latest_breadcrumb(cls):
        props = bpy.context.scene.BIMDocumentProperties
        if len(props.breadcrumbs):
            props.breadcrumbs.remove(len(props.breadcrumbs) - 1)

    @classmethod
    def set_active_document(cls, document):
        bpy.context.scene.BIMDocumentProperties.active_document_id = document.id()
