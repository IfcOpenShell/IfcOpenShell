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

from typing import Union

import numpy as np

import ifcopenshell
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._add_segment_to_layout import _add_segment_to_layout


def create_layout_segment(
    file: ifcopenshell.file, layout: entity_instance, design_parameters: entity_instance
) -> Union[np.array, None]:
    """
    Creates a new IfcAlignmentSegment using the IfcAlignmentParameterSegment design parameters.
    The new segment is appended to the layout alignment and the corresponding IfcCurveSegment is created in the geometric representation if it exists.

    :param layout: The layout to receive the new layout segment. This parameter is expected to be IfcAlignmentHorizontal, IfcAlignmentVertical or IfcAlignmentCant
    :param design_parameters: The parameters defining the segment. Expected to be the appropreate subclass of IfcAlignmentParameterSegment
    :return: 4x4 matrix at end of segment as np.array intended to be used as the start point geometry for the next segment or None if there is the geometric representation is not defined.
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if layout.is_a("IfcAlignmentHorizontal") and not design_parameters.is_a("IfcAlignmentHorizontalSegment"):
        raise TypeError("Expected design_parameters to be IfcAlignmentHorizontalSegment")
    elif layout.is_a("IfcAlignmentVertical") and not design_parameters.is_a("IfcAlignmentVerticalSegment"):
        raise TypeError("Expected design_parameters to be IfcAlignmentVerticalSegment")
    elif layout.is_a("IfcAlignmentCant") and not design_parameters.is_a("IfcAlignmentCantSegment"):
        raise TypeError("Expected design_parameters to be IfcAlignmentCantSegment")

    # create the segment and add it to the layout.
    segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)
    end = _add_segment_to_layout(
        file, layout, segment
    )  # adds to layout and geometric representation (if present, also updates zero length segment position)

    return end
