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

import os
import tempfile

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit


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


def _write_csv(content: str) -> str:
    handle, filepath = tempfile.mkstemp(suffix=".csv", text=True)
    with os.fdopen(handle, "w") as f:
        f.write(content)
    return filepath


def _get_horizontal_segments(alignment):
    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal_layout)
    return segment_nest.RelatedObjects


def test_create_from_csv():
    file = _create_file()

    filepath = _write_csv(
        "500,2500,0,3340,660,1000,4340,5000,1250,7600,4560,950,8480,2010,0\n"
        "0,100,0,2000,135,1600,5000,105,1200,9800,105,0\n"
    )
    alignment = ifcopenshell.api.alignment.create_from_csv(file, filepath)
    os.remove(filepath)

    assert alignment.Name == "Alignment_from_CSV"

    segments = _get_horizontal_segments(alignment)
    assert len(segments) == 8  # 4 tangent runs + 3 circular curves + zero length segment
    expected_types = ["LINE", "CIRCULARARC", "LINE", "CIRCULARARC", "LINE", "CIRCULARARC", "LINE", "LINE"]
    assert [s.DesignParameters.PredefinedType for s in segments] == expected_types

    # the CSV result matches the result of create_by_pi_method with the same PI data
    file2 = _create_file()
    alignment2 = ifcopenshell.api.alignment.create_by_pi_method(
        file2,
        "TestAlignment",
        [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)],
        [(1000.0), (1250.0), (950.0)],
        [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (9800.0, 105.0)],
        [(1600.0), (1200.0)],
    )
    segments2 = _get_horizontal_segments(alignment2)
    assert len(segments) == len(segments2)
    for s1, s2 in zip(segments, segments2):
        d1 = s1.DesignParameters
        d2 = s2.DesignParameters
        assert d1.PredefinedType == d2.PredefinedType
        assert d1.StartPoint.Coordinates == pytest.approx(d2.StartPoint.Coordinates)
        assert d1.StartDirection == pytest.approx(d2.StartDirection)
        assert d1.StartRadiusOfCurvature == pytest.approx(d2.StartRadiusOfCurvature)
        assert d1.EndRadiusOfCurvature == pytest.approx(d2.EndRadiusOfCurvature)
        assert d1.SegmentLength == pytest.approx(d2.SegmentLength)


def test_create_from_csv_spiral_transitions():
    file = _create_file()

    filepath = _write_csv(
        "X,Y,R,Lin,Lout\n"
        "500,2500,0,0,0,3340,660,1000,200,150,4340,5000,1250,180,180,7600,4560,950,0,120,8480,2010,0,0,0\n"
        "0,100,0,2000,135,1600,5000,105,1200,9800,105,0\n"
    )
    alignment = ifcopenshell.api.alignment.create_from_csv(file, filepath)
    os.remove(filepath)

    segments = _get_horizontal_segments(alignment)
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
        "LINE",  # zero length segment
    ]
    assert [s.DesignParameters.PredefinedType for s in segments] == expected_types

    # spirals run from zero curvature to the curve radius and vice versa
    entry_spiral = segments[1].DesignParameters
    assert entry_spiral.StartRadiusOfCurvature == 0.0
    assert entry_spiral.EndRadiusOfCurvature == pytest.approx(1000.0)  # positive, curve to the left
    assert entry_spiral.SegmentLength == pytest.approx(200.0)
    exit_spiral = segments[3].DesignParameters
    assert exit_spiral.StartRadiusOfCurvature == pytest.approx(1000.0)
    assert exit_spiral.EndRadiusOfCurvature == 0.0
    assert exit_spiral.SegmentLength == pytest.approx(150.0)
    assert segments[5].DesignParameters.EndRadiusOfCurvature == pytest.approx(-1250.0)  # curve to the right

    # the CSV result matches the pure PI method solution for the same PI data
    # (geometric continuity of the solution is covered by test_solve_horizontal_alignment_by_pi_method)
    solved = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(
        [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)],
        [(1000.0, 200.0, 150.0), (1250.0, 180.0, 180.0), (950.0, 0.0, 120.0)],
    )
    assert len(solved) == len(segments) - 1  # the file has an additional zero length segment
    for definition, segment in zip(solved, segments):
        d = segment.DesignParameters
        assert d.PredefinedType == definition.predefined_type
        assert d.StartPoint.Coordinates == pytest.approx(definition.start_point)
        assert d.StartDirection == pytest.approx(definition.start_direction)
        assert d.StartRadiusOfCurvature == pytest.approx(definition.start_radius_of_curvature)
        assert d.EndRadiusOfCurvature == pytest.approx(definition.end_radius_of_curvature)
        assert d.SegmentLength == pytest.approx(definition.segment_length)


