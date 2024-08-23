# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import gpu
import bmesh
import bonsai.tool as tool
from bpy.types import SpaceView3D
from mathutils import Vector
from gpu_extras.batch import batch_for_shader


class BoundaryDecorator:
    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def __call__(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        def transparent_color(color, alpha=0.1):
            color = [i for i in color]
            color[3] = alpha
            return color

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        selected_vertices = []
        selected_edges = []
        selected_tris = []
        unselected_vertices = []
        unselected_edges = []
        unselected_tris = []

        for boundary in context.scene.BIMBoundaryProperties.boundaries:
            obj = boundary.obj
            if not obj or not obj.data:  # A boundary may not have data if it has no connection geometry
                continue

            if obj.mode == "EDIT":
                continue  # A profile decorator or something else is used here.
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                obj.data.calc_loop_triangles()

                if obj.select_get():
                    offset = len(selected_vertices)
                    selected_vertices.extend([tuple(obj.matrix_world @ v.co) for v in bm.verts])
                    selected_edges.extend([tuple([v.index + offset for v in e.verts]) for e in bm.edges])
                    selected_tris.extend([tuple([i + offset for i in t.vertices]) for t in obj.data.loop_triangles])
                else:
                    offset = len(unselected_vertices)
                    unselected_vertices.extend([tuple(obj.matrix_world @ v.co) for v in bm.verts])
                    unselected_edges.extend([tuple([v.index + offset for v in e.verts]) for e in bm.edges])
                    unselected_tris.extend([tuple([i + offset for i in t.vertices]) for t in obj.data.loop_triangles])

            if obj.mode != "EDIT":
                bm.free()

        if unselected_edges:
            self.draw_batch("LINES", unselected_vertices, special_elements_color, unselected_edges)
            self.draw_batch("TRIS", unselected_vertices, transparent_color(special_elements_color), unselected_tris)
        if selected_edges:
            self.draw_batch("LINES", selected_vertices, selected_elements_color, selected_edges)
            self.draw_batch("TRIS", selected_vertices, transparent_color(selected_elements_color), selected_tris)
