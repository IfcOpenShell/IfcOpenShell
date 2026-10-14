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

"""Tests that the alignment API reads and writes IfcAlignmentHorizontalSegment.StartDirection in the
project's plane angle unit.

The same alignment is built in files whose plane angle unit is the radian, the degree and the gradian.
Everything measured in radians, and the geometry, must come out the same in all three.
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
import test.bootstrap
from ifcopenshell import ifcopenshell_wrapper
from ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method import _horizontal_design_parameters

A = ifcopenshell.api.alignment
UNITS = ["radian", "degree", "gradian"]
HPOINTS = [(0.0, 0.0), (500.0, 100.0), (900.0, -200.0), (1500.0, -150.0)]
RADII = [(300.0, 60.0, 60.0), (400.0, 0.0, 0.0)]
TOLERANCE = 1e-9


def new_file(angle_unit):
    f = ifcopenshell.api.project.create_file(version="IFC4X3_ADD2")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    units = [ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT")]
    if angle_unit == "radian":
        units.append(ifcopenshell.api.unit.add_si_unit(f, unit_type="PLANEANGLEUNIT"))
    elif angle_unit == "degree":
        units.append(ifcopenshell.api.unit.add_conversion_based_unit(f, name="degree"))
    else:
        # as a gon file such as the BPaimio-Kupittaa railway alignment declares it
        radian = f.createIfcSIUnit(UnitType="PLANEANGLEUNIT", Name="RADIAN")
        units.append(
            f.createIfcConversionBasedUnit(
                Dimensions=f.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0),
                UnitType="PLANEANGLEUNIT",
                Name="Gradian",
                ConversionFactor=f.createIfcMeasureWithUnit(f.createIfcPlaneAngleMeasure(math.pi / 200.0), radian),
            )
        )
    ifcopenshell.api.unit.assign_unit(f, units=units)
    context = ifcopenshell.api.context.add_context(f, context_type="Model")
    ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    return f


def scale(f):
    return ifcopenshell.util.unit.calculate_unit_scale(f, "PLANEANGLEUNIT")


def by_pi_method(angle_unit):
    f = new_file(angle_unit)
    alignment = A.create_by_pi_method(f, "A", HPOINTS, RADII)
    return f, alignment


def horizontal_segments(alignment):
    layout = A.get_horizontal_layout(alignment)
    return [s for s in A.get_alignment_segment_nest(layout).RelatedObjects]


def curve_end(f):
    curve = next(c for c in f.by_type("IfcCompositeCurve") if c.is_a() == "IfcCompositeCurve")
    s = ifcopenshell.geom.settings()
    fn = ifcopenshell_wrapper.map_shape(s, curve)
    return np.array(ifcopenshell_wrapper.function_item_evaluator(s, fn).evaluate(fn.end()))


@pytest.fixture(scope="module")
def reference():
    return by_pi_method("radian")


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("angle_unit", UNITS)
def test_pi_method_writes_directions_in_the_angle_unit(angle_unit, reference):
    f, alignment = by_pi_method(angle_unit)
    _, reference_alignment = reference
    for segment, expected in zip(horizontal_segments(alignment), horizontal_segments(reference_alignment)):
        actual = segment.DesignParameters.StartDirection * scale(f)
        assert actual == pytest.approx(expected.DesignParameters.StartDirection, abs=TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("angle_unit", UNITS)
def test_terminator_direction_in_the_angle_unit(angle_unit, reference):
    # the zero length segment at the end continues in the direction the alignment ends in
    f, alignment = by_pi_method(angle_unit)
    end = curve_end(f)
    terminator = horizontal_segments(alignment)[-1].DesignParameters
    assert terminator.SegmentLength == 0.0
    assert terminator.StartDirection * scale(f) == pytest.approx(math.atan2(end[1, 0], end[0, 0]), abs=TOLERANCE)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("angle_unit", UNITS)
def test_curve_parameters_in_radians(angle_unit, reference):
    f, alignment = by_pi_method(angle_unit)
    _, reference_alignment = reference
    for segment, expected_segment in zip(horizontal_segments(alignment), horizontal_segments(reference_alignment)):
        if segment.DesignParameters.SegmentLength == 0.0:
            continue
        actual = A.get_horizontal_curve_parameters(segment)
        expected = A.get_horizontal_curve_parameters(expected_segment)
        assert actual.delta == pytest.approx(expected.delta, abs=TOLERANCE)
        assert actual.end_point == pytest.approx(expected.end_point, abs=1e-6)
        if expected.pi is not None:
            assert actual.pi == pytest.approx(expected.pi, abs=1e-6)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize("angle_unit", UNITS)
def test_update_layout_segments_writes_directions_in_the_angle_unit(angle_unit, reference):
    # regenerating a layout from the PI method's definitions, which are in radians
    f, alignment = by_pi_method(angle_unit)
    layout = A.get_horizontal_layout(alignment)
    definitions = A.solve_horizontal_alignment_by_pi_method(HPOINTS, RADII)
    parameters = [_horizontal_design_parameters(f, d) for d in definitions]
    old = [s for s in horizontal_segments(alignment) if s.DesignParameters.SegmentLength > 0.0]
    A.update_layout_segments(f, layout, list(zip(old, parameters)))
    for segment, definition in zip(horizontal_segments(alignment), definitions):
        assert segment.DesignParameters.StartDirection * scale(f) == pytest.approx(
            definition.start_direction, abs=TOLERANCE
        )
    end = curve_end(f)
    assert np.allclose(end, curve_end(reference[0]), rtol=0, atol=1e-6)
    # and the zero length segment moved to the new end keeps the end direction
    terminator = horizontal_segments(alignment)[-1].DesignParameters
    assert terminator.StartDirection * scale(f) == pytest.approx(math.atan2(end[1, 0], end[0, 0]), abs=TOLERANCE)
