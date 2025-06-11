# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
from typing import Union, Optional


def edit_true_north(file: ifcopenshell.file, true_north: Optional[Union[tuple[float, float], float]] = 0.0) -> None:
    """Edits the true north

    Given project north being up (i.e. a vector of 0, 1), true north is defined
    as a unitised 2D vector pointing to true north. Alternatively, true north
    may be defined as a rotation from project north to true north.
    Anticlockwise is positive.

    Note that true north is not part of georeferencing, and is only optionally
    provided as a reference value, typically for solar analysis. Remember: grid
    north (what your surveyor will typically use) is not the same as true
    north!

    :param true_north: A unitised 2D vector, where each ordinate is a float, or
        an angle in decimal degrees where anticlockwise is positive.

    Example:

    .. code:: python

        # Both of these are identical, and indicate that:
        # - If project north is up the page, true north is in the top left
        # - The building is therefore facing north east
        ifcopenshell.api.georeference.edit_true_north(model, true_north=30)
        ifcopenshell.api.georeference.edit_true_north(model, true_north=(-0.5, 0.8660254))

        # This unsets true north
        ifcopenshell.api.georeference.edit_true_north(model, true_north=None)
    """
    if isinstance(true_north, (float, int)):
        x, y = ifcopenshell.util.geolocation.angle2yaxis(true_north)
    elif true_north is not None:
        x, y = true_north

    for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
        if context.TrueNorth and true_north is None:
            old_true_north = context.TrueNorth
            context.TrueNorth = None
            if not file.get_total_inverses(old_true_north):
                ifcopenshell.util.element.remove_deep2(file, old_true_north)
            continue

        if context.TrueNorth:
            if file.get_total_inverses(context.TrueNorth) != 1:
                context.TrueNorth = file.create_entity("IfcDirection")
        else:
            context.TrueNorth = file.create_entity("IfcDirection")
        context.TrueNorth.DirectionRatios = (x, y)
