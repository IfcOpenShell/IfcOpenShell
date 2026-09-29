# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

"""
These tests actually belong to the `ifcopenshell.util.shape_builder` test suite
(ifcopenshell-python/test/util/test_shape_builder.py) but live here because they need
`mathutils`.

`mathutils` is available from PyPI either as part of `bpy` or `mathutils` package,
but those are not widely used and there were issues in the past with these going out of date.
Testing against them would also require separately building ifcopenshell for targeted Blender's Python version
(usually for tests we use the minimal Python version supported instead).

Therefore we just test it against the real `mathutils` inside Blender.
"""

from math import radians

import numpy as np
from ifcopenshell.util.shape_builder import (
    V,
    is_x,
    np_angle,
    np_angle_signed,
    np_intersect_line_line,
    np_matrix_to_euler,
    np_normal,
    np_rotation_matrix,
)

from test.bim.bootstrap import NewFile


class TestMathutilsCompatibleMethods(NewFile):
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

    def test_np_matrix_to_euler(self):
        from mathutils import Euler

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
