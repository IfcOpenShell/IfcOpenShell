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

from math import degrees, radians
from typing import Any, Union

import numpy as np
import pytest

import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.shape
import test.bootstrap
from ifcopenshell.util.shape_builder import (
    ShapeBuilder,
    V,
    is_x,
    np_angle,
    np_angle_signed,
    np_intersect_line_line,
    np_matrix_to_euler,
    np_normal,
    np_rotation_matrix,
    np_to_3d,
)


class TestMathutilsCompatibleMethods(test.bootstrap.IFC4):
    def test_np_rotation_matrix(self):
        from mathutils import Matrix, Vector  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

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

    def test_np_matrix_to_euler(self):
        from mathutils import Euler  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

        # Test 3x3.
        rot = Euler((0.5, 0.5, 0.5)).to_matrix()
        assert np.allclose(rot.to_euler(), np_matrix_to_euler(V(rot)))

        rot = rot.to_4x4()
        assert np.allclose(rot.to_euler(), np_matrix_to_euler(V(rot)))

        # Ensure support scaled matrices.
        rot = Euler((0.5, 0.5, 0.5)).to_matrix()
        rot.col[0] *= 2
        assert np.allclose(rot.to_euler(), np_matrix_to_euler(V(rot)))

    def test_np_angle(self):
        from mathutils import Vector  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

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
        import mathutils.geometry  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

        vectors = (0, 0, 0), (1, 0, 0), (0, 1, 0)
        n = mathutils.geometry.normal(vectors)
        assert np.allclose(n, np_normal(vectors))
        assert np.allclose(n, (0, 0, 1))

        vectors = (0, 0, 0), (0, 1, 0), (1, 0, 0)
        n = mathutils.geometry.normal(vectors)
        assert np.allclose(n, np_normal(vectors))
        assert np.allclose(n, (0, 0, -1))

    def test_np_intersect_line_line(self):
        import mathutils.geometry  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

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

    def _l_profile_extrusion(self):
        """A 6-segment IfcCompositeCurve of IfcPolylines, matching the L200x100x10 steel
        angle profile from #7991's beam (Joey's file, entity #318707), extruded 50 units."""
        f = self.file
        coords = [(0.0, 0.0), (100.0, 0.0), (100.0, 10.0), (10.0, 10.0), (10.0, 200.0), (0.0, 200.0)]
        segments = []
        for i in range(len(coords)):
            p0, p1 = coords[i], coords[(i + 1) % len(coords)]
            polyline = f.create_entity(
                "IfcPolyline", Points=[f.create_entity("IfcCartesianPoint", c) for c in (p0, p1)]
            )
            segments.append(f.create_entity("IfcCompositeCurveSegment", "CONTINUOUS", True, polyline))
        composite_curve = f.create_entity("IfcCompositeCurve", segments, False)
        profile = f.create_entity("IfcArbitraryClosedProfileDef", "AREA", None, composite_curve)
        position = f.create_entity(
            "IfcAxis2Placement3D",
            f.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0)),
            f.create_entity("IfcDirection", (0.0, 0.0, 1.0)),
            f.create_entity("IfcDirection", (1.0, 0.0, 0.0)),
        )
        return f.create_entity(
            "IfcExtrudedAreaSolid", profile, position, f.create_entity("IfcDirection", (0.0, 0.0, 1.0)), 50.0
        )

    @staticmethod
    def _tessellate(item):
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, item)
        verts = np.array(shape.verts).reshape(-1, 3)
        faces = np.array(shape.faces).reshape(-1, 3)
        return verts, faces

    @staticmethod
    def _total_area(verts, faces):
        tri = verts[faces]
        cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        return 0.5 * np.linalg.norm(cross, axis=1).sum()

    def test_mirror_composite_curve_of_polylines_is_a_true_reflection(self):
        """#7991: IfcCompositeCurve profiles (filleted/angle steel sections) used to raise
        in mirror(), leaving the profile untouched rather than corrupted. This confirms the
        curve is now actually mirrored, correctly, not just left safely alone."""
        item = self._l_profile_extrusion()
        original_verts, original_faces = self._tessellate(item)
        assert len(original_verts) == 12, "an L-hexagon prism has 12 unique vertices when welded"

        copy = ifcopenshell.util.element.copy_deep(self.file, item)
        builder = ShapeBuilder(self.file)
        mirrored = builder.mirror(copy, mirror_axes=(1.0, 0.0), mirror_point=(0.0, 0.0))

        mirrored_verts, mirrored_faces = self._tessellate(mirrored)
        assert len(mirrored_verts) == 12, "mirroring must not degenerate the profile"

        expected = original_verts.copy()
        expected[:, 0] *= -1

        def as_point_set(arr):
            return set(tuple(np.round(row, 6)) for row in arr)

        assert as_point_set(mirrored_verts) == as_point_set(expected), "mirrored shape is not the exact reflection"
        assert self._total_area(mirrored_verts, mirrored_faces) == pytest.approx(
            self._total_area(original_verts, original_faces)
        ), "mirroring changed the solid's surface area: the wire likely wound the wrong way"

    def _rounded_rectangle_extrusion(self, width=200.0, height=100.0, radius=20.0, depth=50.0):
        """4 straight segments + 4 quarter-circle IfcTrimmedCurve fillet segments, CCW."""
        f = self.file

        def pt(x, y):
            return f.create_entity("IfcCartesianPoint", (float(x), float(y)))

        def polyline_seg(p0, p1):
            polyline = f.create_entity("IfcPolyline", (pt(*p0), pt(*p1)))
            return f.create_entity("IfcCompositeCurveSegment", "CONTINUOUS", True, polyline)

        def arc_seg(center, radius, start_deg, end_deg):
            import math

            circle_position = f.create_entity(
                "IfcAxis2Placement2D", pt(*center), f.create_entity("IfcDirection", (1.0, 0.0))
            )
            circle = f.create_entity("IfcCircle", circle_position, radius)
            start = (
                center[0] + radius * math.cos(math.radians(start_deg)),
                center[1] + radius * math.sin(math.radians(start_deg)),
            )
            end = (
                center[0] + radius * math.cos(math.radians(end_deg)),
                center[1] + radius * math.sin(math.radians(end_deg)),
            )
            trimmed = f.create_entity("IfcTrimmedCurve", circle, (pt(*start),), (pt(*end),), True, "CARTESIAN")
            return f.create_entity("IfcCompositeCurveSegment", "CONTINUOUS", True, trimmed)

        w, h, r = width, height, radius
        segments = [
            polyline_seg((r, 0), (w - r, 0)),
            arc_seg((w - r, r), r, -90, 0),
            polyline_seg((w, r), (w, h - r)),
            arc_seg((w - r, h - r), r, 0, 90),
            polyline_seg((w - r, h), (r, h)),
            arc_seg((r, h - r), r, 90, 180),
            polyline_seg((0, h - r), (0, r)),
            arc_seg((r, r), r, 180, 270),
        ]
        composite_curve = f.create_entity("IfcCompositeCurve", segments, False)
        profile = f.create_entity("IfcArbitraryClosedProfileDef", "AREA", None, composite_curve)
        position = f.create_entity(
            "IfcAxis2Placement3D",
            f.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0)),
            f.create_entity("IfcDirection", (0.0, 0.0, 1.0)),
            f.create_entity("IfcDirection", (1.0, 0.0, 0.0)),
        )
        return f.create_entity(
            "IfcExtrudedAreaSolid", profile, position, f.create_entity("IfcDirection", (0.0, 0.0, 1.0)), depth
        )

    @pytest.mark.parametrize("mirror_axes", [(1.0, 0.0), (0.0, 1.0), (1.0, 1.0)])
    def test_mirror_composite_curve_with_arc_segments_keeps_correct_sweep(self, mirror_axes):
        """A mirrored arc keeps its radius but its sweep direction inverts. If the fillet
        segments end up sweeping the wrong way round (or half the wire self-intersects),
        the solid's total surface area and vertex/triangle counts stop matching the
        original's, even though every individual vertex still lands on a valid reflection."""
        item = self._rounded_rectangle_extrusion()
        original_verts, original_faces = self._tessellate(item)

        copy = ifcopenshell.util.element.copy_deep(self.file, item)
        builder = ShapeBuilder(self.file)
        mirrored = builder.mirror(copy, mirror_axes=mirror_axes, mirror_point=(0.0, 0.0))

        mirrored_verts, mirrored_faces = self._tessellate(mirrored)

        expected = original_verts.copy()
        if mirror_axes[0] > 0:
            expected[:, 0] *= -1
        if mirror_axes[1] > 0:
            expected[:, 1] *= -1

        def as_point_set(arr):
            return set(tuple(np.round(row, 5)) for row in arr)

        assert len(mirrored_verts) == len(original_verts)
        assert as_point_set(mirrored_verts) == as_point_set(expected)
        assert self._total_area(mirrored_verts, mirrored_faces) == pytest.approx(
            self._total_area(original_verts, original_faces), rel=1e-6
        )


