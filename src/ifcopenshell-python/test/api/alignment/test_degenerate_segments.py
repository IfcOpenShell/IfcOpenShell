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

"""Tests for transition segments that don't transition: a spiral with equal start and end radius,
a vertical arc with equal start and end gradient, and a cant transition with equal start and end
cant.

Such a segment is geometrically its constant counterpart (a line, a circular arc, a constant
gradient or a constant cant), but its curve can't be written as the transition's parent curve,
whose terms divide by the change across it. It is mapped to the constant counterpart's geometry
instead, so its curve is valid and the alignment is exactly the one the constant segment gives.
"""

import logging

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.validate
import test.bootstrap
from ifcopenshell import ifcopenshell_wrapper

A = ifcopenshell.api.alignment
LENGTH = 100.0
TOLERANCE = 1e-9

SPIRALS = ["CLOTHOID", "CUBIC", "HELMERTCURVE", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "VIENNESEBEND"]
RADII = [300.0, -1000.0, 0.0]
GRADIENT_ARCS = [("PARABOLICARC", None), ("CIRCULARARC", 3000.0)]
GRADIENTS = [0.01, -0.02, 0.0]
CANT_TRANSITIONS = ["LINEARTRANSITION", "HELMERTCURVE", "BLOSSCURVE", "COSINECURVE", "SINECURVE", "VIENNESEBEND"]
CANTS = [(0.0, 0.1), (0.0, 0.0)]  # (left, right), the same at both ends


def new_file():
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f, units=[ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")])
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    return f


def add_horizontal(f, alignment, kind, r0, r1, start=(10.0, 20.0), direction=0.3):
    A.create_layout_segment(
        f,
        A.get_horizontal_layout(alignment),
        f.createIfcAlignmentHorizontalSegment(
            StartPoint=f.createIfcCartesianPoint(start),
            StartDirection=direction,
            StartRadiusOfCurvature=r0,
            EndRadiusOfCurvature=r1,
            SegmentLength=LENGTH,
            PredefinedType=kind,
        ),
    )


def add_vertical(f, alignment, kind, g0, g1, radius=None):
    A.create_layout_segment(
        f,
        A.get_vertical_layout(alignment),
        f.createIfcAlignmentVerticalSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartHeight=10.0,
            StartGradient=g0,
            EndGradient=g1,
            RadiusOfCurvature=radius,
            PredefinedType=kind,
        ),
    )


def horizontal(kind, radius):
    f = new_file()
    alignment = A.create(f, "H")
    add_horizontal(f, alignment, kind, radius, radius)
    return f


def vertical(kind, gradient, radius):
    f = new_file()
    alignment = A.create(f, "V", include_vertical=True)
    add_horizontal(f, alignment, "LINE", 0.0, 0.0, (0.0, 0.0), 0.0)
    add_vertical(f, alignment, kind, gradient, gradient, radius)
    return f


def cant(kind, left, right):
    f = new_file()
    alignment = A.create(f, "C", include_vertical=True, include_cant=True)
    A.get_cant_layout(alignment).RailHeadDistance = 1.5
    add_horizontal(f, alignment, "LINE", 0.0, 0.0, (0.0, 0.0), 0.0)
    add_vertical(f, alignment, "CONSTANTGRADIENT", 0.0, 0.0)
    A.create_layout_segment(
        f,
        A.get_cant_layout(alignment),
        f.createIfcAlignmentCantSegment(
            StartDistAlong=0.0,
            HorizontalLength=LENGTH,
            StartCantLeft=left,
            EndCantLeft=left,
            StartCantRight=right,
            EndCantRight=right,
            PredefinedType=kind,
        ),
    )
    return f


def curve_of(f):
    for kind in ("IfcSegmentedReferenceCurve", "IfcGradientCurve"):
        if f.by_type(kind):
            return f.by_type(kind)[0]
    return next(c for c in f.by_type("IfcCompositeCurve") if c.is_a() == "IfcCompositeCurve")


def curve_end(f):
    s = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(s, curve_of(f))
    return np.array(ifcopenshell_wrapper.function_item_evaluator(s, fn).evaluate(fn.end()))


def parent_curves(f):
    """The parent curves of the non zero length segments of the layout curve built last"""
    curve = curve_of(f)
    return [s.ParentCurve.is_a() for s in curve.Segments if s.SegmentLength.wrappedValue != 0.0]


def assert_valid(f):
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, logger, express_rules=True)
    assert [e for e in logger.statements if e["level"] == logging.ERROR] == []


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("radius", RADII)
@pytest.mark.parametrize("kind", SPIRALS)
def test_spiral_with_equal_radii(kind, radius):
    f = horizontal(kind, radius)
    expected = horizontal("CIRCULARARC" if radius else "LINE", radius)
    assert parent_curves(f) == parent_curves(expected)
    assert np.allclose(curve_end(f), curve_end(expected), rtol=0, atol=TOLERANCE)
    assert_valid(f)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("gradient", GRADIENTS)
@pytest.mark.parametrize("kind,radius", GRADIENT_ARCS)
def test_vertical_arc_with_equal_gradients(kind, radius, gradient):
    f = vertical(kind, gradient, radius)
    expected = vertical("CONSTANTGRADIENT", gradient, None)
    assert parent_curves(f) == parent_curves(expected)
    assert np.allclose(curve_end(f), curve_end(expected), rtol=0, atol=TOLERANCE)
    assert_valid(f)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("left,right", CANTS)
@pytest.mark.parametrize("kind", CANT_TRANSITIONS)
def test_cant_transition_with_equal_cant(kind, left, right):
    f = cant(kind, left, right)
    expected = cant("CONSTANTCANT", left, right)
    assert parent_curves(f) == parent_curves(expected)
    assert np.allclose(curve_end(f), curve_end(expected), rtol=0, atol=TOLERANCE)
    assert_valid(f)
