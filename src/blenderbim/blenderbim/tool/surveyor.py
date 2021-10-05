# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import blenderbim.core.tool
import blenderbim.tool as tool
import numpy as np


class Surveyor(blenderbim.core.tool.Surveyor):
    @classmethod
    def get_absolute_matrix(cls, obj):
        matrix = np.array(obj.matrix_world)
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "OBJECT_PLACEMENT":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            matrix = np.array(
                ifcopenshell.util.geolocation.local2global(
                    matrix,
                    float(props.blender_eastings) * unit_scale,
                    float(props.blender_northings) * unit_scale,
                    float(props.blender_orthogonal_height) * unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix
