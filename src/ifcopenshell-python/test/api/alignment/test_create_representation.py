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


import math

import pytest
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.unit


def test_create_representation():
    # expected values for horizontal segment ends points (X,Y,dx,dy)
    h_expected = [
        (500.0, 2500.0, math.cos(math.radians(327.0613)), math.sin(math.radians(327.0613))),
        (2142.2378194934668, 1436.0145490066361, 0.8392527899703555, -0.5437414408769801),
        (3660.446048592728, 2050.735651565721, 0.22453168741127044, 0.9744667882222808),
        (4084.1161141648777, 3889.4623490042068, 0.22453168741127047, 0.9744667882222809),
        (5469.395455576321, 4847.565492667097, 0.9910142023415828, -0.13375668490687387),
        (7019.971720182908, 4638.284999653966, 0.9910142023415827, -0.13375668490687387),
        (7790.932377201981, 4006.729563689594, 0.32621900658961334, -0.9452942186111613),
        (8479.999918938518, 2009.9986857258034, 0.32621900658961345, -0.9452942186111613),
    ]

    # expected values for vertical segment ends points (X,Y,dx,dy)
    v_expected = [
        (0.0, 100.0, 0.999846910161925, 0.01749732092783369),
        (1200.0, 121.0, 0.999846910161925, 0.01749732092783369),
        (2799.99999384661, 127.00000006153391, 0.9999500037507449, -0.009999499931751348),
        (4399.99999384661, 111.00000023075212, 0.999950003750745, -0.009999499931751352),
        (5599.9999883553455, 117.00000018438367, 0.999800059982751, 0.019996001062400855),
        (6399.999988355345, 133.0000000745584, 0.999800059982751, 0.019996001062400855),
        (8399.99998428796, 133.00000001862446, 0.999800059981633, -0.019996001118301257),
        (9399.99998428796, 113.00000009997211, 0.999800059981633, -0.019996001118301257),
        (10199.99998062693, 103.00000015081635, 0.9999875002340269, -0.004999937569813611),
        (12799.99998062693, 89.99999997234107, 0.9999875002340269, -0.004999937569813611),
    ]

    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.header.file_description.description = ["ViewDefinition [Alignment-basedView]"]

    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="FHWA Alignment")
    # ifcopenshell.api.unit.assign_unit(file)
    # length = ifcopenshell.api.unit.add_si_unit(file,unit_type="LENGTHUNIT")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")
    ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

    alignment = ifcopenshell.api.alignment.create(
        file, "E-Line", include_vertical=True, start_station=10000.0, include_geometry=False
    )

    # alignment is referenced into spatial structure of site per CT 4.1.5.1
    ifcopenshell.api.spatial.reference_structure(file, products=[alignment], relating_structure=site)

    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    segment1 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((500.0, 2500.0))),
        StartDirection=math.radians(327.0613),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=1956.785654,
        PredefinedType="LINE",
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[1][0]) == x
        and pytest.approx(h_expected[1][1]) == y
        and pytest.approx(h_expected[1][2]) == dx
        and pytest.approx(h_expected[1][3]) == dy
    )
    segment2 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=1919.222667,
        PredefinedType="CIRCULARARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment2)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[2][0]) == x
        and pytest.approx(h_expected[2][1]) == y
        and pytest.approx(h_expected[2][2]) == dx
        and pytest.approx(h_expected[2][3]) == dy
    )
    segment3 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=1886.905454,
        PredefinedType="LINE",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment3)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[3][0]) == x
        and pytest.approx(h_expected[3][1]) == y
        and pytest.approx(h_expected[3][2]) == dx
        and pytest.approx(h_expected[3][3]) == dy
    )
    segment4 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=-1250.0,
        EndRadiusOfCurvature=-1250.0,
        SegmentLength=1848.115835,
        PredefinedType="CIRCULARARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment4)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[4][0]) == x
        and pytest.approx(h_expected[4][1]) == y
        and pytest.approx(h_expected[4][2]) == dx
        and pytest.approx(h_expected[4][3]) == dy
    )
    segment5 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=1564.635765,
        PredefinedType="LINE",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment5)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[5][0]) == x
        and pytest.approx(h_expected[5][1]) == y
        and pytest.approx(h_expected[5][2]) == dx
        and pytest.approx(h_expected[5][3]) == dy
    )
    segment6 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=-950.0,
        EndRadiusOfCurvature=-950.0,
        SegmentLength=1049.119737,
        PredefinedType="CIRCULARARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment6)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    assert (
        pytest.approx(h_expected[6][0]) == x
        and pytest.approx(h_expected[6][1]) == y
        and pytest.approx(h_expected[6][2]) == dx
        and pytest.approx(h_expected[6][3]) == dy
    )
    segment7 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=2112.285084,
        PredefinedType="LINE",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment7)
    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(h_expected[7][0]) == x
        and pytest.approx(h_expected[7][1]) == y
        and pytest.approx(h_expected[7][2]) == dx
        and pytest.approx(h_expected[7][3]) == dy
    )

    vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    segment1 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=1200.0,
        StartHeight=100.0,
        StartGradient=1.75 / 100.0,
        EndGradient=1.75 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment1)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[1][0]) == x
        and pytest.approx(v_expected[1][1]) == y
        and pytest.approx(v_expected[1][2]) == dx
        and pytest.approx(v_expected[1][3]) == dy
    )
    segment2 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=1600.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-1.0 / 100.0,
        PredefinedType="PARABOLICARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment2)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[2][0]) == x
        and pytest.approx(v_expected[2][1]) == y
        and pytest.approx(v_expected[2][2]) == dx
        and pytest.approx(v_expected[2][3]) == dy
    )
    segment3 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=1600.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-1.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment3)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[3][0]) == x
        and pytest.approx(v_expected[3][1]) == y
        and pytest.approx(v_expected[3][2]) == dx
        and pytest.approx(v_expected[3][3]) == dy
    )
    segment4 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=1200.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=2.0 / 100.0,
        PredefinedType="PARABOLICARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment4)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[4][0]) == x
        and pytest.approx(v_expected[4][1]) == y
        and pytest.approx(v_expected[4][2]) == dx
        and pytest.approx(v_expected[4][3]) == dy
    )
    segment5 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=800.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=2.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment5)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[5][0]) == x
        and pytest.approx(v_expected[5][1]) == y
        and pytest.approx(v_expected[5][2]) == dx
        and pytest.approx(v_expected[5][3]) == dy
    )
    segment6 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=2000.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-2.0 / 100.0,
        PredefinedType="PARABOLICARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment6)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[6][0]) == x
        and pytest.approx(v_expected[6][1]) == y
        and pytest.approx(v_expected[6][2]) == dx
        and pytest.approx(v_expected[6][3]) == dy
    )
    segment7 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=1000.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-2.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment7)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[7][0]) == x
        and pytest.approx(v_expected[7][1]) == y
        and pytest.approx(v_expected[7][2]) == dx
        and pytest.approx(v_expected[7][3]) == dy
    )
    segment8 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=800.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-0.5 / 100.0,
        PredefinedType="PARABOLICARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment8)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[8][0]) == x
        and pytest.approx(v_expected[8][1]) == y
        and pytest.approx(v_expected[8][2]) == dx
        and pytest.approx(v_expected[8][3]) == dy
    )
    segment9 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=x,
        HorizontalLength=2600.0,
        StartHeight=y,
        StartGradient=dy / dx,
        EndGradient=-0.5 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment9)
    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    assert (
        pytest.approx(v_expected[9][0]) == x
        and pytest.approx(v_expected[9][1]) == y
        and pytest.approx(v_expected[9][2]) == dx
        and pytest.approx(v_expected[9][3]) == dy
    )

    ifcopenshell.api.alignment.create_representation(file, alignment)

    curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    assert curve.is_a("IfcCompositeCurve")
    for s in curve.Segments:
        assert len(s.UsingCurves) == 1

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    assert curve.is_a("IfcCompositeCurve")
    for index, s in enumerate(curve.Segments):
        assert len(s.UsingCurves) == 1
        assert s.Placement.Location.Coordinates[0] == pytest.approx(h_expected[index][0])
        assert s.Placement.Location.Coordinates[1] == pytest.approx(h_expected[index][1])
        assert s.Placement.RefDirection.DirectionRatios[0] == pytest.approx(h_expected[index][2])
        assert s.Placement.RefDirection.DirectionRatios[1] == pytest.approx(h_expected[index][3])

    curve = ifcopenshell.api.alignment.get_layout_curve(vlayout)
    assert curve.is_a("IfcGradientCurve")
    for index, s in enumerate(curve.Segments):
        assert len(s.UsingCurves) == 1
        assert s.Placement.Location.Coordinates[0] == pytest.approx(v_expected[index][0])
        assert s.Placement.Location.Coordinates[1] == pytest.approx(v_expected[index][1])
        assert s.Placement.RefDirection.DirectionRatios[0] == pytest.approx(v_expected[index][2])
        assert s.Placement.RefDirection.DirectionRatios[1] == pytest.approx(v_expected[index][3])


test_create_representation()
