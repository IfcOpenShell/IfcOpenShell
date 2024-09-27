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

import gpu
import blf
import bpy
import bmesh
import bonsai.tool as tool
from bpy.types import SpaceView3D
from bpy_extras import view3d_utils
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy.app.handlers import persistent


@persistent
def toggle_decorations_on_load(*args):
    if bpy.context.scene.BIMProjectProperties.clipping_planes:
        ClippingPlaneDecorator.install(bpy.context)
    else:
        ClippingPlaneDecorator.uninstall()

    # NOTE: ProjectDecorator cannot be loaded at reopening .blend file
    # since selected_vertices and other data is stored in queried object's
    # custom attributes and they get purged after Blender session is closed
    # as queried object is linked from separate .blend file.


class ProjectDecorator:
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

        try:
            obj = context.scene.BIMProjectProperties.queried_obj
            selected_vertices = obj["selected_vertices"]
            selected_edges = obj["selected_edges"]
            selected_tris = obj["selected_tris"]
        except:
            return

        if selected_edges:
            self.draw_batch("LINES", selected_vertices, selected_elements_color, selected_edges)
            self.draw_batch("TRIS", selected_vertices, transparent_color(selected_elements_color), selected_tris)


class ClippingPlaneDecorator:
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

        for clipping_plane in context.scene.BIMProjectProperties.clipping_planes:
            obj = clipping_plane.obj
            if not obj or not obj.data:
                continue

            if obj.mode == "EDIT":
                continue  # A profile decorator or something else is used here.

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

            verts = [
                tuple(obj.matrix_world @ Vector((0, 0, 0))),
                tuple(obj.matrix_world @ Vector((0, 0, -0.5))),
                tuple(obj.matrix_world @ Vector((-0.05, 0, -0.45))),
                tuple(obj.matrix_world @ Vector((0.05, 0, -0.45))),
                tuple(obj.matrix_world @ Vector((0, -0.05, -0.45))),
                tuple(obj.matrix_world @ Vector((0, 0.05, -0.45))),
            ]
            edges = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5)]
            color = selected_elements_color if obj in context.selected_objects else special_elements_color
            self.draw_batch("LINES", verts, color, edges)

            if obj.mode != "EDIT":
                bm.free()

            if unselected_edges:
                self.draw_batch("LINES", unselected_vertices, special_elements_color, unselected_edges)
                self.draw_batch("TRIS", unselected_vertices, transparent_color(special_elements_color), unselected_tris)
            if selected_edges:
                self.draw_batch("LINES", selected_vertices, selected_elements_color, selected_edges)
                self.draw_batch("TRIS", selected_vertices, transparent_color(selected_elements_color), selected_tris)


class MeasureDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_measurements, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW"))
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

    def draw_text_background(self, context, coords_dim, text_dim):
        padding = 5
        theme = context.preferences.themes.items()[0][1]
        color = (*theme.user_interface.wcol_menu_back.inner[:3], 0.5)  # unwrap color values and adds alpha
        top_left = (coords_dim[0] - padding, coords_dim[1] + text_dim[1] + padding)
        bottom_left = (coords_dim[0] - padding, coords_dim[1] - padding)
        top_right = (coords_dim[0] + text_dim[0] + padding, coords_dim[1] + text_dim[1] + padding)
        bottom_right = (coords_dim[0] + text_dim[0] + padding, coords_dim[1] - padding)

        verts = [top_left, bottom_left, top_right, bottom_right]
        gpu.state.blend_set("ALPHA")
        self.draw_batch("TRIS", verts, color, [(0, 1, 2), (1, 2, 3)])

    def draw_measurements(self, context):
        region = context.region
        rv3d = region.data
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 1
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        font_size = tool.Blender.scale_font_size(12)
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour
        blf.color(self.font_id, *color)

        measure_data = context.scene.BIMPolylineProperties.measure_polyline
        for data in measure_data:
            measurement_prop = data.polyline_point

            for i in range(len(measurement_prop)):
                if i == 0:
                    continue
                pos_dim = (Vector(measurement_prop[i].position) + Vector(measurement_prop[i - 1].position)) / 2
                coords_dim = view3d_utils.location_3d_to_region_2d(region, rv3d, pos_dim)

                formatted_value = measurement_prop[i].dim

                blf.position(self.font_id, coords_dim[0], coords_dim[1], 0)
                text = "d: " + formatted_value
                text_dim = blf.dimensions(self.font_id, text)
                self.draw_text_background(context, coords_dim, text_dim)
                blf.draw(self.font_id, text)

                if i == 1:
                    continue
                pos_angle = measurement_prop[i - 1].position
                coords_angle = view3d_utils.location_3d_to_region_2d(region, rv3d, pos_angle)
                blf.position(self.font_id, coords_angle[0], coords_angle[1], 0)
                text = "a: " + measurement_prop[i].angle
                text_dim = blf.dimensions(self.font_id, text)
                self.draw_text_background(context, coords_angle, text_dim)
                blf.draw(self.font_id, text)
            blf.disable(self.font_id, blf.SHADOW)

    def __call__(self, context):

        self.addon_prefs = tool.Blender.get_addon_preferences()
        decorator_color = self.addon_prefs.decorations_colour
        decorator_color_special = self.addon_prefs.decorator_color_special
        decorator_color_selected = self.addon_prefs.decorator_color_selected
        decorator_color_error = self.addon_prefs.decorator_color_error
        decorator_color_unselected = self.addon_prefs.decorator_color_unselected
        decorator_color_background = self.addon_prefs.decorator_color_background
        theme = context.preferences.themes.items()[0][1]
        decorator_color_object_active = (*theme.view_3d.object_active, 1)  # unwrap color values and adds alpha=1
        decorator_color_x_axis = (*theme.user_interface.axis_x, 1)
        decorator_color_y_axis = (*theme.user_interface.axis_y, 1)
        decorator_color_z_axis = (*theme.user_interface.axis_z, 1)

        gpu.state.blend_set("ALPHA")
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.point_size_set(6)


        measure_data = context.scene.BIMPolylineProperties.measure_polyline
        for data in measure_data:
            polyline_data = data.polyline_point

            polyline_points = []
            polyline_edges = []
            for point_prop in polyline_data:
                point = Vector((point_prop.x, point_prop.y, point_prop.z))
                polyline_points.append(point)

            for i in range(len(polyline_points) - 1):
                polyline_edges.append([i, i + 1])


            # Draw polyline with selected points
            self.line_shader.uniform_float("lineWidth", 2.0)
            self.draw_batch("POINTS", polyline_points, decorator_color_unselected)
            if len(polyline_points) > 1:
                self.draw_batch("LINES", polyline_points, decorator_color_unselected, polyline_edges)
