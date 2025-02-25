# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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
from ifcopenshell import entity_instance
from ifcopenshell import ifcopenshell_wrapper
import math
from typing import Sequence


def get_axis_subcontext(file:ifcopenshell.file):
    axis_geom_subcontext = ifcopenshell.util.representation.get_context(file,"Model","Axis","MODEL_VIEW")
    if(axis_geom_subcontext == None):
        geometric_representation_context = ifcopenshell.api.context.add_context(file,context_type="Model")
        axis_geom_subcontext = ifcopenshell.api.context.add_context(file,context_type="Model",context_identifier="Axis",target_view="MODEL_VIEW",parent=geometric_representation_context)
   
    return axis_geom_subcontext


def map_alignment_vertical_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    segment_type = segment.is_a().upper()
    expected_type = "IFCALIGNMENTVERTICALSEGMENT"
    if not segment_type == expected_type:
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment_type}'.")
    
    start_distance_along = segment.StartDistAlong
    horizontal_length = segment.HorizontalLength
    start_height = segment.StartHeight
    start_gradient = segment.StartGradient
    end_gradient = segment.EndGradient
    radius_of_curvature = segment.RadiusOfCurvature
    
    if math.isclose(horizontal_length, 0):
        # set transition value based on whether this is the final zero-length segment
        transition = "DISCONTINUOUS"
    else:
        transition = "CONTSAMEGRADIENTSAMECURVATURE"

    _type = segment.PredefinedType

    match _type:
        case "CONSTANTGRADIENT":
            parent_curve = file.create_entity(
                type="IfcLine",
                Pnt=file.create_entity(type="IfcCartesianPoint",Coordinates=(0.0,0.0),),
                Dir=file.create_entity(type="IfcVector",
                    Orientation=file.create_entity(type="IfcDirection",DirectionRatios=(1.0,0.0),),
                    Magnitude=1.0,),
                )
                
            dx = math.cos(math.atan(start_gradient))
            dy = math.sin(math.atan(start_gradient))
            curve_segment_length = horizontal_length/dx

            curve_segment = file.create_entity(
                type="IfcCurveSegment",
                Transition=transition,
                Placement=file.create_entity(
                    type="IfcAxis2Placement2D",
                    Location=file.create_entity(type="IfcCartesianPoint",Coordinates=(start_distance_along,start_height)),
                    RefDirection=file.createIfcDirection((dx,dy)),
                ),
                SegmentStart=file.createIfcLengthMeasure(0.0),
                SegmentLength=file.createIfcLengthMeasure(curve_segment_length),
                ParentCurve=parent_curve,
            )
            result = (curve_segment, None)

        case "PARABOLICARC":
            A = start_height
            B = start_gradient
            C = (end_gradient - start_gradient)/(2.0*horizontal_length)

            parent_curve = file.create_entity(
                type="IfcPolynomialCurve",
                Position=file.create_entity(
                    type="IfcAxis2Placement2D",
                    Location=file.create_entity(type="IfcCartesianPoint",Coordinates=(0.0,0.0)),
                    RefDirection=file.createIfcDirection((1.0, 0.0),),
                ),
                CoefficientsX=(0.0,1.0),
                CoefficientsY=(A,B,C),
            )
            
            dx = math.cos(math.atan(start_gradient))
            dy = math.sin(math.atan(start_gradient))
            curve_segment_length = ifcopenshell_wrapper.polynomial_length(A,B,C,horizontal_length)

            curve_segment = file.create_entity(
                type="IfcCurveSegment",
                Transition=transition,
                Placement=file.create_entity(
                    type="IfcAxis2Placement2D",
                    Location=file.create_entity(type="IfcCartesianPoint",Coordinates=(start_distance_along,start_height)),
                    RefDirection=file.createIfcDirection((dx,dy)),
                ),
                SegmentStart=file.createIfcLengthMeasure(0.0),
                SegmentLength=file.createIfcLengthMeasure(curve_segment_length),
                ParentCurve=parent_curve,
            )
            result = (curve_segment, None)

        case "CIRCULARARC":
            start_angle = math.atan(start_gradient)
            end_angle = math.atan(end_gradient)
            if start_angle < end_angle:
                radius = horizontal_length/(math.sin(end_angle) - math.sin(start_angle))    
            else:
                radius = horizontal_length/(math.sin(start_angle) - math.sin(end_angle))    

            parent_curve = file.create_entity(
                type="IfcCircle",
                Position=file.create_entity(
                    type="IfcAxis2Placement2D",
                    Location=file.create_entity(type="IfcCartesianPoint",Coordinates=(0.0,0.0)),
                    RefDirection=file.createIfcDirection((1.0, 0.0),),
                ),
                Radius=radius,
            )

            segment_curve_length = radius*math.fabs(end_angle - start_angle)

            curve_segment = file.create_entity(
                type="IfcCurveSegment",
                Transition=transition,
                Placement=file.create_entity(
                    type="IfcAxis2Placement2D",
                    Location=file.create_entity(type="IfcCartesianPoint",Coordinates=(start_distance_along,start_height)),
                    RefDirection=file.createIfcDirection((1.0,0.0),
                    ),
                ),
                SegmentStart=file.createIfcLengthMeasure(0.0),
                SegmentLength=file.createIfcLengthMeasure(curve_segment_length),
                ParentCurve=parent_curve,
            )
            result = (curve_segment, None)

        case _:
            result = (None, None)

    return result


