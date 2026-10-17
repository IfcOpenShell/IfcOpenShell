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
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment.get_mapped_segments import _get_curve_segment_count


def get_curve_segment(layout: entity_instance, segment: entity_instance) -> entity_instance:
    """
    Returns the IfcCurveSegment associated with the given alignment segment. If the curve segment does not exist, None is returned.

    Example:

    .. code:: python

        model = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        alignment = ifcopenshell.api.alignment.create_by_pi_method(model,
            name="A1", hpoints=[(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)], radii=[20.0])
        horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        alignment_segment = ifcopenshell.api.alignment.get_layout_segments(horizontal)[0]
        curve_segment = ifcopenshell.api.alignment.get_curve_segment(horizontal, alignment_segment)
    """
    index = 0
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
    for related_object in segment_nest.RelatedObjects:
        if related_object == segment:
            break
        n = _get_curve_segment_count(related_object)
        index += n

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    if curve and index < len(curve.Segments):
        return curve.Segments[index]
    else:
        return None
