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

from __future__ import annotations
import os
import bpy
import datetime
import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.util.brick
import ifcopenshell.util.element
import ifcopenshell.util.system
import bonsai.core.brick
import bonsai.core.tool
import bonsai.tool as tool
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Any, Union, TYPE_CHECKING

try:
    import brickschema
    import brickschema.persistent
    from brickschema.namespaces import REF, A
    import urllib.parse
    from rdflib import Literal, URIRef, Namespace, BNode
    from rdflib.namespace import RDF
except:
    # See #1860
    print("Warning: brickschema not available.")

if TYPE_CHECKING:
    import brickschema
    from rdflib import Literal, URIRef, Namespace, BNode
    from bonsai.bim.module.brick.prop import BIMBrickProperties

# silence known rdflib_sqlalchemy TypeError warning
# see https://github.com/BrickSchema/Brick/issues/513#issuecomment-1558493675
import logging

logger = logging.getLogger("rdflib")
logger.setLevel(logging.ERROR)


class Brick(bonsai.core.tool.Brick):
    @classmethod
    def get_brick_props(cls) -> BIMBrickProperties:
        return bpy.context.scene.BIMBrickProperties

    @classmethod
    def add_brick(cls, namespace: str, brick_class: str, label: str) -> str:
        ns = Namespace(namespace)
        brick = ns[ifcopenshell.guid.expand(ifcopenshell.guid.new())]
        with BrickStore.new_changeset() as cs:
            cs.add((brick, A, URIRef(brick_class)))
            cs.add((brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(label)))
        return str(brick)

    @classmethod
    def add_brick_breadcrumb(cls, split_screen: bool = False) -> None:
        props = tool.Brick.get_brick_props()
        if split_screen:
            new = props.split_screen_brick_breadcrumbs.add()
            new.name = props.split_screen_active_brick_class
        else:
            new = props.brick_breadcrumbs.add()
            new.name = props.active_brick_class

    @classmethod
    def add_brick_from_element(cls, element: ifcopenshell.entity_instance, namespace: str, brick_class: str) -> str:
        ns = Namespace(namespace)
        brick = ns[element.GlobalId]
        with BrickStore.new_changeset() as cs:
            cs.add((brick, A, URIRef(brick_class)))
            if element.Name:
                cs.add((brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(element.Name)))
            else:
                cs.add((brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Unnamed")))
        return str(brick)

    @classmethod
    def add_brickifc_project(cls, namespace: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        ns = Namespace(namespace)
        brick_project = ns[project.GlobalId]
        props = tool.Blender.get_bim_props()
        with BrickStore.new_changeset() as cs:
            cs.add((brick_project, A, REF.ifcProject))
            cs.add((brick_project, REF.ifcProjectID, Literal(project.GlobalId)))
            cs.add((brick_project, REF.ifcFileLocation, Literal(props.ifc_file)))
            if project.Name:
                cs.add((brick_project, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal(project.Name)))
        return str(brick_project)

    @classmethod
    def add_brickifc_reference(cls, brick: str, element: ifcopenshell.entity_instance, project: str) -> None:
        with BrickStore.new_changeset() as cs:
            bnode = BNode()
            cs.add((URIRef(brick), REF.hasExternalReference, bnode))
            cs.add((bnode, A, REF.IFCReference))
            cs.add((bnode, REF.hasIfcProjectReference, URIRef(project)))
            cs.add((bnode, REF.ifcGlobalID, Literal(element.GlobalId)))
            if element.Name:
                cs.add((bnode, REF.ifcName, Literal(element.Name)))

    @classmethod
    def add_relation(cls, brick_uri: str, predicate: str, object: str) -> None:
        props = tool.Brick.get_brick_props()
        if predicate == "http://www.w3.org/2000/01/rdf-schema#label":
            with BrickStore.new_changeset() as cs:
                cs.add((URIRef(brick_uri), URIRef(predicate), Literal(object)))
            props.new_brick_relation_type = BrickStore.relationships[0]
            props.add_brick_relation_failed = False
            return
        query = BrickStore.graph.query("ASK { <{object_uri}> a ?o . }".replace("{object_uri}", object))
        if query:
            with BrickStore.new_changeset() as cs:
                cs.add((URIRef(brick_uri), URIRef(predicate), URIRef(object)))
            props.add_brick_relation_failed = False
        else:
            props.add_brick_relation_failed = True

    @classmethod
    def remove_relation(cls, brick_uri: str, predicate: str, object: str) -> None:
        with BrickStore.new_changeset() as cs:
            for s, p, o in BrickStore.graph.triples((brick_uri, predicate, object)):
                cs.remove((s, p, o))
                if isinstance(o, BNode):
                    for triple in BrickStore.graph.triples((object, None, None)):
                        cs.remove(triple)

    @classmethod
    def clear_brick_browser(cls, split_screen: bool = False) -> None:
        props = cls.get_brick_props()
        if split_screen:
            props.split_screen_bricks.clear()
        else:
            props.bricks.clear()

    @classmethod
    def clear_project(cls) -> None:
        BrickStore.purge()
        props = cls.get_brick_props()
        props.active_brick_class = ""
        props.split_screen_active_brick_class = ""

    @classmethod
    def export_brick_attributes(cls, brick_uri: str) -> dict[str, Any]:
        query = BrickStore.graph.query(
            """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label {
                <{brick_uri}> rdfs:label ?label .
            }
            LIMIT 1
        """.replace(
                "{brick_uri}", brick_uri
            )
        )
        name = None
        for row in query:
            name = str(row.get("label"))
        if not name:
            name = brick_uri.split("#")[-1]
        if tool.Ifc.get_schema() == "IFC2X3":
            return {"ItemReference": brick_uri, "Name": name}
        else:
            return {"Identification": brick_uri, "Name": name}

    @classmethod
    def get_active_brick_class(cls, split_screen: bool = False) -> str:
        props = cls.get_brick_props()
        if split_screen:
            return props.split_screen_active_brick_class
        return props.active_brick_class

    @classmethod
    def get_brick(cls, element: ifcopenshell.entity_instance) -> Union[str, None]:
        for rel in element.HasAssociations:
            if rel.is_a("IfcRelAssociatesLibrary"):
                if tool.Ifc.get_schema() == "IFC2X3" and "#" in rel.RelatingLibrary.ItemReference:
                    return rel.RelatingLibrary.ItemReference
                if tool.Ifc.get_schema() != "IFC2X3" and "#" in rel.RelatingLibrary.Identification:
                    return rel.RelatingLibrary.Identification

    @classmethod
    def get_brick_class(cls, element: ifcopenshell.entity_instance) -> Union[str, None]:
        return ifcopenshell.util.brick.get_brick_type(element)

    @classmethod
    def get_brick_path(cls) -> Union[str, None]:
        return BrickStore.path

    @classmethod
    def get_brick_path_name(cls) -> str:
        if BrickStore.path:
            return os.path.basename(BrickStore.path)
        return "Unnamed"

    @classmethod
    def get_brickifc_project(cls) -> Union[str, None]:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        query = BrickStore.graph.query(
            """
            PREFIX ref: <https://brickschema.org/schema/Brick/ref#>
            SELECT ?proj WHERE {
                ?proj a ref:ifcProject .
                ?proj ref:ifcProjectID "{project_globalid}" .
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
    def get_convertable_brick_elements(cls) -> set[ifcopenshell.entity_instance]:
        equipment = set(tool.Ifc.get().by_type("IfcDistributionElement"))
        equipment -= set(tool.Ifc.get().by_type("IfcFlowSegment"))
        equipment -= set(tool.Ifc.get().by_type("IfcFlowFitting"))
        return equipment

    @classmethod
    def get_convertable_brick_spaces(cls) -> set[ifcopenshell.entity_instance]:
        if tool.Ifc.get_schema() == "IFC2X3":
            return set(tool.Ifc.get().by_type("IfcSpatialStructureElement"))
        return set(tool.Ifc.get().by_type("IfcSpatialElement"))

    @classmethod
    def get_convertable_brick_systems(cls) -> set[ifcopenshell.entity_instance]:
        systems = set(tool.Ifc.get().by_type("IfcSystem"))
        systems -= set(tool.Ifc.get().by_type("IfcStructuralAnalysisModel"))
        systems -= set(tool.Ifc.get().by_type("IfcZone"))
        return systems

    @classmethod
    def get_parent_space(cls, space: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        element = ifcopenshell.util.element.get_aggregate(space)
        assert element
        if not element.is_a("IfcProject"):
            return element

    @classmethod
    def get_element_container(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_element_systems(cls, element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.system.get_element_systems(element)

    @classmethod
    def get_element_feeds(cls, element: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        return ifcopenshell.util.brick.get_element_feeds(element)

    @classmethod
    def get_item_class(cls, item: str) -> Union[str, None]:
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
    def get_library_brick_reference(
        cls, library: ifcopenshell.entity_instance, brick_uri: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        if tool.Ifc.get_schema() == "IFC2X3":
            for reference in library.LibraryReference or []:
                if reference.ItemReference == brick_uri:
                    return reference
        else:
            for reference in library.HasLibraryReferences or []:
                if reference.Identification == brick_uri:
                    return reference

    @classmethod
    def get_namespace(cls, uri: str) -> str:
        return uri.split("#")[0] + "#"

    @classmethod
    def import_brick_classes(cls, brick_class: str, split_screen: bool = False) -> None:
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
        props = tool.Brick.get_brick_props()
        if split_screen:
            bricks = props.split_screen_bricks
        else:
            bricks = props.bricks
        for row in query:
            new = bricks.add()
            label = row.get("label")
            if label:
                new.label = label.toPython()
            new.name = row.get("group").toPython().split("#")[-1]
            new.uri = row.get("group").toPython()
            new.total_items = row.get("total_items").toPython()

    @classmethod
    def import_brick_items(cls, brick_class: str, split_screen: bool = False) -> None:
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
        props = tool.Brick.get_brick_props()
        if split_screen:
            bricks = props.split_screen_bricks
        else:
            bricks = props.bricks
        for row in query:
            new = bricks.add()
            label = row.get("label")
            if label:
                new.label = label.toPython()
            new.name = row.get("item").toPython().split("#")[-1]
            new.uri = row.get("item").toPython()

    @classmethod
    def load_brick_file(cls, filepath: str) -> None:
        if not BrickStore.schema:  # important check for running under test cases
            BrickStore.schema = tool.Blender.get_data_dir_path(Path("brick", "Brick.ttl"))
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        with BrickStore.graph.new_changeset("SCHEMA") as cs:
            cs.load_file(BrickStore.schema)
        with BrickStore.graph.new_changeset("PROJECT") as cs:
            cs.load_file(filepath)
        BrickStore.path = filepath
        BrickStore.set_last_saved()
        BrickStore.load_sub_roots()
        BrickStore.load_namespaces()
        BrickStore.load_entity_classes()
        BrickStore.load_relationships()

    @classmethod
    def new_brick_file(cls) -> None:
        if not BrickStore.schema:  # important check for running under test cases
            BrickStore.schema = tool.Blender.get_data_dir_path(Path("brick", "Brick.ttl"))
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        with BrickStore.graph.new_changeset("SCHEMA") as cs:
            cs.load_file(BrickStore.schema)
        BrickStore.graph.bind("digitaltwin", Namespace("https://example.org/digitaltwin#"))
        BrickStore.load_sub_roots()
        BrickStore.load_namespaces()
        BrickStore.load_entity_classes()
        BrickStore.load_relationships()

    @classmethod
    def pop_brick_breadcrumb(cls, split_screen: bool = False) -> str:
        props = cls.get_brick_props()
        if split_screen:
            breadcrumbs = props.split_screen_brick_breadcrumbs
        else:
            breadcrumbs = props.brick_breadcrumbs
        crumb = breadcrumbs[-1]
        name = crumb.name
        last_index = len(breadcrumbs) - 1
        breadcrumbs.remove(last_index)
        return name

    @classmethod
    def remove_brick(cls, brick_uri: str) -> None:
        with BrickStore.new_changeset() as cs:
            for s, p, o in BrickStore.graph.triples((URIRef(brick_uri), None, None)):
                cs.remove((s, p, o))
                if isinstance(o, BNode):
                    for triple in BrickStore.graph.triples((o, None, None)):
                        cs.remove(triple)

    @classmethod
    def run_assign_brick_reference(cls, element=None, library=None, brick_uri=None):
        return bonsai.core.brick.assign_brick_reference(
            tool.Ifc, tool.Brick, element=element, library=library, brick_uri=brick_uri
        )

    @classmethod
    def run_refresh_brick_viewer(cls) -> None:
        return bonsai.core.brick.refresh_brick_viewer(tool.Brick)

    @classmethod
    def run_view_brick_class(cls, brick_class: Union[str, None] = None, split_screen: bool = False) -> None:
        return bonsai.core.brick.view_brick_class(tool.Brick, brick_class=brick_class, split_screen=split_screen)

    @classmethod
    def select_browser_item(cls, item: str, split_screen: bool = False) -> None:
        name = item.split("#")[-1]
        props = cls.get_brick_props()
        if split_screen:
            props.split_screen_active_brick_index = props.split_screen_bricks.find(name)
        else:
            props.active_brick_index = props.bricks.find(name)

    @classmethod
    def set_active_brick_class(cls, brick_class: str, split_screen: bool = False) -> None:
        props = cls.get_brick_props()
        if split_screen:
            props.split_screen_active_brick_class = brick_class
        else:
            props.active_brick_class = brick_class

    @classmethod
    def serialize_brick(cls) -> None:
        BrickStore.get_project().serialize(destination=BrickStore.path, format="turtle")
        BrickStore.set_last_saved()

    @classmethod
    def add_namespace(cls, alias: str, uri: str) -> None:
        assert BrickStore.graph
        BrickStore.graph.bind(alias, Namespace(uri))
        BrickStore.load_namespaces()

    @classmethod
    def clear_breadcrumbs(cls, split_screen: bool = False) -> None:
        props = cls.get_brick_props()
        if split_screen:
            props.split_screen_brick_breadcrumbs.clear()
        else:
            props.brick_breadcrumbs.clear()


class BrickStore:
    schema = None  # this is now a os path
    path: Union[str, None]
    path = None  # file path if the project was loaded in
    graph: Union[brickschema.persistent.VersionedGraphCollection, None]
    graph = None  # this is the VersionedGraphCollection with 2 arbitrarily named graphs: "schema" and "project"
    # "SCHEMA" holds the Brick.ttl metadata; "PROJECT" holds all the authored entities
    last_saved = None
    history = []
    future = []
    current_changesets = 0
    history_size = 64
    namespaces = []
    root_classes = ["Equipment", "Location", "System", "Point"]
    entity_classes = {}
    relationships = []

    @staticmethod
    def purge():
        BrickStore.schema = None
        BrickStore.graph = None
        BrickStore.path = None
        BrickStore.last_saved = None
        BrickStore.namespaces = []
        BrickStore.root_classes = ["Equipment", "Location", "System", "Point"]
        BrickStore.entity_classes = {}
        BrickStore.relationships = []

    @classmethod
    def get_project(cls) -> brickschema.graph.Graph:
        return BrickStore.graph.graph_at(graph="PROJECT")

    @classmethod
    def load_sub_roots(cls) -> None:
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?subRoot ?subClasses WHERE {
                {
                SELECT ?subRoot (COUNT(?subClass) as ?subClasses) WHERE {
                    {
                        ?subRoot rdfs:subClassOf brick:Equipment .
                    } UNION {
                        ?subRoot rdfs:subClassOf brick:Point .
                    }
                    ?subClass rdfs:subClassOf* ?subRoot .
                }
                GROUP BY ?subRoot
                }
            FILTER(?subClasses > 3)
            }
            """
        )
        for row in query:
            sub_root = row.get("subRoot").toPython().split("#")[-1]
            BrickStore.root_classes.append(sub_root)

    @classmethod
    def load_namespaces(cls) -> None:
        BrickStore.namespaces = []
        keyword_filter = [
            "brickschema.org",
            "schema.org",
            "w3.org",
            "purl.org",
            "rdfs.org",
            "qudt.org",
            "ashrae.org",
            "usefulinc.com",
            "xmlns.com",
            "opengis.net",
        ]
        for alias, uri in BrickStore.graph.namespaces():
            ignore_namespace = False
            for keyword in keyword_filter:
                if keyword in str(uri):
                    ignore_namespace = True
                    break
            if not ignore_namespace:
                BrickStore.namespaces.append((alias, str(uri)))

    @classmethod
    def load_entity_classes(cls) -> None:
        for root_class in BrickStore.root_classes:
            query = BrickStore.graph.query(
                """
                PREFIX brick: <https://brickschema.org/schema/Brick#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                SELECT ?class WHERE {
                    ?class rdfs:subClassOf* brick:{root_class} .
                    FILTER NOT EXISTS {
                        ?class owl:deprecated true .
                    }
                }
            """.replace(
                    "{root_class}", root_class
                )
            )
            BrickStore.entity_classes[root_class] = []
            for uri in sorted([x[0].toPython() for x in query]):
                BrickStore.entity_classes[root_class].append(uri)

    @classmethod
    def load_relationships(cls) -> None:
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?relation WHERE {
                ?relation rdfs:subPropertyOf brick:Relationship .
            }
            """
        )
        for uri in sorted([x[0].toPython() for x in query]):
            BrickStore.relationships.append(uri)

    @classmethod
    def set_history_size(cls, size: int) -> None:
        cls.history_size = size
        while len(cls.history) > cls.history_size:
            cls.history.pop(0)

    @classmethod
    def begin_transaction(cls) -> None:
        cls.current_changesets = 0

    @classmethod
    def end_transaction(cls) -> None:
        cls.history.append(cls.current_changesets)
        if len(cls.history) > cls.history_size:
            cls.history.pop(0)

    @classmethod
    @contextmanager
    def new_changeset(cls) -> Generator[Any, None, None]:
        cls.current_changesets += 1
        with BrickStore.graph.new_changeset("PROJECT") as cs:
            yield cs

    @classmethod
    def undo(cls) -> None:
        if not BrickStore.graph or not BrickStore.history:
            return
        total_changesets = BrickStore.history.pop()
        for i in range(0, total_changesets):
            BrickStore.graph.undo()
        BrickStore.future.append(total_changesets)

    @classmethod
    def redo(cls) -> None:
        if not BrickStore.graph or not BrickStore.future:
            return
        total_changesets = BrickStore.future.pop()
        for i in range(0, total_changesets):
            BrickStore.graph.redo()
        BrickStore.history.append(total_changesets)

    @classmethod
    def set_last_saved(cls) -> None:
        save = os.path.getmtime(BrickStore.path)
        save = datetime.datetime.fromtimestamp(save)
        BrickStore.last_saved = f"{save.year}-{save.month}-{save.day} {save.hour}:{save.minute}"
