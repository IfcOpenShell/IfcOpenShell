# This file was generated with the assistance of an AI coding tool.

"""How accurately the kernel integrates the position along a spiral.

A spiral's tangent direction has a closed form, but its position is the integral of that direction,
which the kernel computes numerically. Each case builds a horizontal alignment with one transition and
compares the kernel's positions along it with a high order Gauss-Legendre integration of the kernel's
own tangent directions, so the reference doesn't depend on any spiral's formula.
"""

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
from ifcopenshell import ifcopenshell_wrapper

A = ifcopenshell.api.alignment
TOLERANCE = 1e-9  # metres

# (family, start radius, end radius, length)
SPIRALS = ["CLOTHOID", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "HELMERTCURVE"]
TRANSITIONS = [
    (0.0, 300.0, 100.0),  # entry
    (300.0, 0.0, 100.0),  # exit
    (300.0, 1000.0, 100.0),  # arc to arc, trimmed from part way along its parent curve
    (-1000.0, -300.0, 100.0),  # arc to arc, to the right
    (0.0, 50.0, 200.0),  # long and tight, turning 2 radians
]
CASES = [(family, *t) for family in SPIRALS for t in TRANSITIONS] + [
    ("CUBIC", 0.0, 300.0, 100.0),
    ("CUBIC", 300.0, 0.0, 100.0),
    ("CUBIC", 300.0, 1000.0, 100.0),
]


def build(kind, r0, r1, length):
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, units=[ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    alignment = A.create(f, "H")
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint((10.0, 20.0)),
            StartDirection=0.3,
            StartRadiusOfCurvature=r0,
            EndRadiusOfCurvature=r1,
            SegmentLength=length,
            PredefinedType=kind,
        ),
    )
    curve = next(c for c in f.by_type("IfcCompositeCurve") if c.is_a() == "IfcCompositeCurve")
    s = ifcopenshell.geom.settings()
    return ifcopenshell_wrapper.function_item_evaluator(s, ifcopenshell_wrapper.map_shape(s, curve))


def reference_positions(evaluator, distances, start, pieces=40, order=64):
    """The start position plus the integral of the kernel's tangent up to each distance"""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    positions = []
    for u in distances:
        total = np.zeros(2)
        edges = np.linspace(0.0, u, pieces + 1)
        for a, b in zip(edges[:-1], edges[1:]):
            for t, w in zip(a + (b - a) * (nodes + 1.0) / 2.0, weights):
                tangent = np.array(evaluator.evaluate(float(t)))[:2, 0]
                total += w * (b - a) / 2.0 * tangent / np.linalg.norm(tangent)
        positions.append(start + total)
    return np.array(positions)


@pytest.mark.parametrize("kind,r0,r1,length", CASES)
def test_position_is_the_integral_of_the_tangent(kind, r0, r1, length):
    evaluator = build(kind, r0, r1, length)
    distances = np.linspace(0.0, length, 9)[1:]
    start = np.array(evaluator.evaluate(0.0))[:2, 3]
    expected = reference_positions(evaluator, distances, start)
    actual = np.array([np.array(evaluator.evaluate(float(u)))[:2, 3] for u in distances])
    assert np.max(np.linalg.norm(actual - expected, axis=1)) < TOLERANCE
