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


class ClashDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_text, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_geometry, (context,), "WINDOW", "POST_VIEW"))
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

        text = context.scene.BIMClashProperties.active_clash_text
        p = context.scene.BIMClashProperties.p1.lerp(context.scene.BIMClashProperties.p2, 0.5)

        font_id = 0
        blf.size(font_id, 12)
        coords_2d = location_3d_to_region_2d(context.region, context.region_data, p)
        color = self.addon_prefs.decorations_colour
        blf.color(font_id, *color)
        if coords_2d:
            w, h = blf.dimensions(font_id, text)
            coords_2d -= Vector((w * 0.5, 0))
            blf.position(font_id, coords_2d[0], coords_2d[1], 0)
            blf.draw(font_id, text)  # Set your text here

    def draw_geometry(self, context):
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

        selected_vertices = [context.scene.BIMClashProperties.p1, context.scene.BIMClashProperties.p2]
        selected_edges = []
        if selected_vertices[0] != selected_vertices[1]:
            selected_edges = [[0, 1]]

        self.draw_batch("POINTS", selected_vertices, special_elements_color)
        if selected_edges:
            self.draw_batch("LINES", selected_vertices, special_elements_color, selected_edges)
