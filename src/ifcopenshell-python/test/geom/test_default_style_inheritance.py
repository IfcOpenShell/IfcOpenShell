# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid


def test_subtype_inherits_supertype_default_style_473():
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 1.0, 1.0)
    solid = model.createIfcExtrudedAreaSolid(profile, None, model.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    slab = model.createIfcSlabStandardCase(
        ifcopenshell.guid.new(),
        None,
        None,
        None,
        None,
        model.createIfcLocalPlacement(None, origin),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), slab)
    assert [m.name for m in shape.geometry.materials] == ["IfcSlab"]
