# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from math import pi
from typing import TYPE_CHECKING

import bpy
from bpy.types import PropertyGroup


class BIMCadProperties(PropertyGroup):
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    radius: bpy.props.FloatProperty(name="Radius", default=0.1, subtype="DISTANCE")
    distance: bpy.props.FloatProperty(name="Distance", default=0.1, subtype="DISTANCE")
    copy: bpy.props.BoolProperty(
        name="Copy",
        description="Create a new offset copy of the geometry. If disabled, move the existing edges to the offset location",
        default=True,
    )
    x: bpy.props.FloatProperty(name="X", default=0.2, subtype="DISTANCE")
    y: bpy.props.FloatProperty(name="Y", default=0.1, subtype="DISTANCE")
    gable_roof_edge_angle: bpy.props.FloatProperty(
        name="Gable Roof Edge Angle", default=pi / 2, soft_min=0, soft_max=pi / 2, subtype="ANGLE"
    )

    if TYPE_CHECKING:
        resolution: int
        radius: float
        distance: float
        copy: bool
        x: float
        y: float
        gable_roof_edge_angle: float
