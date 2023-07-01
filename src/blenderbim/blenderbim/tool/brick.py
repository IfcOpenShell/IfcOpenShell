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

import os
import bpy
import ifcopenshell
import ifcopenshell.util.brick
import blenderbim.core.tool
import blenderbim.tool as tool

try:
    import brickschema
    import brickschema.persistent
    import urllib.parse
    from rdflib import Literal, URIRef, Namespace
    from rdflib.namespace import RDF
except:
    # See #1860
    print("Warning: brickschema not available.")

# silence known rdflib_sqlalchemy TypeError warning
# see https://github.com/BrickSchema/Brick/issues/513#issuecomment-1558493675
import logging
logger = logging.getLogger("rdflib")
logger.setLevel(logging.ERROR)

class Brick(blenderbim.core.tool.Brick):
    @classmethod
    def add_brick(cls, namespace, brick_class):
        ns = Namespace(namespace)
        brick = ns[ifcopenshell.guid.expand(ifcopenshell.guid.new())]
        with BrickStore.graph.new_changeset("PROJECT") as cs:
            cs.add((brick, RDF.type, URIRef(brick_class)))
            cs.add((brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Unnamed")))
        return str(brick)

    @classmethod
    def add_brick_breadcrumb(cls):
        new = bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add()
        new.name = bpy.context.scene.BIMBrickProperties.active_brick_class

    @classmethod
    def add_brick_from_element(cls, element, namespace, brick_class):
        ns = Namespace(namespace)
        brick = ns[element.GlobalId]
        BrickStore.graph.add((brick, RDF.type, URIRef(brick_class)))
        if element.Name:
            BrickStore.graph.add((brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(element.Name)))
        return str(brick)

    @classmethod
    def add_brickifc_project(cls, namespace):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        ns = Namespace(namespace)
        ns_brickifc = Namespace("https://brickschema.org/extension/ifc#")
        BrickStore.graph.bind("brickifc", ns_brickifc)
        brick_project = ns[project.GlobalId]
        BrickStore.graph.add((brick_project, RDF.type, ns_brickifc["Project"]))
        if project.Name:
            BrickStore.graph.add(
                (brick_project, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(project.Name))
            )
        BrickStore.graph.add((brick_project, ns_brickifc["projectID"], Literal(project.GlobalId)))
        BrickStore.graph.add(
            (brick_project, ns_brickifc["fileLocation"], Literal(bpy.context.scene.BIMProperties.ifc_file))
        )
        return str(brick_project)

    @classmethod
    def add_brickifc_reference(cls, brick, element, project):
        ns_brickifc = Namespace("https://brickschema.org/extension/ifc#")
        BrickStore.graph.bind("brickifc", ns_brickifc)
        BrickStore.graph.add(
            (
                URIRef(brick),
                ns_brickifc["hasIFCReference"],
                [
                    (ns_brickifc["hasProjectReference"], URIRef(project)),
                    (ns_brickifc["globalID"], Literal(element.GlobalId)),
                ],
            )
        )

    @classmethod
    def add_feed(cls, source, destination):
        ns_brick = Namespace("https://brickschema.org/schema/Brick#")
        BrickStore.graph.add((URIRef(source), ns_brick["feeds"], URIRef(destination)))

    @classmethod
    def clear_brick_browser(cls):
        bpy.context.scene.BIMBrickProperties.bricks.clear()

    @classmethod
    def clear_project(cls):
        BrickStore.purge()
        bpy.context.scene.BIMBrickProperties.active_brick_class == ""
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.clear()

    @classmethod
    def export_brick_attributes(cls, brick_uri):
        if tool.Ifc.get_schema() == "IFC2X3":
            return {"ItemReference": brick_uri, "Name": brick_uri.split("#")[-1]}
        else:
            return {"Identification": brick_uri, "Name": brick_uri.split("#")[-1]}

    @classmethod
    def get_active_brick_class(cls):
        return bpy.context.scene.BIMBrickProperties.active_brick_class

    @classmethod
    def get_brick(cls, element):
        for rel in element.HasAssociations:
            if rel.is_a("IfcRelAssociatesLibrary"):
                if tool.Ifc.get_schema() == "IFC2X3" and "#" in rel.RelatingLibrary.ItemReference:
                    return rel.RelatingLibrary.ItemReference
                if tool.Ifc.get_schema() != "IFC2X3" and "#" in rel.RelatingLibrary.Identification:
                    return rel.RelatingLibrary.Identification

    @classmethod
    def get_brick_class(cls, element):
        return ifcopenshell.util.brick.get_brick_type(element)

    @classmethod
    def get_brick_path(cls):
        return BrickStore.path

    @classmethod
    def get_brick_path_name(cls):
        if BrickStore.path:
            return os.path.basename(BrickStore.path)
        return "Unnamed"

    @classmethod
    def get_brickifc_project(cls):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        query = BrickStore.graph.query(
            """
            PREFIX brickifc: <https://brickschema.org/extension/ifc#>
            SELECT ?proj WHERE {
                ?proj a brickifc:Project .
                ?proj brickifc:projectID "{project_globalid}"
            }
            LIMIT 1
        """.replace(
                "{project_globalid}", project.GlobalId
            )
        )
        results = list(query)
        if results:
            return results[0][0].toPython()

    @classmethod
    def get_convertable_brick_elements(cls):
        return ifcopenshell.util.brick.get_brick_elements(tool.Ifc.get())

    @classmethod
    def get_item_class(cls, item):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            SELECT ?class WHERE {
               <{item}> a ?class .
            }
            LIMIT 1
        """.replace(
                "{item}", item
            )
        )
        for row in query:
            return row.get("class").toPython().split("#")[-1]

    @classmethod
    def get_library_brick_reference(cls, library, brick_uri):
        if tool.Ifc.get_schema() == "IFC2X3":
            for reference in library.LibraryReference or []:
                if reference.ItemReference == brick_uri:
                    return reference
        else:
            for reference in library.HasLibraryReferences or []:
                if reference.Identification == brick_uri:
                    return reference

    @classmethod
    def get_namespace(cls, uri):
        return uri.split("#")[0] + "#"

    @classmethod
    def import_brick_classes(cls, brick_class):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?group (count(?item) as ?total_items) ?label WHERE {
                ?group rdfs:subClassOf brick:{brick_class} .
                ?item rdf:type/rdfs:subClassOf* ?group .
                OPTIONAL {
                    ?group rdfs:label ?label
                }
            }
            GROUP BY ?group
            ORDER BY asc(?group)
        """.replace(
                "{brick_class}", brick_class
            )
        )
        for row in query:
            new = bpy.context.scene.BIMBrickProperties.bricks.add()
            label = row.get("label")
            if label:
                new.label = label.toPython()
            new.name = row.get("group").toPython().split("#")[-1]
            new.uri = row.get("group").toPython()
            new.total_items = row.get("total_items").toPython()

    @classmethod
    def import_brick_items(cls, brick_class):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?item ?label WHERE {
                ?item rdf:type brick:{brick_class} .
                OPTIONAL {
                    ?item rdfs:label ?label
                }
            }
            ORDER BY asc(?item)
        """.replace(
                "{brick_class}", brick_class
            )
        )
        for row in query:
            new = bpy.context.scene.BIMBrickProperties.bricks.add()
            label = row.get("label")
            if label:
                new.label = label.toPython()
            new.name = row.get("item").toPython().split("#")[-1]
            new.uri = row.get("item").toPython()

    @classmethod
    def load_brick_file(cls, filepath):
        if not BrickStore.schema: # important check for running under test cases
            cwd = os.path.dirname(os.path.realpath(__file__))
            BrickStore.schema = os.path.join(cwd, "..", "bim", "schema", "Brick.ttl")
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        with BrickStore.graph.new_changeset("SCHEMA") as cs:
            cs.load_file(BrickStore.schema)
        with BrickStore.graph.new_changeset("PROJECT") as cs:
            cs.load_file(filepath)
        BrickStore.path = filepath

    @classmethod
    def new_brick_file(cls):
        if not BrickStore.schema: # important check for running under test cases
            cwd = os.path.dirname(os.path.realpath(__file__))
            BrickStore.schema = os.path.join(cwd, "..", "bim", "schema", "Brick.ttl")
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        with BrickStore.graph.new_changeset("SCHEMA") as cs:
            cs.load_file(BrickStore.schema)
        BrickStore.graph.bind("digitaltwin", Namespace("https://example.org/digitaltwin#"))
        BrickStore.graph.bind("brick", Namespace("https://brickschema.org/schema/Brick#"))
        BrickStore.graph.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))

    @classmethod
    def pop_brick_breadcrumb(cls):
        crumb = bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[-1]
        name = crumb.name
        last_index = len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) - 1
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.remove(last_index)
        return name

    @classmethod
    def remove_brick(cls, brick_uri):
        if(BrickStore.graph.triples((URIRef(brick_uri), None, None))):
            with BrickStore.graph.new_changeset("PROJECT") as cs:
                for triple in BrickStore.graph.triples((URIRef(brick_uri), None, None)):
                    cs.remove(triple)

    @classmethod
    def run_assign_brick_reference(cls, element=None, library=None, brick_uri=None):
        return blenderbim.core.brick.assign_brick_reference(
            tool.Ifc, tool.Brick, element=element, library=library, brick_uri=brick_uri
        )

    @classmethod
    def run_refresh_brick_viewer(cls):
        return blenderbim.core.brick.refresh_brick_viewer(tool.Brick)

    @classmethod
    def run_view_brick_class(cls, brick_class=None):
        return blenderbim.core.brick.view_brick_class(tool.Brick, brick_class=brick_class)

    @classmethod
    def select_browser_item(cls, item):
        name = item.split("#")[-1]
        props = bpy.context.scene.BIMBrickProperties
        props.active_brick_index = props.bricks.find(name)

    @classmethod
    def set_active_brick_class(cls, brick_class):
        bpy.context.scene.BIMBrickProperties.active_brick_class = brick_class

    @classmethod
    def undo_brick(cls):
        if(len(BrickStore.graph.versions()) > 1):
            BrickStore.graph.undo()

    @classmethod
    def redo_brick(cls):
        with BrickStore.graph.conn() as conn:
            redo_record = conn.execute(
            "SELECT * from redos " "ORDER BY timestamp ASC LIMIT 1"
            ).fetchone()
        if redo_record is not None:
            BrickStore.graph.redo()  

    @classmethod
    def serialize_brick(cls):
        print(BrickStore.path)
        BrickStore.get_project().serialize(destination=BrickStore.path, format="turtle")
        
class BrickStore:
    schema = None # this is now a os path
    path = None   # file path if the project was loaded in
    graph = None  # this is the VersionedGraphCollection with 2 arbitrarily named graphs: "schema" and "project"
                  # "SCHEMA" holds the Brick.ttl metadata; "PROJECT" holds all the authored entities
    
    @staticmethod
    def purge():
        BrickStore.schema = None
        BrickStore.graph = None
        BrickStore.path = None   

    @classmethod
    def get_project(cls):
        return BrickStore.graph.graph_at(graph="PROJECT")