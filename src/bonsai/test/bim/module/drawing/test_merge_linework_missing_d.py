# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

from types import SimpleNamespace

import bpy
import ifcopenshell
import ifcopenshell.guid
from lxml import etree

import bonsai.tool as tool
from bonsai.bim.module.drawing.operator import CreateDrawing
from test.bim.bootstrap import NewFile

IFC_NS = "http://www.ifcopenshell.org/ns"


class TestMergeLineworkAndAddMetadata(NewFile):
    def test_paths_without_geometry_are_skipped(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        wall = ifc.createIfcWall(GlobalId=ifcopenshell.guid.new())
        tool.Ifc.link(wall, bpy.data.objects.new("Wall", None))
        drawing = SimpleNamespace(
            camera_element=ifc.createIfcAnnotation(),
            get_element_by_guid=lambda guid: wall,
            get_element_by_id=lambda step_id: None,
            get_svg_classes=lambda element, layer=None: ["IfcWall"],
            is_manifold=lambda obj: True,
        )
        root = etree.fromstring(
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:ifc="{IFC_NS}"><g>'
            f'<g ifc:guid="{wall.GlobalId}" ifc:layer-id=""><path/><path d="M0,0 L1,0 L1,1 L0,1 L0,0"/></g>'
            "</g></svg>"
        )
        CreateDrawing.merge_linework_and_add_metadata(drawing, root)
        paths = root.xpath("//*[local-name()='path']")
        assert len(paths) == 1
        assert paths[0].get("d")
