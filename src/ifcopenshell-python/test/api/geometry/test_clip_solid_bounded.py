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


class TestClipSolidBounded(test.bootstrap.IFC4):
    def make_extrusion(self):
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        rect = builder.rectangle(size=(4.0, 1.0))
        return builder.extrude(rect, magnitude=3.0)

    def test_returns_boolean_clipping_result(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert result.is_a("IfcBooleanClippingResult")
        assert result.Operator == "DIFFERENCE"

    def test_first_operand_is_the_item(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert result.FirstOperand == extrusion

    def test_second_operand_is_polygonal_bounded_half_space(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert result.SecondOperand.is_a("IfcPolygonalBoundedHalfSpace")

    def test_agreement_flag_is_false(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert result.SecondOperand.AgreementFlag is False

    def test_clip_plane_location_matches(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        plane = result.SecondOperand.BaseSurface
        coords = plane.Position.Location.Coordinates
        assert list(coords) == [2.5, 0.0, 2.0]

    def test_boundary_is_closed_polyline(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        boundary = result.SecondOperand.PolygonalBoundary
        assert boundary.is_a("IfcPolyline")
        pts = [list(p.Coordinates) for p in boundary.Points]
        assert pts[0] == pts[-1], "polygon should be closed"
        assert len(pts) == 5  # 4 unique + closing repeat

    def test_boundary_position_defaults_to_origin(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        pos = result.SecondOperand.Position
        assert list(pos.Location.Coordinates) == [0.0, 0.0, 0.0]

    def test_custom_boundary_position(self):
        extrusion = self.make_extrusion()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
            boundary_position=[1.0, 2.0, 3.0],
        )
        pos = result.SecondOperand.Position
        assert list(pos.Location.Coordinates) == [1.0, 2.0, 3.0]

    def test_chaining_with_clip_solid(self):
        extrusion = self.make_extrusion()
        first_clip = ifcopenshell.api.geometry.clip_solid(
            self.file,
            item=extrusion,
            location=[0.0, 0.0, 3.0],
            normal=[0.0, 0.0, 1.0],
        )
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=first_clip,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert result.is_a("IfcBooleanClippingResult")
        assert result.FirstOperand == first_clip
        assert first_clip.FirstOperand == extrusion

    def test_element_registers_result_in_bbim_boolean(self):
        extrusion = self.make_extrusion()
        wall = self.file.createIfcWall()
        result = ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
            element=wall,
        )
        pset = ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean")
        assert pset is not None
        assert result.id() in json.loads(pset["Data"])

    def test_no_element_does_not_create_pset(self):
        extrusion = self.make_extrusion()
        wall = self.file.createIfcWall()
        ifcopenshell.api.geometry.clip_solid_bounded(
            self.file,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )
        assert ifcopenshell.util.element.get_pset(wall, "BBIM_Boolean") is None


class TestClipSolidBoundedIFC2X3(test.bootstrap.IFC2X3, TestClipSolidBounded):
    pass
