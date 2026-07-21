# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import logging
import math

import numpy as np
import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.validate
from ifcopenshell import ifcopenshell_wrapper


def _create_file():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    return file


def _reference_clothoid_end(length, start_curvature, end_curvature, steps=20000):
    """Composite Simpson integration of the clothoid position functions, as an independent check."""
    l = np.linspace(0.0, length, 2 * steps + 1)
    theta = start_curvature * l + (end_curvature - start_curvature) * l * l / (2.0 * length)
    h = length / (2.0 * steps)
    weights = np.ones(2 * steps + 1)
    weights[1:-1:2] = 4.0
    weights[2:-1:2] = 2.0
    dx = h / 3.0 * float(np.sum(weights * np.cos(theta)))
    dy = h / 3.0 * float(np.sum(weights * np.sin(theta)))
    return dx, dy


def test_compute_clothoid_end():
    for length, k1, k2 in [(200.0, 0.0, 1.0 / 1000.0), (150.0, 1.0 / 1000.0, 0.0), (120.0, -1.0 / 800.0, 1.0 / 500.0)]:
        dx, dy, dtheta = ifcopenshell.api.alignment.compute_clothoid_end(length, k1, k2)
        ref_dx, ref_dy = _reference_clothoid_end(length, k1, k2)
        assert dx == pytest.approx(ref_dx, abs=1.0e-12)
        assert dy == pytest.approx(ref_dy, abs=1.0e-12)
        assert dtheta == pytest.approx(0.5 * (k1 + k2) * length)

    # signed curvatures mirror the unsigned result
    dx, dy, dtheta = ifcopenshell.api.alignment.compute_clothoid_end(200.0, 0.0, 1.0 / 1000.0)
    mx, my, mtheta = ifcopenshell.api.alignment.compute_clothoid_end(200.0, 0.0, -1.0 / 1000.0)
    assert mx == pytest.approx(dx)
    assert my == pytest.approx(-dy)
    assert mtheta == pytest.approx(-dtheta)


def test_solve_produces_continuous_segments():
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0, 200.0, 150.0), (1250.0, 180.0, 180.0), (950.0, 0.0, 120.0)]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)

    expected_types = [
        "LINE",
        "CLOTHOID",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
        "CLOTHOID",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
        "CIRCULARARC",
        "CLOTHOID",
        "LINE",
    ]
    assert [s.predefined_type for s in segments] == expected_types

    # the solution starts at the POB, in the direction of the first PI
    assert segments[0].start_point == pytest.approx((500.0, 2500.0))
    assert segments[0].start_direction == pytest.approx(math.atan2(660.0 - 2500.0, 3340.0 - 500.0))

    # spirals run from zero curvature to the curve radius and vice versa
    entry_spiral = segments[1]
    assert entry_spiral.start_radius_of_curvature == 0.0
    assert entry_spiral.end_radius_of_curvature == pytest.approx(1000.0)  # positive, curve to the left
    assert entry_spiral.segment_length == pytest.approx(200.0)
    exit_spiral = segments[3]
    assert exit_spiral.start_radius_of_curvature == pytest.approx(1000.0)
    assert exit_spiral.end_radius_of_curvature == 0.0
    assert exit_spiral.segment_length == pytest.approx(150.0)
    assert segments[5].end_radius_of_curvature == pytest.approx(-1250.0)  # curve to the right

    # each segment ends exactly where the next one starts, in position and direction
    dist_along = 0.0
    for segment, next_segment in zip(segments[:-1], segments[1:]):
        assert segment.start_dist_along == pytest.approx(dist_along)
        end_x, end_y, end_direction = ifcopenshell.api.alignment.compute_horizontal_segment_end(segment)
        assert end_x == pytest.approx(next_segment.start_point[0], abs=1.0e-9)
        assert end_y == pytest.approx(next_segment.start_point[1], abs=1.0e-9)
        direction_gap = end_direction - next_segment.start_direction
        assert math.atan2(math.sin(direction_gap), math.cos(direction_gap)) == pytest.approx(0.0, abs=1.0e-12)
        dist_along += segment.segment_length


def test_solve_plain_radius_matches_spiral_free_tuple():
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (8480.0, 2010.0)]

    segments1 = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [1000.0, 1250.0])
    segments2 = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(
        hpoints, [(1000.0, 0.0, 0.0), (1250.0, 0.0, 0.0)]
    )
    assert segments1 == segments2


