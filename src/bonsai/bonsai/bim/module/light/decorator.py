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
import bonsai.tool as tool
from bpy.types import SpaceView3D
from math import radians
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bonsai.bim.module.light.data import SolarData


class SolarDecorator:
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

        props = bpy.context.scene.BIMSolarProperties
        origin = Matrix.Translation(props.sun_path_origin)
        location = origin @ (props.sun_position * 1.05)

        self.font_id = 0
        blf.size(self.font_id, 12)
        blf.color(self.font_id, *self.addon_prefs.decorations_colour)
        self.draw_text_at_position(context, f"{props.hour:02}:{props.minute:02}", location)

        self.tn_angle = props.true_north
        angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
        grid_north_p = origin @ angle @ (Vector((0, 0.8, 0)) * props.sun_path_size)
        self.draw_text_at_position(context, "True North", grid_north_p)

    def draw_text_at_position(self, context, text, position):
        coords_2d = location_3d_to_region_2d(context.region, context.region_data, position)
        if not coords_2d:
            return
        for i, line in enumerate(text.split("\n")):
            w, h = blf.dimensions(self.font_id, line)
            co = coords_2d.copy()
            co -= Vector((w * 0.5, 15 * i))
            blf.position(self.font_id, co[0], co[1], 0)
            blf.draw(self.font_id, line)

    def draw_geometry(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        decorator_color_special = self.addon_prefs.decorator_color_special
        decorator_color_error = self.addon_prefs.decorator_color_error
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.point_size_set(12)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        vertex_shader = """
            uniform mat4 ModelViewProjectionMatrix;
            in vec3 pos;
            void main()
            {
                gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);
                gl_PointSize = 10.0;
            }
        """

        fragment_shader = """
            uniform vec4 color;
            out vec4 fragColor;
            void main()
            {
                float dist = length(gl_PointCoord - vec2(0.5));
                if (dist < 0.5) {
                    fragColor = color;
                } else {
                    discard;
                }
            }
        """

        self.shader = gpu.types.GPUShader(vertex_shader, fragment_shader)

        props = bpy.context.scene.BIMSolarProperties

        origin = Matrix.Translation(props.sun_path_origin)

        location = origin @ props.sun_position
        if location.z <= 0:
            gpu.state.point_size_set(6)
            self.draw_batch("POINTS", [location], decorator_color_error)
        else:
            self.draw_batch("POINTS", [location], (0.882353, 0.588235, 0.345098, 1))
            gpu.state.point_size_set(6)

        self.draw_batch("LINES", [location, origin @ Vector((0, 0, 0))], decorator_color_background, [[0, 1]])

        coords = []
        indices = []
        coord_offset = 0
        for h in range(24):
            analemma_verts = SolarData.data["sun_position"].sun_calc.calc_analemma(context, h)
            coords.extend([origin @ v for v in analemma_verts])
            for i in range(len(analemma_verts) - 1):
                indices.append((coord_offset + i, coord_offset + i + 1))
            coord_offset += len(analemma_verts)

        self.draw_batch("LINES", coords, decorator_color_special, indices)

        # True north
        self.tn_angle = props.true_north
        points = [Vector((0, 0, 0)), Vector((0, 0.75, 0))]
        angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
        points = [origin @ angle @ (v * props.sun_path_size) for v in points]
        self.draw_batch("POINTS", points, decorator_color_special)

        verts = [Vector((0, 0, 0)), Vector((0, 0.75, 0))]
        edges = [[0, 1]]
        angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
        verts = [origin @ angle @ (v * props.sun_path_size) for v in verts]
        self.draw_batch("LINES", verts, decorator_color_special, edges)

        verts = [Vector((0, 0.75, 0)), Vector((-0.15, 0.6, 0)), Vector((0.15, 0.6, 0))]
        edges = [[0, 1], [0, 2]]
        verts = [origin @ angle @ (v * props.sun_path_size) for v in verts]
        self.line_shader.uniform_float("lineWidth", 5.0)
        self.draw_batch("LINES", verts, decorator_color_special, edges)
        self.line_shader.uniform_float("lineWidth", 2.0)

        arc_start = Vector((0, 0.25, 0)) * props.sun_path_size
        arc_end = angle @ arc_start
        angle_half = Matrix.Rotation(radians(self.tn_angle / 2), 4, "Z")
        arc_mid = angle_half @ arc_start
        arc_segments = tool.Cad.create_arc_segments(
            pts=[origin @ v for v in [arc_start, arc_mid, arc_end]], num_verts=12, make_edges=True
        )
        verts, edges = arc_segments
        self.draw_batch("LINES", verts, decorator_color_special, edges)
