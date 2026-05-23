# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022, 2023 @Andrej730
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

from __future__ import annotations

import collections.abc
from collections.abc import Sequence
from math import radians
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import numpy as np
import numpy.typing as npt

PRECISION = 1.0e-5

if TYPE_CHECKING:
    # NOTE: mathutils is never used at runtime in ifcopenshell,
    # only for type checking to ensure methods are compatible with
    # Blender vectors.
    from mathutils import Vector  # pyright: ignore[reportMissingImports]  # ty:ignore[unresolved-import]

    # Support both numpy arrays and python sequences as inputs.
    VectorType = Union[Sequence[float], Vector, np.ndarray]
else:
    # Ensure it's exportable, so other modules can reuse it for typing.
    VectorType = Any

SequenceOfVectors = Union[Sequence[VectorType], np.ndarray]


def V(*args: Union[float, int, VectorType, SequenceOfVectors]) -> npt.NDArray[np.float64]:
    """Convert floats / vector / sequence of vectors to numpy array."""
    if isinstance(args[0], (float, int)):
        return np.array(args, dtype="d")

    assert len(args) == 1, "Only single argument is supported if providing a vector or a sequence of them."
    return np.array(args[0], dtype="d")


def ifc_safe_vector_type(v: Union[VectorType, SequenceOfVectors]) -> Any:
    """Convert vector / sequence of vectors to a list of floats safe for IFC attributes."""
    return np.array(v, dtype="d").tolist()


def is_x(value: float, x: float, si_conversion: Optional[float] = None) -> bool:
    if si_conversion is not None:
        value = value * si_conversion
    return (x + PRECISION) > value > (x - PRECISION)


def round_to_precision(x: float, si_conversion: float) -> float:
    return round(x * si_conversion, 5) / si_conversion


def np_round_to_precision(v: np.ndarray, si_conversion: float) -> np.ndarray:
    return np.round(v * si_conversion, 5) / si_conversion


def np_normalized(v: VectorType) -> np.ndarray:
    return np.divide(v, np.linalg.norm(v))


def np_matrix_normalized(matrix: np.ndarray) -> np.ndarray:
    scale_factors = np.linalg.norm(matrix[:3, :3], axis=0)
    rotation_matrix = matrix.copy()
    rotation_matrix[:3, :3] /= scale_factors
    return rotation_matrix


def np_lerp(a: VectorType, b: VectorType, t: float) -> np.ndarray:
    return a + np.subtract(b, a) * t


def np_to_3d(v: VectorType, z: float = 0.0) -> np.ndarray:
    l = len(v)
    if l == 2:
        return np.append(v, z)
    elif l == 4:
        return v[:3]
    assert False, f"Unexpected vector length: {l} ({v})."


def np_to_4d(v: VectorType, z: float = 0.0, w: float = 1.0) -> np.ndarray:
    l = len(v)
    if l == 2:
        return np.append(v, (z, w))
    elif l == 3:
        return np.append(v, w)
    assert False, f"Unexpected vector length: {l} ({v})."


def np_to_4x4(matrix_3x3: np.ndarray) -> np.ndarray:
    matrix_4x4 = np.pad(matrix_3x3, ((0, 1), (0, 1)))
    matrix_4x4[3, 3] = 1
    return matrix_4x4


def np_apply_matrix(vectors: SequenceOfVectors, matrix: npt.NDArray) -> npt.NDArray:
    m3x3 = matrix[:3, :3]
    translation = matrix[:3, 3]
    return vectors @ m3x3.T + translation


def np_angle(a: VectorType, b: VectorType) -> float:
    return np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def np_angle_signed(a: VectorType, b: VectorType) -> float:
    assert len(a) == 2 and len(b) == 2, "Only 2D vectors are supported."
    det = a[1] * b[0] - a[0] * b[1]
    dot = np.dot(a, b)
    return np.arctan2(det, dot)


def np_translation_matrix(vector: VectorType) -> npt.NDArray[np.float64]:
    eye = np.eye(4, dtype=np.float64)
    M_TRANSLATION = (slice(0, 3), 3)
    eye[M_TRANSLATION] = vector
    return eye


def np_rotation_matrix(
    angle: float, size: int, axis: Optional[Union[Literal["X", "Y", "Z"], VectorType]] = None
) -> np.ndarray:
    if not (2 <= size <= 4):
        raise ValueError(f"Size must be [2;4], got {size}.")
    cos_theta: float = np.cos(angle)
    sin_theta: float = np.sin(angle)
    if size == 2:
        return np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]])
    assert axis, "For non-2D matrices 'axis' argument is not optional."
    if isinstance(axis, str):
        if axis == "X":
            matrix = np.array([[1, 0, 0], [0, cos_theta, -sin_theta], [0, sin_theta, cos_theta]])
        elif axis == "Y":
            matrix = np.array([[cos_theta, 0, sin_theta], [0, 1, 0], [-sin_theta, 0, cos_theta]])
        elif axis == "Z":
            matrix = np.array([[cos_theta, -sin_theta, 0], [sin_theta, cos_theta, 0], [0, 0, 1]])
    else:
        axis = axis / np.linalg.norm(axis)
        K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        matrix = cos_theta * np.eye(3) + (1 - cos_theta) * np.outer(axis, axis) + sin_theta * K
    if size == 4:
        return np_to_4x4(matrix)
    return matrix


def np_matrix_to_euler(matrix: np.ndarray) -> tuple[float, float, float]:
    if matrix.shape not in ((3, 3), (4, 4)):
        raise ValueError(f"Matrix must be 3x3 or 4x4, got {matrix.shape}.")
    matrix = np_matrix_normalized(matrix)
    y = -np.arcsin(matrix[2, 0])
    cos_y = np.cos(y)
    x = np.arctan2(matrix[2, 1] / cos_y, matrix[2, 2] / cos_y)
    z = np.arctan2(matrix[1, 0] / cos_y, matrix[0, 0] / cos_y)
    return (x, y, z)


def np_normal(vectors: SequenceOfVectors) -> np.ndarray:
    assert len(vectors) == 3, "3 vectors required"
    verts_np = np.array(vectors[:3])
    v0, v1, v2 = verts_np[:3]
    edge1 = v1 - v0
    edge2 = v2 - v0
    normal = np.cross(edge1, edge2)
    norm = np.linalg.norm(normal)
    return normal / norm


def np_intersect_line_line(
    v1: VectorType, v2: VectorType, v3: VectorType, v4: VectorType
) -> tuple[np.ndarray, np.ndarray]:
    d1 = np.subtract(v2, v1)
    d2 = np.subtract(v4, v3)
    cross_d1_d2 = np.cross(d1, d2)
    cross_d1_d2_norm: float = np.linalg.norm(cross_d1_d2)
    if is_x(cross_d1_d2_norm, 0):
        raise ValueError("Lines are parallel and do not intersect uniquely.")
    r = np.subtract(v3, v1)
    t = np.dot(np.cross(r, d2), cross_d1_d2) / (cross_d1_d2_norm**2)
    u = np.dot(np.cross(r, d1), cross_d1_d2) / (cross_d1_d2_norm**2)
    point_on_line1 = v1 + t * d1
    point_on_line2 = v3 + u * d2
    return point_on_line1, point_on_line2


def intersect_x_axis_2d(p1: VectorType, p2: VectorType, y=0) -> Optional[float]:
    x1, y1 = p1
    x2, y2 = p2
    if is_x(y1, y2):
        return
    t = (y - y1) / (y2 - y1)
    return x1 + t * (x2 - x1)
