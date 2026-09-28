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
import ifcopenshell.util.alignment
from ifcopenshell import entity_instance


def create_by_pi_method(
    file: ifcopenshell.file,
    name: str,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[Union[float, Sequence[float]]],
    vpoints: Sequence[Sequence[float]] = None,
    lengths: Sequence[float] = None,
    start_station: Optional[float] = None,
) -> entity_instance:
    """
    Create an alignment using the PI layout method for both horizontal and vertical alignments.
    If vpoints and lengths are omitted, only a horizontal alignment is created.

    Each element of radii is either a circular curve radius R, a (R, Lin, Lout) sequence with
    clothoid spiral transition curve lengths ahead of and following the circular curve, or a
    (R, Lin, Lout, family) sequence to use a different spiral family (see
    layout_horizontal_alignment_by_pi_method / solve_horizontal_alignment_by_pi_method).

    :param name: value for Name attribute
    :param hpoints: (X,Y) pairs denoting the location of the horizontal PIs, including start and end
    :param radii: radii values to use for transition, optionally with spiral transition lengths
    :param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    :param lengths: parabolic vertical curve horizontal length values to use for transition
    :param start_station: if given, the starting station value. A STATION IfcReferent named
        "<name> <station string>" is added at distance along 0.0 once the geometry exists. If None
        (the default), no stationing referent is created and get_alignment_start_station() reports 0.0.
    :return: Returns an IfcAlignment

    Example:

    .. code:: python

        model = ifcopenshell.api.project.create_file(version="IFC4X3")
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})

        # Horizontal PIs (X, Y), including the start (POB) and end (POE) points
        hpoints = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
        # One entry per interior PI: a circular curve radius, or (R, Lin, Lout) with clothoid spirals
        radii = [1000.0, (1250.0, 150.0, 150.0), 950.0]
        # Vertical PIs (distance along, elevation) and one parabolic curve length per interior VPI
        vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
        lengths = [1600.0, 1200.0, 2000.0, 800.0]

        alignment = ifcopenshell.api.alignment.create_by_pi_method(
            model, "Main Street", hpoints, radii, vpoints, lengths, start_station=1000.0
        )
    """
    include_vertical = True if vpoints and lengths else False
    alignment = ifcopenshell.api.alignment.create(file, name, include_vertical=include_vertical)
    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(file, horizontal_layout, hpoints, radii)
    if include_vertical:
        vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(file, vertical_layout, vpoints, lengths)

    if start_station is not None:
        referent_name = f"{name} {ifcopenshell.util.alignment.station_as_string(file, start_station)}"
        ifcopenshell.api.alignment.add_stationing_referent(file, referent_name, alignment, 0.0, start_station)

    return alignment
