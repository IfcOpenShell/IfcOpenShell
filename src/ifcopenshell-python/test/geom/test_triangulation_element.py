# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom


@pytest.mark.parametrize("verts, faces", [([], []), ([0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0], [0, 1, 2])])
def test_triangulation_element_from_element(verts, faces):
    settings = ifcopenshell.geom.settings()
    wrapper = ifcopenshell.ifcopenshell_wrapper
    file = ifcopenshell.file()
    wall = file.createIfcWall()
    guid = ifcopenshell.guid.new()

    shape = wrapper.triangulation_element(
        wrapper.element(settings, wall.id(), -1, "", wall.is_a(), guid, "Body", None, wall),
        wrapper.triangulation(settings, wall.is_a(), f"shape-{wall.id()}", verts, faces, [], [], [], [], [], [], []),
    )

    assert shape.id == wall.id()
    assert shape.parent_id == -1
    assert shape.type == wall.is_a()
    assert shape.guid == guid
    assert shape.context == "Body"
    assert shape.geometry.id == f"shape-{wall.id()}"
    assert shape.geometry.verts == tuple(verts)
    assert shape.geometry.faces == tuple(faces)
    assert shape.transformation.matrix == (
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    )
