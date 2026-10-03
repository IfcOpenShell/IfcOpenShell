# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_batched_openings_fall_back_to_sequential_cuts_4118():
    path = Path(__file__).parent.parent / "fixtures/geom/boolean_sequential_cut_4118.ifc"
    model = ifcopenshell.open(path)
    wall = model.by_guid("hON7WSrHHnTkfOmLpZvgHF")
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, wall, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(21.487, rel=1e-4)
