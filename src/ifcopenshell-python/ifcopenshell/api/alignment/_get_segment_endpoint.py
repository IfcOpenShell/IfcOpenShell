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


import ifcopenshell.api.alignment
import ifcopenshell.geom
from ifcopenshell import entity_instance, ifcopenshell_wrapper
from ifcopenshell.api.alignment._map_alignment_segment import _map_alignment_segment
from typing import Union
import math
import numpy as np


def _get_segment_endpoint(file: ifcopenshell.file, segment: entity_instance) -> Union[np.array, None]:
    """
    Computes the 4x4 matrix for a segment end point. The segment can be an IfcAlignmentSegment
    or IfcCurveSegment
    """

    expected_types = ["IfcAlignmentSegment", "IfcCurveSegment"]
    if not segment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {segment.is_a()}"
        )

    file.begin_transaction()  # use a transaction so we can discard any temporary IFC entities created

    curve_segment = segment
    if segment.is_a("IfcAlignmentSegment"):
        layout = ifcopenshell.api.alignment.get_layout(segment)
        mapped_segments = _map_alignment_segment(file, layout, segment)
        curve_segment = mapped_segments[0] if mapped_segments[1] == None else mapped_segments[1]

        # Inside of the IfcOpenShell C++ implementation where the IfcCurveSegment calculations occur,
        # the composite curve owning the segment is evaluated to determine if a horizontal, vertical, or cant segment is being evaluated.
        # This is necessary to determine how the end point of the curve segment is calculated.
        # A temporary curve segment has been created and it needs to be associated with the correct composite curve for the end point to be calculated correctly.
        # Inside the C++ implementation, if a composite curve isn't associated with the segment the segment is assumed to be horizontal. For this reason
        # a temporary IfcCompositeCurve for horizontal segments doesn't need to be created.
        if layout.is_a("IfcAlignmentVertical"):
            gc = file.createIfcGradientCurve(Segments=[curve_segment])
        elif layout.is_a("IfcAlignmentCant"):
            # The evaluation of cant segments depend on the start conditions of the next segment. In the absense of a next segment the
            # optional EndPoint is used. Since a tempoaryar IfcSegmentReferenceCurve is being used, there is not a next segment.
            # For this reason the EndPoint must be created from the design parameters of the sementic segment definiton.
            Dsl = segment.DesignParameters.StartCantLeft
            Dsr = segment.DesignParameters.StartCantRight
            Del = segment.DesignParameters.EndCantLeft if segment.DesignParameters.EndCantLeft != None else Dsl
            Der = segment.DesignParameters.EndCantRight if segment.DesignParameters.EndCantRight != None else Dsr
            cant = Der - Del
            rh = layout.RailHeadDistance
            Ay = cant / rh
            Az = math.sqrt(rh**2 - cant**2) / rh

            src = file.createIfcSegmentedReferenceCurve(
                Segments=[curve_segment],
                EndPoint=file.createIfcAxis2Placement3D(
                    Location=file.createIfcCartesianPoint((segment.DesignParameters.StartDistAlong, 0.5 * cant, 0.0)),
                    RefDirection=file.createIfcDirection((1.0, 0.0, 0.0)),
                    Axis=file.createIfcDirection((0.0, Ay, Az)),
                ),
            )

    settings = ifcopenshell.geom.settings()

    segment_fn = ifcopenshell_wrapper.map_shape(settings, curve_segment.wrapped_data)
    segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
    x = segment_fn.end()
    e = segment_evaluator.evaluate(x)
    end = np.array(e)

    file.discard_transaction()

    return end