def test_create_from_csv_cant():
    file = _create_file()

    filepath = _write_csv(
        "X,Y,R,Lin,Lout,E\n"
        "500,2500,0,0,0,0,3340,660,1000,200,150,0.15,4340,5000,1250,180,180,0.12,7600,4560,950,140,120,0.1,8480,2010,0,0,0,0\n"
        "0,100,0,2000,135,1600,5000,105,1200,9800,105,0\n"
    )
    alignment = ifcopenshell.api.alignment.create_from_csv(file, filepath, rail_head_distance=1.5)
    os.remove(filepath)

    cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment)
    assert cant_layout is not None
    assert cant_layout.RailHeadDistance == pytest.approx(1.5)

    vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    assert vertical_layout is not None

    horizontal_segments = _get_horizontal_segments(alignment)
    cant_segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(cant_layout)
    cant_segments = cant_segment_nest.RelatedObjects

    # cant segments correspond one-for-one with the horizontal segments
    assert len(cant_segments) == len(horizontal_segments)

    dist_along = 0.0
    for horizontal_segment, cant_segment in zip(horizontal_segments[:-1], cant_segments[:-1]):
        h = horizontal_segment.DesignParameters
        c = cant_segment.DesignParameters
        assert c.StartDistAlong == pytest.approx(dist_along)
        assert c.HorizontalLength == pytest.approx(h.SegmentLength)
        if h.PredefinedType == "CLOTHOID":
            assert c.PredefinedType == "LINEARTRANSITION"
        else:
            assert c.PredefinedType == "CONSTANTCANT"
        dist_along += h.SegmentLength

    # the first curve is to the left, so the cant is applied to the right rail
    entry_cant = cant_segments[1].DesignParameters
    assert entry_cant.StartCantLeft == pytest.approx(0.0)
    assert entry_cant.EndCantLeft == pytest.approx(0.0)
    assert entry_cant.StartCantRight == pytest.approx(0.0)
    assert entry_cant.EndCantRight == pytest.approx(0.15)
    curve_cant = cant_segments[2].DesignParameters
    assert curve_cant.StartCantRight == pytest.approx(0.15)

    # the second curve is to the right, so the cant is applied to the left rail
    assert cant_segments[6].DesignParameters.StartCantLeft == pytest.approx(0.12)
    assert cant_segments[6].DesignParameters.StartCantRight == pytest.approx(0.0)


def test_create_from_csv_cant_requires_transitions():
    file = _create_file()

    filepath = _write_csv(
        "X,Y,R,Lin,Lout,E\n"
        "500,2500,0,0,0,0,3340,660,1000,0,0,0.15,4340,5000,0,0,0,0\n"
        "0,100,0,2000,135,1600,5000,105,0\n"
    )
    with pytest.raises(ValueError):
        ifcopenshell.api.alignment.create_from_csv(file, filepath)
    os.remove(filepath)


def test_create_from_csv_cant_requires_vertical():
    file = _create_file()

    filepath = _write_csv("X,Y,R,Lin,Lout,E\n" "500,2500,0,0,0,0,3340,660,1000,200,150,0.15,4340,5000,0,0,0,0\n")
    with pytest.raises(ValueError):
        ifcopenshell.api.alignment.create_from_csv(file, filepath)
    os.remove(filepath)


test_create_from_csv()
test_create_from_csv_spiral_transitions()
test_create_from_csv_cant()
test_create_from_csv_cant_requires_transitions()
test_create_from_csv_cant_requires_vertical()
