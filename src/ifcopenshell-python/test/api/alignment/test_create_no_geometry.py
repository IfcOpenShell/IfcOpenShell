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


def test_create_no_geometry():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    # creates an IfcAlignment with an IfcAlignmentHorizontal layout containing only the zero length segment
    ali = ifcopenshell.api.alignment.create(file, "A1", include_vertical=True, include_geometry=False)

    # append a segment to the horizontal layout
    horizontal_alignment = ifcopenshell.api.alignment.get_horizontal_layout(ali)
    vertical_alignment = ifcopenshell.api.alignment.get_vertical_layout(ali)

    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve == None

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, horizontal_alignment, design_parameters)
    assert end == None

    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=50.0,
        StartHeight=20.0,
        StartGradient=1.0 / 100.0,
        EndGradient=1.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vertical_alignment, design_parameters)
    assert end == None


test_create_no_geometry()
