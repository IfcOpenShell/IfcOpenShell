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
from bpy_extras import view3d_utils
import blenderbim.core.tool

# from blenderbim.bim.module.model.decorator import WallPolylineDecorator
import math
import mathutils
from mathutils import Matrix, Vector


class Raycasting(blenderbim.core.tool.Raycasting):
    @classmethod
    def get_visible_objects(cls, context):
        depsgraph = context.evaluated_depsgraph_get()
        all_objs = []
        for dup in depsgraph.object_instances:
            if dup.is_instance:  # Real dupli instance
                obj = dup.instance_object
                all_objs.append(obj)
            else:  # Usual object
                obj = dup.object
                all_objs.append(obj)
        return all_objs

    @classmethod
    def get_objects_2d_bounding_boxes(cls, context, obj):
        obj_matrix = obj.matrix_world.copy()
        bbox = [obj_matrix @ Vector(v) for v in obj.bound_box]

        transposed_bbox = []
        bbox_2d = []

        for v in bbox:
            coord_2d = view3d_utils.location_3d_to_region_2d(context.region, context.space_data.region_3d, v)
            if coord_2d is not None:
                transposed_bbox.append(coord_2d)

        region = context.region
        borders = (region.width, region.height)
        for i, axis in enumerate(zip(*transposed_bbox)):
            if all(ax < 0 or ax > borders[i] for ax in axis):  # Filter only objects in viewport
                return (obj, None)
            min_point = min(axis)
            max_point = max(axis)
            bbox_2d.extend([min_point, max_point])

        return (obj, bbox_2d)

    @classmethod
    def in_view_2d_bounding_box(cls, mouse_pos, bbox):
        x, y = mouse_pos
        xmin, xmax, ymin, ymax = bbox

        if xmin < x < xmax and ymin < y < ymax:
            return True
        else:
            return False

    @classmethod
    def get_viewport_ray_data(cls, context, event):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)
        ray_target = ray_origin + view_vector
        ray_direction = ray_target - ray_origin

        return ray_origin, ray_target, ray_direction

    @classmethod
    def get_object_ray_data(cls, context, event, obj_matrix):
        ray_origin, ray_target, _ = cls.get_viewport_ray_data(context, event)
        matrix_inv = obj_matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        return ray_origin_obj, ray_target_obj, ray_direction_obj

    @classmethod
    def obj_ray_cast(cls, context, event, obj):
        ray_origin_obj, _, ray_direction_obj = cls.get_object_ray_data(context, event, obj.matrix_world.copy())
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
        if success:
            return location, normal, face_index
        else:
            return None, None, None

    @classmethod
    def ray_cast_to_plane(cls, context, event, plane_origin, plane_normal):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)

        intersection = Vector((0, 0, 0))
        try:
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_direction)
            intersection = mathutils.geometry.intersect_line_plane(ray_target, loc, plane_origin, plane_normal)
        except:
            intersection = Vector((0, 0, 0))

        if intersection == None:
            intersection = Vector((0, 0, 0))

        return intersection
