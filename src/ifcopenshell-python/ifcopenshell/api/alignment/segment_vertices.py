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


import numpy as np

import ifcopenshell
import ifcopenshell.util.unit
from ifcopenshell import entity_instance, ifcopenshell_wrapper

def _intersect_lines(p1,d1,p2,d2):
    x1,y1 = p1
    dx1,dy1 = d1
    x2,y2 = p2
    dx2,dy2 = d2
    
    det = dx1*dy2 - dy1*dx2
    if abs(det) < 1e-12:
        return None # lines are parallel
    
    t = ((x2 - x1) * dy2 - (y2 - y1) * dx2)/det

    x = x1 + t*dx1
    y = y1 + t*dy1

    return (x,y)


def segment_vertices(file: ifcopenshell.file, curve_segment: entity_instance):
    """
    Genererates segment vertices. Segment vertices are the points where the tangents
    at the start and end of the segment intersect (the PI point) and where lines
    perpendicular to the start and end of the segment intersect (CC).

    :param curve_segment: A curve segment
    :return: tuples for Start, End, PI, CC
    """
    supported_segment_types = ["IFCCURVESEGMENT"]
    segment_type = curve_segment.is_a().upper()
    if not segment_type in supported_segment_types:
        raise NotImplementedError(
            f"Expected entity type to be one of {[_ for _ in supported_segment_types]}, got '{segment_type}"
        )
    
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    settings = ifcopenshell.geom.settings()
    segment_fn = ifcopenshell_wrapper.map_shape(settings, curve_segment.wrapped_data)
    segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)

    s = segment_evaluator.evaluate(segment_fn.start())
    start = np.array(s)
    sx = float(start[0, 3]) / unit_scale
    sy = float(start[1, 3]) / unit_scale
    sdx = float(start[0, 0])
    sdy = float(start[1, 0])    

    e = segment_evaluator.evaluate(segment_fn.end())
    end = np.array(e)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    ex = float(end[0, 3]) / unit_scale
    ey = float(end[1, 3]) / unit_scale
    edx = float(end[0, 0])
    edy = float(end[1, 0])

    pi = _intersect_lines((sx,sy),(sdx,sdy),(ex,ey),(edx,edy))

    sdx = float(start[0, 1])
    sdy = float(start[1, 1])    
    edx = float(end[0, 1])
    edy = float(end[1, 1])

    cc = _intersect_lines((sx,sy),(sdx,sdy),(ex,ey),(edx,edy))

    return (sx,sy), (ex,ey), pi, cc
