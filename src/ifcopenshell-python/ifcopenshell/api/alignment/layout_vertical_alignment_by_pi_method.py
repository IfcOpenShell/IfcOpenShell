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

import math
from collections.abc import Sequence


def layout_vertical_alignment_by_pi_method(
    file: ifcopenshell.file, layout: entity_instance, vpoints: Sequence[Sequence[float]], lengths: Sequence[float]
) -> None:
    """
    Appends IfcAlignmentVerticalSegment to a previously defined IfcAlignmentVertical using the PI layout method.
    The zero length segment is updated.

    :param file: file
    :param layout: An IfcAlignmentVertical layout
    :param vpoints: (distance_along, Z_height) pairs denoting the location of the vertical PIs, including start and end.
    :param lengths: horizontal length of parabolic vertical curves
    :return: None
    """
    if not (len(vpoints) - 2 == len(lengths)):
        raise ValueError("lengths should have two fewer elements that vpoints")

    xPBG, yPBG = vpoints[0]
    xPVI, yPVI = vpoints[1]
    i = 1
    for length in lengths:
        # back gradient
        dxBG = xPVI - xPBG
        dyBG = yPVI - yPBG
        start_slope = math.tan(math.atan2(dyBG, dxBG))

        # forward gradient
        i += 1
        xPFG, yPFG = vpoints[i]
        dxFG = xPFG - xPVI
        dyFG = yPFG - yPVI
        end_slope = math.tan(math.atan2(dyFG, dxFG))

        xEVC = xPVI + length / 2.0
        yEVC = yPVI + end_slope * length / 2.0

        # create gradient
        gradient_length = dxBG - length / 2.0
        if 1.0e-03 < gradient_length:
            design_parameters = file.createIfcAlignmentVerticalSegment(
                StartTag=None,
                EndTag=None,
                StartDistAlong=xPBG,
                HorizontalLength=gradient_length,
                StartHeight=yPBG,
                StartGradient=start_slope,
                EndGradient=start_slope,
                RadiusOfCurvature=None,
                PredefinedType="CONSTANTGRADIENT",
            )
            ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)

        # create vertical curve
        if 0.0 < length:
            k = (end_slope - start_slope) / length
            xBVC = xPVI - length / 2.0
            yBVC = yPVI - start_slope * length / 2.0

            design_parameters = file.createIfcAlignmentVerticalSegment(
                StartTag=None,
                EndTag=None,
                StartDistAlong=xBVC,
                HorizontalLength=length,
                StartHeight=yBVC,
                StartGradient=start_slope,
                EndGradient=end_slope,
                RadiusOfCurvature=1 / k,
                PredefinedType="PARABOLICARC",
            )
            ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)

        # start of next curve is end of this curve
        xPBG = xEVC
        yPBG = yEVC
        xPVI = xPFG
        yPVI = yPFG

    # create last gradient run
    dx = xPVI - xPBG
    dy = yPVI - yPBG
    slope = math.tan(math.atan2(dy, dx))
    gradient_length = dx

    if 1.0e-03 < gradient_length:
        design_parameters = file.createIfcAlignmentVerticalSegment(
            StartTag=None,
            EndTag=None,
            StartDistAlong=xPBG,
            HorizontalLength=gradient_length,
            StartHeight=yPBG,
            StartGradient=slope,
            EndGradient=slope,
            RadiusOfCurvature=None,
            PredefinedType="CONSTANTGRADIENT",
        )
        ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)
