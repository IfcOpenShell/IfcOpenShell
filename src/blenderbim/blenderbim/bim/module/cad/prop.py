# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from blenderbim.bim.module.model.data import AuthoringData
from blenderbim.bim.module.model.root import ConstrTypeEntityNotFound
from bpy.types import PropertyGroup


class BIMCadProperties(PropertyGroup):
    resolution: bpy.props.IntProperty(name="Arc Resolution", min=1, default=1)
    radius: bpy.props.FloatProperty(name="Radius", default=0.1)
    distance: bpy.props.FloatProperty(name="Distance", default=0.1)
    x: bpy.props.FloatProperty(name="X", default=0.2)
    y: bpy.props.FloatProperty(name="Y", default=0.1)
