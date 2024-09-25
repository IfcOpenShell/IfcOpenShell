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

import blf
import gpu
import bmesh
import bonsai.tool as tool
from bpy.types import SpaceView3D
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d


class ItemDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_text, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

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

        for item in context.scene.BIMGeometryProperties.item_objs:
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

    def draw(self, context):
        def transparent_color(color, alpha=0.3):
            color = [i for i in color]
            color[3] = alpha
            return color

        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        selected_verts = []
        selected_edges = []
        selected_tris = []
        unselected_verts = []
        unselected_edges = []
        unselected_tris = []
        for item in context.scene.BIMGeometryProperties.item_objs:
            if (obj := item.obj) and obj.hide_get() == False:
                if obj.select_get():
                    if context.mode != "OBJECT":
                        continue
                    edges = selected_edges
                    verts = selected_verts
                    tris = selected_tris
                else:
                    edges = unselected_edges
                    verts = unselected_verts
                    tris = unselected_tris

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
                edges.extend(bbox_edges)
                verts.extend(bbox_verts)

                if (total_tris := len(obj.data.loop_triangles)) == 0:
                    continue

                if total_tris > 1000:  # For performance
                    continue

                offset = len(verts)
                verts.extend([tuple(obj.matrix_world @ v.co) for v in obj.data.vertices])
                tris.extend([tuple([i + offset for i in t.vertices]) for t in obj.data.loop_triangles])

        if unselected_verts:
            self.draw_batch("LINES", unselected_verts, transparent_color(unselected_elements_color), unselected_edges)
            self.draw_batch("TRIS", unselected_verts, transparent_color(special_elements_color), unselected_tris)

        if selected_verts:
            self.draw_batch("LINES", selected_verts, selected_elements_color, selected_edges)
            self.draw_batch("TRIS", selected_verts, transparent_color(selected_elements_color), selected_tris)
