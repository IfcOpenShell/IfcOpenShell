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

import os

import bpy
from natsort import natsorted

import bonsai.tool as tool


def refresh():
    DocumentData.is_loaded = False
    ObjectDocumentData.is_loaded = False


class DocumentData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_documents": cls.total_documents(),
            "document_objects": cls.document_objects(),
        }
        cls.is_loaded = True

    @classmethod
    def total_documents(cls):
        file = tool.Ifc.get()
        return len(file.by_type("IfcDocumentInformation")) + len(file.by_type("IfcDocumentReference"))

    @classmethod
    def document_objects(cls):
        document_objects = {}
        file = tool.Ifc.get()

        for rel in file.by_type("IfcRelAssociatesDocument"):
            document_id = rel.RelatingDocument.id()
            if document_id not in document_objects:
                document_objects[document_id] = []

            for related_object in rel.RelatedObjects:
                element = related_object
                obj = tool.Ifc.get_object(element)
                if obj:
                    document_objects[document_id].append({"id": element.id(), "name": obj.name, "obj": obj})

        return document_objects

    @classmethod
    def load_document_objects_into_props(cls, document_id):
        if not cls.is_loaded:
            cls.load()

        props = tool.Document.get_document_props()
        props.document_objects.clear()

        if document_id not in cls.data["document_objects"]:
            return

        sorted_objects = natsorted(cls.data["document_objects"][document_id], key=lambda x: x["name"].lower())

        for obj_data in sorted_objects:
            item = props.document_objects.add()
            item.name = obj_data["name"]


class ObjectDocumentData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "documents": cls.documents(),
        }
        cls.is_loaded = True

    @staticmethod
    def convert_to_file_uri(location: str) -> str:
        if not location:
            return ""

        uri = location
        if "://" not in uri:
            if not os.path.isabs(uri):
                uri = os.path.abspath(os.path.join(os.path.dirname(tool.Ifc.get_path()), uri))
            uri = "file://" + uri
        return uri

    @classmethod
    def documents(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return results
        for rel in getattr(element, "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesDocument"):
                relating_document = rel.RelatingDocument

                is_information = relating_document.is_a("IfcDocumentInformation")
                is_reference = relating_document.is_a("IfcDocumentReference")

                if not (is_information or is_reference):
                    continue

                name = relating_document.Name

                location = None
                identification = None

                if is_information:
                    identification = tool.Document.get_document_information_id(relating_document)

                    location = getattr(relating_document, "Location", None)
                    description = getattr(relating_document, "Description", "No description")
                else:
                    description = relating_document.Description
                    referenced_document = tool.Document.get_reference_document(relating_document)

                    if not name and referenced_document:
                        name = referenced_document.Name

                    identification = tool.Document.get_external_reference_id(relating_document)
                    if not identification and referenced_document:
                        identification = tool.Document.get_document_information_id(referenced_document)

                    location = relating_document.Location
                    # IFC2X3 IfcDocumentInformation has no Location to fall back to.
                    if location is None and referenced_document and tool.Ifc.get_schema() != "IFC2X3":
                        location = referenced_document.Location

                location = cls.convert_to_file_uri(location) if location else None

                results.append(
                    {
                        "id": relating_document.id(),
                        "identification": identification,
                        "name": name,
                        "location": location,
                        "is_information": is_information,
                        "description": description,
                    }
                )
        return results
