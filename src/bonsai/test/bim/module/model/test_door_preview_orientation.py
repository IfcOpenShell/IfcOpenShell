# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

"""Hover-preview orientation for door/window fillings must be schema
independent: the preview a ProductDecorator draws while the user hovers a
filling over a wall follows the wall's rotation on IFC4 and must do the same
on IFC2X3, where the type classes are spelled IfcDoorStyle/IfcWindowStyle."""

import bpy
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.geometry.decorator import ItemDecorator
from bonsai.bim.module.model.decorator import ProductDecorator
from bonsai.bim.module.model.wall import DumbWallGenerator
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _xy_extents(verts) -> tuple[float, float]:
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    return max(xs) - min(xs), max(ys) - min(ys)


class TestDoorPreviewFollowsWall(NewFile):
    @pytest.mark.parametrize("schema", ["IFC2X3", "IFC4"])
    def test_hover_preview_and_placement_follow_a_rotated_wall(self, schema):
        pprops = tool.Project.get_project_props()
        pprops.export_schema = schema
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        assert ifc.schema == schema

        bpy.ops.bim.add_default_type(ifc_element_type="IfcWallType")
        wall_type = ifc.by_type("IfcWallType")[-1]

        # Wall drawn along +Y, so an unrotated preview reads as 90 degrees off.
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline.add()
        for co in ((0.0, 0.0, 0.0), (0.0, 3.0, 0.0)):
            point = polyline_data.polyline_points.add()
            point.x, point.y, point.z = co
        walls, _ = DumbWallGenerator(wall_type).generate(insertion_type="POLYLINE")
        polyline_props.insertion_polyline.clear()
        wall_obj = walls[0]["obj"] if isinstance(walls[0], dict) else walls[0]
        bpy.context.view_layer.update()
        wall = tool.Ifc.get_entity(wall_obj)

        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcElementType"
        door_class = "IfcDoorStyle" if schema == "IFC2X3" else "IfcDoorType"
        rprops.ifc_class = door_class
        if schema != "IFC2X3":
            rprops.ifc_predefined_type = "DOOR"
        rprops.representation_template = "DOOR"
        bpy.ops.bim.add_element()
        door_type = ifc.by_type(door_class)[-1]
        door_type_obj = tool.Ifc.get_object(door_type)
        assert door_type.RepresentationMaps

        layers = tool.Model.get_material_layer_parameters(wall)
        axes = tool.Model.get_wall_axis(wall_obj, layers=layers)
        mouse = tool.Cad.point_on_edge(Vector((0.0, 1.5, 0.0)), axes["base"])
        try:
            snap_vertex = polyline_props.snap_mouse_point[0]
        except IndexError:
            snap_vertex = polyline_props.snap_mouse_point.add()
        snap_vertex.x, snap_vertex.y, snap_vertex.z = mouse
        snap_vertex.snap_type = "EDGE"
        snap_vertex.snap_object = wall_obj.name

        handler = ProductDecorator()
        handler.relating_type = door_type
        handler.preview_mode = "GENERIC"
        handler.obj_data = ItemDecorator.get_obj_data(door_type_obj)
        handler.obj_data["raw_verts"] = [Vector(v) for v in handler.obj_data["verts"]]
        handler.obj_matrix_i = door_type_obj.matrix_world.inverted()
        data = handler.get_generic_preview_data()
        assert data

        # The door is ~0.9 wide and ~0.1 deep: on a +Y wall the rotated
        # preview footprint must be longer along Y than along X.
        x_extent, y_extent = _xy_extents(data["verts"])
        assert y_extent > x_extent, f"preview not rotated with the wall: x={x_extent:.3f} y={y_extent:.3f}"

        # Click-to-place parity: door matrix aligns with the wall and the
        # wall stays active, on both schemas.
        tool.Blender.select_and_activate_single_object(bpy.context, wall_obj)
        bpy.context.scene.cursor.location = mouse
        bpy.ops.bim.add_occurrence(relating_type_id=door_type.id())
        door_obj = tool.Ifc.get_object(ifc.by_type("IfcDoor")[-1])
        door_x = (door_obj.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
        wall_x = (wall_obj.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
        assert abs(door_x.dot(wall_x)) > 0.999
        assert bpy.context.active_object is wall_obj
