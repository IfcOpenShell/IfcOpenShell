# This file was generated with the assistance of an AI coding tool.


import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


def clipped_wall_volume(library, origin, normal, ref_direction, agreement, polygonal):
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    profile = model.createIfcRectangleProfileDef(
        "AREA", None, model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((2.5, 0.0))), 5.0, 0.2
    )
    wall = model.createIfcExtrudedAreaSolid(profile, placement, model.createIfcDirection((0.0, 0.0, 1.0)), 2.8)
    plane = model.createIfcPlane(
        model.createIfcAxis2Placement3D(
            model.createIfcCartesianPoint(origin),
            model.createIfcDirection(normal),
            model.createIfcDirection(ref_direction),
        )
    )
    if polygonal:
        corners = [(-1.0, -1.0), (6.0, -1.0), (6.0, 1.0), (-1.0, 1.0), (-1.0, -1.0)]
        boundary = model.createIfcPolyline([model.createIfcCartesianPoint(c) for c in corners])
        half_space = model.createIfcPolygonalBoundedHalfSpace(plane, agreement, placement, boundary)
    else:
        half_space = model.createIfcHalfSpaceSolid(plane, agreement)
    clipping = model.createIfcBooleanClippingResult("DIFFERENCE", wall, half_space)
    representation = model.createIfcShapeRepresentation(context, "Body", "Clipping", [clipping])
    product = model.createIfcWall(
        ifcopenshell.guid.new(),
        None,
        "Wall",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library=library)
    return ifcopenshell.util.shape.get_volume(shape.geometry)


@pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("manifold") or not ifcopenshell.geom.has_geometry_library("opencascade"),
    reason="requires the manifold and OpenCASCADE kernels",
)
@pytest.mark.parametrize("polygonal", [False, True], ids=["unbounded", "polygonal"])
@pytest.mark.parametrize(
    "origin,normal,ref_direction,agreement",
    [
        ((0.0, 0.0, 2.4), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), True),
        ((0.0, 0.0, 2.4), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), False),
        ((0.0, 0.0, 2.4), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), True),
        ((0.0, 0.0, 2.4), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), False),
        ((0.0, 0.0, 2.8), (0.08 / 5.0, 0.0, 1.0), (1.0, 0.0, -0.08 / 5.0), False),
    ],
    ids=["down_true", "up_false", "up_true", "down_false", "inclined_up_false"],
)
def test_manifold_half_space_clipping_matches_opencascade_9767(origin, normal, ref_direction, agreement, polygonal):
    expected = clipped_wall_volume("opencascade", origin, normal, ref_direction, agreement, polygonal)
    actual = clipped_wall_volume("manifold", origin, normal, ref_direction, agreement, polygonal)
    assert actual == pytest.approx(expected, abs=1e-3)


@pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("manifold") or not ifcopenshell.geom.has_geometry_library("opencascade"),
    reason="requires the manifold and OpenCASCADE kernels",
)
def test_manifold_vertical_half_space_clipping_matches_opencascade_9767():
    args = ((4.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), False, False)
    expected = clipped_wall_volume("opencascade", *args)
    actual = clipped_wall_volume("manifold", *args)
    assert actual == pytest.approx(expected, abs=1e-3)
