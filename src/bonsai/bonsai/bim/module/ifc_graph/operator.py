# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

# This file was generated with the assistance of an AI coding tool.

from typing import Union

import bpy
import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.module.ifc_graph.ui import (
    COLOR_DEFAULT,
    COLOR_ORIGIN,
    COLOR_RELATIONSHIP,
    NODE_TYPE,
    SOCKET_TYPE,
    TREE_TYPE,
)

MAX_FORWARD_REFS = 10
MAX_INVERSE_REFS = 25
NODE_WIDTH = 260.0
COLUMN_PITCH = 420.0
ROW_MARGIN = 30.0
VALUE_LIMIT = 40


def format_value(value: object) -> str:
    text = str(value)
    if len(text) > VALUE_LIMIT:
        text = text[: VALUE_LIMIT - 3] + "..."
    return text


def get_forward_refs(element: ifcopenshell.entity_instance) -> list[tuple[str, list[ifcopenshell.entity_instance]]]:
    """Get (attribute_name, referenced_entities) pairs for forward attributes."""
    refs = []
    for key, value in element.get_info().items():
        if key in ("id", "type"):
            continue
        if isinstance(value, ifcopenshell.entity_instance):
            if value.id():
                refs.append((key, [value]))
        elif isinstance(value, tuple):
            # Inline value wrappers (id 0) are displayed as text, not as nodes.
            entities = [v for v in value if isinstance(v, ifcopenshell.entity_instance) and v.id()]
            if entities:
                refs.append((key, entities))
    return refs


def get_scalar_rows(element: ifcopenshell.entity_instance) -> list[tuple[str, str]]:
    """Get (attribute_name, formatted_value) pairs for non-entity attributes."""
    rows = []
    for key, value in element.get_info().items():
        if key in ("id", "type") or value is None:
            continue
        if isinstance(value, ifcopenshell.entity_instance):
            if not value.id():
                rows.append((key, format_value(value)))
        elif isinstance(value, tuple):
            if not any(isinstance(v, ifcopenshell.entity_instance) and v.id() for v in value):
                rows.append((key, format_value(value)))
        else:
            rows.append((key, format_value(value)))
    return rows


def find_referencing_attribute(inverse: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance) -> str:
    for key, value in inverse.get_info().items():
        if key in ("id", "type"):
            continue
        if value == element:
            return key
        if isinstance(value, tuple) and any(v == element for v in value if isinstance(v, ifcopenshell.entity_instance)):
            return key
    return "Ref"


def estimate_node_height(node: bpy.types.Node) -> float:
    sockets = len(node.inputs) + len(node.outputs)
    return 60.0 + 22.0 * sockets + 20.0 * len(node.attributes) + 30.0


def place_node(tree: bpy.types.NodeTree, node: bpy.types.Node, x: float, start_y: float) -> None:
    """Drop the node down the column at x until it overlaps nothing."""
    height = estimate_node_height(node)
    y = start_y
    moved = True
    while moved:
        moved = False
        for other in tree.nodes:
            if other == node or abs(other.location.x - x) >= COLUMN_PITCH / 2:
                continue
            other_top = other.location.y + ROW_MARGIN
            other_bottom = other.location.y - estimate_node_height(other) - ROW_MARGIN
            if y > other_bottom and y - height < other_top:
                y = other_bottom
                moved = True
    node.location = (x, y)


def add_attribute_row(node: bpy.types.Node, name: str, value: str) -> None:
    row = node.attributes.add()
    row.name = name
    row.value = value


def add_entity_node(tree: bpy.types.NodeTree, element: ifcopenshell.entity_instance) -> tuple[bpy.types.Node, bool]:
    """Get or create the node for an entity, keyed by STEP ID for deduplication."""
    name = f"#{element.id()}"
    node = tree.nodes.get(name)
    if node:
        return node, False
    node = tree.nodes.new(NODE_TYPE)
    node.name = name
    node.label = f"{element.is_a()} #{element.id()}"
    node.step_id = element.id()
    node.width = NODE_WIDTH
    node.use_custom_color = True
    node.color = COLOR_RELATIONSHIP if element.is_a("IfcRelationship") else COLOR_DEFAULT
    ref_socket = node.inputs.new(SOCKET_TYPE, "Ref")
    ref_socket.link_limit = 0
    for key, value in get_scalar_rows(element):
        add_attribute_row(node, key, value)
    return node, True


def get_or_create_output(node: bpy.types.Node, name: str) -> bpy.types.NodeSocket:
    socket = node.outputs.get(name)
    if not socket:
        socket = node.outputs.new(SOCKET_TYPE, name)
        socket.link_limit = 0
    return socket


