# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell

    import bonsai.tool as tool


def generate_contours(
    terrain: type[tool.Terrain], element: ifcopenshell.entity_instance, interval: float, index_interval: int
) -> int:
    """Replace the terrain's contours with new ones every ``interval`` (SI) metres.

    :return: The number of contours created.
    """
    # Slice first: if the interval is unusable this raises before anything is removed.
    levels = terrain.get_contour_levels(element, interval)
    terrain.set_contour_settings(element, interval, index_interval)
    for contour in terrain.get_contours(element):
        terrain.remove_contour(contour)
    for i, z, polylines in levels:
        is_index = bool(index_interval) and i % index_interval == 0
        terrain.create_contour(element, i * interval, z, polylines, is_index)
    return len(levels)


def update_contours(terrain: type[tool.Terrain], element: ifcopenshell.entity_instance) -> int:
    if not (settings := terrain.get_contour_settings(element)):
        return 0
    interval, index_interval = settings
    return generate_contours(terrain, element, interval, index_interval)


def remove_contours(terrain: type[tool.Terrain], element: ifcopenshell.entity_instance) -> None:
    for contour in terrain.get_contours(element):
        terrain.remove_contour(contour)
    terrain.remove_contour_settings(element)
