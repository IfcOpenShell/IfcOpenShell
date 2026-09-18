# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace

import numpy as np
import pytest

import ifcopenshell.util.shape


@pytest.fixture
def rectangle_geometry():
    vertices = np.array(((0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0)), dtype=np.float64)

    def create(faces):
        faces = np.array(faces, dtype=np.int32)
        return SimpleNamespace(verts_buffer=vertices.tobytes(), faces_buffer=faces.tobytes())

    return create


@pytest.mark.parametrize(
    "function", (ifcopenshell.util.shape.get_side_area, ifcopenshell.util.shape.get_footprint_area)
)
@pytest.mark.parametrize(
    ("faces", "expected_area"),
    (
        (((0, 1, 2), (0, 2, 3)), 2.0),
        (((0, 2, 1), (0, 3, 2)), 0.0),
    ),
)
def test_area_respects_winding_by_default(function, rectangle_geometry, faces, expected_area):
    assert function(rectangle_geometry(faces), axis="Z") == pytest.approx(expected_area)


@pytest.mark.parametrize(
    "function", (ifcopenshell.util.shape.get_side_area, ifcopenshell.util.shape.get_footprint_area)
)
@pytest.mark.parametrize("faces", (((0, 1, 2), (0, 2, 3)), ((0, 2, 1), (0, 3, 2))))
def test_area_can_ignore_winding(function, rectangle_geometry, faces):
    assert function(rectangle_geometry(faces), axis="Z", ignore_winding=True) == pytest.approx(2.0)
