# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Cyril Waechter <cyril@biminsight.ch>
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
import mathutils
import bonsai.core.tool
import bonsai.tool as tool
from mathutils import Matrix, Vector
from typing import Any, Sequence


class Boundary(bonsai.core.tool.Boundary):
    @classmethod
    def get_assign_connection_geometry_settings(cls, obj: bpy.types.Object) -> dict[str, Any]:
        from bonsai.bim.module.geometry.helper import Helper

        ifc = tool.Ifc.get()
        helper = Helper(ifc)
        mesh = obj.data
        curves = helper.auto_detect_curve_bounded_plane(mesh)
        outer_boundary = cls.polyline_from_indexes(mesh, curves["outer_curve"])
        inner_boundaries = tuple(cls.polyline_from_indexes(mesh, boundary) for boundary in curves["inner_curves"])

        # Create placement matrix
        location = outer_boundary[0]
        i = (outer_boundary[1] - outer_boundary[0]).normalized()
        k = mesh.polygons[0].normal
        j = k.cross(i)
        matrix = mathutils.Matrix()
        matrix[0].xyz = i
        matrix[1].xyz = j
        matrix[2].xyz = k
        matrix.transpose()
        matrix.translation = location

        return {
            "rel_space_boundary": tool.Ifc.get_entity(obj),
            "outer_boundary": cls.polyline_to_2d(outer_boundary, matrix),
            "inner_boundaries": tuple(cls.polyline_to_2d(boundary, matrix) for boundary in inner_boundaries),
            "location": location,
            "axis": k,
            "ref_direction": i,
        }

    @classmethod
    def polyline_from_indexes(cls, mesh: bpy.types.Mesh, indexes: Sequence[int]) -> tuple[Vector, ...]:
        return tuple(mesh.vertices[i].co for i in indexes)

    @classmethod
    def polyline_to_2d(cls, polyline: Sequence[Vector], placement_matrix: Matrix) -> tuple[Vector, ...]:
        matrix_inv = placement_matrix.inverted()
        return tuple((matrix_inv @ v).to_2d() for v in polyline)

    @classmethod
    def move_origin_to_space_origin(cls, obj: bpy.types.Object) -> None:
        boundary = tool.Ifc.get_entity(obj)
        space = tool.Ifc.get_object(boundary.RelatingSpace)
        translation = obj.matrix_world.translation - space.matrix_world.translation
        obj.data.transform(mathutils.Matrix.Translation(translation))
        obj.matrix_world = space.matrix_world

    @classmethod
    def decorate_boundary(cls, obj: bpy.types.Object) -> None:
        new = bpy.context.scene.BIMBoundaryProperties.boundaries.add()
        new.obj = obj
        obj.show_in_front = True

    @classmethod
    def undecorate_boundary(cls, obj: bpy.types.Object) -> None:
        obj.show_in_front = False
