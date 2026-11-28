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

import ifcopenshell
import ifcopenshell.api.root
import lxml.etree as etree

import bonsai.tool as tool
from bonsai.bim.module.drawing.operator import CreateDrawing

SVG = "{http://www.w3.org/2000/svg}"
IFC = "{http://www.ifcopenshell.org/ns}"


def square(x):
    return f"M{x},0 L{x + 2},0 L{x + 2},2 L{x},2 L{x},0"


def add_element_group(parent, guid, *paths):
    g = etree.SubElement(parent, SVG + "g", {IFC + "guid": guid})
    for d in paths:
        etree.SubElement(g, SVG + "path", {"d": d})


def test_merging_one_piece_leaves_the_classes_of_disjoint_pieces_alone(monkeypatch):
    ifc = ifcopenshell.file(schema="IFC4")
    camera = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation")
    wall_a = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
    wall_b = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
    walls = {"guidA": wall_a, "guidB": wall_b}
    monkeypatch.setattr(tool.Ifc, "get_object", lambda element: object())
    root = etree.Element(SVG + "svg")
    main = etree.SubElement(root, SVG + "g")
    add_element_group(main, "guidB", square(1))
    add_element_group(main, "guidA", square(5), square(0))
    fake_self = SimpleNamespace(
        camera_element=camera,
        get_element_by_guid=walls.get,
        get_element_by_id=lambda element_id: None,
        get_svg_classes=lambda element, layer=None: [],
        is_manifold=lambda obj: True,
    )

    CreateDrawing.merge_linework_and_add_metadata(fake_self, root)

    pieces = [set(g.get("class").split()) for g in main.findall("g")]
    assert {"cut", "guidA"} in pieces
    assert {"cut", "guidA", "guidB"} in pieces
