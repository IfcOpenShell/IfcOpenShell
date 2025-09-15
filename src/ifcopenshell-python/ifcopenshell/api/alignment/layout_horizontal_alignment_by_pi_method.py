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

import ifcopenshell.util
import ifcopenshell.util.unit


def layout_horizontal_alignment_by_pi_method(
    file: ifcopenshell.file, layout: entity_instance, hpoints: Sequence[Sequence[float]], radii: Sequence[float]
) -> None:
    """
    Appends IfcAlignmentHorizontalSegment to a previously defined IfcAlignmentHorizontal using the PI layout method.
    The zero length segment is updated.

    :param file: file
    :param layout: An IfcAlignmentHorizontal layout
    :param hpoints: (X, Y) pairs denoting the location of the horizontal PIs, including start (POB) and end (POE).
    :param radii: radius values to use for transition
    :return: None
    """
    if not (len(hpoints) - 2 == len(radii)):
        raise ValueError("radii should have two fewer elements that hpoints")

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")

    xBT, yBT = hpoints[0]
    xPI, yPI = hpoints[1]

    i = 1

    for radius in radii:
        # back tangent
        dxBT = xPI - xBT
        dyBT = yPI - yBT
        angleBT = math.atan2(dyBT, dxBT)
        lengthBT = math.sqrt(dxBT * dxBT + dyBT * dyBT)

        # forward tangent
        i += 1
        xFT, yFT = hpoints[i]
        dxFT = xFT - xPI
        dyFT = yFT - yPI
        angleFT = math.atan2(dyFT, dxFT)

        delta = angleFT - angleBT

        tangent = abs(radius * math.tan(delta / 2))

        lc = abs(radius * delta)

        radius *= delta / abs(delta)

        xPC = xPI - tangent * math.cos(angleBT)
        yPC = yPI - tangent * math.sin(angleBT)

        xPT = xPI + tangent * math.cos(angleFT)
        yPT = yPI + tangent * math.sin(angleFT)

        tangent_run = lengthBT - tangent

        # create back tangent run
        if 1.0e-03 < tangent_run:
            pt = file.createIfcCartesianPoint(
                Coordinates=(xBT, yBT),
            )
            design_parameters = file.createIfcAlignmentHorizontalSegment(
                StartTag=None,
                EndTag=None,
                StartPoint=pt,
                StartDirection=angleBT / angle_unit_scale,
                StartRadiusOfCurvature=0.0,
                EndRadiusOfCurvature=0.0,
                SegmentLength=tangent_run,
                GravityCenterLineHeight=None,
                PredefinedType="LINE",
            )
            ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)

        # create circular curve
        if radius != 0.0:
            pc = file.createIfcCartesianPoint(
                Coordinates=(xPC, yPC),
            )
            design_parameters = file.createIfcAlignmentHorizontalSegment(
                StartTag=None,
                EndTag=None,
                StartPoint=pc,
                StartDirection=angleBT / angle_unit_scale,
                StartRadiusOfCurvature=float(radius),
                EndRadiusOfCurvature=float(radius),
                SegmentLength=lc,
                GravityCenterLineHeight=None,
                PredefinedType="CIRCULARARC",
            )
            ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)

        xBT = xPT
        yBT = yPT
        xPI = xFT
        yPI = yFT

    # done processing radii
    # create last tangent run
    dx = xPI - xBT
    dy = yPI - yBT
    angleBT = math.atan2(dy, dx)
    tangent_run = math.sqrt(dx * dx + dy * dy)

    if 1.0e-03 < tangent_run:
        pt = file.createIfcCartesianPoint(Coordinates=(xBT, yBT))

        design_parameters = file.createIfcAlignmentHorizontalSegment(
            StartTag=None,
            EndTag=None,
            StartPoint=pt,
            StartDirection=angleBT / angle_unit_scale,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=tangent_run,
            GravityCenterLineHeight=None,
            PredefinedType="LINE",
        )
        ifcopenshell.api.alignment.create_layout_segment(file, layout, design_parameters)
