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
from ifcopenshell import entity_instance


def get_alignment_segment_nest(layout: entity_instance) -> entity_instance:
    """
    Searches for the IfcRelNest that contains IfcAlignmentSegment

    :param layout: an alignment layout, expected to be one of IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :return: Returns the IfcRelNests
    """
    for nest in layout.IsNestedBy:
        for related_object in nest.RelatedObjects:
            if related_object.is_a("IfcAlignmentSegment"):
                return nest
    return None
