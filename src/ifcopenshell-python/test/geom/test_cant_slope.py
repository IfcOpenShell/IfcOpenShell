# This file was generated with the assistance of an AI coding tool.

"""The slope of the deviating elevation along a cant segment.

A cant segment's frame points along the track at the slope of its deviating elevation: its RefDirection
is pitched up from the distance along, (cos θ, 0, sin θ), by the arctangent θ of the derivative of the
deviating elevation. Each case builds an
alignment with one cant transition and compares that angle with a central difference of the evaluated
deviating elevation, for every cant parent curve and in metres and feet.
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

A = ifcopenshell.api.alignment
LENGTH = 100.0  # in project units
RAIL_HEAD_DISTANCE = 1.5
TOLERANCE = 1e-9

# the cant transition and the parent curve the API maps it to
TRANSITIONS = {
    "LINEARTRANSITION": "IfcClothoid",
    "COSINECURVE": "IfcCosineSpiral",
    "SINECURVE": "IfcSineSpiral",
    "BLOSSCURVE": "IfcThirdOrderPolynomialSpiral",
    "HELMERTCURVE": "IfcSecondOrderPolynomialSpiral",
    "VIENNESEBEND": "IfcSeventhOrderPolynomialSpiral",
}
# ((start left, start right), (end left, end right)), in project units
RAILS = {
    "left-hand-entry": ((0.0, 0.0), (0.0, 0.15)),
    "left-hand-exit": ((0.0, 0.15), (0.0, 0.0)),
    "right-hand-entry": ((0.0, 0.0), (0.15, 0.0)),
    "both-rails": ((0.02, 0.10), (0.04, 0.20)),
}
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


def build(unit, kind, start, end):
    f = new_file(unit)
    alignment = A.create(f, "C", include_vertical=True, include_cant=True)
    A.get_cant_layout(alignment).RailHeadDistance = RAIL_HEAD_DISTANCE
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint((0.0, 0.0)),
            StartDirection=0.0,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=LENGTH,
            PredefinedType="LINE",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=10.0,
            StartGradient=0.0,
            EndGradient=0.0,
            PredefinedType="CONSTANTGRADIENT",
        ),
    )
    A.create_layout_segment(
        f,
        A.get_cant_layout(alignment),
        f.createIfcAlignmentCantSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartCantLeft=start[0],
            EndCantLeft=end[0],
            StartCantRight=start[1],
            EndCantRight=end[1],
            PredefinedType=kind,
        ),
    )
    return f


def cant_evaluator(f):
    s = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(s, f.by_type("IfcSegmentedReferenceCurve")[0])
    return ifcopenshell_wrapper.function_item_evaluator(s, fn.get_cant())


@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize("rails", list(RAILS))
@pytest.mark.parametrize("kind", list(TRANSITIONS))
def test_refdirection_follows_the_slope_of_the_deviating_elevation(kind, rails, unit):
    start, end = RAILS[rails]
    f = build(unit, kind, start, end)
    assert next(s.ParentCurve.is_a() for s in f.by_type("IfcSegmentedReferenceCurve")[0].Segments) == TRANSITIONS[kind]

    evaluator = cant_evaluator(f)
    length = LENGTH * ifcopenshell.util.unit.calculate_unit_scale(f)  # the kernel works in metres
    h = 1e-4 * length
    # not at the middle, where a helmert curve's two halves meet and its slope has a corner
    for u in np.linspace(0.05, 0.95, 10) * length:
        frame = np.array(evaluator.evaluate(float(u)))
        before = np.array(evaluator.evaluate(float(u - h)))[1, 3]
        after = np.array(evaluator.evaluate(float(u + h)))[1, 3]
        slope = (after - before) / (2.0 * h)
        assert math.atan2(frame[2, 0], frame[0, 0]) == pytest.approx(math.atan(slope), abs=TOLERANCE), u
