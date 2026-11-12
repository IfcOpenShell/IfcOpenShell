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


class ClashDecorator(tool.Blender.ViewportDecorator):
    draw_methods = (
        ("draw_text", "POST_PIXEL"),
        ("draw_geometry", "POST_VIEW"),
    )

    def draw_text(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

        props = tool.Clash.get_clash_props()
        text = props.active_clash_text
        p = props.p1.lerp(props.p2, 0.5)

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

        props = tool.Clash.get_clash_props()
        selected_vertices = [props.p1, props.p2]
        selected_edges = []
        if selected_vertices[0] != selected_vertices[1]:
            selected_edges = [[0, 1]]

        self.draw_batch("POINTS", selected_vertices, special_elements_color)
        if selected_edges:
            self.draw_batch("LINES", selected_vertices, special_elements_color, selected_edges)
