# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


def create_model():
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    return model, context


def create_product(model, context, item):
    representation = model.createIfcShapeRepresentation(
        context, "Body", "GeometricSet", [model.createIfcGeometricSet([item])]
    )
    return model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        ObjectPlacement=model.createIfcLocalPlacement(
            None, model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
        ),
        Representation=model.createIfcProductDefinitionShape(None, None, [representation]),
    )


def test_surface_of_revolution_of_open_profile_is_a_sheet():
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10336
    # A 100 mm line revolved about a parallel axis 100 mm away is a cylinder
    # sheet without end caps, as product #69 in IfcArbitraryOpenProfileDef.ifc.
    model, context = create_model()
    profile = model.createIfcArbitraryOpenProfileDef(
        "CURVE",
        None,
        model.createIfcPolyline(
            [model.createIfcCartesianPoint((-50.0, 0.0)), model.createIfcCartesianPoint((50.0, 0.0))]
        ),
    )
    surface = model.createIfcSurfaceOfRevolution(
        profile,
        model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        model.createIfcAxis1Placement(
            model.createIfcCartesianPoint((0.0, 100.0, 0.0)), model.createIfcDirection((1.0, 0.0, 0.0))
        ),
    )
    product = create_product(model, context, surface)

    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), product)

    assert ifcopenshell.util.shape.get_area(shape.geometry) == pytest.approx(2 * math.pi * 0.1 * 0.1, rel=0.01)


def test_open_profile_of_an_arc_is_an_open_loop():
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10336
    # A half ellipse, as products #146 and #156 in IfcArbitraryOpenProfileDef.ifc,
    # is mapped to an open loop, so that it is swept as a wire and not closed
    # into the area under the arc.
    model, context = create_model()
    ellipse = model.createIfcEllipse(
        model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0))), 50.0, 25.0
    )
    curve = model.createIfcTrimmedCurve(
        ellipse,
        [model.createIfcCartesianPoint((50.0, 0.0))],
        [model.createIfcCartesianPoint((-50.0, 0.0))],
        True,
        "CARTESIAN",
    )
    profile = model.createIfcArbitraryOpenProfileDef("CURVE", None, curve)

    item = ifcopenshell.geom.map_shape(ifcopenshell.geom.settings(), profile)

    assert type(item).__name__ == "loop"
    assert item.closed is False
