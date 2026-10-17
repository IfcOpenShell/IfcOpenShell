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


def get_layout_curve(layout: entity_instance) -> entity_instance:
    """
    Returns the representation curve for the layout. This will be an IfcCompositeCurve, IfcGradientCurve, or IfcSegmentReferenceCurve
    for IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant, respectively.

    :param layout: An alignment layout
    :return: The geometric representation curve

    Example:

    .. code:: python

        model = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        alignment = ifcopenshell.api.alignment.create_by_pi_method(model,
            name="A1", hpoints=[(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)], radii=[20.0])
        layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        composite_curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    """
    alignment = ifcopenshell.api.alignment.get_alignment(layout)

    curve = ifcopenshell.api.alignment.get_curve(alignment)
    if curve:
        if layout.is_a("IfcAlignmentHorizontal"):
            # Layout is horizontal so get the IfcCompositeCurve
            if curve.is_a("IfcGradientCurve"):
                curve = curve.BaseCurve
            elif curve.is_a("IfcSegmentedReferenceCurve"):
                curve = curve.BaseCurve.BaseCurve
        elif layout.is_a("IfcAlignmentVertical"):
            # Layout is vertical so get the IfcGradientCurve
            if curve.is_a("IfcSegmentedReferenceCurve"):
                curve = curve.BaseCurve

    return curve
