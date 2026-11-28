# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_2d_partitioned_cut_keeps_all_openings_5186():
    path = Path(__file__).parent.parent / "fixtures/geom/boolean_2d_partition_5186.ifc"
    model = ifcopenshell.open(path)
    plate = model.by_guid("1WBDhI_tDBTwvxTS1DmXvO")
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, plate, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(0.004051, rel=1e-3)
