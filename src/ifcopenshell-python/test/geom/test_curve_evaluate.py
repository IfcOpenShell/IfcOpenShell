# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Tests for evaluate(derivative, u) on the curves, edges and loops of the geometry taxonomy.

Where to_polygon() can sample the item, evaluate() has to give the same points at the parameters
of the polygon's vertices. Derivatives are compared to central differences of the order below.
"""

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
from ifcopenshell import ifcopenshell_wrapper as W

SETTINGS = ifcopenshell.geom.settings()
STEP = 1e-5


@pytest.fixture
def model():
    model = ifcopenshell.file(schema="IFC4")
    units = [
        model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
        model.createIfcSIUnit(None, "PLANEANGLEUNIT", None, "RADIAN"),
    ]
    model.createIfcProject(ifcopenshell.guid.new(), UnitsInContext=model.createIfcUnitAssignment(units))
    return model


def point(model, *coordinates):
    return model.createIfcCartesianPoint([float(c) for c in coordinates])


def placement(model, location=(1.0, 2.0, 3.0), axis=(1.0, 1.0, 1.0), ref_direction=(1.0, -1.0, 0.0)):
    return model.createIfcAxis2Placement3D(
        point(model, *location), model.createIfcDirection(axis), model.createIfcDirection(ref_direction)
    )


def map_shape(curve):
    return ifcopenshell.geom.map_shape(SETTINGS, curve)


def evaluate(item, derivative, u):
    return np.array(item.evaluate(derivative, u))


def assert_derivatives_follow(item, u, orders=(1, 2)):
    for order in orders:
        difference = (evaluate(item, order - 1, u + STEP) - evaluate(item, order - 1, u - STEP)) / (2 * STEP)
        assert np.allclose(evaluate(item, order, u), difference, atol=1e-6)


def assert_follows_polygon(item, polygon, end):
    count = len(polygon) - 1
    assert count >= 1
    for i, vertex in enumerate(polygon):
        assert np.allclose(evaluate(item, 0, end * i / count), vertex, atol=1e-9)


def assert_loop_follows_polygon(loop):
    for i, edge in enumerate(loop.children):
        polygon = edge.to_polygon(SETTINGS)
        count = len(polygon) - 1
        for j, vertex in enumerate(polygon):
            assert np.allclose(evaluate(loop, 0, i + j / count), vertex, atol=1e-9)
    polygon = np.array(loop.to_polygon(SETTINGS))
    assert np.allclose(evaluate(loop, 0, 0.0), polygon[0], atol=1e-9)
    assert np.allclose(evaluate(loop, 0, float(len(loop.children))), polygon[-1], atol=1e-9)


def test_line(model):
    line = map_shape(
        model.createIfcLine(
            point(model, 1, 2, 3), model.createIfcVector(model.createIfcDirection((0.0, 3.0, 4.0)), 2.0)
        )
    )
    assert np.allclose(evaluate(line, 0, 0.0), (1.0, 2.0, 3.0))
    assert np.allclose(evaluate(line, 0, 5.0), (1.0, 5.0, 7.0))
    assert np.allclose(evaluate(line, 1, 5.0), (0.0, 0.6, 0.8))
    assert np.allclose(evaluate(line, 2, 5.0), 0.0)
    polygon = line.to_polygon(SETTINGS, -2.0, 6.0, 4)
    for i, vertex in enumerate(polygon):
        assert np.allclose(evaluate(line, 0, -2.0 + 8.0 * i / 4), vertex)


def test_circle(model):
    circle = map_shape(model.createIfcCircle(placement(model), 2.0))
    assert_follows_polygon(circle, circle.to_polygon(SETTINGS), 2 * np.pi)
    centre = np.array((1.0, 2.0, 3.0))
    for u in (0.0, 0.7, 4.0):
        radial = evaluate(circle, 0, u) - centre
        assert np.isclose(np.linalg.norm(radial), 2.0)
        assert np.isclose(radial @ (1.0, 1.0, 1.0), 0.0)
        assert np.isclose(np.linalg.norm(evaluate(circle, 1, u)), 2.0)
        assert np.isclose(evaluate(circle, 1, u) @ radial, 0.0)
        assert np.allclose(evaluate(circle, 2, u), -radial)
        assert_derivatives_follow(circle, u, orders=(1, 2, 3, 4))


@pytest.mark.parametrize("semi_axes", ((3.0, 1.5), (1.5, 3.0)))
def test_ellipse(model, semi_axes):
    ellipse = map_shape(model.createIfcEllipse(placement(model), *semi_axes))
    assert_follows_polygon(ellipse, ellipse.to_polygon(SETTINGS), 2 * np.pi)
    x = np.array((1.0, -1.0, 0.0)) / np.sqrt(2)
    y = np.cross(np.array((1.0, 1.0, 1.0)) / np.sqrt(3), x)
    for u in (0.0, 0.7, 4.0):
        local = evaluate(ellipse, 0, u) - (1.0, 2.0, 3.0)
        assert np.isclose((local @ x / semi_axes[0]) ** 2 + (local @ y / semi_axes[1]) ** 2, 1.0)
        assert_derivatives_follow(ellipse, u)


def bspline_reference(control_points, weights, knots, degree, u):
    def basis(i, p):
        if p == 0:
            return 1.0 if knots[i] <= u < knots[i + 1] else 0.0
        value = 0.0
        if knots[i + p] > knots[i]:
            value += (u - knots[i]) / (knots[i + p] - knots[i]) * basis(i, p - 1)
        if knots[i + p + 1] > knots[i + 1]:
            value += (knots[i + p + 1] - u) / (knots[i + p + 1] - knots[i + 1]) * basis(i + 1, p - 1)
        return value

    blend = np.array([w * basis(i, degree) for i, w in enumerate(weights)])
    return blend @ np.array(control_points) / blend.sum()


CONTROL_POINTS = ((0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (3.0, 3.0, 1.0), (4.0, 0.0, 2.0), (6.0, 1.0, 0.0), (7.0, 3.0, 1.0))
MULTIPLICITIES = (4, 1, 1, 4)
KNOTS = (0.0, 1.0, 2.5, 4.0)
EXPANDED_KNOTS = (0.0, 0.0, 0.0, 0.0, 1.0, 2.5, 4.0, 4.0, 4.0, 4.0)


@pytest.mark.parametrize("weights", (None, (1.0, 0.5, 2.0, 1.0, 3.0, 1.0)))
def test_bspline(model, weights):
    points = [point(model, *p) for p in CONTROL_POINTS]
    if weights is None:
        curve = model.createIfcBSplineCurveWithKnots(
            3, points, "UNSPECIFIED", False, False, MULTIPLICITIES, KNOTS, "UNSPECIFIED"
        )
    else:
        curve = model.createIfcRationalBSplineCurveWithKnots(
            3, points, "UNSPECIFIED", False, False, MULTIPLICITIES, KNOTS, "UNSPECIFIED", weights
        )
    spline = map_shape(curve)
    assert np.allclose(evaluate(spline, 0, 0.0), CONTROL_POINTS[0])
    assert np.allclose(evaluate(spline, 0, 4.0), CONTROL_POINTS[-1])
    for u in (0.3, 1.0, 1.7, 2.5, 3.9):
        expected = bspline_reference(CONTROL_POINTS, weights or (1.0,) * 6, EXPANDED_KNOTS, 3, u)
        assert np.allclose(evaluate(spline, 0, u), expected)
    for u in (0.3, 1.7, 3.2):
        assert_derivatives_follow(spline, u, orders=(1, 2, 3))
    if weights is None:
        assert np.allclose(evaluate(spline, 4, 1.7), 0.0)
    with pytest.raises(RuntimeError, match="outside"):
        spline.evaluate(0, 4.5)


def test_bspline_derivatives_with_large_control_points(model):
    spline = map_shape(
        model.createIfcBSplineCurveWithKnots(
            2,
            [point(model, -9e307, 0), point(model, 9e307, 0), point(model, 0, 0)],
            "UNSPECIFIED",
            False,
            False,
            (3, 3),
            (0.0, 4.0),
            "UNSPECIFIED",
        )
    )
    assert np.allclose(evaluate(spline, 1, 0.0), (9e307, 0.0, 0.0))
    assert np.allclose(evaluate(spline, 2, 0.0), (-3.375e307, 0.0, 0.0))


def test_cartesian_trimmed_bspline_reports_unsupported_projection(model):
    curve = model.createIfcBSplineCurveWithKnots(
        2,
        [point(model, 0, 0), point(model, 1, 2), point(model, 3, 0)],
        "UNSPECIFIED",
        False,
        False,
        (3, 3),
        (0.0, 1.0),
        "UNSPECIFIED",
    )
    edge = map_shape(model.createIfcTrimmedCurve(curve, [point(model, 0, 0)], [point(model, 3, 0)], True, "CARTESIAN"))
    with pytest.raises(RuntimeError, match="Cartesian trim point projection is not implemented for B-spline curves"):
        edge.evaluate(0, 0.5)


def test_rational_bspline_arc(model):
    points = [point(model, 1, 0), point(model, 1, 1), point(model, 0, 1)]
    spline = map_shape(
        model.createIfcRationalBSplineCurveWithKnots(
            2, points, "CIRCULAR_ARC", False, False, (3, 3), (0.0, 1.0), "UNSPECIFIED", (1.0, np.sqrt(0.5), 1.0)
        )
    )
    for u in (0.0, 0.2, 0.5, 1.0):
        position = evaluate(spline, 0, u)
        assert np.isclose(np.linalg.norm(position), 1.0)
        assert np.isclose(evaluate(spline, 1, u) @ position, 0.0)
    assert_derivatives_follow(spline, 0.3, orders=(1, 2, 3, 4))


@pytest.mark.parametrize("sense", (True, False))
def test_trimmed_circle(model, sense):
    circle = model.createIfcCircle(placement(model), 2.0)
    edge = map_shape(
        model.createIfcTrimmedCurve(
            circle, [model.createIfcParameterValue(0.5)], [model.createIfcParameterValue(2.0)], sense, "PARAMETER"
        )
    )
    polygon = edge.to_polygon(SETTINGS)
    assert len(polygon) > 2
    assert_follows_polygon(edge, polygon, 1.0)
    basis = map_shape(circle)
    start, end = 0.5, 2.0 if sense else 2.0 - 2 * np.pi
    assert np.allclose(evaluate(edge, 0, 0.0), evaluate(basis, 0, start))
    assert np.allclose(evaluate(edge, 0, 1.0), evaluate(basis, 0, end))
    assert np.allclose(evaluate(edge, 1, 0.0), (end - start) * evaluate(basis, 1, start))
    assert_derivatives_follow(edge, 0.4)


def test_trimmed_ellipse_between_points(model):
    ellipse = model.createIfcEllipse(model.createIfcAxis2Placement3D(point(model, 0, 0, 0), None, None), 3.0, 1.5)
    edge = map_shape(
        model.createIfcTrimmedCurve(ellipse, [point(model, 3, 0, 0)], [point(model, 0, 1.5, 0)], True, "CARTESIAN")
    )
    assert_follows_polygon(edge, edge.to_polygon(SETTINGS), 1.0)
    assert np.allclose(evaluate(edge, 0, 0.0), (3.0, 0.0, 0.0))
    assert np.allclose(evaluate(edge, 0, 1.0), (0.0, 1.5, 0.0))
    assert_derivatives_follow(edge, 0.4)


def test_trimmed_line(model):
    line = model.createIfcLine(
        point(model, 1, 2, 3), model.createIfcVector(model.createIfcDirection((0.0, 3.0, 4.0)), 1.0)
    )
    edge = map_shape(
        model.createIfcTrimmedCurve(
            line, [model.createIfcParameterValue(5.0)], [model.createIfcParameterValue(10.0)], True, "PARAMETER"
        )
    )
    assert_follows_polygon(edge, edge.to_polygon(SETTINGS), 1.0)
    assert np.allclose(evaluate(edge, 0, 0.5), (1.0, 6.5, 9.0))
    assert np.allclose(evaluate(edge, 1, 0.5), (0.0, 3.0, 4.0))
    assert np.allclose(evaluate(edge, 2, 0.5), 0.0)
    with pytest.raises(RuntimeError, match="outside"):
        edge.evaluate(0, 1.5)


def test_bspline_edge_spans_the_knot_range(model):
    points = [point(model, *p) for p in CONTROL_POINTS]
    spline = map_shape(
        model.createIfcBSplineCurveWithKnots(
            3, points, "UNSPECIFIED", False, False, MULTIPLICITIES, KNOTS, "UNSPECIFIED"
        )
    )
    edge = W.edge()
    edge.basis = spline
    assert np.allclose(evaluate(edge, 0, 0.0), CONTROL_POINTS[0])
    assert np.allclose(evaluate(edge, 0, 0.25), evaluate(spline, 0, 1.0))
    assert np.allclose(evaluate(edge, 1, 0.25), 4.0 * evaluate(spline, 1, 1.0))
    assert np.allclose(evaluate(edge, 0, 1.0), CONTROL_POINTS[-1])


def test_offset_curve(model):
    offset = W.offset_curve()
    offset.basis = map_shape(
        model.createIfcCircle(placement(model, axis=(0.0, 0.0, 1.0), ref_direction=(1.0, 0.0, 0.0)), 2.0)
    )
    offset.reference = W.direction3(0.0, 0.0, 1.0)
    offset.offset = 0.5
    for u in (0.0, 0.7, 4.0):
        assert np.allclose(evaluate(offset, 0, u), (1.0 + 1.5 * np.cos(u), 2.0 + 1.5 * np.sin(u), 3.0))
        assert np.allclose(evaluate(offset, 1, u), (-1.5 * np.sin(u), 1.5 * np.cos(u), 0.0))
    with pytest.raises(RuntimeError, match="beyond the first"):
        offset.evaluate(2, 0.0)


def test_offset_of_an_edge(model):
    line = model.createIfcLine(
        point(model, 4, 0, 0), model.createIfcVector(model.createIfcDirection((0.0, 1.0, 0.0)), 1.0)
    )
    offset = W.offset_curve()
    offset.basis = map_shape(
        model.createIfcTrimmedCurve(
            line, [model.createIfcParameterValue(0.0)], [model.createIfcParameterValue(3.0)], True, "PARAMETER"
        )
    )
    offset.reference = W.direction3(0.0, 0.0, 1.0)
    offset.offset = 0.5
    assert np.allclose(evaluate(offset, 0, 0.5), (3.5, 1.5, 0.0))
    assert np.allclose(evaluate(offset, 1, 0.5), (0.0, 3.0, 0.0))


def test_polyline(model):
    loop = map_shape(model.createIfcPolyline([point(model, 0, 0), point(model, 4, 0), point(model, 4, 3)]))
    assert_loop_follows_polygon(loop)
    assert np.allclose(evaluate(loop, 0, 0.5), (2.0, 0.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 1.0), (4.0, 0.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 1.5), (4.0, 1.5, 0.0))
    assert np.allclose(evaluate(loop, 1, 0.5), (4.0, 0.0, 0.0))
    assert np.allclose(evaluate(loop, 1, 1.5), (0.0, 3.0, 0.0))
    assert np.allclose(evaluate(loop, 2, 1.5), 0.0)
    for u in (-0.1, 2.1):
        with pytest.raises(RuntimeError, match="outside"):
            loop.evaluate(0, u)


def test_indexed_poly_curve_with_an_arc(model):
    points = model.createIfcCartesianPointList2D(((0.0, 0.0), (4.0, 0.0), (5.0, 1.0), (4.0, 2.0), (0.0, 2.0)))
    segments = [model.createIfcLineIndex((1, 2)), model.createIfcArcIndex((2, 3, 4)), model.createIfcLineIndex((4, 5))]
    loop = map_shape(model.createIfcIndexedPolyCurve(points, segments))
    assert len(loop.children) == 3
    assert len(loop.children[1].to_polygon(SETTINGS)) > 2
    assert_loop_follows_polygon(loop)
    assert np.allclose(evaluate(loop, 0, 1.5), (5.0, 1.0, 0.0))
    assert np.allclose(evaluate(loop, 1, 1.5) / np.linalg.norm(evaluate(loop, 1, 1.5)), (0.0, 1.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 2.5), (2.0, 2.0, 0.0))
    for u in (0.5, 1.3, 2.5):
        assert_derivatives_follow(loop, u)


def test_composite_curve_with_a_reversed_segment(model):
    circle = model.createIfcCircle(model.createIfcAxis2Placement3D(point(model, 4, 1, 0), None, None), 1.0)
    arc = model.createIfcTrimmedCurve(circle, [point(model, 4, 2, 0)], [point(model, 4, 0, 0)], False, "CARTESIAN")
    segments = [
        model.createIfcCompositeCurveSegment(
            "CONTINUOUS", True, model.createIfcPolyline([point(model, 0, 0, 0), point(model, 4, 0, 0)])
        ),
        model.createIfcCompositeCurveSegment("CONTINUOUS", False, arc),
        model.createIfcCompositeCurveSegment(
            "CONTINUOUS", False, model.createIfcPolyline([point(model, 0, 2, 0), point(model, 4, 2, 0)])
        ),
    ]
    loop = map_shape(model.createIfcCompositeCurve(segments, False))
    assert len(loop.children) == 3
    assert_loop_follows_polygon(loop)
    assert np.allclose(evaluate(loop, 0, 1.0), (4.0, 0.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 1.5), (5.0, 1.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 2.0), (4.0, 2.0, 0.0))
    assert np.allclose(evaluate(loop, 0, 2.75), (1.0, 2.0, 0.0))
    assert np.allclose(evaluate(loop, 1, 2.75), (-4.0, 0.0, 0.0))
    for u in (0.5, 1.3, 2.5):
        assert_derivatives_follow(loop, u)
