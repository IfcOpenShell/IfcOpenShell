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


def add_instance_flooring_coverings_from_walls(ifc, spatial, collector, geometry):
    z = spatial.get_active_obj_z()
    union = spatial.get_union_shape_from_selected_objects()
    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)
        bm = spatial.get_bmesh_from_polygon(poly, h=0)

        name = "Covering" + str(i)
        obj = spatial.get_named_obj_from_bmesh(name, bmesh = bm)

        spatial.set_obj_origin_to_bboxcenter(obj)
        spatial.traslate_obj_to_z_location(obj, z)
        spatial.link_obj_to_active_collection(obj)

        points = spatial.get_2d_vertices_from_obj(obj)

        spatial.assign_type_to_obj(obj)
        spatial.assign_container_to_obj(obj)

        spatial.assign_swept_area_outer_curve_from_2d_vertices(obj, vertices = points)
        body = spatial.get_body_representation(obj)
        spatial.regen_obj_representation(ifc, geometry, obj, body)

