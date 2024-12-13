# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import pytest
import test.bootstrap
import ifcopenshell.api
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder, V, is_x
from math import degrees, radians, tan
from mathutils import Vector


class TestRectangle(test.bootstrap.IFC4):
    def test_get_rectangle_coords(self):
        builder = ShapeBuilder(self.file)

        # 2D.
        coords = builder.get_rectangle_coords((1, 2), (3, 4))
        assert np.allclose(coords, [[3.0, 4.0], [4.0, 4.0], [4.0, 6.0], [3.0, 6.0]])

        # 3D, XY plane.
        coords = builder.get_rectangle_coords((1, 2, 0), (3, 4, 0))
        assert np.allclose(coords, [[3.0, 4.0, 0.0], [4.0, 4.0, 0.0], [4.0, 6.0, 0.0], [3.0, 6.0, 0.0]])

        # 3D, XZ plane.
        coords = builder.get_rectangle_coords((1, 0, 2), (3, 0, 4))
        assert np.allclose(coords, [[3.0, 0.0, 4.0], [4.0, 0.0, 4.0], [4.0, 0.0, 6.0], [3.0, 0.0, 6.0]])


class TestCreatePolyline(test.bootstrap.IFC4):
    def test_simple_polyline(self):
        builder = ShapeBuilder(self.file)

        # rectangle
        points = Vector((0, 0)), Vector((1, 0)), Vector((1, 1)), Vector((0, 1))
        position = Vector((2, 0))
        polyline = builder.polyline(points, closed=True, position_offset=position)

        points = [p + position for p in points]
        assert np.allclose(np.array(points), np.array(polyline.Points.CoordList))
        # use 1 line index if there are no arcs
        assert len(polyline.Segments) == 1
        segment = polyline.Segments[0]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (1, 2, 3, 4, 1)

    def test_polyline_with_arc(self):
        builder = ShapeBuilder(self.file)

        points = Vector((1, 0)), Vector((0.707, 0.707)), Vector((0, 1)), Vector((0, 2))
        position = Vector((2, 0))
        arc_points = (1,)
        # 4=IfcIndexedPolyCurve(#3,(IfcArcIndex((1,2,3)),IfcLineIndex((3,4,1))),$)
        polyline = builder.polyline(points, closed=False, position_offset=position, arc_points=arc_points)
        points = [p + position for p in points]
        assert np.allclose(np.array(points), np.array(polyline.Points.CoordList))
        assert len(polyline.Segments) == 2

        segment = polyline.Segments[0]
        assert segment.is_a("IfcArcIndex")
        assert segment.wrappedValue == (1, 2, 3)

        segment = polyline.Segments[1]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (3, 4)

    def test_closed_polyline_ending_with_arc(self):
        builder = ShapeBuilder(self.file)

        points = Vector((0, 0)), Vector((1, 0)), Vector((0.5, 0.5))
        position = Vector((2, 0))
        arc_points = (2,)
        # 4=IfcIndexedPolyCurve(#3,(IfcLineIndex((1,2)),IfcArcIndex((2,3,1))),$)
        polyline = builder.polyline(points, closed=True, position_offset=position, arc_points=arc_points)
        points = [p + position for p in points]
        assert np.allclose(np.array(points), np.array(polyline.Points.CoordList))
        assert len(polyline.Segments) == 2

        segment = polyline.Segments[0]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (1, 2)

        segment = polyline.Segments[1]
        assert segment.is_a("IfcArcIndex")
        assert segment.wrappedValue == (2, 3, 1)


