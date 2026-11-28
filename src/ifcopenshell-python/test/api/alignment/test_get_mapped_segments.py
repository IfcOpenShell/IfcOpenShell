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

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.nest
import ifcopenshell.api.unit
import ifcopenshell.guid


def _new_file_with_axis_context():
    file = ifcopenshell.file(schema="IFC4X3")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    angle = ifcopenshell.api.unit.add_si_unit(file, unit_type="PLANEANGLEUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length, angle])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    return file


def _fake_curve_segment(file, segment_length):
    # A structurally-valid but geometrically-meaningless IfcCurveSegment. get_mapped_segments()
    # only ever returns these by reference -- it never evaluates them -- so their actual shape
    # doesn't matter for testing the index math.
    placement = file.createIfcAxis2Placement2D(
        Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
    )
    parent_curve = file.createIfcLine(
        Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
        Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
    )
    return file.createIfcCurveSegment(
        Transition="DISCONTINUOUS",
        Placement=placement,
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(segment_length),
        ParentCurve=parent_curve,
    )


def test_get_mapped_segments_returns_consecutive_helmert_curve_segments():
    # HELMERTCURVE is the one horizontal segment type that maps to two IfcCurveSegment geometric
    # representations instead of one. get_mapped_segments() previously returned
    # (curve.Segments[index - segment_count], curve.Segments[index]) for the second half, which is
    # one position too far -- curve.Segments[index] belongs to whatever segment comes *after* the
    # Helmert curve (or is out of range for the last real segment). The fix returns
    # curve.Segments[index - 1], the Helmert curve's own second half.
    #
    # This builds the IFC graph directly instead of going through create_layout_segment(), which
    # requires a registered geometry mapping for the schema to compute segment end points --
    # get_mapped_segments() itself is pure graph traversal and needs no geometry evaluation.
    file = _new_file_with_axis_context()

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment")
    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)

    # curve already has the mandatory zero-length terminal IfcCurveSegment; insert the LINE and
    # HELMERTCURVE curve segments in front of it.
    line_curve_segment = _fake_curve_segment(file, 100.0)
    helmert_curve_segment_a = _fake_curve_segment(file, 50.0)
    helmert_curve_segment_b = _fake_curve_segment(file, 50.0)
    curve.Segments = (line_curve_segment, helmert_curve_segment_a, helmert_curve_segment_b) + curve.Segments
    assert len(curve.Segments) == 4  # LINE, Helmert x2, zero-length terminal

    line_design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )
    helmert_design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((100.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )
    line_layout_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=line_design_parameters
    )
    helmert_layout_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=helmert_design_parameters
    )
    # append then swap into place ahead of the mandatory zero-length terminal segment, in order --
    # the same two steps _add_segment_to_layout() performs per segment, minus the geometric
    # end-point calculation.
    ifcopenshell.api.nest.assign_object(file, related_objects=[line_layout_segment], relating_object=layout)
    ifcopenshell.api.nest.reorder_nesting(file, line_layout_segment, -1, -1)
    ifcopenshell.api.nest.assign_object(file, related_objects=[helmert_layout_segment], relating_object=layout)
    ifcopenshell.api.nest.reorder_nesting(file, helmert_layout_segment, -1, -1)

    # order is [LINE, HELMERTCURVE, zero-length terminal segment]; the terminal segment is also
    # PredefinedType="LINE" (with SegmentLength=0.0)
    layout_segments = ifcopenshell.api.alignment.get_layout_segments(layout)
    assert [s.DesignParameters.PredefinedType for s in layout_segments] == ["LINE", "HELMERTCURVE", "LINE"]
    assert layout_segments[1] == helmert_layout_segment

    mapped_segments = ifcopenshell.api.alignment.get_mapped_segments(helmert_layout_segment)
    assert len(mapped_segments) == 2
    first_half, second_half = mapped_segments
    assert first_half is not None
    assert second_half is not None

    # the two halves must be the two consecutive IfcCurveSegment entities belonging to the Helmert
    # curve, identity-checked against curve.Segments -- not, e.g., the LINE segment's curve
    # segment and the Helmert's first half (the pre-fix off-by-one).
    assert first_half == helmert_curve_segment_a
    assert second_half == helmert_curve_segment_b
    assert first_half == curve.Segments[1]
    assert second_half == curve.Segments[2]


def test_get_mapped_segments_and_segment_vertices_for_helmert_curve():
    # End-to-end regression test built the realistic way, via create_layout_segment() -- matching
    # every other test in this suite. This requires a registered geometry mapping for the schema
    # (ifcopenshell_wrapper.map_shape) to compute each segment's end point while chaining the
    # layout together, and again inside segment_vertices() itself.
    file = _new_file_with_axis_context()

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment")
    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    line_design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, layout, line_design_parameters)

    helmert_design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((100.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, layout, helmert_design_parameters)

    # layout order is [LINE, HELMERTCURVE, zero-length terminal segment]
    layout_segments = ifcopenshell.api.alignment.get_layout_segments(layout)
    helmert_layout_segment = layout_segments[-2]
    assert helmert_layout_segment.DesignParameters.PredefinedType == "HELMERTCURVE"

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    # curve.Segments is [LINE cs(0), Helmert cs(1), Helmert cs(2), zero-length cs(3)]
    assert len(curve.Segments) == 4

    mapped_segments = ifcopenshell.api.alignment.get_mapped_segments(helmert_layout_segment)
    assert len(mapped_segments) == 2
    first_half, second_half = mapped_segments
    assert first_half is not None
    assert second_half is not None
    assert first_half == curve.Segments[1]
    assert second_half == curve.Segments[2]

    # segment_vertices() must not raise for a HELMERTCURVE alignment segment (previously: NameError
    # from the `segment[1]` typo)
    start, end, ti, ni = ifcopenshell.api.alignment.segment_vertices(file, helmert_layout_segment)
    assert start is not None
    assert end is not None


test_get_mapped_segments_returns_consecutive_helmert_curve_segments()
test_get_mapped_segments_and_segment_vertices_for_helmert_curve()
