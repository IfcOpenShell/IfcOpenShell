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

import bpy
from bonsai.bim.module.model.data import AuthoringData
from bpy.types import PropertyGroup
from math import pi


class BIMCadProperties(PropertyGroup):
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    radius: bpy.props.FloatProperty(name="Radius", default=0.1, subtype="DISTANCE")
    distance: bpy.props.FloatProperty(name="Distance", default=0.1, subtype="DISTANCE")
    x: bpy.props.FloatProperty(name="X", default=0.2, subtype="DISTANCE")
    y: bpy.props.FloatProperty(name="Y", default=0.1, subtype="DISTANCE")
    gable_roof_edge_angle: bpy.props.FloatProperty(
        name="Gable Roof Edge Angle", default=pi / 2, soft_min=0, soft_max=pi / 2, subtype="ANGLE"
    )
    gable_roof_separate_verts: bpy.props.BoolProperty(name="Separate Verts", default=True)
