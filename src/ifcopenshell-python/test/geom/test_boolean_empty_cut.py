# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_implausible_empty_cut_does_not_erase_element_5779():
    path = Path(__file__).parent.parent / "fixtures/geom/boolean_empty_cut_5779.ifc"
    model = ifcopenshell.open(path)
    member = model.by_guid("0FVvn8$6P4YPtgToXsYJFv")
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, member, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(shape.geometry) > 1e-4
