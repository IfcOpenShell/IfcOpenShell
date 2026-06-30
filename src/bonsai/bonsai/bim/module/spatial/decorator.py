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
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

import bonsai.tool as tool


class GridDecorator(tool.Blender.ViewportDecorator):
    draw_methods = (
        ("draw_text", "POST_PIXEL"),
        ("draw", "POST_VIEW"),
    )

    def draw_text(self, context):
        if not tool.Blender.is_addon_enabled():
            return
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        font_id = 0
        blf.size(font_id, 12)
        blf.enable(font_id, blf.SHADOW)

        grid_props = tool.Spatial.get_grid_props()
        for axis in grid_props.grid_axes:
            if not (obj := axis.obj) or obj.visible_get() is False:
                continue
            if obj.select_get() and context.mode != "OBJECT":
                continue

            tag = obj.name.split("/")[-1].split(".")[0]
            matrix_world = obj.matrix_world
            v1 = matrix_world @ obj.data.vertices[0].co
            v2 = matrix_world @ obj.data.vertices[1].co

            color = selected_elements_color if obj.select_get() else unselected_elements_color
            blf.color(font_id, *color)

            coords_2d = location_3d_to_region_2d(context.region, context.region_data, v1)
            if coords_2d:
                w, h = blf.dimensions(font_id, tag)
                coords_2d -= Vector((w * 0.5, h * 0.5))
                blf.position(font_id, coords_2d[0], coords_2d[1], 0)
                blf.draw(font_id, tag)

            coords_2d = location_3d_to_region_2d(context.region, context.region_data, v2)
            if coords_2d:
                w, h = blf.dimensions(font_id, tag)
                coords_2d -= Vector((w * 0.5, h * 0.5))
                blf.position(font_id, coords_2d[0], coords_2d[1], 0)
                blf.draw(font_id, tag)
        blf.disable(font_id, blf.SHADOW)

    def draw(self, context):
        if not tool.Blender.is_addon_enabled():
            return
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 1.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        selected_verts = []
        selected_edges = []
        unselected_verts = []
        unselected_edges = []
        grid_props = tool.Spatial.get_grid_props()
        for axis in grid_props.grid_axes:
            if not (obj := axis.obj) or obj.visible_get() is False:
                continue
            if obj.select_get():
                if context.mode != "OBJECT":
                    continue
                edges = selected_edges
                verts = selected_verts
            else:
                edges = unselected_edges
                verts = unselected_verts
            i = len(verts)
            edges.append([i, i + 1])
            matrix_world = obj.matrix_world
            v1 = matrix_world @ obj.data.vertices[0].co
            v2 = matrix_world @ obj.data.vertices[1].co
            verts.extend([v1, v2])

        if unselected_verts:
            self.draw_batch("LINES", unselected_verts, decorator_color_background, unselected_edges)

        if selected_verts:
            self.draw_batch("LINES", selected_verts, selected_elements_color, selected_edges)
