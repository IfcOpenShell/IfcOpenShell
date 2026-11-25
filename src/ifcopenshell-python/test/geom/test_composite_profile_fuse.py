# This file was generated with the assistance of an AI coding tool.

import collections
import os

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def test_opening_through_a_composite_profile_of_touching_layers_leaves_a_closed_solid():
    # An ArchiCAD style composite wall: two layers side by side and a thin strip on the back
    # face, all touching. Extruded as separate solids with coincident faces, an opening cut
    # across the layer boundaries leaves open edges and, with more openings, failed booleans
    # (test file 793). The touching profiles must extrude into a single solid.
    length, height = 2.0, 1.0
    layers = [(0.0, 0.15), (0.15, 0.3)]
    strip = (0.3, 0.315, 0.4, 0.45)  # x0, x1, y0, y1 on the back of the second layer
    hole_z, hole_length, hole_y, hole_height = 0.5, 0.5, 0.3, 0.3

    model = ifcopenshell.file(schema="IFC4")

    def polygon(points):
        points = [model.createIfcCartesianPoint(p) for p in points]
        return model.createIfcArbitraryClosedProfileDef("AREA", None, model.createIfcPolyline(points + points[:1]))

    profiles = [polygon([(x0, 0.0), (x1, 0.0), (x1, height), (x0, height)]) for x0, x1 in layers]
    x0, x1, y0, y1 = strip
    profiles.append(polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
    composite = model.createIfcCompositeProfileDef("AREA", None, profiles)

    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    z = model.createIfcDirection((0.0, 0.0, 1.0))
    wall = model.createIfcExtrudedAreaSolid(composite, origin, z, length)
    hole_profile = model.createIfcRectangleProfileDef(
        "AREA",
        None,
        model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.15, hole_y + hole_height / 2.0))),
        0.6,
        hole_height,
    )
    hole = model.createIfcExtrudedAreaSolid(
        hole_profile, model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, hole_z))), z, hole_length
    )
    result = model.createIfcBooleanResult("DIFFERENCE", wall, hole)

    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    geometry = ifcopenshell.geom.create_shape(settings, result, geometry_library="opencascade")

    faces = geometry.faces
    edges = collections.Counter()
    for a, b, c in zip(faces[0::3], faces[1::3], faces[2::3]):
        for p, q in ((a, b), (b, c), (c, a)):
            edges[(min(p, q), max(p, q))] += 1
    assert all(count == 2 for count in edges.values())

    solid = (
        sum((x1 - x0) * height for x0, x1 in layers) * length + (strip[1] - strip[0]) * (strip[3] - strip[2]) * length
    )
    removed = hole_length * (hole_height * layers[-1][1] + (strip[1] - strip[0]) * (strip[3] - strip[2]))
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(solid - removed, rel=1e-6)


def test_a_scaled_derived_profile_touching_a_mirrored_profile_extrudes_into_closed_solids():
    # The T profile of this composite is scaled by a derived profile, which converts it onto a
    # B-spline surface, and its web tip touches the leg of a mirrored L profile. The fuse
    # connects the two faces without unifying them, and extruding both leaves a side face
    # shared by two solids. Such profiles must be extruded one by one, as closed solids.
    path = os.path.join(os.path.dirname(__file__), "../../../../test/input/IfcCompositeProfileDef.ifc")
    model = ifcopenshell.open(path)
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    geometry = ifcopenshell.geom.create_shape(settings, model.by_id(66), geometry_library="opencascade").geometry

    faces = geometry.faces
    edges = collections.Counter()
    for a, b, c in zip(faces[0::3], faces[1::3], faces[2::3]):
        for p, q in ((a, b), (b, c), (c, a)):
            edges[(min(p, q), max(p, q))] += 1
    assert all(count == 2 for count in edges.values())
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(2.6537e-05, rel=1e-3)
