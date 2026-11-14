# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


@pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("opencascade"),
    reason="opencascade geometry kernel is unavailable",
)
@pytest.mark.parametrize("hole", [(0.9, 2.3), (-0.1, 0.9), (1.8, 2.8)], ids=["middle", "bottom", "top"])
def test_swept_disk_opening_volume_9256(hole):
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    length = 2.7
    radius = 0.016
    directrix = model.createIfcPolyline(
        [model.createIfcCartesianPoint((0.0, 0.0, 0.0)), model.createIfcCartesianPoint((0.0, 0.0, length))]
    )
    solid = model.createIfcSweptDiskSolid(directrix, radius, None, None, None)
    bar = model.createIfcReinforcingBar(
        ifcopenshell.guid.new(),
        None,
        "Bar",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(
            None, None, [model.createIfcShapeRepresentation(context, "Body", "AdvancedSweptSolid", [solid])]
        ),
    )
    profile = model.createIfcRectangleProfileDef(
        "AREA", None, model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0))), 1.2, 0.5
    )
    extrusion = model.createIfcExtrudedAreaSolid(
        profile,
        model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, hole[0]))),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        hole[1] - hole[0],
    )
    opening = model.createIfcOpeningElement(
        ifcopenshell.guid.new(),
        None,
        "Hole",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(
            None, None, [model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])]
        ),
    )
    model.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, None, None, bar, opening)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    shape = ifcopenshell.geom.create_shape(settings, bar, geometry_library="opencascade")
    kept = length - (min(hole[1], length) - max(hole[0], 0.0))
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(math.pi * radius**2 * kept, rel=0.02)
