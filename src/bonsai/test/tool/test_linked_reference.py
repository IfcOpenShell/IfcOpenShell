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

import math

import bpy
import ifcopenshell
import ifcopenshell.api.document
import pytest
from mathutils import Matrix

import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.tool.linked_reference import LinkedReference as subject
from bonsai.tool.linked_reference import LinkedReferenceError

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    '<rect x="10" y="10" width="50" height="30" fill="none" stroke="black"/>'
    "</svg>"
)
SVG_TWO_SHAPES = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    '<rect x="10" y="10" width="50" height="30" fill="none" stroke="black"/>'
    '<circle cx="80" cy="80" r="15" fill="none" stroke="red"/>'
    "</svg>"
)


def add_link(filepath: str):
    link = subject.get_props().references.add()
    link.name = filepath
    link.filepath = filepath
    return link


class TestMatrixString(test.bim.bootstrap.NewFile):
    def test_round_trip(self):
        matrix = Matrix.Translation((1.0, 2.0, 3.0)) @ Matrix.Rotation(math.radians(45), 4, "Z")
        assert subject.string_to_matrix(subject.matrix_to_string(matrix)) == matrix


class TestLoadLink(test.bim.bootstrap.NewFile):
    def test_svg_loads_as_curves_parented_to_anchor(self, tmp_path):
        svg = tmp_path / "background.svg"
        svg.write_text(SVG)
        link = add_link(str(svg))
        anchor = subject.load_link(link)
        assert link.is_loaded
        assert anchor.type == "EMPTY"
        children = list(anchor.children)
        assert children
        assert all(obj.type == "CURVE" for obj in children)
        assert all(obj.parent == anchor for obj in children)
        collection = subject.get_collection()
        assert collection and anchor.name in collection.objects

    def test_missing_file_raises(self):
        link = add_link("/tmp/does-not-exist-7334.svg")
        with pytest.raises(LinkedReferenceError):
            subject.load_link(link)
        assert not link.is_loaded

    def test_dxf_loads_as_mesh_with_unit_scaling(self, tmp_path):
        ezdxf = pytest.importorskip("ezdxf")
        dxf = tmp_path / "background.dxf"
        doc = ezdxf.new("R2010", setup=False)
        doc.units = ezdxf.units.MM
        msp = doc.modelspace()
        msp.add_line((0, 0), (1000, 0))
        doc.saveas(str(dxf))
        link = add_link(str(dxf))
        anchor = subject.load_link(link)
        (obj,) = anchor.children
        assert obj.type == "MESH"
        assert len(obj.data.vertices) == 2
        assert max(v.co.x for v in obj.data.vertices) == pytest.approx(1.0)


class TestRefreshLink(test.bim.bootstrap.NewFile):
    def test_refresh_replaces_geometry_and_keeps_placement(self, tmp_path):
        svg = tmp_path / "background.svg"
        svg.write_text(SVG)
        link = add_link(str(svg))
        anchor = subject.load_link(link)
        old_children = set(anchor.children)
        matrix = Matrix.Translation((5.0, 3.0, 0.0)) @ Matrix.Rotation(math.radians(30), 4, "Z")
        anchor.matrix_world = matrix
        bpy.context.view_layer.update()

        svg.write_text(SVG_TWO_SHAPES)
        subject.refresh_link(link)
        bpy.context.view_layer.update()

        new_children = list(anchor.children)
        assert new_children and not old_children.intersection(new_children)
        assert len(new_children) > len(old_children)
        for i in range(4):
            for j in range(4):
                assert anchor.matrix_world[i][j] == pytest.approx(matrix[i][j])
        child = new_children[0]
        expected = matrix @ child.matrix_basis
        for i in range(4):
            for j in range(4):
                assert child.matrix_world[i][j] == pytest.approx(expected[i][j], abs=1e-5)


class TestIfcPersistence(test.bim.bootstrap.NewFile):
    def test_document_reference_round_trip(self, tmp_path):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        tool.Ifc.set(ifc)
        reference = subject.add_document_reference("/tmp/background.svg")
        document = tool.Document.get_reference_document(reference)
        assert document.Scope == "LINKED_REFERENCE"
        assert reference.Location == "/tmp/background.svg"

        subject.load_from_ifc()
        references = subject.get_props().references
        assert len(references) == 1
        assert references[0].filepath == "/tmp/background.svg"
        assert references[0].ifc_definition_id == reference.id()
        assert not references[0].is_loaded

        subject.remove_document_reference(references[0])
        assert not ifc.by_type("IfcDocumentReference")
        assert not ifc.by_type("IfcDocumentInformation")

    def test_store_placement_writes_matrix_to_reference(self, tmp_path):
        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        tool.Ifc.set(ifc)
        svg = tmp_path / "background.svg"
        svg.write_text(SVG)
        link = add_link(str(svg))
        link.ifc_definition_id = subject.add_document_reference(str(svg)).id()
        anchor = subject.load_link(link)
        anchor.matrix_world = Matrix.Translation((7.0, 0.0, 0.0))
        bpy.context.view_layer.update()
        subject.sync_placements_to_ifc()
        reference = ifc.by_id(link.ifc_definition_id)
        assert subject.string_to_matrix(reference[1]) == Matrix.Translation((7.0, 0.0, 0.0))
