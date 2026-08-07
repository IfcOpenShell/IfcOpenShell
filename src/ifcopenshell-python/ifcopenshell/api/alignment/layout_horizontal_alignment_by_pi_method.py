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
import ifcopenshell.util.unit
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method import (
    HorizontalSegmentDefinition,
    solve_horizontal_alignment_by_pi_method,
)


def _create_cant_segment(
    file: ifcopenshell.file,
    cant_layout: entity_instance,
    segment: HorizontalSegmentDefinition,
) -> None:
    """
    Appends the cant segment corresponding to one horizontal segment definition. Cant is applied
    to a single rail (the rail on the outside of the curve). Constant cant is modeled with
    CONSTANTCANT and varying cant (over a transition curve) with LINEARTRANSITION.
    """
    is_transition = segment.start_cant != segment.end_cant
    if segment.raise_left_rail:
        start_left, start_right = segment.start_cant, 0.0
        end_left, end_right = segment.end_cant, 0.0
    else:
        start_left, start_right = 0.0, segment.start_cant
        end_left, end_right = 0.0, segment.end_cant

    design_parameters = file.createIfcAlignmentCantSegment(
        StartTag=None,
        EndTag=None,
        StartDistAlong=segment.start_dist_along,
        HorizontalLength=segment.segment_length,
        StartCantLeft=start_left,
        EndCantLeft=end_left if is_transition else None,
        StartCantRight=start_right,
        EndCantRight=end_right if is_transition else None,
        PredefinedType="LINEARTRANSITION" if is_transition else "CONSTANTCANT",
    )
    ifcopenshell.api.alignment.create_layout_segment(file, cant_layout, design_parameters)


def layout_horizontal_alignment_by_pi_method(
    file: ifcopenshell.file,
    layout: entity_instance,
    hpoints: Sequence[Sequence[float]],
    radii: Sequence[Union[float, Sequence[float]]],
    cant_layout: Optional[entity_instance] = None,
    cants: Optional[Sequence[float]] = None,
) -> None:
    """
    Appends IfcAlignmentHorizontalSegment to a previously defined IfcAlignmentHorizontal using the PI layout method.
    The zero length segment is updated.

    The geometry is computed by solve_horizontal_alignment_by_pi_method; see that function for the
    meaning of hpoints, radii, and cants. This function writes the resulting segment definitions to
    the layout.

    Optionally, a cant profile can be created alongside the horizontal layout. Cant segments are
    created one-for-one with the horizontal segments: zero cant on tangent runs (CONSTANTCANT),
    linearly varying cant over spiral transitions (LINEARTRANSITION), and constant cant over
    circular curves (CONSTANTCANT). The cant is applied to the rail on the outside of the curve.
    Cant values are expressed in the project length unit. IfcAlignmentCant.RailHeadDistance is
    taken from the cant_layout. Curves with a non-zero cant require entry and exit spiral
    transition curves so the cant profile is continuous.

    :param file: file
    :param layout: An IfcAlignmentHorizontal layout
    :param hpoints: (X, Y) pairs denoting the location of the horizontal PIs, including start (POB) and end (POE).
    :param radii: radius values to use for transition, optionally with spiral transition lengths
    :param cant_layout: An IfcAlignmentCant layout to receive the cant segments. Required when cants is provided.
    :param cants: cant values, one per PI curve, applied to the outer rail. Required when cant_layout is provided.
    :return: None
    """
    if (cant_layout is None) != (cants is None):
        raise ValueError("cant_layout and cants must be provided together")

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")

    for segment in solve_horizontal_alignment_by_pi_method(hpoints, radii, cants):
        if cant_layout is not None:
            _create_cant_segment(file, cant_layout, segment)
        start_point = file.createIfcCartesianPoint(
            Coordinates=segment.start_point,
        )
        design_parameters = file.createIfcAlignmentHorizontalSegment(
            StartTag=None,
            EndTag=None,
            StartPoint=start_point,
            StartDirection=segment.start_direction / angle_unit_scale,
            StartRadiusOfCurvature=segment.start_radius_of_curvature,
            EndRadiusOfCurvature=segment.end_radius_of_curvature,
            SegmentLength=segment.segment_length,
            GravityCenterLineHeight=None,
            PredefinedType=segment.predefined_type,
        )
        ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)
