# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


def refresh():
    LibrariesData.is_loaded = False
    LibraryReferencesData.is_loaded = False


class LibrariesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "libraries": cls.libraries(),
            "library_attributes": cls.library_attributes(),
            "reference_attributes": cls.reference_attributes(),
        }

    @classmethod
    def libraries(cls):
        results = []
        for library in tool.Ifc.get().by_type("IfcLibraryInformation"):
            results.append({"id": library.id(), "name": library.Name})
        return results

    @classmethod
    def library_attributes(cls):
        library_id = bpy.context.scene.BIMLibraryProperties.active_library_id
        if not library_id:
            return []
        results = []
        data = tool.Ifc.get().by_id(library_id).get_info()
        if tool.Ifc.get_schema() == "IFC2X3":
            del data["VersionDate"]
        for key, value in data.items():
            if key in ["id", "type"]:
                continue
            if value is not None:
                results.append({"name": key, "value": str(value)})
        return results

    @classmethod
    def reference_attributes(cls):
        props = bpy.context.scene.BIMLibraryProperties
        try:
            reference_id = props.references[props.active_reference_index].ifc_definition_id
        except:
            return []
        if not reference_id:
            return []
        results = []
        data = tool.Ifc.get().by_id(reference_id).get_info()
        del data["ReferencedLibrary"]
        for key, value in data.items():
            if key in ["id", "type"]:
                continue
            if value is not None:
                results.append({"name": key, "value": str(value)})
        return results


class LibraryReferencesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "references": cls.references(),
        }

    @classmethod
    def references(cls):
        results = []
        for rel in getattr(tool.Ifc.get_entity(bpy.context.active_object), "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesLibrary"):
                library = rel.RelatingLibrary
                results.append(
                    {
                        "id": library.id(),
                        "identification": (
                            library.ItemReference if tool.Ifc.get_schema() == "IFC2X3" else library.Identification
                        ),
                        "name": library.Name or "Unnamed",
                    }
                )
        return results
