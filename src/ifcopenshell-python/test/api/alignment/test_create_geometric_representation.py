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
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.nest
import ifcopenshell.api.unit
from ifcopenshell.api.alignment._create_geometric_representation import (
    _create_geometric_representation,
)


def test_child_alignment_with_vertical_and_cant_gets_a_segmented_reference_curve():
    # IFC CT 4.1.4.4.1.2 "Reusing Horizontal Layout": a child IfcAlignment nests its own
    # IfcAlignmentVertical and IfcAlignmentCant while reusing the parent's horizontal layout. There
    # is no public API to build this today (add_vertical_layout() only ever creates children that
    # nest a single IfcAlignmentVertical), so the len(child_layouts) == 2 branch inside
    # _create_geometric_representation() -- which builds the child's IfcSegmentedReferenceCurve --
    # was unreachable and its `file.creatIfcShapeRepresentation` typo (missing "e") went unnoticed.
    # This constructs that scenario directly against the private helper to exercise the fix.
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    # parent: horizontal + vertical, geometry deferred so _create_geometric_representation is
    # invoked exactly once, explicitly, below.
    parent_alignment = ifcopenshell.api.alignment.create(file, "Parent", include_vertical=True, include_geometry=False)

    # child: vertical + cant, both nested directly to a new child alignment, reusing the parent's
    # horizontal -- the CT 4.1.4.4.1.2 shape that has no builder function yet.
    child_alignment = file.createIfcAlignment(GlobalId=ifcopenshell.guid.new(), Name="Child of Parent")
    child_vertical_layout = file.createIfcAlignmentVertical(GlobalId=ifcopenshell.guid.new())
    child_cant_layout = file.createIfcAlignmentCant(GlobalId=ifcopenshell.guid.new(), RailHeadDistance=1.0)
    ifcopenshell.api.nest.assign_object(
        file, related_objects=[child_vertical_layout, child_cant_layout], relating_object=child_alignment
    )
    ifcopenshell.api.aggregate.assign_object(file, products=[child_alignment], relating_object=parent_alignment)

    # before the fix this raised AttributeError: 'file' object has no attribute
    # 'creatIfcShapeRepresentation'
    _create_geometric_representation(file, parent_alignment)

    curve = ifcopenshell.api.alignment.get_curve(child_alignment)
    assert curve is not None
    assert curve.is_a("IfcSegmentedReferenceCurve")
    assert curve.BaseCurve.is_a("IfcGradientCurve")

    assert child_alignment.ObjectPlacement == parent_alignment.ObjectPlacement


test_child_alignment_with_vertical_and_cant_gets_a_segmented_reference_curve()
