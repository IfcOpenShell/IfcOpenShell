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

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    import bonsai.tool as tool


def add_instance_flooring_covering_from_cursor(
    ifc: type[tool.Ifc], root: type[tool.Root], spatial: type[tool.Spatial]
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

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if isinstance(space_polygon, str):
        return

    obj = spatial.create_object("Covering")
    spatial.set_obj_origin_to_cursor_position_and_zero_elevation(obj)
    spatial.translate_obj_to_z_location(obj, z)
    spatial.assign_type_to_obj(obj)
    spatial.set_covering_representation_from_polygon(obj, space_polygon, polygon_is_si=True)


def add_instance_ceiling_covering_from_cursor(
    ifc: type[tool.Ifc], root: type[tool.Root], covering: type[tool.Covering], spatial: type[tool.Spatial]
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

    obj = spatial.create_object("Covering")
    spatial.set_obj_origin_to_cursor_position_and_zero_elevation(obj)
    spatial.translate_obj_to_z_location(obj, z + ceiling_height)
    spatial.assign_type_to_obj(obj)
    spatial.set_covering_representation_from_polygon(obj, space_polygon, polygon_is_si=True)


def regen_selected_covering_object(root: type[tool.Root], spatial: type[tool.Spatial]) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    active_obj = spatial.get_active_obj()
    selected_objects = spatial.get_selected_objects()

    if selected_objects and active_obj:
        x, y, z, h, mat = spatial.get_x_y_z_h_mat_from_obj(active_obj)

    space_polygon = spatial.get_space_polygon_from_context_visible_objects(x, y)

    if isinstance(space_polygon, str):
        return

    spatial.set_covering_representation_from_polygon(active_obj, space_polygon, polygon_is_si=True)


# TODO CHECK IF IT IS POSSIBLE TO CREATE ONLY ONE CORE FUNCTION FOR _FROM_WALLS
def add_instance_flooring_coverings_from_walls(root: type[tool.Root], spatial: type[tool.Spatial]) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    z = spatial.get_active_obj_z()
    union = spatial.get_union_shape_from_selected_objects()
    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)

        name = "Covering" + str(i)
        obj = spatial.create_object(name)
        spatial.set_obj_origin_to_polygon_center(obj, poly, polygon_is_si=False)
        spatial.translate_obj_to_z_location(obj, z)
        spatial.assign_type_to_obj(obj)
        spatial.set_covering_representation_from_polygon(obj, poly, polygon_is_si=False)


def add_instance_ceiling_coverings_from_walls(
    root: type[tool.Root], spatial: type[tool.Spatial], covering: type[tool.Covering]
) -> None:
    if not root.get_default_container():
        raise NoDefaultContainer()

    z = covering.get_z_from_ceiling_height() + spatial.get_active_obj_z()
    union = spatial.get_union_shape_from_selected_objects()
    for i, linear_ring in enumerate(union.interiors):
        poly = spatial.get_buffered_poly_from_linear_ring(linear_ring)

        name = "Covering" + str(i)
        obj = spatial.create_object(name)
        spatial.set_obj_origin_to_polygon_center(obj, poly, polygon_is_si=False)
        spatial.translate_obj_to_z_location(obj, z)
        spatial.assign_type_to_obj(obj)
        spatial.set_covering_representation_from_polygon(obj, poly, polygon_is_si=False)


class NoDefaultContainer(Exception):
    pass
