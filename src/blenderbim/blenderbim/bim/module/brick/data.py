# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool
from blenderbim.tool.brick import BrickStore

try:
    from rdflib import URIRef, BNode
except:
    # See #1860
    print("Warning: brickschema not available.")


def refresh():
    BrickschemaData.is_loaded = False
    BrickschemaReferencesData.is_loaded = False


class BrickschemaData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "is_loaded": cls.get_is_loaded(),
            "attributes": cls.attributes(),
        }

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None

    @classmethod
    def attributes(cls):
        if BrickStore.graph is None:
            return []
        props = bpy.context.scene.BIMBrickProperties
        try:
            brick = props.bricks[props.active_brick_index]
        except:
            return []
        uri = brick.uri
        namespace = str(uri.split("#")[0])
        if namespace == "https://brickschema.org/schema/Brick":
            return []
        results = []
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT ?predicate ?object ?sp ?sv WHERE {
               <{uri}> ?predicate ?object .
               OPTIONAL {
               { ?predicate rdfs:range brick:TimeseriesReference . }
                UNION
               { ?predicate a brick:EntityProperty . }
                ?object ?sp ?sv }
            }
        """.replace(
                "{uri}", uri
            )
        )
        for row in query:
            predicate = row.get("predicate").toPython().split("#")[-1]
            object = row.get("object")
            results.append(
                {
                    "predicate": predicate,
                    "object": object.toPython().split("#")[-1],
                    "is_uri": isinstance(object, URIRef),
                    "object_uri": object.toPython(),
                    "is_globalid": predicate == "globalID",
                }
            )
            if isinstance(row.get("object"), BNode):
                for s, p, o in BrickStore.graph.triples((object, None, None)):
                    results.append(
                        {
                            "predicate": predicate + ":" + p.toPython().split("#")[-1],
                            "object": o.toPython().split("#")[-1],
                            "is_uri": isinstance(o, URIRef),
                            "object_uri": o.toPython(),
                            "is_globalid": p.toPython().split("#")[-1] == "globalID",
                        }
                    )
        return results


class BrickschemaReferencesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"is_loaded": cls.get_is_loaded(), "libraries": cls.libraries(), "references": cls.references()}

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None

    @classmethod
    def libraries(cls):
        results = []
        ifc = tool.Ifc.get()
        if not ifc:
            return results
        for library in ifc.by_type("IfcLibraryInformation"):
            if tool.Ifc.get_schema() == "IFC2X3":
                results.append((str(library.id()), library.Name or "Unnamed", ""))
            elif ".ttl" in library.Location:
                results.append((str(library.id()), library.Name or "Unnamed", ""))
        return results

    @classmethod
    def references(cls):
        results = []
        for rel in getattr(tool.Ifc.get_entity(bpy.context.active_object), "HasAssociations", []):
            if rel.is_a("IfcRelAssociatesLibrary"):
                reference = rel.RelatingLibrary
                if tool.Ifc.get_schema() == "IFC2X3" and "#" not in reference.ItemReference:
                    continue
                if tool.Ifc.get_schema() != "IFC2X3" and "#" not in reference.Identification:
                    continue
                results.append(
                    {
                        "id": reference.id(),
                        "identification": reference.ItemReference
                        if tool.Ifc.get_schema() == "IFC2X3"
                        else reference.Identification,
                        "name": reference.Name or "Unnamed",
                    }
                )
        return results
