# This file was generated with the assistance of an AI coding tool.

"""The frame of an IfcSegmentedReferenceCurve: X along the 3D curve, Y to the left, Z up, rolled by the cant.

Each case builds an alignment with one cant segment, under a horizontal line or arc and a flat or 4%
grade, and evaluates the segmented reference curve in 3D:

- RefDirection is the tangent of the 3D curve (a central difference of the evaluated positions);
- the frame is orthonormal and right-handed;
- in the section normal to RefDirection, Axis makes the cross slope angle with the horizontal to the left.
  The angle runs from the start to the end of the transition in proportion to the deviating elevation.

The cant curve alone (a segment's own frame) is checked the same way in the plane of distance along and
deviating elevation: RefDirection = (cos θ, 0, sin θ) with tan θ the slope of the deviating elevation.
"""

import math

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.unit
from ifcopenshell import ifcopenshell_wrapper
from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint

A = ifcopenshell.api.alignment
LENGTH = 100.0  # in project units
RAIL_HEAD_DISTANCE = 1.5
HEIGHT = 10.0

TANGENT_TOLERANCE = 1e-8
ORTHONORMAL_TOLERANCE = 1e-12
ANGLE_TOLERANCE = 1e-9

# the cant segment types and the parent curve the API maps each to
KINDS = {
    "CONSTANTCANT": "IfcLine",
    "LINEARTRANSITION": "IfcClothoid",
    "COSINECURVE": "IfcCosineSpiral",
    "SINECURVE": "IfcSineSpiral",
    "BLOSSCURVE": "IfcThirdOrderPolynomialSpiral",
    "HELMERTCURVE": "IfcSecondOrderPolynomialSpiral",
    "VIENNESEBEND": "IfcSeventhOrderPolynomialSpiral",
}
# ((start left, start right), (end left, end right)), in project units
TRANSITION_RAILS = {
    "left-hand-entry": ((0.0, 0.0), (0.0, 0.15)),
    "right-hand-exit": ((0.15, 0.0), (0.0, 0.0)),
    "both-rails": ((0.02, 0.10), (0.04, 0.20)),
}
CONSTANT_RAILS = {"left-hand": ((0.0, 0.15), (0.0, 0.15)), "right-hand": ((0.15, 0.0), (0.15, 0.0))}
HORIZONTALS = {"line": 0.0, "arc": 300.0}  # radius, 0 for a line
GRADES = [0.0, 0.04]
UNITS = ["metre", "foot"]


def new_file(unit):
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    if unit == "foot":
        length = ifcopenshell.api.unit.add_conversion_based_unit(f, name="foot")
    else:
        length = ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(f, units=[length])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    return f


def build(unit, kind, rails, radius, grade):
    (sl, sr), (el, er) = rails
    f = new_file(unit)
    alignment = A.create(f, "C", include_vertical=True, include_cant=True)
    A.get_cant_layout(alignment).RailHeadDistance = RAIL_HEAD_DISTANCE
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint((0.0, 0.0)),
            StartDirection=0.0,
            StartRadiusOfCurvature=radius,
            EndRadiusOfCurvature=radius,
            SegmentLength=LENGTH,
            PredefinedType="CIRCULARARC" if radius else "LINE",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=HEIGHT,
            StartGradient=grade,
            EndGradient=grade,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )
    constant = kind == "CONSTANTCANT"
    A.create_layout_segment(
        f,
        A.get_cant_layout(alignment),
        f.createIfcAlignmentCantSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartCantLeft=sl,
            EndCantLeft=None if constant else el,
            StartCantRight=sr,
            EndCantRight=None if constant else er,
            PredefinedType=kind,
        ),
    )
    src = f.by_type("IfcSegmentedReferenceCurve")[0]
    assert src.Segments[0].ParentCurve.is_a() == KINDS[kind]
    return f, src


def cases():
    for kind in KINDS:
        for rails, value in (CONSTANT_RAILS if kind == "CONSTANTCANT" else TRANSITION_RAILS).items():
            yield kind, rails, value


def cross_slope_angle(left, right):
    """The angle of Axis from the horizontal to the left, in the section: 90 degrees when level."""
    cant = right - left
    return math.atan2(math.sqrt(RAIL_HEAD_DISTANCE**2 - cant**2), cant)


def evaluators(f, src):
    s = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(s, src)
    return (
        ifcopenshell_wrapper.function_item_evaluator(s, fn),
        ifcopenshell_wrapper.function_item_evaluator(s, fn.get_cant()),
    )


def matrix(evaluator, u):
    return np.array(evaluator.evaluate(float(u)))


def stations(f):
    length = LENGTH * ifcopenshell.util.unit.calculate_unit_scale(f)  # the kernel works in metres
    # not at the middle, where a helmert curve's two halves meet and its slope has a corner
    return length, np.linspace(0.05, 0.95, 10) * length