def create_link(tree: bpy.types.NodeTree, from_socket: bpy.types.NodeSocket, to_socket: bpy.types.NodeSocket) -> None:
    for link in tree.links:
        if link.from_socket == from_socket and link.to_socket == to_socket:
            return
    tree.links.new(from_socket, to_socket)


def expand_entity_node(tree: bpy.types.NodeTree, ifc_file: ifcopenshell.file, node: bpy.types.Node) -> None:
    """Add one more degree of separation (forward and inverse) around a node."""
    element = ifc_file.by_id(node.step_id)
    parent_x, parent_y = node.location
    for attr_name, refs in get_forward_refs(element):
        shown = refs[:MAX_FORWARD_REFS]
        if len(shown) < len(refs):
            add_attribute_row(node, attr_name, f"showing {len(shown)} of {len(refs)} references")
        socket = get_or_create_output(node, attr_name)
        for ref in shown:
            child, created = add_entity_node(tree, ref)
            if created:
                place_node(tree, child, parent_x + COLUMN_PITCH, parent_y)
            create_link(tree, socket, child.inputs[0])
    inverses = sorted(ifc_file.get_inverse(element), key=lambda e: e.id())
    shown_inverses = inverses[:MAX_INVERSE_REFS]
    if len(shown_inverses) < len(inverses):
        add_attribute_row(node, "Inverses", f"showing {len(shown_inverses)} of {len(inverses)}")
    for inverse in shown_inverses:
        child, created = add_entity_node(tree, inverse)
        if created:
            place_node(tree, child, parent_x - COLUMN_PITCH, parent_y)
        socket = get_or_create_output(child, find_referencing_attribute(inverse, element))
        create_link(tree, socket, node.inputs[0])
    node.is_expanded = True


def get_ifc_graph_tree(context: bpy.types.Context) -> Union[bpy.types.NodeTree, None]:
    space = context.space_data
    if space and space.type == "NODE_EDITOR" and space.tree_type == TREE_TYPE and space.edit_tree:
        return space.edit_tree
    for group in bpy.data.node_groups:
        if group.bl_idname == TREE_TYPE:
            return group
    return None


class LoadIfcGraph(bpy.types.Operator):
    bl_idname = "bim.load_ifc_graph"
    bl_label = "Load Graph From Selection"
    bl_description = "Show the graph of IFC relationships around the selected objects' entities"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC project loaded")
            return False
        return True

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        elements = []
        seen = set()
        for obj in context.selected_objects:
            step_id = tool.Blender.get_ifc_definition_id(obj)
            if not step_id or step_id in seen:
                continue
            try:
                elements.append(ifc_file.by_id(step_id))
            except RuntimeError:
                continue
            seen.add(step_id)
        if not elements:
            self.report({"ERROR"}, "No selected objects with IFC entities")
            return {"CANCELLED"}
        tree = get_ifc_graph_tree(context)
        if not tree:
            tree = bpy.data.node_groups.new("IFC Graph", TREE_TYPE)
        tree.nodes.clear()
        for element in elements:
            node, _ = add_entity_node(tree, element)
            node.is_origin = True
            node.color = COLOR_ORIGIN
            place_node(tree, node, 0.0, 0.0)
            expand_entity_node(tree, ifc_file, node)
        space = context.space_data
        if space and space.type == "NODE_EDITOR" and space.tree_type == TREE_TYPE:
            space.node_tree = tree
        self.report({"INFO"}, f"Loaded graph with {len(tree.nodes)} entities")
        return {"FINISHED"}


class ExpandIfcGraphNode(bpy.types.Operator):
    bl_idname = "bim.expand_ifc_graph_node"
    bl_label = "Expand IFC Graph Node"
    bl_description = "Show one more degree of related entities around this node"
    bl_options = {"REGISTER", "UNDO"}
    node_name: bpy.props.StringProperty(name="Node Name")

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC project loaded")
            return False
        return True

    def execute(self, context):
        tree = get_ifc_graph_tree(context)
        node = tree.nodes.get(self.node_name) if tree else None
        if not node:
            self.report({"ERROR"}, "Graph node not found, reload the graph")
            return {"CANCELLED"}
        ifc_file = tool.Ifc.get()
        try:
            ifc_file.by_id(node.step_id)
        except RuntimeError:
            self.report({"ERROR"}, "Entity no longer exists, reload the graph")
            return {"CANCELLED"}
        expand_entity_node(tree, ifc_file, node)
        return {"FINISHED"}
