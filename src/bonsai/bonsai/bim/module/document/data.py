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
            "total_information": cls.total_information(),
            "parent_document": cls.parent_document(),
        }
        cls.is_loaded = True

    @classmethod
    def total_information(cls):
        return len(
            [
                rel
                for rel in tool.Ifc.get().by_type("IfcProject")[0].HasAssociations or []
                if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument.is_a("IfcDocumentInformation")
            ]
        )

    @classmethod
    def parent_document(cls):
        props = bpy.context.scene.BIMDocumentProperties
        if len(props.breadcrumbs):
            parent = tool.Ifc.get().by_id(int(props.breadcrumbs[-1].name))
            if tool.Ifc.get_schema() == "IFC2X3":
                return str(parent.DocumentId)
            return str(parent.Identification)
        return ""


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
                if not rel.RelatingDocument.is_a("IfcDocumentReference"):
                    continue

                name = rel.RelatingDocument.Name

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
                    }
                )
        return results
