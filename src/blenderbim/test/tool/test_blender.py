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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.blender import Blender as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Blender)


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
