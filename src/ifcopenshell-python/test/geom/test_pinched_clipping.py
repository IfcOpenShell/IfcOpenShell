# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_clipping_whose_bound_touches_a_wall_face_is_applied():
    # A wall end is clipped by a vertical plane turned 18.7 degrees off the wall axis,
    # between 1.4 m and 1.75 m up. The polygonal bound of the half-space is as wide as the
    # wall is thick, so one of its sides lies exactly on the outer face and the clipped
    # solid touches itself along the line where the plane meets that face (#619).
    length, thickness, height = 2.0, 0.25, 2.43
    apex_x, bottom, notch_height = 0.20243167440119, 1.4, 0.35
    nx, ny = 0.947284187399111, 0.320394550989254
    bound_width = thickness / nx

    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    z = model.createIfcDirection((0.0, 0.0, 1.0))
    profile = model.createIfcRectangleProfileDef(
        "AREA",
        None,
        model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((length / 2.0, 0.0))),
        length,
        thickness,
    )
    wall = model.createIfcExtrudedAreaSolid(profile, model.createIfcAxis2Placement3D(origin), z, height)
    position = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((apex_x, thickness / 2.0, bottom)), model.createIfcDirection((nx, ny, 0.0)), z
    )
    bound = model.createIfcPolyline(
        [
            model.createIfcCartesianPoint(p)
            for p in [(0.0, 0.0), (notch_height, 0.0), (notch_height, bound_width), (0.0, bound_width), (0.0, 0.0)]
        ]
    )
    half_space = model.createIfcPolygonalBoundedHalfSpace(model.createIfcPlane(position), True, position, bound)
    clipped = model.createIfcBooleanClippingResult("DIFFERENCE", wall, half_space)

    # In plan the removed piece is the quadrilateral between the wall end, the inner face,
    # the clipping plane and the side of the bound through the apex, which is perpendicular to it.
    half = thickness / 2.0
    plan = [
        (apex_x, half),
        (apex_x + thickness * ny / nx, -half),
        (0.0, -half),
        (0.0, half - apex_x * ny / nx),
    ]
    removed = 0.5 * abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(plan, plan[1:] + plan[:1])))
    expected = length * thickness * height - removed * notch_height

    settings = ifcopenshell.geom.settings()
    geometry = ifcopenshell.geom.create_shape(settings, clipped, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(expected, rel=1e-6)
