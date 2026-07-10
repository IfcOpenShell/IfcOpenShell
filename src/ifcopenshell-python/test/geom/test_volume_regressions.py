# This file was generated with the assistance of an AI coding tool.

import math
from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
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


def revolved_square_volume(end_half_size):
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

    def square(half_size):
        position = model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((1.5, 0.0)))
        return model.createIfcRectangleProfileDef("AREA", None, position, 2 * half_size, 2 * half_size)

    axis = model.createIfcAxis1Placement(
        model.createIfcCartesianPoint((0.0, 0.0, 0.0)), model.createIfcDirection((0.0, 1.0, 0.0))
    )
    if end_half_size is None:
        solid = model.createIfcRevolvedAreaSolid(square(0.5), placement, axis, math.pi / 2)
    else:
        solid = model.createIfcRevolvedAreaSolidTapered(
            square(0.5), placement, axis, math.pi / 2, square(end_half_size)
        )
    representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    product = model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        None,
        "Revolve",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade")
    return ifcopenshell.util.shape.get_volume(shape.geometry)


@pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("opencascade"), reason="opencascade geometry kernel is unavailable"
)
@pytest.mark.parametrize("end_half_size", [None, 0.5, 0.25], ids=["plain", "same_end", "half_end"])
def test_revolved_area_solid_tapered_volume_3540(end_half_size):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/3540
    end = 0.5 if end_half_size is None else end_half_size
    expected = math.pi * (0.5**2 + 0.5 * end + end**2)
    assert revolved_square_volume(end_half_size) == pytest.approx(expected, rel=0.02)


@pytest.mark.parametrize("axis_first", [True, False], ids=["axis_first", "body_first"])
def test_create_shape_prefers_body_over_axis_9771(axis_first):
    model = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model)
    model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
    axis_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Axis",
        target_view="GRAPH_VIEW",
        parent=model_context,
    )
    body_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )
    column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
    points = [model.createIfcCartesianPoint((0.0, 0.0, 0.0)), model.createIfcCartesianPoint((0.0, 0.0, 3.0))]
    axis = model.createIfcShapeRepresentation(axis_context, "Axis", "Curve3D", [model.createIfcPolyline(points)])
    body = ifcopenshell.api.geometry.add_profile_representation(
        model,
        context=body_context,
        profile=model.createIfcRectangleProfileDef("AREA", None, None, 0.3, 0.5),
        depth=3.0,
    )
    representations = [axis, body] if axis_first else [body, axis]
    column.Representation = model.createIfcProductDefinitionShape(Representations=representations)
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), column)
    assert len(shape.geometry.verts) // 3 == 8
