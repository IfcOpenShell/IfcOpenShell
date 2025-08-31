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


def test_add_vertical_alignment():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")

    alignment = ifcopenshell.api.alignment.create(file, "A1", include_vertical=False)

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 2  # nests for layout and referents
    layout_nest = ifcopenshell.api.alignment.get_alignment_layout_nest(alignment)
    assert len(layout_nest.RelatedObjects) == 1
    assert layout_nest.RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    assert len(referent_nest.RelatedObjects) == 2
    assert referent_nest.RelatedObjects[0].is_a("IfcReferent")

    curve = ifcopenshell.api.alignment.get_curve(alignment)
    assert curve.is_a("IfcCompositeCurve")

    vertical_layout = ifcopenshell.api.alignment.add_vertical_layout(file, alignment)

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 2
    assert len(layout_nest.RelatedObjects) == 2
    assert layout_nest.RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    assert layout_nest.RelatedObjects[1].is_a("IfcAlignmentVertical")

    curve = ifcopenshell.api.alignment.get_curve(alignment)
    assert curve.is_a("IfcGradientCurve")

    # add a second vertical alignment
    vertical_layout = ifcopenshell.api.alignment.add_vertical_layout(file, alignment)

    assert len(alignment.IsDecomposedBy) == 1  # 1 IfcRelAggreates relationship for the child algiments
    assert len(alignment.IsDecomposedBy[0].RelatedObjects) == 2

    for child_alignment in alignment.IsDecomposedBy[0].RelatedObjects:
        assert child_alignment.is_a("IfcAlignment")
        assert len(child_alignment.IsNestedBy) == 2
        child_layout_nest = ifcopenshell.api.alignment.get_alignment_layout_nest(child_alignment)
        assert len(child_layout_nest.RelatedObjects) == 1  # The IfcAlignmentVertical
        assert child_layout_nest.RelatedObjects[0].is_a("IfcAlignmentVertical")

    assert len(alignment.IsNestedBy) == 2
    assert len(layout_nest.RelatedObjects) == 1
    assert layout_nest.RelatedObjects[0].is_a("IfcAlignmentHorizontal")


test_add_vertical_alignment()
