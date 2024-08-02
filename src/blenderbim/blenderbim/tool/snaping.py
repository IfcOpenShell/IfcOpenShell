# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Cyril Waechter <cyril@biminsight.ch>
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
import blenderbim.core.tool
import mathutils
from mathutils import Matrix, Vector


class Snaping(blenderbim.core.tool.Snaping):
    @classmethod
    def get_snap_points_on_raycasted_obj(cls, obj, face_index):
        snap_points = {}
        matrix = obj.matrix_world.copy()
        face = obj.data.polygons[face_index]
        vertices = []
        for i in face.vertices:
            vertices.append(matrix @ obj.data.vertices[i].co)
        
        edges_center = []
        for v1, v2 in zip(vertices, vertices[1:] + [vertices[0]]):
            middle_dist = (v2-v1) / 2
            edges_center.append(v1 + middle_dist)

        snap_points.update({tuple(vertex): "Vertices" for vertex in vertices})
        snap_points.update({tuple(edge_center): "Edge Center" for edge_center in edges_center})

        return snap_points

    @classmethod
    def select_snap_point(cls, snap_points, hit, threshold):
        shortest_distance = None
        snap_point = None
        for point, snap_type in snap_points.items():
            point = Vector(point)
            distance = (point - hit).length
            if distance > threshold:
                continue
            if shortest_distance and distance < shortest_distance:
                shortest_distance = distance
                snap_point = (point, snap_type)

            elif not shortest_distance:
                shortest_distance = distance
                snap_point = (point, snap_type)
            else:
                pass
            
        return snap_point

    @classmethod
    def update_snaping_point(cls, snap_point, snap_type):
        try:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        except:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point.add()

        snap_vertex.x = snap_point[0]
        snap_vertex.y = snap_point[1]
        snap_vertex.z = snap_point[2]
        snap_vertex.snap_type = snap_type

    @classmethod
    def insert_polyline_point(cls, x=None, y=None):
        snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
            
        polyline_point = bpy.context.scene.BIMModelProperties.polyline_point.add()
        if x is not None and y is not None:
            polyline_point.x = x
            polyline_point.y = y
            polyline_point.z = 0 # TODO Update to the the default container height
        else:
            polyline_point.x = snap_vertex.x
            polyline_point.y = snap_vertex.y
            polyline_point.z = 0 # TODO Update to the the default container height

    @classmethod
    def clear_polyline(cls):
        bpy.context.scene.BIMModelProperties.polyline_point.clear()

    @classmethod
    def remove_last_polyline_point(cls):
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        polyline_data.remove(len(polyline_data) - 1)
