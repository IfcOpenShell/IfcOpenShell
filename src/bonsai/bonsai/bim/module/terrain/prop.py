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

from typing import TYPE_CHECKING

import bpy
from bpy.types import PropertyGroup


class BIMTerrainProperties(PropertyGroup):
    contour_interval: bpy.props.FloatProperty(
        name="Interval",
        description="Elevation difference between neighbouring contour lines",
        default=1.0,
        min=0.001,
        subtype="DISTANCE",
    )
    contour_index_interval: bpy.props.IntProperty(
        name="Index Every",
        description="Every Nth contour is an index contour, styled with the IndexContour class. 0 turns them off",
        default=5,
        min=0,
    )

    label_spacing: bpy.props.FloatProperty(
        name="Label Spacing",
        description="Distance between labels along a contour",
        default=15.0,
        min=0.1,
        subtype="DISTANCE",
    )

    if TYPE_CHECKING:
        contour_interval: float
        contour_index_interval: int
        label_spacing: float
