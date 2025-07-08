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
from ifcopenshell import entity_instance
from collections.abc import Sequence


def create_by_pi_method(
    file: ifcopenshell.file,
    name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[float],
    vpoints: Sequence[Sequence[float]] = None,
    lengths: Sequence[float] = None,
    start_station: float = 0.0,
) -> entity_instance:
    """
    Create an alignment using the PI layout method for both horizontal and vertical alignments.
    If vpoints and lengths are omitted, only a horizontal alignment is created.

    :param name: value for Name attribute
    :param points: (X,Y) pairs denoting the location of the horizontal PIs, including start and end
    :param radii: radii values to use for transition
    :param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    :param lengths: parabolic vertical curve horizontal length values to use for transition
    :return: Returns an IfcAlignment
    """
    include_vertical = True if vpoints and lengths else False
    alignment = ifcopenshell.api.alignment.create(
        file, name, include_vertical=include_vertical, start_station=start_station
    )
    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(file, horizontal_layout, hpoints, radii)
    if include_vertical:
        vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(file, vertical_layout, vpoints, lengths)

    return alignment
