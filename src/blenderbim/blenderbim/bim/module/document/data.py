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
import ifcopenshell
import ifcopenshell.util.schema
import blenderbim.tool as tool


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
            "total_references": cls.total_references(),
        }
        cls.is_loaded = True

    @classmethod
    def total_information(cls):
        return len(tool.Ifc.get().by_type("IfcDocumentInformation"))

    @classmethod
    def total_references(cls):
        return len(tool.Ifc.get().by_type("IfcDocumentReference"))


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
                if tool.Ifc.get_schema() == "IFC2X3":
                    identification = rel.RelatingDocument.ItemReference
                else:
                    identification = rel.RelatingDocument.Identification
                results.append(
                    {
                        "type": rel.RelatingDocument.is_a(),
                        "id": rel.RelatingDocument.id(),
                        "identification": identification,
                        "name": rel.RelatingDocument.Name,
                    }
                )
        return results