def assert_orthonormal(rotation):
    assert np.allclose(rotation.T @ rotation, np.eye(3), rtol=0, atol=ORTHONORMAL_TOLERANCE), rotation
    assert np.linalg.det(rotation) == pytest.approx(1.0, abs=ORTHONORMAL_TOLERANCE)


@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("grade", GRADES)
@pytest.mark.parametrize("horizontal", list(HORIZONTALS))
@pytest.mark.parametrize("kind,rails,value", list(cases()))
def test_3d_frame(kind, rails, value, horizontal, grade, unit):
    f, src = build(unit, kind, value, HORIZONTALS[horizontal], grade)
    curve, cant = evaluators(f, src)
    scale = ifcopenshell.util.unit.calculate_unit_scale(f)
    length, us = stations(f)
    (sl, sr), (el, er) = value
    d0, d1 = 0.5 * (sl + sr) * scale, 0.5 * (el + er) * scale
    phi0, phi1 = cross_slope_angle(sl, sr), cross_slope_angle(el, er)
    h = 1e-4
    for u in us:
        frame = matrix(curve, u)
        rotation = frame[:3, :3]
        assert_orthonormal(rotation)

        tangent = matrix(curve, u + h)[:3, 3] - matrix(curve, u - h)[:3, 3]
        tangent /= np.linalg.norm(tangent)
        assert np.allclose(rotation[:, 0], tangent, rtol=0, atol=TANGENT_TOLERANCE), (u, rotation[:, 0], tangent)

        ref_dir, axis = rotation[:, 0], rotation[:, 2]
        left = np.array([-ref_dir[1], ref_dir[0], 0.0])
        left /= np.linalg.norm(left)
        normal = np.cross(ref_dir, left)
        deviating_elevation = matrix(cant, u)[1, 3]
        expected = phi0 if d1 == d0 else phi0 + (phi1 - phi0) * (deviating_elevation - d0) / (d1 - d0)
        assert math.atan2(axis @ normal, axis @ left) == pytest.approx(expected, abs=ANGLE_TOLERANCE), u

        # the elevation is the gradient curve's, raised by the deviating elevation
        assert frame[2, 3] == pytest.approx(HEIGHT * scale + grade * u + deviating_elevation, abs=1e-9)


@pytest.mark.parametrize("kind,rails,value", list(cases()))
def test_terminal_curve_segment_placement(kind, rails, value):
    """The zero-length curve segment ending the cant curve is placed as cant segments are: RefDirection in the
    plane of distance along and deviating elevation, Axis (0, cos φ, sin φ) in the cross section. The cant
    frame it is placed at has RefDirection pitched up by the slope, (cos θ, 0, sin θ), and Axis rolled in the
    section normal to it."""
    f, src = build("metre", kind, value, 0.0, 0.0)
    segment = A.get_layout_segments(A.get_cant_layout(f.by_type("IfcAlignment")[0]))[0]
    end = _get_segment_endpoint(f, segment)
    placement = src.Segments[-1].Placement
    assert placement.RefDirection.DirectionRatios == pytest.approx((end[0, 0], end[2, 0], 0.0), abs=1e-12)
    (_, _), (el, er) = value
    phi = cross_slope_angle(el, er)
    assert placement.Axis.DirectionRatios == pytest.approx((0.0, math.cos(phi), math.sin(phi)), abs=ANGLE_TOLERANCE)


@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("kind,rails,value", list(cases()))
def test_cant_segment_frame(kind, rails, value, unit):
    """In the cant curve alone, RefDirection = (cos θ, 0, sin θ), tan θ = D', and the frame is a pitch by θ
    of the section rolled by the cross slope angle."""
    f, src = build(unit, kind, value, 0.0, 0.0)
    _, cant = evaluators(f, src)
    length, us = stations(f)
    h = 1e-4 * length
    for u in us:
        frame = matrix(cant, u)
        rotation = frame[:3, :3]
        assert_orthonormal(rotation)
        slope = (matrix(cant, u + h)[1, 3] - matrix(cant, u - h)[1, 3]) / (2.0 * h)
        theta = math.atan(slope)
        assert np.allclose(rotation[:, 0], [math.cos(theta), 0.0, math.sin(theta)], rtol=0, atol=1e-9), u
        phi = math.atan2(rotation[2, 2] * math.cos(theta) - rotation[0, 2] * math.sin(theta), rotation[1, 2])
        expected = np.array(
            [
                [math.cos(theta), math.sin(theta) * math.cos(phi), -math.sin(theta) * math.sin(phi)],
                [0.0, math.sin(phi), math.cos(phi)],
                [math.sin(theta), -math.cos(theta) * math.cos(phi), math.cos(theta) * math.sin(phi)],
            ]
        )
        assert np.allclose(rotation, expected, rtol=0, atol=1e-9), (u, rotation, expected)
