# This file was generated with the assistance of an AI coding tool.

import math
from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


@pytest.mark.parametrize("axis", [0, 2], ids=["x", "z"])
@pytest.mark.parametrize("reverse", [False, True], ids=["forward", "reverse"])
@pytest.mark.parametrize("offset", [0.0, 10.0], ids=["origin", "translated"])
def test_swept_disk_volume_9571(axis, reverse, offset):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/9571
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    start = [offset, offset, offset]
    end = start.copy()
    end[axis] += 1.0
    points = [start, end][::-1] if reverse else [start, end]
    directrix = model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in points])
    radius = 0.008
    solid = model.createIfcSweptDiskSolid(directrix, radius, None, None, None)
    representation = model.createIfcShapeRepresentation(context, "Body", "AdvancedSweptSolid", [solid])
    product = model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        None,
        "Bar",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade")
    # Default tessellation underestimates this small circular section by about 1%.
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(math.pi * radius**2, rel=0.02)


@pytest.mark.parametrize("deflection", [1e-3, 1e-4], ids=["default", "fine"])
def test_advanced_brep_through_hole_volume_9570(deflection):
    # Preserve the reported edge loops, seam, bound orientations and SameSense values.
    path = Path(__file__).parent.parent / "fixtures/geom/advanced_brep_through_hole_9570.ifc"
    model = ifcopenshell.open(path)
    product = model.by_type("IfcBuildingElementProxy")[0]
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    settings.set("mesher-linear-deflection", deflection)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade")
    expected = 1.0 * 0.8 * 0.6 - math.pi * 0.15**2 * 0.6
    # Allow tessellation error, but reject the reported 12.9% excess volume.
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(expected, rel=0.005)
