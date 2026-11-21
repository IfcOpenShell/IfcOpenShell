# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_cut_that_removes_nothing_is_retried_5630():
    path = Path(__file__).parent.parent / "fixtures/geom/boolean_noop_cut_5630.ifc"
    model = ifcopenshell.open(path)
    terrain = model.by_guid("2wL7jYuq59KQKwqwB9u81u")
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, terrain, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(6058.593, rel=1e-4)