class TestVertex(test.bootstrap.IFC4):
    def test_run(self):
        builder = ShapeBuilder(self.file)
        vertex = builder.vertex((1, 2, 3))
        assert np.allclose(vertex.VertexGeometry.Coordinates, (1, 2, 3))


class TestEdge(test.bootstrap.IFC4):
    def test_run(self):
        builder = ShapeBuilder(self.file)
        edge = builder.edge((1, 0, 0), (1, 2, 3))
        assert np.allclose(edge.EdgeStart.VertexGeometry.Coordinates, (1, 0, 0))
        assert np.allclose(edge.EdgeEnd.VertexGeometry.Coordinates, (1, 2, 3))


class TestFace(test.bootstrap.IFC4):
    def test_run(self):
        builder = ShapeBuilder(self.file)
        face = builder.face(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)))
        assert np.allclose(face.Bounds[0].Bound.Polygon[0], (0, 0, 0))
        assert np.allclose(face.Bounds[0].Bound.Polygon[1], (1, 0, 0))
        assert np.allclose(face.Bounds[0].Bound.Polygon[2], (1, 1, 0))
        assert np.allclose(face.Bounds[0].Bound.Polygon[3], (0, 1, 0))


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


class TestFaceset(test.bootstrap.IFC4):
    @pytest.mark.parametrize("with_inner", [False, True])
    def test_polygonal_face_set_simple_and_with_voids(self, with_inner):
        self.builder = ShapeBuilder(self.file)

        v0 = (0.0, 0.0, 0.0)
        v1 = (4.0, 0.0, 0.0)
        v2 = (4.0, 4.0, 0.0)
        v3 = (0.0, 4.0, 0.0)

        v4 = (1.0, 1.0, 0.0)
        v5 = (3.0, 1.0, 0.0)
        v6 = (3.0, 3.0, 0.0)
        v7 = (1.0, 3.0, 0.0)

        if with_inner:
            points = [v0, v1, v2, v3, v4, v5, v6, v7]

            faces = [
                [[0, 1, 2, 3], [4, 5, 6, 7]],  # outer loop with inner hole
            ]
        else:
            points = [v0, v1, v2, v3]

            faces = [[0, 1, 2, 3]]  # only outer loop

        result = self.builder.polygonal_face_set(points, faces)

        assert result.is_a("IfcPolygonalFaceSet")
        assert result.Coordinates.is_a("IfcCartesianPointList3D")
        assert len(result.Faces) == 1
        if with_inner:
            assert result.Faces[0].is_a("IfcIndexedPolygonalFaceWithVoids")
        else:
            assert result.Faces[0].is_a("IfcIndexedPolygonalFace")

        shp = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), result)
        if with_inner:
            assert ifcopenshell.util.shape.get_area(shp) == pytest.approx(12.0)
        else:
            assert ifcopenshell.util.shape.get_area(shp) == pytest.approx(16.0)

    def test_polygonal_face_set_invalid_face_types(self):
        self.builder = ShapeBuilder(self.file)
        with pytest.raises(ValueError, match="Expected a sequence of int or sequence of sequence of int"):
            self.builder.polygonal_face_set([], ["123"])
        with pytest.raises(ValueError, match="Expected a sequence of int or sequence of sequence of int"):
            self.builder.polygonal_face_set([], [[1.0, 2.0, 3.0]])
        with pytest.raises(ValueError, match="Expected a sequence of int or sequence of sequence of int"):
            self.builder.polygonal_face_set([], [[[[1, 2], 3], [4, 5, 6]]])
