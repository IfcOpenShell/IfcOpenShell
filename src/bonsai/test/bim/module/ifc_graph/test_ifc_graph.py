# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestIfcGraph(NewFile):
    def add_wall(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        return obj, tool.Ifc.get_entity(obj)

    def get_tree(self):
        return next(g for g in bpy.data.node_groups if g.bl_idname == "BIMIfcGraphTree")

    def get_wall_node(self, tree, wall):
        return next(n for n in tree.nodes if n.step_id == wall.id())

    def test_loading_the_graph_marks_the_selected_entity_as_the_origin(self):
        _, wall = self.add_wall()
        assert bpy.ops.bim.load_ifc_graph() == {"FINISHED"}
        node = self.get_wall_node(self.get_tree(), wall)
        assert node.is_origin

    def test_loading_the_graph_adds_related_entities(self):
        _, wall = self.add_wall()
        bpy.ops.bim.load_ifc_graph()
        assert len(self.get_tree().nodes) > 1

    def test_loading_without_an_ifc_selection_is_cancelled(self):
        bpy.ops.bim.create_project()
        bpy.ops.object.select_all(action="DESELECT")
        with pytest.raises(RuntimeError, match="No selected objects with IFC entities"):
            bpy.ops.bim.load_ifc_graph()

    def test_collapse_removes_what_expand_added(self):
        _, wall = self.add_wall()
        bpy.ops.bim.load_ifc_graph()
        tree = self.get_tree()
        wall_node = self.get_wall_node(tree, wall)
        related = next(n for n in tree.nodes if n != wall_node)
        count_before = len(tree.nodes)
        bpy.ops.bim.expand_ifc_graph_node(node_name=related.name)
        assert len(tree.nodes) > count_before
        bpy.ops.bim.collapse_ifc_graph_node(node_name=related.name)
        assert len(tree.nodes) == count_before
        assert self.get_wall_node(tree, wall).is_origin

    def test_reloading_the_graph_replaces_the_previous_nodes(self):
        _, wall = self.add_wall()
        bpy.ops.bim.load_ifc_graph()
        count = len(self.get_tree().nodes)
        bpy.ops.bim.load_ifc_graph()
        assert len(self.get_tree().nodes) == count
