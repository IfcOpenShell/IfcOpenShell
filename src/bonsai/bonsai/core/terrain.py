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
    # Slice first: if the interval is unusable this raises before anything is changed.
    levels = terrain.get_contour_levels(element, interval)
    terrain.set_contour_settings(element, interval, index_interval)
    # Reuse the contour already at each elevation, so whatever points at it (e.g. a label) stays linked.
    existing = {}
    for contour in terrain.get_contours(element):
        if (elevation := terrain.get_contour_elevation(contour)) is not None:
            existing[round(elevation, 6)] = contour
        else:
            terrain.remove_contour(contour)
    for i, z, polylines in levels:
        elevation = i * interval
        is_index = bool(index_interval) and i % index_interval == 0
        if contour := existing.pop(round(elevation, 6), None):
            terrain.update_contour(contour, element, elevation, z, polylines, is_index)
        else:
            terrain.create_contour(element, elevation, z, polylines, is_index)
    for contour in existing.values():
        terrain.remove_contour(contour)
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


def label_contours(
    terrain: type[tool.Terrain],
    element: ifcopenshell.entity_instance,
    drawing: ifcopenshell.entity_instance,
    relating_type: ifcopenshell.entity_instance | None = None,
    spacing: float = 15.0,
) -> int:
    """Label the terrain's contours in a plan drawing with their elevations.

    Labels the user has moved are kept, and new ones keep clear of them; the rest of the
    previously generated labels in this drawing are replaced.

    :param spacing: Distance between labels along a contour, in SI metres.
    :return: The number of labels created.
    """
    kept = []
    for contour in terrain.get_contours(element):
        for label in terrain.get_contour_labels(contour, drawing):
            if terrain.is_label_moved(label):
                kept.append(label)
            else:
                terrain.remove_contour_label(label)
    template = terrain.get_label_template(element)
    placements = terrain.get_label_placements(element, drawing, relating_type, spacing, kept)
    for contour, matrix in placements:
        terrain.create_contour_label(drawing, contour, matrix, relating_type, template)
    return len(placements)
