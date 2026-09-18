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

from typing import TYPE_CHECKING

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import Node, NodeSocket, NodeTree, Panel

import bonsai.tool as tool
from bonsai.bim.module.ifc_graph.prop import IfcGraphAttribute

TREE_TYPE = "BIMIfcGraphTree"
NODE_TYPE = "BIMIfcGraphEntityNode"
SOCKET_TYPE = "BIMIfcGraphSocket"

COLOR_ORIGIN = (0.201, 0.383, 0.232)
COLOR_RELATIONSHIP = (0.213, 0.264, 0.336)
COLOR_DEFAULT = (0.266, 0.266, 0.266)


class IfcGraphTree(NodeTree):
    """Read-only node view of the relationships around selected IFC entities."""

    bl_idname = TREE_TYPE
    bl_label = "IFC Graph"
    bl_icon = "GRAPH"

    @classmethod
    def poll(cls, context):
        return True


class IfcGraphSocket(NodeSocket):
    """Connection point representing an IFC entity reference."""

    bl_idname = SOCKET_TYPE
    bl_label = "IFC Reference"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.24, 0.59, 0.94, 1.0)


class IfcGraphEntityNode(Node):
    """One IFC entity instance, with scalar attributes listed inline.

    Output sockets are forward attributes referencing other entities, links
    always flow from the referencing entity to the referenced one.
    """

    bl_idname = NODE_TYPE
    bl_label = "IFC Entity"

    step_id: IntProperty(name="STEP ID")
    is_expanded: BoolProperty(name="Expanded", default=False)
    is_origin: BoolProperty(name="Origin", default=False)
    attributes: CollectionProperty(name="Attributes", type=IfcGraphAttribute)
    expansion_links: StringProperty(default="[]")
    expansion_base_attr_count: IntProperty(default=0)

    if TYPE_CHECKING:
        step_id: int
        is_expanded: bool
        is_origin: bool
        attributes: bpy.types.bpy_prop_collection_idprop[IfcGraphAttribute]
        expansion_links: str
        expansion_base_attr_count: int

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == TREE_TYPE

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        for attribute in self.attributes:
            col.label(text=f"{attribute.name}: {attribute.value}")
        row = layout.row(align=True)
        if self.is_expanded:
            op = row.operator("bim.collapse_ifc_graph_node", text="Collapse", icon="ZOOM_OUT")
            op.node_name = self.name
        else:
            op = row.operator("bim.expand_ifc_graph_node", text="Expand", icon="ZOOM_IN")
            op.node_name = self.name
        op = row.operator("bim.inspect_from_step_id", text="Inspect", icon="VIEWZOOM")
        op.step_id = self.step_id


class BIM_PT_ifc_graph(Panel):
    bl_idname = "BIM_PT_ifc_graph"
    bl_label = "IFC Graph"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "IFC Graph"

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "tree_type", None) == TREE_TYPE

    def draw(self, context):
        layout = self.layout
        if not tool.Ifc.get():
            layout.label(text="No IFC Project Loaded", icon="ERROR")
            return
        layout.operator("bim.load_ifc_graph", icon="FILE_REFRESH")
        layout.label(text="Select objects in the viewport,")
        layout.label(text="then load their entity graph.")
