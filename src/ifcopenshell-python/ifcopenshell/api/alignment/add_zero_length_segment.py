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

import math

import ifcopenshell
import ifcopenshell.api.alignment
from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint
from ifcopenshell.api.alignment._update_zero_length_segment_placement import _update_zero_length_segment_placement
import ifcopenshell.api.nest
import ifcopenshell.util.unit
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._update_curve_segment_transition_code import (
    _update_curve_segment_transition_code,
)


def add_zero_length_segment(file: ifcopenshell.file, layout: entity_instance) -> bool:
    """
    Adds a zero length segment to the end of a layout.

    If the layout already has a zero length segment, nothing is changed.

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcCompositeCurve, IfcGradientCurve, IfcSegmentedReferenceCurve
    :return: True if segment is added
    """

    # These are valid curve types for alignment, but don't have the zero-length segment
    if layout.is_a("IfcOffsetCurveByDistances") or layout.is_a("IfcPolyline") or layout.is_a("IfcIndexedPolyCurve"):
        return

    expected_types = [
        "IfcAlignmentHorizontal",
        "IfcAlignmentVertical",
        "IfcAlignmentCant",
        "IfcCompositeCurve",
        "IfcGradientCurve",
        "IfcSegmentedReferenceCurve",
    ]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected layout type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if ifcopenshell.api.alignment.has_zero_length_segment(layout):
        return False

    if layout.is_a("IfcCompositeCurve") or layout.is_a("IfcGradientCurve") or layout.is_a("IfcSegmentedReferenceCurve"):
        parent_curve = file.createIfcLine(
            Pnt=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
            Dir=file.createIfcVector(
                Orientation=file.createIfcDirection(DirectionRatios=((1.0, 0.0))),
                Magnitude=1.0,
            ),
        )
        if layout.is_a("IfcSegmentedReferenceCurve"):
            placement = file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                RefDirection=file.createIfcDirection((1.0, 0.0, 0.0)),
                Axis=file.createIfcDirection((0.0, 0.0, 1.0)),
            )
        else:
            placement = file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint((0.0, 0.0)),
                RefDirection=file.createIfcDirection((1.0, 0.0)),
            )

        zero_length_curve_segment = file.createIfcCurveSegment(
            Transition="DISCONTINUOUS",
            Placement=placement,
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(0.0),
            ParentCurve=parent_curve,
        )

        if layout.Segments and 0 < len(layout.Segments):
            # If there are segments, get the last segment and compute the end point and tangent direction
            # because this becomes of placement of the zero length segment
            last_segment = layout.Segments[-1]
            end_point = _get_segment_endpoint(file, last_segment)
            _update_zero_length_segment_placement(file, zero_length_curve_segment, end_point)
            _update_curve_segment_transition_code(last_segment, zero_length_curve_segment)

        layout.Segments += (zero_length_curve_segment,)

        # add zero length segments to base curves
        if layout.is_a("IfcSegmentedReferenceCurve"):
            ifcopenshell.api.alignment.add_zero_length_segment(file, layout.BaseCurve)
        elif layout.is_a("IfcGradientCurve"):
            ifcopenshell.api.alignment.add_zero_length_segment(file, layout.BaseCurve)

    else:
        zero_length_curve_segment = None
        if layout.is_a("IfcAlignmentHorizontal"):
            x = 0.0
            y = 0.0
            dx = 1.0
            dy = 0.0
            last_segment = None
            for rel in layout.IsNestedBy:
                if 0 < len(rel.RelatedObjects):
                    last_segment = rel.RelatedObjects[-1]
                    break

            if last_segment:
                e = _get_segment_endpoint(file, last_segment)

                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
                x = float(e[0, 3]) / unit_scale
                y = float(e[1, 3]) / unit_scale
                dx = float(e[0, 0])
                dy = float(e[1, 0])

            angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
            design_parameters = file.createIfcAlignmentHorizontalSegment(
                StartPoint=file.createIfcCartesianPoint((x, y)),
                StartDirection=math.atan2(dy, dx) / angle_unit_scale,
                StartRadiusOfCurvature=0.0,
                EndRadiusOfCurvature=0.0,
                SegmentLength=0.0,
                PredefinedType="LINE",
            )
            zero_length_curve_segment = file.createIfcAlignmentSegment(
                GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
            )
        elif layout.is_a("IfcAlignmentVertical"):
            last_segment_dist_along = 0.0
            last_segment_height = 0.0
            last_segment_end_gradient = 0.0
            last_segment = None
            for rel in layout.IsNestedBy:
                if 0 < len(rel.RelatedObjects):
                    last_segment = rel.RelatedObjects[-1]
                    break

            if last_segment:
                last_segment_dist_along = (
                    last_segment.DesignParameters.StartDistAlong + last_segment.DesignParameters.HorizontalLength
                )
                last_segment_end_gradient = last_segment.DesignParameters.EndGradient
                e = _get_segment_endpoint(file, last_segment)
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
                last_segment_height = float(e[1, 3]) / unit_scale

            design_parameters = file.createIfcAlignmentVerticalSegment(
                StartDistAlong=last_segment_dist_along,
                HorizontalLength=0.0,
                StartHeight=last_segment_height,
                StartGradient=last_segment_end_gradient,
                EndGradient=last_segment_end_gradient,
                PredefinedType="CONSTANTGRADIENT",
            )
            zero_length_curve_segment = file.createIfcAlignmentSegment(
                GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
            )
        elif layout.is_a("IfcAlignmentCant"):
            last_segment_dist_along = 0.0
            last_segment_cant_left = 0.0
            last_segment_cant_right = 0.0
            for rel in layout.IsNestedBy:
                if 0 < len(rel.RelatedObjects):
                    last_segment = rel.RelatedObjects[-1]
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
                    break

            design_parameters = file.createIfcAlignmentCantSegment(
                StartDistAlong=last_segment_dist_along,
                HorizontalLength=0.0,
                StartCantLeft=last_segment_cant_left,
                StartCantRight=last_segment_cant_right,
                PredefinedType="CONSTANTCANT",
            )
            zero_length_curve_segment = file.createIfcAlignmentSegment(
                GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
            )

        ifcopenshell.api.nest.assign_object(file, related_objects=[zero_length_curve_segment], relating_object=layout)

    return True
