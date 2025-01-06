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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_instance_flooring_covering_from_cursor(ifc: tool.Ifc, root: tool.Root, spatial: tool.Spatial) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    active_obj = spatial.get_active_obj()
    selected_objects = spatial.get_selected_objects()
    relating_type_id = spatial.get_relating_type_id()

    relating_type = None
    if relating_type_id:
        relating_type = ifc.get().by_id(int(relating_type_id))
        if not relating_type.is_a("IfcCoveringType"):
            relating_type = None

    if selected_objects and active_obj:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_obj(active_obj)
    else:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_cursor()

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if isinstance(space_polygon, str):
        return

    bm = spatial.get_bmesh_from_polygon(space_polygon, h=0)
    name = "Covering"
    mesh = spatial.get_named_mesh_from_bmesh(name=name, bmesh=bm)

    obj = spatial.get_named_obj_from_mesh(name, mesh)

    spatial.set_obj_origin_to_cursor_position_and_zero_elevation(obj)
    spatial.translate_obj_to_z_location(obj, z)
    points = spatial.get_2d_vertices_from_obj(obj)
    points = spatial.get_scaled_2d_vertices(points)
    spatial.assign_type_to_obj(obj)

    spatial.assign_swept_area_outer_curve_from_2d_vertices(obj, vertices=points)
    body = spatial.get_body_representation(obj)
    print(obj, body)
    spatial.regen_obj_representation(obj, body)


def add_instance_ceiling_covering_from_cursor(
    ifc: tool.Ifc, root: tool.Root, covering: tool.Covering, spatial: tool.Spatial
) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    active_obj = spatial.get_active_obj()
    selected_objects = spatial.get_selected_objects()
    relating_type_id = spatial.get_relating_type_id()

    relating_type = None
    if relating_type_id:
        relating_type = ifc.get().by_id(int(relating_type_id))
        if not relating_type.is_a("IfcCoveringType"):
            relating_type = None

    if selected_objects and active_obj:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_obj(active_obj)
    else:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_cursor()
        ceiling_height = covering.get_z_from_ceiling_height()

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if isinstance(space_polygon, str):
        return

    bm = spatial.get_bmesh_from_polygon(space_polygon, h=0)
    name = "Covering"
    mesh = spatial.get_named_mesh_from_bmesh(name=name, bmesh=bm)

    obj = spatial.get_named_obj_from_mesh(name, mesh)

    spatial.set_obj_origin_to_cursor_position_and_zero_elevation(obj)
    spatial.translate_obj_to_z_location(obj, z + ceiling_height)
    points = spatial.get_2d_vertices_from_obj(obj)
    points = spatial.get_scaled_2d_vertices(points)
    spatial.assign_type_to_obj(obj)

    spatial.assign_swept_area_outer_curve_from_2d_vertices(obj, vertices=points)
    body = spatial.get_body_representation(obj)
    spatial.regen_obj_representation(obj, body)


def regen_selected_covering_object(root: tool.Root, spatial: tool.Spatial) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    active_obj = spatial.get_active_obj()
    selected_objects = spatial.get_selected_objects()

    if selected_objects and active_obj:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_obj(active_obj)

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if isinstance(space_polygon, str):
        return

    bm = spatial.get_bmesh_from_polygon(space_polygon, h=0)

    name = "Aux"
    mesh = spatial.get_named_mesh_from_bmesh(name=name, bmesh=bm)
    mesh = spatial.get_transformed_mesh_from_local_to_global(mesh)
    obj = spatial.get_named_obj_from_mesh(name, mesh)

    points = spatial.get_2d_vertices_from_obj(obj)
    points = spatial.get_scaled_2d_vertices(points)

    spatial.assign_swept_area_outer_curve_from_2d_vertices(active_obj, vertices=points)
    body = spatial.get_body_representation(active_obj)
    spatial.regen_obj_representation(active_obj, body)


# TODO CHECK IF IT IS POSSIBLE TO CREATE ONLY ONE CORE FUNCTION FOR _FROM_WALLS
def add_instance_flooring_coverings_from_walls(root: tool.Root, spatial: tool.Spatial) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    z = spatial.get_active_obj_z()
    union = spatial.get_union_shape_from_selected_objects()
    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)
        bm = spatial.get_bmesh_from_polygon(poly, h=0)

        name = "Covering" + str(i)
        obj = spatial.get_named_obj_from_bmesh(name, bmesh=bm)

        spatial.set_obj_origin_to_bboxcenter(obj)
        spatial.translate_obj_to_z_location(obj, z)

        points = spatial.get_2d_vertices_from_obj(obj)
        points = spatial.get_scaled_2d_vertices(points)

        spatial.assign_type_to_obj(obj)

        spatial.assign_swept_area_outer_curve_from_2d_vertices(obj, vertices=points)
        body = spatial.get_body_representation(obj)
        spatial.regen_obj_representation(obj, body)


def add_instance_ceiling_coverings_from_walls(root: tool.Root, spatial: tool.Spatial, covering: tool.Covering) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    z = covering.get_z_from_ceiling_height() + spatial.get_active_obj_z()
    union = spatial.get_union_shape_from_selected_objects()
    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)
        bm = spatial.get_bmesh_from_polygon(poly, h=0)

        name = "Covering" + str(i)
        obj = spatial.get_named_obj_from_bmesh(name, bmesh=bm)

        spatial.set_obj_origin_to_bboxcenter(obj)
        spatial.translate_obj_to_z_location(obj, z)

        points = spatial.get_2d_vertices_from_obj(obj)
        points = spatial.get_scaled_2d_vertices(points)

        spatial.assign_type_to_obj(obj)

        spatial.assign_swept_area_outer_curve_from_2d_vertices(obj, vertices=points)
        body = spatial.get_body_representation(obj)
        spatial.regen_obj_representation(obj, body)


class NoDefaultContainer(Exception):
    pass
