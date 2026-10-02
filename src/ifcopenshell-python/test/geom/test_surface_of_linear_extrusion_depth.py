# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid


@pytest.mark.parametrize(
    "unit_prefix, depth, expected",
    [(None, 5.0, 5.0), ("MILLI", 5.0, 0.005)],
    ids=["metre", "millimetre"],
)
def test_surface_of_linear_extrusion_depth(unit_prefix, depth, expected):
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", unit_prefix, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    profile = model.createIfcArbitraryOpenProfileDef(
        "CURVE",
        None,
        model.createIfcPolyline([model.createIfcCartesianPoint((0.0, 0.0)), model.createIfcCartesianPoint((1.0, 0.0))]),
    )
    surface = model.createIfcSurfaceOfLinearExtrusion(
        profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), depth
    )

    item = ifcopenshell.geom.map_shape(ifcopenshell.geom.settings(), surface)

    assert item.depth == pytest.approx(expected)
