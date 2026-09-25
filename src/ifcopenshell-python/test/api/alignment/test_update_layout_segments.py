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

"""update_layout_segments keeps existing IfcAlignmentSegments (and their GlobalIds) where the caller
maps new segments onto them, and the rebuilt geometry matches a freshly built layout."""

import pytest

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
from ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method import _horizontal_design_parameters
from ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method import _vertical_design_parameters


def _file():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    ifcopenshell.api.unit.assign_unit(file, units=[ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")])
    return file


HPOINTS = [(0.0, 0.0), (500.0, 0.0), (900.0, 300.0), (1300.0, 300.0)]
VPOINTS = [(0.0, 100.0), (300.0, 106.0), (700.0, 101.0), (1000.0, 104.0)]


def _alignment(file, radii, vlengths=(100.0, 80.0)):
    return ifcopenshell.api.alignment.create_by_pi_method(file, "A", HPOINTS, radii, VPOINTS, list(vlengths))


def _real(layout):
    return [s for s in ifcopenshell.api.alignment.get_layout_segments(layout) if not _is_terminator(s)]


def _is_terminator(segment):
    dp = segment.DesignParameters
    length = dp.SegmentLength if dp.is_a("IfcAlignmentHorizontalSegment") else dp.HorizontalLength
    return length == 0.0


def _geometry(layout):
    """Every IfcCurveSegment of the layout's curve, as comparable numbers."""
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    out = []
    for cs in curve.Segments:
        placement = cs.Placement
        length = cs.SegmentLength.wrappedValue if hasattr(cs.SegmentLength, "wrappedValue") else cs.SegmentLength
        out.append(
            (cs.ParentCurve.is_a(), tuple(round(c, 6) for c in placement.Location.Coordinates), round(length, 6))
        )
    return out


def _terminator_start(layout):
    dp = next(s for s in ifcopenshell.api.alignment.get_layout_segments(layout) if _is_terminator(s)).DesignParameters
    if dp.is_a("IfcAlignmentHorizontalSegment"):
        return tuple(round(c, 6) for c in dp.StartPoint.Coordinates) + (round(dp.StartDirection, 9),)
    return (round(dp.StartDistAlong, 6), round(dp.StartHeight, 6), round(dp.StartGradient, 9))


def _terminal_curve_segment(layout):
    placement = ifcopenshell.api.alignment.get_layout_curve(layout).Segments[-1].Placement
    return tuple(round(c, 6) for c in placement.Location.Coordinates) + tuple(
        round(c, 9) for c in placement.RefDirection.DirectionRatios
    )


def _no_orphan_curve_segments(file):
    used = sum(len(c.Segments or ()) for c in file.by_type("IfcCompositeCurve"))
    assert len(file.by_type("IfcCurveSegment")) == used


def test_parameter_change_keeps_every_guid_and_matches_a_fresh_layout():
    file = _file()
    alignment = _alignment(file, [(200.0, 60.0, 60.0), (300.0, 0.0, 0.0)])
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    before = [s.GlobalId for s in _real(h)]

    new_radii = [(250.0, 80.0, 80.0), (400.0, 0.0, 0.0)]  # same structure, different radius/spirals
    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(HPOINTS, new_radii)
    assert len(definitions) == len(before)
    parameters = [_horizontal_design_parameters(file, d) for d in definitions]
    ifcopenshell.api.alignment.update_layout_segments(file, h, list(zip(_real(h), parameters)))

    assert [s.GlobalId for s in _real(h)] == before
    reference_file = _file()  # keep the file alive: its entities don't
    reference = ifcopenshell.api.alignment.get_horizontal_layout(_alignment(reference_file, new_radii))
    assert _geometry(h) == _geometry(reference)
    # the zero-length terminator (segment and curve segment) is moved and turned to stay tangent to the
    # new last segment, exactly as a freshly built layout's is
    assert _terminator_start(h) == _terminator_start(reference)
    assert _terminal_curve_segment(h) == _terminal_curve_segment(reference)
    _no_orphan_curve_segments(file)


def test_last_segment_change_keeps_the_terminator_tangent():
    """Only the last tangent's direction changes (the end point moves); the terminator follows it."""
    file = _file()
    alignment = _alignment(file, [200.0, 300.0])
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    points = HPOINTS[:-1] + [(1300.0, 500.0)]
    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(points, [200.0, 300.0])
    ifcopenshell.api.alignment.update_layout_segments(
        file, h, [(k, _horizontal_design_parameters(file, d)) for k, d in zip(_real(h), definitions)]
    )
    reference_file = _file()
    reference = ifcopenshell.api.alignment.get_horizontal_layout(
        ifcopenshell.api.alignment.create_by_pi_method(
            reference_file, "R", points, [200.0, 300.0], VPOINTS, [100.0, 80.0]
        )
    )
    assert _terminator_start(h) == _terminator_start(reference)
    assert _terminal_curve_segment(h) == _terminal_curve_segment(reference)
    x, y, direction = _terminator_start(h)
    assert (round(x, 3), round(y, 3)) == (1300.0, 500.0)


def test_deleting_a_pi_keeps_the_remaining_guids():
    file = _file()
    alignment = _alignment(file, [(200.0, 0.0, 0.0), (300.0, 0.0, 0.0)])
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    real = _real(h)
    assert [s.DesignParameters.PredefinedType for s in real] == ["LINE", "CIRCULARARC", "LINE", "CIRCULARARC", "LINE"]

    # delete PI 2: its arc and the tangent before it go; the rest are kept, the last tangent rejoined
    points = [HPOINTS[0], HPOINTS[1], HPOINTS[3]]
    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(points, [200.0])
    assert [d.predefined_type for d in definitions] == ["LINE", "CIRCULARARC", "LINE"]
    keep = [real[0], real[1], real[4]]
    ifcopenshell.api.alignment.update_layout_segments(
        file, h, [(k, _horizontal_design_parameters(file, d)) for k, d in zip(keep, definitions)]
    )
    assert [s.GlobalId for s in _real(h)] == [k.GlobalId for k in keep]
    assert (
        len(file.by_type("IfcAlignmentSegment"))
        == len(keep) + 1 + len(_real(ifcopenshell.api.alignment.get_vertical_layout(alignment))) + 1
    )
    reference_file = _file()
    reference = ifcopenshell.api.alignment.get_horizontal_layout(
        ifcopenshell.api.alignment.create_by_pi_method(reference_file, "B", points, [200.0], VPOINTS, [100.0, 80.0])
    )
    assert _geometry(h) == _geometry(reference)
    _no_orphan_curve_segments(file)


def test_inserting_a_pi_creates_only_the_new_segments():
    file = _file()
    points = [HPOINTS[0], HPOINTS[1], HPOINTS[3]]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(file, "A", points, [200.0], VPOINTS, [100.0, 80.0])
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    real = _real(h)
    before = {s.GlobalId for s in real}

    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(HPOINTS, [200.0, 300.0])
    # LINE ARC | LINE ARC (new PI) | LINE: the old last tangent stays last
    mapping = [real[0], real[1], None, None, real[2]]
    ifcopenshell.api.alignment.update_layout_segments(
        file, h, [(k, _horizontal_design_parameters(file, d)) for k, d in zip(mapping, definitions)]
    )
    after = [s.GlobalId for s in _real(h)]
    assert after[0] == real[0].GlobalId and after[1] == real[1].GlobalId and after[4] == real[2].GlobalId
    assert len(set(after[2:4]) - before) == 2
    _no_orphan_curve_segments(file)


def test_vertical_layout_curve_length_change_keeps_guids():
    file = _file()
    alignment = _alignment(file, [200.0, 300.0])
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    before = [s.GlobalId for s in _real(v)]
    parameters = list(_vertical_design_parameters(file, VPOINTS, [140.0, 60.0]))
    assert len(parameters) == len(before)
    ifcopenshell.api.alignment.update_layout_segments(file, v, list(zip(_real(v), parameters)))
    assert [s.GlobalId for s in _real(v)] == before
    reference_file = _file()
    reference = ifcopenshell.api.alignment.get_vertical_layout(
        _alignment(reference_file, [200.0, 300.0], (140.0, 60.0))
    )
    assert _geometry(v) == _geometry(reference)
    assert _terminator_start(v) == _terminator_start(reference)
    assert _terminal_curve_segment(v) == _terminal_curve_segment(reference)


def test_segment_representations_are_rebuilt():
    file = _file()
    alignment = _alignment(file, [200.0, 300.0])
    ifcopenshell.api.alignment.create_segment_representations(file, alignment)
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(HPOINTS, [250.0, 350.0])
    ifcopenshell.api.alignment.update_layout_segments(
        file, h, [(k, _horizontal_design_parameters(file, d)) for k, d in zip(_real(h), definitions)]
    )
    curve = ifcopenshell.api.alignment.get_layout_curve(h)
    for segment, curve_segment in zip(_real(h), curve.Segments):
        assert segment.Representation.Representations[0].Items[0] == curve_segment


def test_rejects_segments_from_another_layout():
    file = _file()
    alignment = _alignment(file, [200.0, 300.0])
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    definitions = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(HPOINTS, [200.0, 300.0])
    with pytest.raises(ValueError):
        ifcopenshell.api.alignment.update_layout_segments(
            file, h, [(_real(v)[0], _horizontal_design_parameters(file, definitions[0]))]
        )
