# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import json

import ifcopenshell.api.geometry
import ifcopenshell.util.element
import ifcopenshell.util.shape_builder
import test.bootstrap


class TestClipSolid(test.bootstrap.IFC4):
    def make_extrusion(self):
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        rect = builder.rectangle(size=(1.0, 1.0))
        return builder.extrude(rect, magnitude=4.0)

    def test_returns_boolean_clipping_result(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        assert result.is_a("IfcBooleanClippingResult")
        assert result.Operator == "DIFFERENCE"

    def test_first_operand_is_the_item(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        assert result.FirstOperand == extrusion

    def test_second_operand_is_half_space_solid(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        assert result.SecondOperand.is_a("IfcHalfSpaceSolid")

    def test_clip_plane_location_matches(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        plane = result.SecondOperand.BaseSurface
        coords = plane.Position.Location.Coordinates
        assert list(coords) == [0.0, 0.0, 3.0]

    def test_chaining_two_clips(self):
        extrusion = self.make_extrusion()
        first_clip = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        second_clip = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=first_clip,
            location=[0.0, 0.0, 1.0],
            normal=[0.0, 0.0, -1.0],
        )
        assert second_clip.is_a("IfcBooleanClippingResult")
        assert second_clip.FirstOperand == first_clip
        assert first_clip.FirstOperand == extrusion

    def test_angled_clip_plane(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.26],
            normal=[0.419, 0.0, 0.908],
        )
        assert result.is_a("IfcBooleanClippingResult")
        assert result.SecondOperand.is_a("IfcHalfSpaceSolid")

    def test_element_registers_result_in_bbim_boolean(self):
        extrusion = self.make_extrusion()
        wall = self.file.createIfcWall()
        result = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
            element=wall,
        )
        pset = ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean")
        assert pset is not None
        assert result.id() in json.loads(pset["Data"])

    def test_element_appends_to_existing_bbim_boolean(self):
        extrusion = self.make_extrusion()
        wall = self.file.createIfcWall()
        first = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
            element=wall,
        )
        second = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=first,
            location=[0.0, 0.0, 1.0],
            normal=[0.0, 0.0, -1.0],
            element=wall,
        )
        pset = ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean")
        ids = json.loads(pset["Data"])
        assert first.id() in ids
        assert second.id() in ids

    def test_no_element_does_not_create_pset(self):
        extrusion = self.make_extrusion()
        wall = self.file.createIfcWall()
        ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        assert ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean") is None


class TestClipSolidIFC2X3(test.bootstrap.IFC2X3, TestClipSolid):
    pass
