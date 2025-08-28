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
# this test will focus on the edge cases of no initial tangent run, no final tangent run, and
# compound curve (no tangent between curves)
def test_horizontal_layout_by_pi_method():
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

    coordinates = [(838.760, 224.745), (965.926, 258.819), (1226.296, 258.819), (1350.817, 291.415)]
    radii = [(1000.0), (1000.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, radii)

    assert len(alignment.IsDecomposedBy) == 0  # no child alignments
    assert len(alignment.IsNestedBy) == 2
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    layout_nest = ifcopenshell.api.alignment.get_alignment_layout_nest(alignment)
    assert referent_nest.RelatedObjects[0].is_a("IfcReferent")
    assert layout_nest.RelatedObjects[0].is_a("IfcAlignmentHorizontal")
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout_nest.RelatedObjects[0])
    assert len(segment_nest.RelatedObjects) == 3  # segments in horizontal layout


test_horizontal_layout_by_pi_method()
