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
import ifcopenshell.util
from ifcopenshell import entity_instance
from typing import Sequence

import ifcopenshell.util.representation


def get_basis_curve(alignment: entity_instance) -> entity_instance:
    """
    Returns the basis curve for an alignment. This curve is the geometric representation that is used
    as the basis curve for vertical and cant alignments.

    :param alignment: The alignment
    :return: The geometric representation that is used as a basis curve, typically an IfcCompositeCurve, or None if the alignment does not have a representation

    Example:

    .. code:: python
        alignment = model.by_type("IfcAlignment")[0]
        composite_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    """
    axis = None

    representations = ifcopenshell.util.representation.get_representations_iter(alignment)
    for representation in representations:
        if (representation.RepresentationIdentifier == "Axis" and representation.RepresentationType == "Curve2D") or (
            representation.RepresentationIdentifier == "FootPrint" and representation.RepresentationType == "Curve2D"
        ):
            axis = representation
            break

    return None if axis == None or axis.Items == None or len(axis.Items) == 0 else axis.Items[0]
