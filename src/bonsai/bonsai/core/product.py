# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import TYPE_CHECKING

import bonsai.core.geometry

if TYPE_CHECKING:
    import bpy

    import bonsai.tool as tool


Z_ROTATION_ALIGNMENT_TOLERANCE = 1e-9


def _z_rotation_diff(target_z: float, source_z: float) -> float:
    """Signed Z-Euler difference wrapped to [-π, π]."""
    return (target_z - source_z + math.pi) % (2 * math.pi) - math.pi


def copy_z_rotation_to_selected(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    surveyor: type[tool.Surveyor],
    *,
    active: bpy.types.Object,
    targets: Iterable[bpy.types.Object],
    flip: bool = False,
) -> int:
    """Apply ``active``'s Z-Euler rotation to each target."""
    source_z = surveyor.get_z_rotation(active)  # ty:ignore[missing-argument]
    if flip:
        source_z += math.pi
    rotated = 0
    for obj in targets:
        target_z = surveyor.get_z_rotation(obj)  # ty:ignore[missing-argument]
        if abs(_z_rotation_diff(target_z, source_z)) < Z_ROTATION_ALIGNMENT_TOLERANCE:
            continue
        surveyor.set_z_rotation(obj, source_z)  # ty:ignore[missing-argument]
        rotated += 1
        if ifc.get_entity(obj) is not None:
            bonsai.core.geometry.edit_object_placement(ifc, geometry, surveyor, obj=obj)
    return rotated
