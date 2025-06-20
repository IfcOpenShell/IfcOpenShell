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
import ifcopenshell
import ifcopenshell.util.schema
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
            "total_document_informations": cls.total_document_informations(),
            "total_document_references": cls.total_document_references(),
            "total_referenced_objects": cls.total_referenced_objects(),
            "document_objects": cls.document_objects(),
        }
        cls.is_loaded = True

    @classmethod
    def total_document_informations(cls):
        file = tool.Ifc.get()
        info_count = len(file.by_type("IfcDocumentInformation"))
        return info_count

    @classmethod
    def total_document_references(cls):
        file = tool.Ifc.get()
        ref_count = len(file.by_type("IfcDocumentReference"))
        return ref_count

    @classmethod
    def total_referenced_objects(cls):
        file = tool.Ifc.get()
        document_rels = file.by_type("IfcRelAssociatesDocument")
        documented_objects = set()
        for rel in document_rels:
            for related_object in rel.RelatedObjects:
                obj = tool.Ifc.get_object(related_object)
                if obj:
                    documented_objects.add(related_object.id())

        return len(documented_objects)

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
        props = tool.Document.get_document_props()
        props.document_objects.clear()

        if "document_objects" not in cls.data or document_id not in cls.data["document_objects"]:
            return

        sorted_objects = sorted(cls.data["document_objects"][document_id], key=lambda x: x["name"].lower())

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

    @classmethod
    def documents(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return results
        for rel in getattr(element, "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesDocument"):
                is_information = rel.RelatingDocument.is_a("IfcDocumentInformation")
                is_reference = rel.RelatingDocument.is_a("IfcDocumentReference")

                if not (is_information or is_reference):
                    continue

                name = rel.RelatingDocument.Name

                location = None
                identification = None
                description = None

                if is_information:
                    if tool.Ifc.get_schema() == "IFC2X3":
                        identification = rel.RelatingDocument.DocumentId
                    else:
                        identification = rel.RelatingDocument.Identification

                    location = getattr(rel.RelatingDocument, "Location", None)

                else:
                    description = rel.RelatingDocument.Description
                    if tool.Ifc.get_schema() == "IFC2X3":
                        if not name and rel.RelatingDocument.ReferenceToDocument:
                            name = rel.RelatingDocument.ReferenceToDocument[0].Name

                        identification = rel.RelatingDocument.ItemReference
                        if not identification and rel.RelatingDocument.ReferenceToDocument:
                            identification = rel.RelatingDocument.ReferenceToDocument[0].DocumentId
                        location = rel.RelatingDocument.Location
                    else:
                        if not name and rel.RelatingDocument.ReferencedDocument:
                            name = rel.RelatingDocument.ReferencedDocument.Name

                        identification = rel.RelatingDocument.Identification
                        if not identification and rel.RelatingDocument.ReferencedDocument:
                            identification = rel.RelatingDocument.ReferencedDocument.Identification

                        location = rel.RelatingDocument.Location
                        if location is None and rel.RelatingDocument.ReferencedDocument:
                            location = rel.RelatingDocument.ReferencedDocument.Location

                if location:
                    if not "://" in location:
                        if not os.path.isabs(location):
                            location = os.path.abspath(os.path.join(os.path.dirname(tool.Ifc.get_path()), location))
                        location = "file://" + location

                results.append(
                    {
                        "id": rel.RelatingDocument.id(),
                        "identification": identification,
                        "name": name,
                        "location": location,
                        "is_information": is_information,
                        "description": description,
                    }
                )
        return results
