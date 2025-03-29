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
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import numpy as np
from ifcopenshell import entity_instance


def add_zero_length_segment(file: ifcopenshell.file, entity: entity_instance) -> None:
    """
    Adds a zero length segment to the end of entity.

    :param entity: An IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant or IfcCompositeCurve (or subtype)
    :return: None
    """
    expected_types = [
        "IfcAlignmentHorizontal",
        "IfcAlignmentVertical",
        "IfcAlignmentCant",
        "IfcCompositeCurve",
        "IfcGradientCurve",
        "IfcSegmentedReferenceCurve",
    ]
    if not entity.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{entity.is_a()}"
        )

    if ifcopenshell.api.alignment.has_zero_length_segment(entity):
        return  # do nothing if the entity already has a zero length segment

    if entity.is_a("IfcCompositeCurve"):
        last_segment = entity.Segments[-1]
        settings = ifcopenshell.geom.settings()
        segment_fn = ifcopenshell_wrapper.map_shape(settings, last_segment.wrapped_data)
        segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
        e = segment_evaluator.evaluate(segment_fn.end())
        end = np.array(e)
        x = float(end[0, 3])
        y = float(end[1, 3])
        dx = float(end[0, 0])
        dy = float(end[1, 0])

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
                Location=file.createIfcCartesianPoint(((x, y))),
                RefDirection=file.createIfcDirection((dx, dy)),
            ),
            SegmentStart=file.createIfcLengthMeasure(0.0),
            SegmentLength=file.createIfcLengthMeasure(0.0),
            ParentCurve=parent_curve,
        )
        ifcopenshell.api.alignment.add_segment_to_curve(file, curve_segment, entity)
    else:
        for rel in entity.IsNestedBy:
            if 0 < len(rel.RelatedObjects):
                last_segment = rel.RelatedObjects[-1]
                if last_segment.is_a("IfcAlignmentSegment"):
                    if entity.is_a("IfcAlignmentHorizontal"):
                        design_parameters = file.createIfcAlignmentHorizontalSegment(
                            StartPoint=file.createIfcCartesianPoint(
                                (0.0, 0.0)
                            ),  # this is a little problematic. need to know the end point and tangent
                            StartDirection=0.0,  # of the previous segment, which requires geometry mapping
                            SegmentLength=0.0,
                            PredefinedType="LINE",
                        )
                        segment = file.createIfcAlignmentSegment(
                            GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
                        )
                        ifcopenshell.api.nest.assign_object(
                            file,
                            related_objects=[
                                segment,
                            ],
                            relating_object=entity,
                        )
                        break
                    elif entity.is_a("IfcAlignmentVertical"):
                        design_parameters = file.createIfcAlignmentVerticalSegment(
                            StartDistAlong=last_segment.DesignParameters.StartDistAlong
                            + last_segment.DesignParameters.HorizontalLength,
                            HorizontalLength=0.0,
                            StartHeight=0.0,
                            StartGradient=last_segment.DesignParameters.EndGradient,
                            EndGradient=last_segment.DesignParameters.EndGradient,
                            PredefinedType="CONSTANTGRADIENT",
                        )
                        segment = file.createIfcAlignmentSegment(
                            GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
                        )
                        ifcopenshell.api.nest.assign_object(
                            file,
                            related_objects=[
                                segment,
                            ],
                            relating_object=entity,
                        )
                        break
                    elif entity.is_a("IfcAlignmentCant"):
                        design_parameters = file.createIfcAlignmentCantSegment(
                            StartDistAlong=last_segment.DesignParameters.StartDistAlong
                            + last_segment.DesignParameters.HorizontalLength,
                            HorizontalLength=0.0,
                            StartCantLeft=(
                                last_segment.DesignParameters.EndCantLeft
                                if last_segment.DesignParameters.EndCantLeft != None
                                else last_segment.DesignParameters.StartCantLeft
                            ),
                            StartCantRight=(
                                last_segment.DesignParameters.EndCantRight
                                if last_segment.DesignParameters.EndCantRight != None
                                else last_segment.DesignParameters.StartCantRight
                            ),
                            PredefinedType="CONSTANTCANT",
                        )
                        segment = file.createIfcAlignmentSegment(
                            GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
                        )
                        ifcopenshell.api.nest.assign_object(
                            file,
                            related_objects=[
                                segment,
                            ],
                            relating_object=entity,
                        )
                        break
