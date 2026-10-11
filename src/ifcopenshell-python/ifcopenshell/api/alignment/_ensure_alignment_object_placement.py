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
from ifcopenshell import entity_instance


def _ensure_alignment_object_placement(file: ifcopenshell.file, alignment: entity_instance) -> None:
    """
    Ensures the alignment has an ObjectPlacement.

    IfcAlignment is a subtype of IfcPositioningElement, which carries a
    HasPlacement WHERE rule requiring ObjectPlacement to exist. An alignment
    built by a route other than create() can reach this point with no
    placement. This creates the same 2D origin placement create() assigns to
    a new alignment, so the alignment satisfies its own WHERE rule and any
    referent nested under it can share a placement that genuinely exists.

    :param alignment: the alignment to check and, if needed, update
    :return: None
    """

    if alignment.ObjectPlacement:
        return

    alignment.ObjectPlacement = file.createIfcLocalPlacement(
        PlacementRelTo=None,
        RelativePlacement=file.createIfcAxis2Placement2D(Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))),
    )