def test_solve_cant_profile():
    hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0, 200.0, 150.0), (1250.0, 180.0, 180.0), (950.0, 140.0, 120.0)]
    cants = [0.15, 0.12, 0.1]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii, cants)

    # cant varies linearly over spirals, is constant over circular curves, and is zero on tangents
    for segment in segments:
        if segment.predefined_type == "LINE":
            assert segment.start_cant == 0.0 and segment.end_cant == 0.0
        elif segment.predefined_type == "CIRCULARARC":
            assert segment.start_cant == segment.end_cant != 0.0
    entry_spiral = segments[1]
    assert (entry_spiral.start_cant, entry_spiral.end_cant) == (0.0, 0.15)
    exit_spiral = segments[3]
    assert (exit_spiral.start_cant, exit_spiral.end_cant) == (0.15, 0.0)

    # the first curve is to the left, so the outer rail is the right rail
    assert entry_spiral.raise_left_rail is False
    # the second curve is to the right, so the outer rail is the left rail
    assert segments[5].raise_left_rail is True

    # the cant profile is continuous across segment boundaries
    for segment, next_segment in zip(segments[:-1], segments[1:]):
        assert segment.end_cant == pytest.approx(next_segment.start_cant)


def test_solve_errors():
    hpoints = [(0.0, 0.0), (1000.0, 0.0), (2000.0, 1000.0)]

    with pytest.raises(ValueError):  # radii count mismatch
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [500.0, 500.0])
    with pytest.raises(ValueError):  # cants count mismatch
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 50.0, 50.0)], [0.1, 0.1])
    with pytest.raises(ValueError):  # malformed radii element
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 50.0)])
    with pytest.raises(ValueError):  # spiral lengths without a radius
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(0.0, 50.0, 50.0)])
    with pytest.raises(ValueError):  # cant without spiral transitions is discontinuous
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 0.0, 0.0)], [0.1])
    with pytest.raises(ValueError):  # spirals deflect more than the PI deflection angle
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(500.0, 5000.0, 5000.0)])
    with pytest.raises(ValueError):  # zero deflection angle
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(
            [(0.0, 0.0), (1000.0, 0.0), (2000.0, 0.0)], [(500.0, 50.0, 50.0)]
        )


def test_author_transition_curve_alignment():
    """
    End-to-end example: author a tangent -> clothoid -> circular arc -> clothoid -> tangent
    alignment with cant, then check the written geometry for continuity with the geometry engine
    and validate the file against the schema and express rules.
    """
    file = _create_file()

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file,
        "TestAlignment",
        [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0)],
        [(1000.0, 200.0, 150.0)],
        [(0.0, 100.0), (2000.0, 135.0), (4000.0, 105.0)],
        [1600.0],
        cants=[0.15],
        rail_head_distance=1.5,
    )

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal_layout)
    expected_types = ["LINE", "CLOTHOID", "CIRCULARARC", "CLOTHOID", "LINE", "LINE"]  # last is the zero length segment
    assert [s.DesignParameters.PredefinedType for s in segment_nest.RelatedObjects] == expected_types

    cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment)
    assert cant_layout.RailHeadDistance == pytest.approx(1.5)
    cant_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(cant_layout)
    # cant segments correspond one-for-one with the horizontal segments
    assert len(cant_nest.RelatedObjects) == len(segment_nest.RelatedObjects)

    # verify continuity of position and direction between consecutive segments of the
    # geometric representation
    curve = ifcopenshell.api.alignment.get_layout_curve(horizontal_layout)
    settings = ifcopenshell.geom.settings()
    for segment, next_segment in zip(curve.Segments[:-1], curve.Segments[1:]):
        fn = ifcopenshell_wrapper.map_shape(settings, segment.wrapped_data)
        evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, fn)
        end = np.array(evaluator.evaluate(fn.end()))
        end_position = end[0:2, 3]
        end_direction = math.atan2(end[1, 0], end[0, 0])
        start_position = next_segment.Placement.Location.Coordinates
        d = next_segment.Placement.RefDirection.DirectionRatios
        start_direction = math.atan2(d[1], d[0])
        assert end_position[0] == pytest.approx(start_position[0], abs=1.0e-5)
        assert end_position[1] == pytest.approx(start_position[1], abs=1.0e-5)
        direction_gap = math.atan2(math.sin(end_direction - start_direction), math.cos(end_direction - start_direction))
        assert direction_gap == pytest.approx(0.0, abs=1.0e-9)

    # the file is schema and express rule valid
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(file, logger, express_rules=True)
    assert [entry for entry in logger.statements if entry["level"] == logging.ERROR] == []


test_compute_clothoid_end()
test_solve_produces_continuous_segments()
test_solve_plain_radius_matches_spiral_free_tuple()
test_solve_cant_profile()
test_solve_errors()
test_author_transition_curve_alignment()
