# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_profile_of_lines_trimmed_against_their_direction_extrudes_to_the_authored_volume():
    # Advance Steel writes every line of a profile with its direction pointing from Trim2
    # back to Trim1 while keeping SenseAgreement true, so Trim2 lies at parameter -1. The
    # segment still has to run from Trim1 to Trim2 or the profile falls apart (test file 762).
    width, height, depth = 0.084, 0.343, 1.07
    corners = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]

    model = ifcopenshell.file(schema="IFC4")
    segments = []
    for start, end in zip(corners, corners[1:] + corners[:1]):
        length = abs(end[0] - start[0]) + abs(end[1] - start[1])
        backwards = ((start[0] - end[0]) / length, (start[1] - end[1]) / length)
        line = model.createIfcLine(
            model.createIfcCartesianPoint(start),
            model.createIfcVector(model.createIfcDirection(backwards), length),
        )
        trimmed = model.createIfcTrimmedCurve(
            line, [model.createIfcCartesianPoint(start)], [model.createIfcCartesianPoint(end)], True, "CARTESIAN"
        )
        segments.append(model.createIfcCompositeCurveSegment("CONTINUOUS", True, trimmed))
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, model.createIfcCompositeCurve(segments, False))
    solid = model.createIfcExtrudedAreaSolid(
        profile,
        model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        model.createIfcDirection((0.0, 0.0, 1.0)),
        depth,
    )

    settings = ifcopenshell.geom.settings()
    geometry = ifcopenshell.geom.create_shape(settings, solid, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(width * height * depth, rel=1e-6)
    assert "GEO208" not in ifcopenshell.get_log()
