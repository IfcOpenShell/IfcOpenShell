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
import ifcopenshell.guid
from ifcopenshell.api.alignment._get_segment_start_point_label import (
    _get_segment_start_point_label,
)


def test_vertical_constant_gradient_to_constant_gradient_label_has_trailing_period():
    # Every other label in the lookup tables ends with a period (e.g. "P.C.", "P.V.C.",
    # "P.V.T."); CONSTANTGRADIENT -> CONSTANTGRADIENT ("P.V.I") was missing its trailing period.
    file = ifcopenshell.file(schema="IFC4X3")

    dp1 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=0.0,
        StartGradient=0.01,
        EndGradient=0.01,
        PredefinedType="CONSTANTGRADIENT",
    )
    dp2 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=100.0,
        HorizontalLength=100.0,
        StartHeight=1.0,
        StartGradient=0.02,
        EndGradient=0.02,
        PredefinedType="CONSTANTGRADIENT",
    )
    prev_segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=dp1)
    segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=dp2)

    assert _get_segment_start_point_label(prev_segment, segment) == "P.V.I."


test_vertical_constant_gradient_to_constant_gradient_label_has_trailing_period()
