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
from typing import Sequence


def create_horizontal_alignment_by_pi_method(
    file: ifcopenshell.file, name: str, hpoints: Sequence[Sequence[float]], radii: Sequence[float]
) -> entity_instance:
    """
    Create a horizontal alignment using the PI layout method.

    :param name: value for Name attribute
    :param hpoints: (X, Y) pairs denoting the location of the horizontal PIs, including start (POB) and end (POE).
    :param radii: radius values to use for transition
    :return: Returns a IfcAlignmentHorizontal
    """
    if not (len(hpoints) - 2 == len(radii)):
        raise ValueError("radii should have two fewer elements that hpoints")

    # Create the horizontal alignment (IfcAlignmentHorizontal) and nest alignment segments
    horizontal_alignment = file.create_entity(
        type="IfcAlignmentHorizontal",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=f"{name} - Horizontal",
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
    )

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
        pt = file.create_entity(
            type="IfcCartesianPoint",
            Coordinates=(xBT, yBT),
        )
        design_parameters = file.create_entity(
            type="IfcAlignmentHorizontalSegment",
            StartTag=None,
            EndTag=None,
            StartPoint=pt,
            StartDirection=angleBT,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=tangent_run,
            GravityCenterLineHeight=None,
            PredefinedType="LINE",
        )
        alignment_segment = file.create_entity(
            type="IfcAlignmentSegment",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            ObjectType=None,
            ObjectPlacement=None,
            Representation=None,
            DesignParameters=design_parameters,
        )

        ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal_alignment, alignment_segment)

        # create circular curve
        if radius != 0.0:
            pc = file.create_entity(
                type="IfcCartesianPoint",
                Coordinates=(xPC, yPC),
            )
            design_parameters = file.create_entity(
                type="IfcAlignmentHorizontalSegment",
                StartTag=None,
                EndTag=None,
                StartPoint=pc,
                StartDirection=angleBT,
                StartRadiusOfCurvature=float(radius),
                EndRadiusOfCurvature=float(radius),
                SegmentLength=lc,
                GravityCenterLineHeight=None,
                PredefinedType="CIRCULARARC",
            )
            alignment_segment = file.create_entity(
                type="IfcAlignmentSegment",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=None,
                Name=None,
                Description=None,
                ObjectType=None,
                ObjectPlacement=None,
                Representation=None,
                DesignParameters=design_parameters,
            )
            ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal_alignment, alignment_segment)

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
    pt = file.create_entity(type="IfcCartesianPoint", Coordinates=(xBT, yBT))

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag=None,
        EndTag=None,
        StartPoint=pt,
        StartDirection=angleBT,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=tangent_run,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal_alignment, alignment_segment)

    # create zero length terminator segment
    poe = file.create_entity(type="IfcCartesianPoint", Coordinates=(xPI, yPI))

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag="POE",
        EndTag="POE",
        StartPoint=poe,
        StartDirection=angleBT,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=0.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )
    ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal_alignment, alignment_segment)

    return horizontal_alignment
