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
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
import bonsai.core.tool
import bonsai.tool as tool
import numpy as np
import numpy.typing as npt
from mathutils import Matrix


class Surveyor(bonsai.core.tool.Surveyor):
    @classmethod
    def get_absolute_matrix(cls, obj: bpy.types.Object) -> npt.NDArray[np.float64]:
        M_TRANSLATION = (slice(0, 3), 3)
        matrix = np.array(obj.matrix_world)
        props = tool.Georeference.get_georeference_props()
        if props.has_blender_offset and tool.Blender.get_object_bim_props(obj).blender_offset_type != "NOT_APPLICABLE":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            coordinate_offset = tool.Geometry.get_cartesian_point_offset(obj)
            if coordinate_offset is not None:
                matrix[M_TRANSLATION] -= coordinate_offset
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
