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


# other test cases cover the typical vertical by PI method (test_create_alignment_by_pi_method)
# this test will focus on the edge cases of no initial gradient, no final gradient, and
# compound vertical curve (no gradient between curves)
def test_vertical_layout_by_pi_method():
    file = ifcopenshell.file(schema="IFC4X3")
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

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", include_vertical=True)
    hlayout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment1 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),  # Actual coordinate unknown
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=10000.0,
        PredefinedType="LINE",
    )

    ifcopenshell.api.alignment.create_layout_segment(file, hlayout, segment1)

    vpoints = [(0.0, 110.0), (400.0, 100.0), (800.0, 115.0), (1300.0, 125.0), (1800.0, 105.0)]
    lengths = [(800.0), (0.0), (1000.0)]
    vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(file, vlayout, vpoints, lengths)

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments

    assert len(alignment.IsNestedBy) == 2

    layout_nest = ifcopenshell.api.alignment.get_alignment_layout_nest(alignment)
    assert len(layout_nest.RelatedObjects) == 2

    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    assert len(referent_nest.RelatedObjects) == 6

    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(vlayout)
    assert len(segment_nest.RelatedObjects) == 3


test_vertical_layout_by_pi_method()
