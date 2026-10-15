# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W


@pytest.fixture
def model():
    model = ifcopenshell.file(schema="IFC4")
    profile = model.createIfcRectangleHollowProfileDef("AREA", None, None, 1.0, 1.0, 0.1, None, None)
    model.createIfcExtrudedAreaSolid(profile, None, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    return model


def test_cgal_polyhedron_with_holes_5485(model):
    settings = ifcopenshell.geom.settings(TRIANGULATION_TYPE=W.POLYHEDRON_WITH_HOLES)
    shape = ifcopenshell.geom.create_shape(settings, model.by_type("IfcExtrudedAreaSolid")[0], geometry_library="cgal")
    assert sorted(map(len, shape.faces)) == [1] * 8 + [2] * 2


def test_cgal_polyhedron_without_holes_5485(model):
    settings = ifcopenshell.geom.settings(TRIANGULATION_TYPE=W.POLYHEDRON_WITHOUT_HOLES)
    shape = ifcopenshell.geom.create_shape(settings, model.by_type("IfcExtrudedAreaSolid")[0], geometry_library="cgal")
    sizes = [len(f) for f in shape.faces]
    assert sizes.count(4) == 8
    assert set(sizes) == {3, 4}
