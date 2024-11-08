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
from bonsai.tool.brick import BrickStore

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
            "active_relations": cls.active_relations(),
        }

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None  # `if BrickStore.graph` by itself takes ages.

    @classmethod
    def active_relations(cls):
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
            SELECT DISTINCT ?predicate ?object ?label ?sp ?sv  WHERE {
                <{uri}> ?predicate ?object .
                OPTIONAL {
                    ?object rdfs:label ?label . 
                }
                OPTIONAL {
                    { ?predicate rdfs:range brick:TimeseriesReference . }
                    UNION
                    { ?predicate a brick:EntityProperty . }
                    ?object ?sp ?sv .
                }
            }
            GROUP BY ?object
        """.replace(
                "{uri}", uri
            )
        )
        for row in query:
            predicate_uri = row.get("predicate")
            predicate_name = predicate_uri.toPython().split("#")[-1]
            object_uri = row.get("object")
            object_name = row.get("label")
            if not object_name:
                if isinstance(object_uri, BNode):
                    object_name = "[]"
                else:
                    try:
                        object_name = object_uri.toPython().split("#")[-1]
                    except:
                        object_name = str(object_uri)
            results.append(
                {
                    "predicate_uri": predicate_uri,
                    "predicate_name": predicate_name,
                    "object_uri": object_uri,
                    "object_name": object_name,
                    "is_uri": isinstance(object_uri, URIRef),
                    "is_globalid": predicate_name == "ifcGlobalID",
                }
            )
            if isinstance(object_uri, BNode):
                for subject2, predicate2, object2 in BrickStore.graph.triples((object_uri, None, None)):
                    predicate2_name = predicate2.toPython().split("#")[-1]
                    try:
                        object2_name = object2.toPython().split("#")[-1]
                    except:
                        object2_name = str(object2)
                    results.append(
                        {
                            "predicate_uri": None,
                            "predicate_name": predicate_name + ":" + predicate2_name,
                            "object_uri": object2,
                            "object_name": object2_name,
                            "is_uri": isinstance(object2, URIRef),
                            "is_globalid": predicate2_name == "ifcGlobalID",
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
            elif library.Location and ".ttl" in library.Location:
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
                        "identification": (
                            reference.ItemReference if tool.Ifc.get_schema() == "IFC2X3" else reference.Identification
                        ),
                        "name": reference.Name or "Unnamed",
                    }
                )
        return results
