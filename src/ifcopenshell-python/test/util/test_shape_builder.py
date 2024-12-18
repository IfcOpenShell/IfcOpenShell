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
from ifcopenshell.util.shape_builder import (
    ShapeBuilder,
    is_x,
    np_rotation_matrix,
    np_to_3d,
    np_angle,
    V,
    np_angle_signed,
    np_normal,
    np_intersect_line_line,
)
from math import degrees, radians
from typing import Any, Union


class TestMathutilsCompatibleMethods(test.bootstrap.IFC4):
    def test_np_rotation_matrix(self):
        from mathutils import Matrix, Vector

        # 2D.
        assert np.allclose(Matrix.Rotation(radians(45), 2), np_rotation_matrix(radians(45), 2))
        assert np.allclose(Matrix.Rotation(radians(45), 2, "Z"), np_rotation_matrix(radians(45), 2, "Z"))

        # 3D.
        assert np.allclose(Matrix.Rotation(radians(45), 3, "X"), np_rotation_matrix(radians(45), 3, "X"))
        assert np.allclose(Matrix.Rotation(radians(45), 3, "Y"), np_rotation_matrix(radians(45), 3, "Y"))
        assert np.allclose(Matrix.Rotation(radians(45), 3, "Z"), np_rotation_matrix(radians(45), 3, "Z"))
        rotation_vector_args = radians(45), 3, Vector((1, 1, 1)).normalized()
        assert np.allclose(Matrix.Rotation(*rotation_vector_args), np_rotation_matrix(*rotation_vector_args))

        # Size 4.
        assert np.allclose(Matrix.Rotation(radians(45), 4, "X"), np_rotation_matrix(radians(45), 4, "X"))
        assert np.allclose(Matrix.Rotation(radians(45), 4, "Y"), np_rotation_matrix(radians(45), 4, "Y"))
        assert np.allclose(Matrix.Rotation(radians(45), 4, "Z"), np_rotation_matrix(radians(45), 4, "Z"))
        rotation_vector_args = radians(45), 4, Vector((1, 1, 1)).normalized()
        assert np.allclose(Matrix.Rotation(*rotation_vector_args), np_rotation_matrix(*rotation_vector_args))

    def test_np_angle(self):
        from mathutils import Vector

        v1, v2 = (1, 0, 0), (0, 1, 0)
        angle = np_angle(v1, v2)
        assert is_x(angle, Vector(v1).angle(Vector(v2)))
        assert is_x(angle, radians(90))

        v1, v2 = v1[:2], v2[:2]
        angle = np_angle_signed(v1, v2)
        assert is_x(angle, Vector(v1).angle_signed(Vector(v2)))
        assert is_x(angle, -radians(90))

        v1, v2 = (0, 1, 0), (1, 0, 0)
        angle = np_angle(v1, v2)
        assert is_x(angle, Vector(v1).angle(Vector(v2)))
        assert is_x(angle, radians(90))

        v1, v2 = v1[:2], v2[:2]
        angle = np_angle_signed(v1, v2)
        assert is_x(angle, Vector(v1).angle_signed(Vector(v2)))
        assert is_x(angle, radians(90))

    def test_np_normal(self):
        import mathutils.geometry

        vectors = (0, 0, 0), (1, 0, 0), (0, 1, 0)
        n = mathutils.geometry.normal(vectors)
        assert np.allclose(n, np_normal(vectors))
        assert np.allclose(n, (0, 0, 1))

        vectors = (0, 0, 0), (0, 1, 0), (1, 0, 0)
        n = mathutils.geometry.normal(vectors)
        assert np.allclose(n, np_normal(vectors))
        assert np.allclose(n, (0, 0, -1))

    def test_np_intersect_line_line(self):
        import mathutils.geometry

        p1, p2 = [0, 0, 0], [1, 1, 1]
        q1, q2 = [0, 1, 0], [1, 0, 1]
        expected = mathutils.geometry.intersect_line_line(tuple(p1), tuple(p2), tuple(q1), tuple(q2))
        result = np_intersect_line_line(p1, p2, q1, q2)
        assert np.allclose(expected, result)


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
        points = V([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        position = (2.0, 0.0)
        polyline = builder.polyline(points, closed=True, position_offset=position)

        points += position
        assert np.allclose(points, polyline.Points.CoordList)
        # use 1 line index if there are no arcs
        assert len(polyline.Segments) == 1
        segment = polyline.Segments[0]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (1, 2, 3, 4, 1)

    def test_polyline_with_arc(self):
        builder = ShapeBuilder(self.file)

        points = V([(1, 0), (0.707, 0.707), (0, 1), (0, 2)])
        position = (2, 0)
        arc_points = (1,)
        # 4=IfcIndexedPolyCurve(# 3,(IfcArcIndex((1,2,3)),IfcLineIndex((3,4,1))),$)
        polyline = builder.polyline(points, closed=False, position_offset=position, arc_points=arc_points)
        points += position
        assert np.allclose(points, polyline.Points.CoordList)
        assert len(polyline.Segments) == 2

        segment = polyline.Segments[0]
        assert segment.is_a("IfcArcIndex")
        assert segment.wrappedValue == (1, 2, 3)

        segment = polyline.Segments[1]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (3, 4)

    def test_closed_polyline_ending_with_arc(self):
        builder = ShapeBuilder(self.file)

        points = V([(0, 0), (1, 0), (0.5, 0.5)])
        position = (2, 0)
        arc_points = (2,)
        # 4=IfcIndexedPolyCurve(#3,(IfcLineIndex((1,2)),IfcArcIndex((2,3,1))),$)
        polyline = builder.polyline(points, closed=True, position_offset=position, arc_points=arc_points)
        points += position
        assert np.allclose(points, polyline.Points.CoordList)
        assert len(polyline.Segments) == 2

        segment = polyline.Segments[0]
        assert segment.is_a("IfcLineIndex")
        assert segment.wrappedValue == (1, 2)

        segment = polyline.Segments[1]
        assert segment.is_a("IfcArcIndex")
        assert segment.wrappedValue == (2, 3, 1)


class TestMirror(test.bootstrap.IFC4):
    def test_mirror(self):
        builder = ShapeBuilder(self.file)
        rectangle = builder.rectangle(size=(100, 100))
        assert np.allclose(rectangle.Points.CoordList, ((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)))
        builder.mirror(rectangle, mirror_axes=(1, 0))
        assert np.allclose(rectangle.Points.CoordList, ((0.0, 0.0), (-100.0, 0.0), (-100.0, 100.0), (0.0, 100.0)))


class TestCalculateTransitions(test.bootstrap.IFC4):
    def calculate_and_test(self, params: dict[str, Any], length: Union[float, None]):
        np_X, np_Y = 0, 1
        np_XY = slice(2)
        np_YX = [1, 0]

        end_profile = params["end_profile"]
        start_half_dim: np.ndarray = params["start_half_dim"]
        end_half_dim: np.ndarray = params["end_half_dim"]
        offset: np.ndarray = params["offset"]
        offset = offset if not end_profile else offset[np_YX]
        angle = params["angle"]

        calculated_length = self.builder.mep_transition_calculate(**params)
        if length is None:
            assert calculated_length is None
            return

        assert calculated_length is not None and is_x(calculated_length, length)

        # angle confirmation methods:
        # A - between two profiles of different dimensions
        # B - between two profiles of same dimensions, no offset by x
        # C - between two profiles of same dimensions, has offset by x
        diff = np.subtract(start_half_dim[np_XY], end_half_dim[np_XY])
        same_dimension = is_x(diff[np_X] if not end_profile else diff[np_Y], 0)
        if not same_dimension:
            confirmation_method = "A"
        else:
            confirmation_method = "B" if is_x(offset[np_X], 0) else "C"

        if confirmation_method == "A":
            A = (end_half_dim if end_profile else start_half_dim) * (1, 0, 0)
            end_profile_offset = np_to_3d(offset, length)
            D = (start_half_dim if end_profile else end_half_dim) * (1, 0, 0)
            B, C = -A, -D
            C += end_profile_offset
            D += end_profile_offset
            tested_angle = degrees(np_angle(A - D, B - C))
            assert is_x(tested_angle, angle)

        elif confirmation_method == "B":
            O = np.zeros(3)
            A = (-start_half_dim[np_X], 0, length) + np_to_3d(offset)
            B = A * (-1, 1, 1)
            tested_angle = degrees(np_angle(A - O, B - O))
            assert is_x(tested_angle, angle)

        elif confirmation_method == "C":
            A = V(-start_half_dim[np_X], 0, 0)
            H = A + (0, 0, length)
            H[np_Y] += offset[np_Y]
            D = H.copy()
            D[np_X] += offset[np_X]
            tested_angle = degrees(np_angle(H - A, D - A))
            assert is_x(tested_angle, angle)

        calculated_angle = self.builder.mep_transition_calculate(
            **params | {"angle": None, "length": calculated_length}
        )
        assert calculated_angle is not None
        assert is_x(calculated_angle, angle)

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
        params["offset"][0] = 10.0
        self.calculate_and_test(params, None)
