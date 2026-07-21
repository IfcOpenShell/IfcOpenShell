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
from typing import Optional, Union

import ifcopenshell
import ifcopenshell.api.alignment
from ifcopenshell import entity_instance


def create_by_pi_method(
    file: ifcopenshell.file,
    name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[Union[float, Sequence[float]]],
    vpoints: Sequence[Sequence[float]] = None,
    lengths: Sequence[float] = None,
    start_station: float = 0.0,
    cants: Optional[Sequence[float]] = None,
    rail_head_distance: float = 1.0,
) -> entity_instance:
    """
    Create an alignment using the PI layout method for both horizontal and vertical alignments.
    If vpoints and lengths are omitted, only a horizontal alignment is created.

    Each element of radii is either a circular curve radius R or a (R, Lin, Lout) sequence where
    Lin and Lout are the lengths of clothoid spiral transition curves ahead of and following the
    circular curve (see layout_horizontal_alignment_by_pi_method).

    If cants is provided, a cant layout is created as well. Cant segments are created one-for-one
    with the horizontal segments: zero cant on tangent runs, linearly varying cant over spiral
    transitions, and constant cant over circular curves, applied to the rail on the outside of the
    curve. A vertical alignment is required when cants is provided.

    :param name: value for Name attribute
    :param points: (X,Y) pairs denoting the location of the horizontal PIs, including start and end
    :param radii: radii values to use for transition, optionally with spiral transition lengths
    :param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    :param lengths: parabolic vertical curve horizontal length values to use for transition
    :param cants: cant values, one per PI curve, applied to the outer rail
    :param rail_head_distance: value assigned to IfcAlignmentCant.RailHeadDistance
    :return: Returns an IfcAlignment
    """
    include_vertical = True if vpoints and lengths else False
    include_cant = cants is not None
    if include_cant and not include_vertical:
        raise ValueError("a vertical alignment is required when cants is provided; supply vpoints and lengths")
    alignment = ifcopenshell.api.alignment.create(
        file,
        name,
        include_vertical=include_vertical,
        include_cant=include_cant,
        start_station=start_station,
        rail_head_distance=rail_head_distance,
    )
    cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment) if include_cant else None
    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
        file, horizontal_layout, hpoints, radii, cant_layout=cant_layout, cants=cants
    )
    if include_vertical:
        vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(file, vertical_layout, vpoints, lengths)

    return alignment
