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
import ifcopenshell.api.nest
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import numpy as np
from ifcopenshell import entity_instance
import ifcopenshell.util
import ifcopenshell.util.element


def remove_last_segment(file: ifcopenshell.file, entity: entity_instance) -> entity_instance:
    """
    Removes the last segment from the end of entity.

    :param entity: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant or IfcCompositeCurve
    :return: The segment
    """
    expected_types = [
        "IfcAlignmentHorizontal",
        "IfcAlignmentVertical",
        "IfcAlignmentCant",
        "IfcCompositeCurve",
        "IfcGradientCurve",
        "IfcSegmentedReferenceCurve",
    ]
    if not entity.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{entity.is_a()}"
        )

    if entity.is_a("IfcCompositeCurve"):
        last_segment = entity.Segments[-1]
        entity.Segments = tuple(set(entity.Segments) - {last_segment})
        entity.Segments[-1].Transition = "DISCONTINUOUS"
        return last_segment
    else:
        components = ifcopenshell.util.element.get_components(entity)
        last_segment = components[-1]
        ifcopenshell.api.nest.unassign_object(file, (last_segment,))
        return last_segment
