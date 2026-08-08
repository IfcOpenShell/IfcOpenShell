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

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.util.alignment

COORDINATES = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
RADII = [1000.0, 1250.0, 950.0]
VPOINTS = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
LENGTHS = [1600.0, 1200.0, 2000.0, 800.0]


def _new_file():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    return file


def _new_file_no_context():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    return file


def _build_alignment(file, start_station=0.0):
    return ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", COORDINATES, RADII, VPOINTS, LENGTHS, start_station
    )


def _real_segments(layout):
    segments = ifcopenshell.api.alignment.get_layout_segments(layout)
    return segments[:-1] if ifcopenshell.api.alignment.has_zero_length_segment(layout) else segments


def _label(tag):
    return tag.rsplit("(", 1)[1].rstrip(")")


def test_wrong_layout_type_raises_type_error():
    file = _new_file()
    alignment = _build_alignment(file)
    with pytest.raises(TypeError):
        ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, alignment)


def test_not_nested_under_alignment_raises_value_error():
    file = _new_file_no_context()
    horizontal = file.createIfcAlignmentHorizontal(GlobalId=ifcopenshell.guid.new())
    with pytest.raises(ValueError):
        ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)


def test_returns_none():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    result = ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)

    assert result is None


def test_no_referents_or_rel_nests_created():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    referents_before = len(file.by_type("IfcReferent"))
    rel_nests_before = len(file.by_type("IfcRelNests"))

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)

    assert len(file.by_type("IfcReferent")) == referents_before
    assert len(file.by_type("IfcRelNests")) == rel_nests_before


def test_no_real_segments_leaves_tags_none():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    result = ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)

    assert result is None
    segments = ifcopenshell.api.alignment.get_layout_segments(horizontal)
    assert len(segments) == 1  # only the auto zero-length segment
    assert segments[0].DesignParameters.StartTag is None
    assert segments[0].DesignParameters.EndTag is None


def test_single_real_segment_produces_only_boundary_tags():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, horizontal, design_parameters)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal, label_end_tag=True)

    segments = _real_segments(horizontal)
    assert len(segments) == 1
    dp = segments[0].DesignParameters
    assert _label(dp.StartTag) == "P.O.B."
    assert _label(dp.EndTag) == "P.O.E."


def test_end_tag_not_labelled_by_default():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_geometry=False)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, horizontal, design_parameters)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)

    segments = _real_segments(horizontal)
    assert len(segments) == 1
    dp = segments[0].DesignParameters
    assert _label(dp.StartTag) == "P.O.B."
    assert dp.EndTag is None


def test_horizontal_tag_labels_and_adjacency():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal, label_end_tag=True)

    segments = _real_segments(horizontal)
    assert len(segments) == 7

    start_labels = [_label(s.DesignParameters.StartTag) for s in segments]
    end_labels = [_label(s.DesignParameters.EndTag) for s in segments]

    assert start_labels == ["P.O.B.", "P.C.", "P.T.", "P.C.", "P.T.", "P.C.", "P.T."]
    assert end_labels == ["P.C.", "P.T.", "P.C.", "P.T.", "P.C.", "P.T.", "P.O.E."]

    # every real segment has both tags set
    assert all(s.DesignParameters.StartTag is not None for s in segments)
    assert all(s.DesignParameters.EndTag is not None for s in segments)

    # adjacent segments agree on the tag describing their shared transition point
    for i in range(len(segments) - 1):
        assert segments[i].DesignParameters.EndTag == segments[i + 1].DesignParameters.StartTag


def test_vertical_tag_labels_and_adjacency():
    file = _new_file()
    alignment = _build_alignment(file)
    vertical = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, vertical, label_end_tag=True)

    segments = _real_segments(vertical)
    assert len(segments) == 9

    start_labels = [_label(s.DesignParameters.StartTag) for s in segments]
    end_labels = [_label(s.DesignParameters.EndTag) for s in segments]

    assert start_labels == [
        "V.P.O.B.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
    ]
    assert end_labels == [
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "P.V.C.",
        "P.V.T.",
        "V.P.O.E.",
    ]

    assert all(s.DesignParameters.StartTag is not None for s in segments)
    assert all(s.DesignParameters.EndTag is not None for s in segments)

    for i in range(len(segments) - 1):
        assert segments[i].DesignParameters.EndTag == segments[i + 1].DesignParameters.StartTag


def test_cant_layout_boundary_tags():
    file = _new_file_no_context()
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_cant=True, include_geometry=False)
    cant = ifcopenshell.api.alignment.get_cant_layout(alignment)

    dp1 = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, cant, dp1)

    dp2 = file.createIfcAlignmentCantSegment(
        StartDistAlong=100.0,
        HorizontalLength=50.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, cant, dp2)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, cant, label_end_tag=True)

    segments = _real_segments(cant)
    assert _label(segments[0].DesignParameters.StartTag) == "C.P.O.B."
    assert _label(segments[-1].DesignParameters.EndTag) == "C.P.O.E."
    # CONSTANTCANT -> CONSTANTCANT is currently an unfilled "xx" placeholder in the cant lookup
    # table (_get_segment_start_point_label.py) -- out of scope to fill in here.
    assert _label(segments[0].DesignParameters.EndTag) == "xx"
    assert _label(segments[-1].DesignParameters.StartTag) == "xx"


def test_exact_tag_format():
    file = _new_file()
    alignment = _build_alignment(file)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(file, horizontal)

    start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
    segments = _real_segments(horizontal)
    assert segments[0].DesignParameters.StartTag == (
        f"{ifcopenshell.util.alignment.station_as_string(file, start_station)} (P.O.B.)"
    )


test_wrong_layout_type_raises_type_error()
test_not_nested_under_alignment_raises_value_error()
test_returns_none()
test_no_referents_or_rel_nests_created()
test_no_real_segments_leaves_tags_none()
test_single_real_segment_produces_only_boundary_tags()
test_end_tag_not_labelled_by_default()
test_horizontal_tag_labels_and_adjacency()
test_vertical_tag_labels_and_adjacency()
test_cant_layout_boundary_tags()
test_exact_tag_format()
