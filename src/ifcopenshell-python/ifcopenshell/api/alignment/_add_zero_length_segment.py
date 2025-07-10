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
import ifcopenshell.util.stationing
from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._get_segment_start_point_label import _get_segment_start_point_label


def _add_zero_length_segment(file: ifcopenshell.file, layout: entity_instance) -> None:
    """
    Adds a zero length segment to the end of a layout. Also adds a zero length segment to the end of the corresponding geometric curve.

    If the layout already has a zero length segment, nothing is changed

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :return: None
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected layout type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if ifcopenshell.api.alignment.has_zero_length_segment(layout):
        return

    segment = None
    if layout.is_a("IfcAlignmentHorizontal"):
        design_parameters = file.createIfcAlignmentHorizontalSegment(
            StartPoint=file.createIfcCartesianPoint(
                (0.0, 0.0)
            ),  # this is a little problematic. need to know the end point and tangent
            StartDirection=0.0,  # of the previous segment, which requires geometry mapping
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=0.0,
            PredefinedType="LINE",
        )
        segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)
    elif layout.is_a("IfcAlignmentVertical"):
        last_segment_dist_along = 0.0
        last_segment_end_gradient = 0.0
        for rel in layout.IsNestedBy:
            if 0 < len(rel.RelatedObjects):
                last_segment = rel.RelatedObjects[1]
                last_segment_dist_along = (
                    last_segment.DesignParameters.StartDistAlong + last_segment.DesignParameters.HorizontalLength
                )
                last_segment_end_gradient = last_segment.DesignParameters.EndGradient

        design_parameters = file.createIfcAlignmentVerticalSegment(
            StartDistAlong=last_segment_dist_along,
            HorizontalLength=0.0,
            StartHeight=0.0,
            StartGradient=last_segment_end_gradient,
            EndGradient=last_segment_end_gradient,
            PredefinedType="CONSTANTGRADIENT",
        )
        segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)
    elif layout.is_a("IfcAlignmentCant"):
        last_segment_dist_along = 0.0
        last_segment_cant_left = 0.0
        last_segment_cant_right = 0.0
        for rel in layout.IsNestedBy:
            if 0 < len(rel.RelatedObjects):
                last_segment = rel.RelatedObjects[1]
                last_segment_dist_along = (
                    last_segment.DesignParameters.StartDistAlong + last_segment.DesignParameters.HorizontalLength
                )
                last_segment_cant_left = (
                    last_segment.DesignParameters.EndCantLeft
                    if last_segment.DesignParameters.EndCantLeft != None
                    else last_segment.DesignParameters.StartCantLeft
                )
                last_segment_cant_right = (
                    last_segment.DesignParameters.EndCantRight
                    if last_segment.DesignParameters.EndCantRight != None
                    else last_segment.DesignParameters.StartCantRight
                )

        design_parameters = file.createIfcAlignmentCantSegment(
            StartDistAlong=last_segment_dist_along,
            HorizontalLength=0.0,
            StartCantLeft=last_segment_cant_left,
            StartCantRight=last_segment_cant_right,
            PredefinedType="CONSTANTCANT",
        )
        segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)

    ifcopenshell.api.nest.assign_object(file, related_objects=[segment], relating_object=layout)

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)

    has_zero_length_segment = False
    if curve.Segments != None and 0 < len(curve.Segments):
        last_segment = curve.Segments[-1]
        has_zero_length_segment = (
            True
            if last_segment.Transition == "DISCONTINUOUS" and last_segment.SegmentLength.wrappedValue == 0.0
            else False
        )

    if not has_zero_length_segment:
        parent_curve = file.createIfcLine(
            Pnt=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
            Dir=file.createIfcVector(
                Orientation=file.createIfcDirection(DirectionRatios=((1.0, 0.0))),
                Magnitude=1.0,
            ),
        )
        curve_segment = file.createIfcCurveSegment(
            Transition="DISCONTINUOUS",
            Placement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint((0.0, 0.0)),
                RefDirection=file.createIfcDirection((1.0, 0.0)),
            ),
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(0.0),
            ParentCurve=parent_curve,
        )
        curve.Segments = [
            curve_segment,
        ]

    name = f"{_get_segment_start_point_label(segment,None)} {ifcopenshell.util.stationing.station_as_string(file,0.0)}"
    ifcopenshell.api.alignment.add_stationing_referent(file, segment, curve, 0.0, 0.0, name=name)
