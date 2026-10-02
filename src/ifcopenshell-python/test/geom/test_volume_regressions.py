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


def test_shared_composite_curve_segment_with_reversed_sense_keeps_its_shape_8050():
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment(
        [
            model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            model.createIfcSIUnit(None, "PLANEANGLEUNIT", None, "RADIAN"),
        ]
    )
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    radius = 0.2

    def point(x, y):
        return model.createIfcCartesianPoint((x, y))

    def line_segment(start, end):
        curve = model.createIfcPolyline([point(*start), point(*end)])
        return model.createIfcCompositeCurveSegment("CONTINUOUS", True, curve)

    corner = model.createIfcAxis2Placement2D(point(1.0, 1.0), model.createIfcDirection((1.0, 0.0)))
    arc = model.createIfcTrimmedCurve(
        model.createIfcCircle(corner, radius),
        [model.createIfcParameterValue(math.pi)],
        [model.createIfcParameterValue(1.5 * math.pi)],
        True,
        "PARAMETER",
    )
    shared_segments = [
        line_segment((0.0, 0.0), (1.0, 0.0)),
        line_segment((1.0, 0.0), (1.0, 1.0 - radius)),
        model.createIfcCompositeCurveSegment("CONTINUOUS", False, arc),
        line_segment((1.0 - radius, 1.0), (0.0, 1.0)),
        line_segment((0.0, 1.0), (0.0, 0.0)),
    ]
    depths = {}
    for i in range(2):
        profile = model.createIfcArbitraryClosedProfileDef(
            "AREA", None, model.createIfcCompositeCurve(shared_segments, False)
        )
        solid = model.createIfcExtrudedAreaSolid(
            profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 2.0 + 0.5 * i
        )
        representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
        product = model.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(),
            None,
            f"Beam{i}",
            None,
            None,
            model.createIfcLocalPlacement(
                None, model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((3.0 * i, 0.0, 0.0)))
            ),
            model.createIfcProductDefinitionShape(None, None, [representation]),
        )
        depths[product.id()] = 2.0 + 0.5 * i

    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    iterator = ifcopenshell.geom.iterator(settings, model, 1, geometry_library="opencascade")
    volumes = {}
    assert iterator.initialize()
    while True:
        shape = iterator.get()
        volumes[shape.id] = ifcopenshell.util.shape.get_volume(shape.geometry)
        if not iterator.next():
            break

    area = 1.0 - math.pi * radius**2 / 4
    assert set(volumes) == set(depths)
    for product_id, depth in depths.items():
        assert volumes[product_id] == pytest.approx(area * depth, rel=0.002)


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
