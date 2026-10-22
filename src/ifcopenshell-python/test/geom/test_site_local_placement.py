# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid


def test_nested_sites_keep_relative_positions_6102():
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)

    def placement(parent, x):
        point = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((x, 0.0, 0.0)))
        return model.createIfcLocalPlacement(parent, point)

    root = placement(None, 100.0)
    model.createIfcSite(ifcopenshell.guid.new(), None, "Root", None, None, root)
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 1.0, 1.0)
    solid = model.createIfcExtrudedAreaSolid(profile, None, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    shape = model.createIfcProductDefinitionShape(
        None, None, [model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])]
    )
    proxies = []
    for x in (10.0, 30.0):
        sub = placement(root, x)
        model.createIfcSite(ifcopenshell.guid.new(), None, "Sub", None, None, sub)
        proxies.append(
            model.createIfcBuildingElementProxy(
                ifcopenshell.guid.new(), None, None, None, None, placement(sub, 0.0), shape
            )
        )
    settings = ifcopenshell.geom.settings()
    settings.set("site-local-placement", True)
    xs = [ifcopenshell.geom.create_shape(settings, p).transformation.matrix[12] for p in proxies]
    assert xs == pytest.approx([10.0, 30.0])
