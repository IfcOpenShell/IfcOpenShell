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
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
import pytest
from test.bim.bootstrap import NewFile
from bonsai.tool.blender import Blender as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Blender)


class TestCopyNodeGraph(NewFile):
    def test_run(self):
        material_to = bpy.data.materials.new("material_to")
        material_to.use_nodes = True
        material_to_nodes = material_to.node_tree.nodes
        assert len(material_to_nodes) == 2
        for node in material_to_nodes:
            material_to_nodes.remove(node)
        assert len(material_to_nodes) == 0

        material_from = bpy.data.materials.new("material_from")
        material_from.use_nodes = True

        subject.copy_node_graph(material_to, material_from)
        assert len(material_to_nodes) == 2


class TestSortPanelsForRegister(NewFile):
    def test_run(self):
        items = ["A", "B", "C", "D"]
        items_to_parents = {"A": "D", "D": "C", "C": "B"}
        sorted_items = subject.sort_panels_for_register(items, items_to_parents)
        assert tuple(sorted_items) == ("B", "C", "D", "A")

        with pytest.raises(AssertionError):
            subject.sort_panels_for_register(items, {"A": "K"})

        with pytest.raises(AssertionError):
            subject.sort_panels_for_register(items, {"J": "A"})