def map_alignment_horizontal_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    segment_type = segment.is_a().upper()
    expected_type = "IFCALIGNMENTHORIZONTALSEGMENT"
    if not segment_type == expected_type:
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment_type}'.")

    start_point = segment.StartPoint
    start_direction = segment.StartDirection
    start_radius = segment.StartRadiusOfCurvature
    length = segment.SegmentLength
    _type = segment.PredefinedType

    if math.isclose(length, 0):
        # set transition value based on whether this is the final zero-length segment
        transition = "DISCONTINUOUS"
    else:
        transition = "CONTSAMEGRADIENTSAMECURVATURE"

    if _type == "LINE":
        parent_curve = file.create_entity(
            type="IfcLine",
            Pnt=file.create_entity(
                type="IfcCartesianPoint",
                Coordinates=(0.0, 0.0),
            ),
            Dir=file.create_entity(
                type="IfcVector",
                Orientation=file.create_entity(
                    type="IfcDirection",
                    DirectionRatios=(1.0, 0.0),
                ),
                Magnitude=1.0,
            ),
        )
        curve_segment = file.create_entity(
            type="IfcCurveSegment",
            Transition=transition,
            Placement=file.create_entity(
                type="IfcAxis2Placement2D",
                Location=start_point,
                RefDirection=file.createIfcDirection(
                    (math.cos(start_direction), math.sin(start_direction)),
                ),
            ),
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(length),
            ParentCurve=parent_curve,
        )
        result = (curve_segment, None)
    elif _type == "CIRCULARARC":
        parent_curve = file.createIfcCircle(
            Position=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0)),
                RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
            ),
            Radius=abs(start_radius),
        )

        curve_segment = file.create_entity(
            type="IfcCurveSegment",
            Transition=transition,
            Placement=file.create_entity(
                type="IfcAxis2Placement2D",
                Location=start_point,
                RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
            ),
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(length * start_radius / abs(start_radius)),
            ParentCurve=parent_curve,
        )
        result = (curve_segment, None)

    else:
        result = (None, None)

    return result


def name_segments(prefix: str, segments: Sequence[entity_instance]) -> None:
    """
    Sets the segment name like ("H1" for horizontal, "V1" for vertical, "C1" for cant)
    """
    for i, segment in enumerate(segments):
        segment.Name = f"{prefix}{i + 1}"


def create_segment_representations(
    file: ifcopenshell.file,
    global_placement: entity_instance,
    curve_segments: Sequence[entity_instance],
    segments: Sequence[entity_instance],
):
    """
    Creates curve segment representations
    """
    axis_geom_subcontext = get_axis_subcontext(file)
    
    for curve_segment, alignment_segment in zip(curve_segments, segments):
        axis_representation = file.create_entity(
            type="IfcShapeRepresentation",
            ContextOfItems=axis_geom_subcontext,
            RepresentationIdentifier="Axis",
            RepresentationType="Segment",
            Items=(curve_segment,),
        )
        product = file.create_entity(
            type="IfcProductDefinitionShape", Name=None, Description=None, Representations=(axis_representation,)
        )
        alignment_segment.ObjectPlacement = global_placement
        alignment_segment.Representation = product
