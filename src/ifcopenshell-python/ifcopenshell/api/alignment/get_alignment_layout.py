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

from collections.abc import Sequence

from ifcopenshell import entity_instance


def get_alignment_layout(segment: entity_instance) -> entity_instance:
    """
    Returns the layout alignment that the segment is nested into
    """
    expected_types = ["IfcAlignmentSegment"]
    if not segment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{segment.is_a()}"
        )

    layout = None
    layouts = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    for nest in segment.Nests:
        if nest.RelatingObject.is_a() in layouts:
            layout = nest.RelatingObject
            break

    return layout
