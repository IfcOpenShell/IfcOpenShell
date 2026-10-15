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

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import test.bootstrap


# other test cases cover the typical vertical by PI method (test_create_alignment_by_pi_method)
# this test will focus on the edge cases of no initial tangent run, no final tangent run, and
# compound curve (no tangent between curves)
@test.bootstrap.requires_ifc4x3
def test_horizontal_layout_by_pi_method():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
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

    coordinates = [(838.760, 224.745), (965.926, 258.819), (1226.296, 258.819), (1350.817, 291.415)]
    radii = [(1000.0), (1000.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, start_station=10000.0
    )

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 2
    stationing_nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    layout_nest = ifcopenshell.api.alignment.get_alignment_layout_nest(alignment)
    assert stationing_nest.RelatedObjects[0].is_a("IfcReferent")
    assert layout_nest.RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout_nest.RelatedObjects[0])
    assert len(segment_nest.RelatedObjects) == 3  # segments in horizontal layout


def _horizontal_segments(alignment):
    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
    return [s.DesignParameters for s in segment_nest.RelatedObjects if s.DesignParameters.SegmentLength > 0.0]


# a PI with no curve and no deflection (the alignment goes straight on through it) splits the
# straight in two
@test.bootstrap.requires_ifc4x3
def test_horizontal_layout_by_pi_method_zero_deflection_without_curve():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")

    coordinates = [(0.0, 0.0), (100.0, 0.0), (250.0, 0.0)]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, [0.0])

    segments = _horizontal_segments(alignment)
    assert [s.PredefinedType for s in segments] == ["LINE", "LINE"]
    assert [s.SegmentLength for s in segments] == pytest.approx([100.0, 150.0])
    assert segments[1].StartPoint.Coordinates == pytest.approx((100.0, 0.0))


# a curve can't be fitted at a PI with no deflection
@test.bootstrap.requires_ifc4x3
def test_horizontal_layout_by_pi_method_zero_deflection_with_curve():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")

    coordinates = [(0.0, 0.0), (100.0, 0.0), (250.0, 0.0)]
    with pytest.raises(ValueError):
        ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, [500.0])


# a curve whose tangents cross the +/-180 degree direction (heading west) turns by the deflection
# angle, not by 360 degrees less it
@test.bootstrap.requires_ifc4x3
def test_horizontal_layout_by_pi_method_deflection_across_west():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")

    for back, forward, radius in ((170.0, 190.0, 200.0), (190.0, 170.0, -200.0)):  # a left and a right turn
        b, f = math.radians(back), math.radians(forward)
        coordinates = [
            (0.0, 0.0),
            (100.0 * math.cos(b), 100.0 * math.sin(b)),
            (100.0 * (math.cos(b) + math.cos(f)), 100.0 * (math.sin(b) + math.sin(f))),
        ]
        alignment = ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, [200.0])

        layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        segments = ifcopenshell.api.alignment.get_alignment_segment_nest(layout).RelatedObjects
        arc = segments[1].DesignParameters
        assert arc.PredefinedType == "CIRCULARARC"
        assert arc.StartRadiusOfCurvature == pytest.approx(radius)
        assert arc.SegmentLength == pytest.approx(200.0 * math.radians(20.0))
