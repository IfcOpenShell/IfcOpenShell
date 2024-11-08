# The code in this file originally comes from the following article:
#
# IFC-graph for facilitating building information access and query
#
# Junxiang Zhu, Peng Wu *, Xiang Lei
#
# School of Design and the Built Environment, Curtin University,
# Bentley 6102, Western Australia, Australia
#
# The article was made available online 13 February 2023 in the journal
# Automation in Construction 148 (2023) 104778
#
# 0926-5805/© 2023 The Authors.
# Published by Elsevier B.V.
#
# This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).
#
# Some modifications have been made to the code.
#

from py2neo.data import Node, Relationship
from uuid import uuid4
import ifcopenshell
import ifcopenshell.util.schema
from py2neo import Graph


# Create the basic node with literal attributes and the class hierarchy
def create_pure_node_from_ifc_entity(ifc_entity, ifc_file, hierarchy=True):
    node = Node()
    if ifc_entity.id() != 0:
        node["id"] = ifc_entity.id()
    else:
        node["id"] = str(uuid4())
    node["name"] = ifc_entity.is_a()
    if hierarchy:
        node.add_label(ifc_entity.is_a())
        declaration = ifcopenshell.util.schema.get_declaration(ifc_entity)
        for supertype in ifcopenshell.util.schema.get_supertypes(declaration):
            node.add_label(supertype.name())
    else:
        node.add_label(ifc_entity.is_a())
    attributes_type = ["ENTITY INSTANCE", "AGGREGATE OF ENTITY INSTANCE", "DERIVED"]
    for i in range(ifc_entity.__len__()):
        if not ifc_entity.wrapped_data.get_argument_type(i) in attributes_type:
            name = ifc_entity.wrapped_data.get_argument_name(i)
            name_value = ifc_entity.wrapped_data.get_argument(i)
            node[name] = name_value
    node.__primarylabel__ = "Root"
    node.__primarykey__ = "id"
    return node


# Process literal attributes, entity attributes, and relationship attributes
def create_graph_from_ifc_entity_all(graph, ifc_entity, ifc_file):
    node = create_pure_node_from_ifc_entity(ifc_entity, ifc_file)
    graph.merge(node)
    for i in range(ifc_entity.__len__()):
        if ifc_entity[i]:
            if ifc_entity.wrapped_data.get_argument_type(i) == "ENTITY INSTANCE":
                if ifc_entity[i].is_a() in ["IfcOwnerHistory"] and ifc_entity.is_a() != "IfcProject":
                    continue
                else:
                    sub_node = create_pure_node_from_ifc_entity(ifc_entity[i], ifc_file)
                    REL = Relationship(node, ifc_entity.wrapped_data.get_argument_name(i), sub_node)
                    graph.merge(REL)
            elif ifc_entity.wrapped_data.get_argument_type(i) == "AGGREGATE OF ENTITY INSTANCE":
                for sub_entity in ifc_entity[i]:
                    sub_node = create_pure_node_from_ifc_entity(sub_entity, ifc_file)
                    REL = Relationship(node, ifc_entity.wrapped_data.get_argument_name(i), sub_node)
                    graph.merge(REL)
    for rel_name in ifc_entity.wrapped_data.get_inverse_attribute_names():
        if ifc_entity.wrapped_data.get_inverse(rel_name):
            inverse_relations = ifc_entity.wrapped_data.get_inverse(rel_name)
            for wrapped_rel_entity in inverse_relations:
                rel_entity = ifc_file.by_id(wrapped_rel_entity.id())
                sub_node = create_pure_node_from_ifc_entity(rel_entity, ifc_file)
                REL = Relationship(node, rel_name, sub_node)
                graph.merge(REL)
    return


def create_full_graph(graph, ifc_file):
    idx = 1
    length = len(ifc_file.wrapped_data.entity_names())
    for entity_id in ifc_file.wrapped_data.entity_names():
        entity = ifc_file.by_id(entity_id)
        print(idx, "/", length, entity)
        create_graph_from_ifc_entity_all(graph, entity, ifc_file)
        idx += 1
    return
