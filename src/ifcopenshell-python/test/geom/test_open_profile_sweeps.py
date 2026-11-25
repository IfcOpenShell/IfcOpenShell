# This file was generated with the assistance of an AI coding tool.
import math

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape


def make_model():
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    placement = model.createIfcAxis2Placement3D(origin)
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment(
        [
            model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            model.createIfcSIUnit(None, "PLANEANGLEUNIT", None, "RADIAN"),
        ]
    )
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    return model, context, placement


def open_profile(model, points):
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in points])
    return model.createIfcArbitraryOpenProfileDef("CURVE", None, polyline)


def product_with(model, context, placement, item):
    representation = model.createIfcShapeRepresentation(context, "Body", "SurfaceModel", [item])
    return model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        None,
        "Sheet",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )


def geometry_of(product, geometry_library="opencascade"):
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    return ifcopenshell.geom.create_shape(settings, product, geometry_library=geometry_library).geometry


def boundary_edge_count(geometry):
    faces = ifcopenshell.util.shape.get_faces(geometry)
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    return int(np.sum(counts == 1))


def test_surface_of_revolution_of_an_open_profile_is_a_shell():
    model, context, placement = make_model()
    axis = model.createIfcAxis1Placement(
        model.createIfcCartesianPoint((0.0, 0.0, 0.0)), model.createIfcDirection((0.0, 1.0, 0.0))
    )
    surface = model.createIfcSurfaceOfRevolution(open_profile(model, [(1.0, 0.0), (1.0, 0.5)]), placement, axis)
    geometry = geometry_of(product_with(model, context, placement, surface))
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(2 * math.pi * 1.0 * 0.5, rel=1e-2)
    assert boundary_edge_count(geometry) > 0


def test_surface_of_linear_extrusion_of_an_open_profile_is_a_ribbon():
    model, context, placement = make_model()
    direction = model.createIfcDirection((0.0, 0.0, 1.0))
    surface = model.createIfcSurfaceOfLinearExtrusion(
        open_profile(model, [(0.0, 0.0), (1.0, 0.0)]), placement, direction, 0.5
    )
    geometry = geometry_of(product_with(model, context, placement, surface))
    assert len(ifcopenshell.util.shape.get_vertices(geometry)) == 4
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(0.5)
    assert boundary_edge_count(geometry) == 4


def test_surface_of_linear_extrusion_of_a_single_arc_is_a_shell():
    model, context, placement = make_model()
    circle = model.createIfcCircle(model.createIfcAxis2Placement2D(model.createIfcCartesianPoint((0.0, 0.0))), 1.0)
    arc = model.createIfcTrimmedCurve(
        circle, [model.createIfcParameterValue(0.0)], [model.createIfcParameterValue(math.pi / 2)], True, "PARAMETER"
    )
    profile = model.createIfcArbitraryOpenProfileDef("CURVE", None, arc)
    direction = model.createIfcDirection((0.0, 0.0, 1.0))
    surface = model.createIfcSurfaceOfLinearExtrusion(profile, placement, direction, 1.0)
    geometry = geometry_of(product_with(model, context, placement, surface))
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(math.pi / 2, rel=1e-2)
    assert boundary_edge_count(geometry) > 0


def test_surface_of_linear_extrusion_of_a_closed_curve_is_an_open_tube():
    model, context, placement = make_model()
    square = model.createIfcPolyline(
        [model.createIfcCartesianPoint(p) for p in [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]]
    )
    profile = model.createIfcArbitraryClosedProfileDef("CURVE", None, square)
    direction = model.createIfcDirection((0.0, 0.0, 1.0))
    surface = model.createIfcSurfaceOfLinearExtrusion(profile, placement, direction, 1.0)
    geometry = geometry_of(product_with(model, context, placement, surface))
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(4.0)
    assert boundary_edge_count(geometry) == 8


def test_cgal_kernel_rejects_a_swept_surface_instead_of_closing_it():
    model, context, placement = make_model()
    direction = model.createIfcDirection((0.0, 0.0, 1.0))
    surface = model.createIfcSurfaceOfLinearExtrusion(
        open_profile(model, [(0.0, 0.0), (1.0, 0.0)]), placement, direction, 0.5
    )
    product = product_with(model, context, placement, surface)
    with pytest.raises(RuntimeError):
        geometry_of(product, geometry_library="cgal")
