# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import blf
import gpu
import bmesh
import ifcopenshell
import bonsai.tool as tool
import numpy as np
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from typing import Sequence


class ItemDecorator:
    is_installed = False
    handlers = []
    objs: dict[str, dict[str, list]]
    obj_is_selected: dict[str, bool]
    obj_is_boolean: dict[str, list[ifcopenshell.entity_instance]]
    obj_matrix: dict[str, Matrix]

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        obj_is_selected: dict[str, bool] = {}
        obj_is_boolean: dict[str, list[ifcopenshell.entity_instance]] = {}
        objs: dict[str, dict[str, list]] = {}
        obj_matrix: dict[str, Matrix] = {}
        props = tool.Geometry.get_geometry_props()
        for item_obj in props.item_objs:
            if obj := item_obj.obj:
                obj: bpy.types.Object
                objs[obj.name] = cls.get_obj_data(obj)
                obj_is_selected[obj.name] = obj.select_get()
                item = tool.Geometry.get_active_representation(obj)
                assert item
                obj_is_boolean[obj.name] = [i for i in tool.Ifc.get().get_inverse(item) if i.is_a("IfcBooleanResult")]
                obj_matrix[obj.name] = obj.matrix_world.copy()

        handler = cls()
        handler.objs = objs
        handler.obj_is_selected = obj_is_selected
        handler.obj_is_boolean = obj_is_boolean
        handler.obj_matrix = obj_matrix
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_text, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

    @classmethod
    def get_obj_data(cls, obj: bpy.types.Object) -> dict[str, list]:
        verts = []
        edges = []
        tris = []
        special_verts = []
        special_edges = []

        if len(obj.data.loop_triangles) > 0:
            verts = [tuple(obj.matrix_world @ v.co) for v in obj.data.vertices]
            tris = [tuple(t.vertices) for t in obj.data.loop_triangles]

        i = len(verts)
        matrix_world = obj.matrix_world
        bbox_verts = [matrix_world @ Vector(co) for co in obj.bound_box]
        bbox_edges = [
            (0 + i, 3 + i),
            (3 + i, 7 + i),
            (7 + i, 4 + i),
            (4 + i, 0 + i),
            (0 + i, 1 + i),
            (3 + i, 2 + i),
            (7 + i, 6 + i),
            (4 + i, 5 + i),
            (1 + i, 2 + i),
            (2 + i, 6 + i),
            (6 + i, 5 + i),
            (5 + i, 1 + i),
        ]
        edges = bbox_edges
        verts.extend(bbox_verts)

        if "HalfSpaceSolid" in obj.name:
            # Arrow shape
            special_verts = [
                tuple(obj.matrix_world @ Vector((0, 0, 0))),
                tuple(obj.matrix_world @ Vector((0, 0, 0.5))),
                tuple(obj.matrix_world @ Vector((0.05, 0, 0.45))),
                tuple(obj.matrix_world @ Vector((-0.05, 0, 0.45))),
                tuple(obj.matrix_world @ Vector((0, 0.05, 0.45))),
                tuple(obj.matrix_world @ Vector((0, -0.05, 0.45))),
            ]
            special_edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]

        return {
            "verts": verts,
            "edges": edges,
            "tris": tris,
            "special_verts": special_verts,
            "special_edges": special_edges,
        }

    @classmethod
    def uninstall(cls):
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_text(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        font_id = 0
        blf.size(font_id, 12)
        blf.enable(font_id, blf.SHADOW)
        color = selected_elements_color
        blf.color(font_id, *color)

        props = tool.Geometry.get_geometry_props()
        for item in props.item_objs:
            if (obj := item.obj) and obj.hide_get() == False:
                if obj.select_get():
                    centroid = obj.matrix_world @ Vector(obj.bound_box[0]).lerp(Vector(obj.bound_box[6]), 0.5)
                    tag = obj.name.split("/")[1]
                    coords_2d = location_3d_to_region_2d(context.region, context.region_data, centroid)
                    if coords_2d:
                        w, h = blf.dimensions(font_id, tag)
                        coords_2d -= Vector((w * 0.5, h * 0.5))
                        blf.position(font_id, coords_2d[0], coords_2d[1], 0)
                        blf.draw(font_id, tag)
        blf.disable(font_id, blf.SHADOW)

    def draw(self, context: bpy.types.Context) -> None:
        def transparent_color(color: Sequence[float], alpha: float = 0.05) -> list[float]:
            color = [i for i in color]
            color[3] = alpha
            return color

        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        for obj_name, data in self.objs.items():
            if (obj := bpy.data.objects.get(obj_name)) and obj.hide_get() == False:
                if self.obj_is_selected[obj_name] != obj.select_get() or not np.allclose(
                    self.obj_matrix[obj_name], obj.matrix_world
                ):
                    self.obj_is_selected[obj_name] = obj.select_get()
                    data = ItemDecorator.get_obj_data(obj)
                    self.objs[obj_name] = data
                if obj.select_get():
                    if context.mode != "OBJECT":
                        continue
                    self.draw_batch("LINES", data["verts"], selected_elements_color, data["edges"])
                    self.draw_batch("TRIS", data["verts"], transparent_color(selected_elements_color), data["tris"])
                    self.draw_batch("LINES", data["special_verts"], selected_elements_color, data["special_edges"])
                elif self.obj_is_boolean[obj_name]:
                    self.draw_batch("LINES", data["verts"], special_elements_color, data["edges"])
                    self.draw_batch("TRIS", data["verts"], transparent_color(special_elements_color), data["tris"])
                    self.draw_batch("LINES", data["special_verts"], special_elements_color, data["special_edges"])
                else:
                    self.draw_batch(
                        "LINES", data["verts"], transparent_color(unselected_elements_color, alpha=0.2), data["edges"]
                    )
                    self.draw_batch("TRIS", data["verts"], transparent_color(special_elements_color), data["tris"])
                    self.draw_batch("LINES", data["special_verts"], special_elements_color, data["special_edges"])
