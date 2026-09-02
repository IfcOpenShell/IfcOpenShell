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

"""Hover-preview correctness for door fillings must be schema independent
and wall-angle independent: the ghost a ProductDecorator draws while the
user hovers a filling over a wall must land where the placed door will
land, on IFC4 and on IFC2X3 (where the type classes are spelled
IfcDoorStyle/IfcWindowStyle), for walls at any angle and any origin,
including the rl1 sill offset and the wall's Z."""

import math

import bpy
import numpy as np
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.geometry.decorator import ItemDecorator
from bonsai.bim.module.model.decorator import ProductDecorator
from bonsai.bim.module.model.wall import DumbWallGenerator
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model

RL1 = 0.3


def _principal_xy_angle_vs(dir_world: Vector, verts) -> float:
    pts = np.array([(v[0], v[1]) for v in verts])
    pts = pts - pts.mean(axis=0)
    evals, evecs = np.linalg.eigh(pts.T @ pts)
    principal = Vector((evecs[0, -1], evecs[1, -1], 0.0)).normalized()
    d = Vector((dir_world.x, dir_world.y, 0.0)).normalized()
    cosang = max(-1.0, min(1.0, abs(principal.dot(d))))
    return math.degrees(math.acos(cosang))


class TestDoorPreviewFollowsWall(NewFile):
    @pytest.mark.parametrize("schema", ["IFC2X3", "IFC4"])
    @pytest.mark.parametrize("wall_angle", [0, 30, 90, 135])
    def test_hover_preview_matches_the_placed_door(self, schema, wall_angle):
        pprops = tool.Project.get_project_props()
        pprops.export_schema = schema
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        assert ifc.schema == schema

        bpy.ops.bim.add_default_type(ifc_element_type="IfcWallType")
        wall_type = ifc.by_type("IfcWallType")[-1]
        tool.Model.get_model_props().rl1 = RL1

        # Wall away from the world origin so a preview displaced by the
        # wall's own translation cannot pass.
        a = math.radians(wall_angle)
        p0 = Vector((5.0, 3.0, 0.0))
        p1 = p0 + Vector((math.cos(a), math.sin(a), 0.0)) * 3.0
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline.add()
        for co in (p0, p1):
            point = polyline_data.polyline_points.add()
            point.x, point.y, point.z = co
        walls, _ = DumbWallGenerator(wall_type).generate(insertion_type="POLYLINE")
        polyline_props.insertion_polyline.clear()
        wall_obj = walls[0]["obj"] if isinstance(walls[0], dict) else walls[0]
        bpy.context.view_layer.update()
        wall = tool.Ifc.get_entity(wall_obj)
        wall_x = (wall_obj.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()

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
        mid = (axes["base"][0] + axes["base"][1]) / 2
        mouse = tool.Cad.point_on_edge(Vector((mid.x, mid.y, 0.0)), axes["base"])
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

        preview_angle = _principal_xy_angle_vs(wall_x, data["verts"])
        assert preview_angle < 5.0, f"preview not rotated with the wall: {preview_angle:.2f} degrees off"

        # Click-to-place, then require the ghost to sit exactly where the
        # placed door sits (position, rotation, sill and wall Z in one).
        tool.Blender.select_and_activate_single_object(bpy.context, wall_obj)
        bpy.context.scene.cursor.location = mouse
        bpy.ops.bim.add_occurrence(relating_type_id=door_type.id())
        door_obj = tool.Ifc.get_object(ifc.by_type("IfcDoor")[-1])
        door_x = (door_obj.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
        assert abs(door_x.dot(wall_x)) > 0.999
        assert bpy.context.active_object is wall_obj

        placed_centroid = Vector((0.0, 0.0, 0.0))
        for v in door_obj.data.vertices:
            placed_centroid += door_obj.matrix_world @ v.co
        placed_centroid /= len(door_obj.data.vertices)
        preview_centroid = Vector((0.0, 0.0, 0.0))
        preview_mesh_verts = data["verts"][: len(door_obj.data.vertices)]
        for v in preview_mesh_verts:
            preview_centroid += Vector(v)
        preview_centroid /= len(preview_mesh_verts)
        gap = (preview_centroid - placed_centroid).length
        assert gap < 0.05, f"preview does not match the placed door: {gap:.3f} m apart"
