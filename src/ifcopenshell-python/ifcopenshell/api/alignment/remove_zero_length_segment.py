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
import ifcopenshell.api.alignment.remove_last_segment


def remove_zero_length_segment(file: ifcopenshell.file, entity: entity_instance) -> entity_instance:
    """
    Removes the zero length segment from the end of entity.

    :param entity: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant or IfcCompositeCurve
    :return: The zero length segment
    """
    if not ifcopenshell.api.alignment.has_zero_length_segment(entity):
        return None

    return ifcopenshell.api.alignment.remove_last_segment(file, entity)
