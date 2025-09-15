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
import ifcopenshell.util.alignment
from ifcopenshell import entity_instance
import ifcopenshell.ifcopenshell_wrapper as wrapper
import ifcopenshell.util.unit
import numpy as np
import math

from ifcopenshell.api.alignment._get_segment_start_point_label import _get_segment_start_point_label
from ifcopenshell.api.alignment._map_alignment_horizontal_segment import _map_alignment_horizontal_segment
from ifcopenshell.api.alignment._map_alignment_vertical_segment import _map_alignment_vertical_segment
from ifcopenshell.api.alignment._update_curve_segment_transition_code import _update_curve_segment_transition_code


def add_zero_length_segment(file: ifcopenshell.file, layout: entity_instance, include_referent: bool = True) -> bool:
    """
    Adds a zero length segment to the end of a layout.

    If the layout already has a zero length segment, nothing is changed.

    :param layout: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcCompositeCurve, IfcGradientCurve, IfcSegmentedReferenceCurve
    :param include_referent: If True, an IfcReferent representing the ending point of the layout is included for IfcLinearElement layouts (i.e. business logic)
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
        x = 0.0
        y = 0.0
        dx = 1.0
        dy = 0.0
        segment_start = 0.0

        last_segment = None
        if layout.Segments and 0 < len(layout.Segments):
            # If there are segments, get the last segment and compute the end point and tangent direction
            # because this becomes of placement of the zero length segment
            last_segment = layout.Segments[-1]
            settings = ifcopenshell.geom.settings()
            fn = wrapper.map_shape(settings, last_segment.wrapped_data)
            eval = wrapper.function_item_evaluator(settings, fn)
            e = np.array(eval.evaluate(fn.end()))
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
            e[:3, 3] /= unit_scale
            x = float(e[0, 3])
            y = float(e[1, 3])
            dx = float(e[0, 0])
            dy = float(e[1, 0])

        parent_curve = file.createIfcLine(
            Pnt=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
            Dir=file.createIfcVector(
                Orientation=file.createIfcDirection(DirectionRatios=((1.0, 0.0))),
                Magnitude=1.0,
            ),
        )
        zero_length_curve_segment = file.createIfcCurveSegment(
            Transition="DISCONTINUOUS",
            Placement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint((x, y)),
                RefDirection=file.createIfcDirection((dx, dy)),
            ),
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(0.0),
            ParentCurve=parent_curve,
        )

        layout.Segments += (zero_length_curve_segment,)

        if last_segment:
            _update_curve_segment_transition_code(last_segment, zero_length_curve_segment)

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
                file.begin_transaction()  # use a transaction so we can discard any temporary IFC entities created

                settings = ifcopenshell.geom.settings()
                mapped_segments = _map_alignment_horizontal_segment(file, last_segment)
                geometry_segment = mapped_segments[0] if mapped_segments[1] == None else mapped_segments[1]
                fn = wrapper.map_shape(settings, geometry_segment.wrapped_data)
                eval = wrapper.function_item_evaluator(settings, fn)
                e = np.array(eval.evaluate(fn.end()))
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
                x = float(e[0, 3]) / unit_scale
                y = float(e[1, 3]) / unit_scale
                dx = float(e[0, 0])
                dy = float(e[1, 0])

                file.discard_transaction()

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
                file.begin_transaction()
                last_segment_dist_along = (
                    last_segment.DesignParameters.StartDistAlong + last_segment.DesignParameters.HorizontalLength
                )
                last_segment_end_gradient = last_segment.DesignParameters.EndGradient
                settings = ifcopenshell.geom.settings()
                mapped_segments = _map_alignment_vertical_segment(file, last_segment)
                geometry_segment = mapped_segments[0] if mapped_segments[1] == None else mapped_segments[1]
                fn = wrapper.map_shape(settings, geometry_segment.wrapped_data)
                eval = wrapper.function_item_evaluator(settings, fn)
                e = np.array(eval.evaluate(fn.end()))
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
                last_segment_height = float(e[1, 3]) / unit_scale

                file.discard_transaction()

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

        if include_referent:
            alignment = ifcopenshell.api.alignment.get_alignment(layout)
            station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
            name = f"{_get_segment_start_point_label(zero_length_curve_segment,None)} ({ifcopenshell.util.alignment.station_as_string(file,station)})"
            referent = ifcopenshell.api.alignment.add_stationing_referent(
                file, alignment, 0.0, station, name, zero_length_curve_segment
            )
            referent.Description = f"Positions zero length segment {zero_length_curve_segment.id()}"

    return True
