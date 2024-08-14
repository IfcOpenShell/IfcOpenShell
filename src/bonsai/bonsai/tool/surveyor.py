# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import bonsai.core.tool
import bonsai.tool as tool
import numpy as np
from mathutils import Matrix


class Surveyor(bonsai.core.tool.Surveyor):
    @classmethod
    def get_absolute_matrix(cls, obj: bpy.types.Object) -> Matrix:
        matrix = np.array(obj.matrix_world)
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and obj.BIMObjectProperties.blender_offset_type != "NOT_APPLICABLE":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            if (
                obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT"
                and obj.BIMObjectProperties.cartesian_point_offset
            ):
                offset_x, offset_y, offset_z = map(float, obj.BIMObjectProperties.cartesian_point_offset.split(","))
                matrix[0][3] -= offset_x
                matrix[1][3] -= offset_y
                matrix[2][3] -= offset_z
            matrix = np.array(
                ifcopenshell.util.geolocation.local2global(
                    matrix,
                    float(props.blender_offset_x) * unit_scale,
                    float(props.blender_offset_y) * unit_scale,
                    float(props.blender_offset_z) * unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix
