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
import ifcopenshell.api.alignment
from ifcopenshell import entity_instance


def _add_zero_length_segment(file: ifcopenshell.file, layout: entity_instance) -> None:
    """
    Adds a zero length segment to the end of a layout. Also adds a zero length segment to the end of the corresponding geometric curve.

    This function depends on the assumptions made in ifcopenshell.api.alignment.create and is called by that function.
    This is not a general purpose function.

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :return: None
    """

    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected layout type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    ifcopenshell.api.alignment.add_zero_length_segment(file, layout)

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    if curve:
        ifcopenshell.api.alignment.add_zero_length_segment(file, curve)
