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
    def disable_document_assignment_ui(cls, obj):
        obj.BIMObjectDocumentProperties.is_adding = ""

    @classmethod
    def disable_editing_document(cls):
        bpy.context.scene.BIMDocumentProperties.active_document_id = 0

    @classmethod
    def disable_editing_ui(cls):
        bpy.context.scene.BIMDocumentProperties.is_editing = ""

    @classmethod
    def enable_document_assignment_ui(cls, obj):
        obj.BIMObjectDocumentProperties.is_adding = "IfcDocumentReference"

    @classmethod
    def enable_information_editing_ui(cls):
        bpy.context.scene.BIMDocumentProperties.is_editing = "information"

    @classmethod
    def enable_reference_editing_ui(cls):
        bpy.context.scene.BIMDocumentProperties.is_editing = "reference"

    @classmethod
    def export_document_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMDocumentProperties.document_attributes)

    @classmethod
    def import_document_attributes(cls, document):
        props = bpy.context.scene.BIMDocumentProperties
        props.document_attributes.clear()
        blenderbim.bim.helper.import_attributes2(document, props.document_attributes)

    @classmethod
    def import_information(cls):
        props = bpy.context.scene.BIMDocumentProperties
        props.documents.clear()
        for element in tool.Ifc.get().by_type("IfcDocumentInformation"):
            new = props.documents.add()
            new.ifc_definition_id = element.id()
            new.name = element.Name or "Unnamed"
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = element.DocumentId or "*"
            else:
                new.identification = element.Identification or "*"

    @classmethod
    def import_references(cls):
        props = bpy.context.scene.BIMDocumentProperties
        props.documents.clear()
        for element in tool.Ifc.get().by_type("IfcDocumentReference"):
            new = props.documents.add()
            new.ifc_definition_id = element.id()
            new.name = element.Name or "Unnamed"
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = element.ItemReference or "*"
            else:
                new.identification = element.Identification or "*"

    @classmethod
    def is_document_information(cls, document):
        return document.is_a("IfcDocumentInformation")

    @classmethod
    def set_active_document(cls, document):
        bpy.context.scene.BIMDocumentProperties.active_document_id = document.id()