class TestCalculateTransitions(test.bootstrap.IFC4):
    def calculate_and_test(self, params, length):
        end_profile = params["end_profile"]
        start_half_dim = params["start_half_dim"]
        end_half_dim = params["end_half_dim"]
        offset = params["offset"]
        offset = offset if not end_profile else offset.yx
        angle = params["angle"]

        calculated_length = self.builder.mep_transition_calculate(**params)
        if length is None:
            assert calculated_length is None
            return

        assert is_x(calculated_length, length)

        # angle confirmation methods:
        # A - between two profiles of different dimensions
        # B - between two profiles of same dimensions, no offset by x
        # C - between two profiles of same dimensions, has offset by x
        diff = start_half_dim.xy - end_half_dim.xy
        same_dimension = is_x(diff.x if not end_profile else diff.y, 0)
        if not same_dimension:
            confirmation_method = "A"
        else:
            confirmation_method = "B" if is_x(offset.x, 0) else "C"

        if confirmation_method == "A":
            A = (end_half_dim if end_profile else start_half_dim) * V(1, 0, 0)
            end_profile_offset = offset.to_3d() + V(0, 0, length)
            D = (start_half_dim if end_profile else end_half_dim) * V(1, 0, 0)
            B, C = -A, -D
            C += end_profile_offset
            D += end_profile_offset
            tested_angle = degrees((A - D).angle(B - C))
            assert is_x(tested_angle, angle)

        elif confirmation_method == "B":
            O = V(0, 0, 0)
            A = V(-start_half_dim.x, 0, length) + offset.to_3d()
            B = A * V(-1, 1, 1)
            tested_angle = degrees((A - O).angle(B - O))
            assert is_x(tested_angle, angle)

        elif confirmation_method == "C":
            A = V(-start_half_dim.x, 0, 0)
            H = A + V(0, 0, length)
            H.y += offset.y
            D = H.copy()
            D.x += offset.x
            tested_angle = degrees((H - A).angle(D - A))
            assert is_x(tested_angle, angle)

        angle = self.builder.mep_transition_calculate(**params | {"angle": None, "length": calculated_length})
        assert is_x(angle, angle)

    def test_mep_transition_same_dims_no_offset(self):
        self.builder = ShapeBuilder(self.file)
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(100, 50, 0),
            "offset": V(0, 0),
            "end_profile": False,
            "angle": 90,
            "verbose": True,
        }
        self.calculate_and_test(params, 100)

    def test_mep_transition_same_dims_has_x_offset(self):
        self.builder = ShapeBuilder(self.file)
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(100, 50, 0),
            "offset": V(50, 50),
            "end_profile": False,
            "angle": 30,
            "verbose": True,
        }
        self.calculate_and_test(params, 70.71068)

    def test_mep_transition_same_dims_has_y_offset(self):
        self.builder = ShapeBuilder(self.file)
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(100, 50, 0),
            "offset": V(0, 50),
            "end_profile": False,
            "angle": 90,
            "verbose": True,
        }
        self.calculate_and_test(params, 86.60254)

    def test_mep_transition_diff_dims_no_offset(self):
        self.builder = ShapeBuilder(self.file)
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(50, 100, 0),
            "offset": V(0, 0),
            "end_profile": False,
            "angle": 30,
            "verbose": True,
        }
        self.calculate_and_test(params, 186.60254)

    def test_mep_transition_diff_dims_has_x_y_offset(self):
        self.builder = ShapeBuilder(self.file)
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(50, 100, 0),
            "offset": V(50, 50),
            "end_profile": False,
            "angle": 30,
            "verbose": True,
        }
        self.calculate_and_test(params, 165.83124)

    def test_mep_transition_y_offset_too_big(self):
        self.builder = ShapeBuilder(self.file)

        # method A
        params = {
            "start_half_dim": V(100, 50, 0),
            "end_half_dim": V(50, 100, 0),
            # offset.y > h - 190 > 186.6
            "offset": V(0, 190),
            "end_profile": False,
            "angle": 30,
            "verbose": True,
        }
        self.calculate_and_test(params, None)

        # method B
        params["end_half_dim"] = V(100, 100, 0)
        self.calculate_and_test(params, None)

        # method C
        params["offset"].x = 10
        self.calculate_and_test(params, None)
