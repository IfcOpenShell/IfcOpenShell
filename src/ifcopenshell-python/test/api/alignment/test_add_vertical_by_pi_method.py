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


def test_add_vertical_by_pi_method():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(Name="Test")
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    # single horizontal alignment
    alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(file, "TestAlignment", coordinates, radii)

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 1  # nesting IfcAlignemtHorizontal
    assert len(alignment.IsNestedBy[0].RelatedObjects) == 1  # nesting one IfcAlignmentHorizontal
    assert alignment.IsNestedBy[0].RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    assert (
        len(alignment.IsNestedBy[0].RelatedObjects[0].IsNestedBy) == 1
    )  # nesting of segments beneath IfcAlignmentHorizontal
    assert len(alignment.IsNestedBy[0].RelatedObjects[0].IsNestedBy[0].RelatedObjects) == 8  # segments

    # add first vertical
    ifcopenshell.api.alignment.add_vertical_alignment_by_pi_method(file, alignment, vpoints, lengths)
    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 1  # 1 nesting relationsip for the alignments
    assert len(alignment.IsNestedBy[0].RelatedObjects) == 2  # nesting IfcAlignmentHorizontal and IfcAlignmentVertical
    assert alignment.IsNestedBy[0].RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    assert alignment.IsNestedBy[0].RelatedObjects[1].is_a("IfcAlignmentVertical")

    # add second vertical
    ifcopenshell.api.alignment.add_vertical_alignment_by_pi_method(file, alignment, vpoints, lengths)
    assert len(alignment.IsDecomposedBy) == 1  # 1 IfcRelAggreates relationship for the child algiments
    assert (
        len(alignment.IsDecomposedBy[0].RelatedObjects) == 2
    )  # two child alignments, one for the first vertical and one for the vertical just added
    for child_alignment in alignment.IsDecomposedBy[0].RelatedObjects:
        assert child_alignment.is_a("IfcAlignment")
        assert len(child_alignment.IsNestedBy) == 1  # one nesting relationship for the IfcAlignmentVertical
        assert len(child_alignment.IsNestedBy[0].RelatedObjects) == 1  # The IfcAlignmentVertical
        assert child_alignment.IsNestedBy[0].RelatedObjects[0].is_a("IfcAlignmentVertical")
    assert len(alignment.IsNestedBy) == 1  # 1 nesting relationsip for the alignments
    assert len(alignment.IsNestedBy[0].RelatedObjects) == 1  # nesting one IfcAlignmentHorizontal
    assert alignment.IsNestedBy[0].RelatedObjects[0].is_a("IfcAlignmentHorizontal")
