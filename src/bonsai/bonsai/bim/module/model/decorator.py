# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
# This file was modified with the assistance of an AI coding tool.

from __future__ import annotations

import math
from collections.abc import Sequence
from math import cos, pi, radians, sin, tan
from typing import Any, Literal, NamedTuple

import blf
import bmesh
import bpy
import gpu
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import mathutils
from bpy.types import SpaceView3D
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
from mathutils import Matrix, Quaternion, Vector

import bonsai.core.geometry
import bonsai.tool as tool
from bonsai.bim.decorator_cache import TokenCache
from bonsai.bim.module.drawing.gizmos import (
    ARC_SEGMENTS,
    DOOR_SWING_ANGLE_MAX,
    DOOR_SWING_ANGLE_MIN,
)
from bonsai.bim.module.drawing.helper import format_distance


def highlight_color(color, alpha=0.1):
    color = [i + (1 - i) * 0.5 for i in color]
    return color


def _stroke_lines_alpha(
    context: bpy.types.Context,
    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    color_rgb: tuple[float, float, float],
    line_width: float,
    line_alpha: float,
) -> None:
    """Render ``segments`` (a list of (start, end) tuples) as one anti-aliased
    LINES batch in world space. Early-returns when ``context.region`` is
    unavailable (e.g. when called from a ``_RestrictContext``)."""
    if not segments:
        return
    verts: list[tuple[float, float, float]] = []
    indices: list[tuple[int, int]] = []
    for start, end in segments:
        base = len(verts)
        verts.append(tuple(start))
        verts.append(tuple(end))
        indices.append((base, base + 1))
    if not tool.Blender.validate_shader_batch_data(verts, indices):
        return
    region = getattr(context, "region", None)
    if region is None:
        return
    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    shader.bind()
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", line_width)
    shader.uniform_float("color", (*color_rgb, line_alpha))
    batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=indices)
    gpu.state.blend_set("ALPHA")
    batch.draw(shader)
    gpu.state.blend_set("NONE")


class ProfileDecorator:
    installed = None

    @classmethod
    def install(cls, context, get_custom_bmesh=None, draw_faces=False, exit_edit_mode_callback=None):
        """Note that operators that change mesh in `exit_edit_mode_callback` can freeze blender.
        The workaround is to move their code to function and use it for callback.

        Example: https://devtalk.blender.org/t/calling-operator-that-saves-bmesh-freezes-blender-forever/28595"""
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(
            handler, (context, get_custom_bmesh, draw_faces, exit_edit_mode_callback), "WINDOW", "POST_VIEW"
        )

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_faces(self, bm, vertices_coords):
        """Submit a non-mutating beauty-triangulated TRIS batch over ``bm``'s faces."""
        faces_color = tool.Blender.transparent_color(self.addon_prefs.decorator_color_special)
        tool.Blender.draw_bmesh_face_tris(bm, vertices_coords, faces_color, self.draw_batch)

    def __call__(self, context, get_custom_bmesh=None, draw_faces=False, exit_edit_mode_callback=None):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        error_elements_color = self.addon_prefs.decorator_color_error
        background_elements_color = self.addon_prefs.decorator_color_background

        obj = context.active_object

        if obj is None or obj.mode != "EDIT":
            if exit_edit_mode_callback:
                ProfileDecorator.uninstall()
                exit_edit_mode_callback()
            return

        if get_custom_bmesh:
            bm = get_custom_bmesh()
        else:
            bm = bmesh.from_edit_mesh(obj.data)

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        ### Actually drawing
        all_vertices = []
        error_vertices = []
        selected_vertices = []
        unselected_vertices = []
        # special = associated with arcs/circles
        special_vertices = []
        special_vertex_indices = {}
        selected_edges = []
        unselected_edges = []
        arc_edges = []
        roof_angle_edges = []
        preview_edges = []

        arc_groups = []
        circle_groups = []
        for i, group in enumerate(obj.vertex_groups):
            if "IFCARCINDEX" in group.name:
                arc_groups.append(i)
            elif "IFCCIRCLE" in group.name:
                circle_groups.append(i)

        arcs = {}
        circles = {}

        # https://docs.blender.org/api/blender_python_api_2_63_8/bmesh.html#CustomDataAccess
        # This is how we access vertex groups via bmesh, apparently, it's not very intuitive
        deform_layer = bm.verts.layers.deform.active
        angle_layer = bm.edges.layers.float.get("BBIM_gable_roof_angles")
        preview_layer = bm.edges.layers.int.get("BBIM_preview")

        for vertex in bm.verts:
            co = tuple(obj.matrix_world @ vertex.co)
            all_vertices.append(co)
            if vertex.hide:
                continue

            is_arc, is_circle = False, False
            # deform_layer is None if there are no verts assigned to vertex groups
            # even if there are vertex groups in the obj.vertex_groups
            if deform_layer:
                for group_index in tool.Blender.bmesh_get_vertex_groups(vertex, deform_layer):
                    if is_arc := group_index in arc_groups:
                        arcs.setdefault(group_index, []).append(vertex)
                        special_vertex_indices[vertex.index] = group_index
                    if is_circle := group_index in circle_groups:
                        circles.setdefault(group_index, []).append(vertex)
                        special_vertex_indices[vertex.index] = group_index

            if vertex.select:
                selected_vertices.append(co)
            else:
                if len(vertex.link_edges) > 1 and is_circle:
                    error_vertices.append(co)
                elif is_circle:
                    special_vertices.append(co)
                elif len(vertex.link_edges) != 2:
                    error_vertices.append(co)
                elif is_arc:
                    special_vertices.append(co)
                else:
                    unselected_vertices.append(co)

        for edge in bm.edges:
            edge_indices = [v.index for v in edge.verts]
            if edge.hide:
                continue
            if edge.select:
                selected_edges.append(edge_indices)
            else:
                i1, i2 = edge.verts[0].index, edge.verts[1].index
                # making sure that both vertices are in the same group
                if i1 in special_vertex_indices and special_vertex_indices[i1] == special_vertex_indices.get(i2, None):
                    arc_edges.append(edge_indices)
                elif angle_layer and edge[angle_layer] > 0:
                    roof_angle_edges.append(edge_indices)
                elif preview_layer and edge[preview_layer] == 1:
                    preview_edges.append(edge_indices)
                else:
                    unselected_edges.append(edge_indices)

        ### Actually drawing
        # POLYLINE_UNIFORM_COLOR is good for smoothed lines since `bgl.enable(GL_LINE_SMOOTH)` is deprecated
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.shader.bind()

        # Draw faces
        if draw_faces:
            self.draw_faces(bm, all_vertices)

        self.draw_batch("LINES", all_vertices, background_elements_color, arc_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, preview_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, roof_angle_edges)
        self.draw_batch("LINES", all_vertices, unselected_elements_color, unselected_edges)
        self.draw_batch("LINES", all_vertices, selected_elements_color, selected_edges)

        self.draw_batch("POINTS", unselected_vertices, tool.Blender.transparent_color(unselected_elements_color, 0.5))
        self.draw_batch("POINTS", error_vertices, error_elements_color)
        self.draw_batch("POINTS", special_vertices, special_elements_color)
        self.draw_batch("POINTS", selected_vertices, selected_elements_color)

        # Draw arcs
        arc_centroids = []
        arc_segments = []
        for arc in arcs.values():
            if len(arc) != 3:
                continue
            sorted_arc = [None, None, None]
            for v1 in arc:
                connections = 0
                for link_edge in v1.link_edges:
                    v2 = link_edge.other_vert(v1)
                    if v2 in arc:
                        connections += 1
                if connections == 2:  # Midpoint
                    sorted_arc[1] = v1
                else:
                    sorted_arc[2 if sorted_arc[2] is None else 0] = v1
            points = [tuple(obj.matrix_world @ v.co) for v in sorted_arc]
            centroid = tool.Cad.get_center_of_arc(points)
            if centroid:
                arc_centroids.append(tuple(centroid))
            arc_segments.append(tool.Cad.create_arc_segments(pts=points, num_verts=17, make_edges=True))

        self.draw_batch("POINTS", arc_centroids, background_elements_color)
        for verts, edges in arc_segments:
            self.draw_batch("LINES", verts, special_elements_color, edges)

        # Draw circles
        circle_centroids = []
        circle_segments = []
        for circle in circles.values():
            if len(circle) != 2:
                continue
            p1 = obj.matrix_world @ circle[0].co
            p2 = obj.matrix_world @ circle[1].co
            radius = (p2 - p1).length / 2
            centroid = p1.lerp(p2, 0.5)
            circle_centroids.append(tuple(centroid))
            segments = self.create_circle_segments(360, 20, radius)
            matrix = obj.matrix_world.copy()
            matrix.translation = centroid
            segments = [[list(matrix @ Vector(v)) for v in segments[0]], segments[1]]
            circle_segments.append(segments)

        self.draw_batch("POINTS", circle_centroids, background_elements_color)
        for verts, edges in circle_segments:
            self.draw_batch("LINES", verts, special_elements_color, edges)

    def create_matrix(self, p, x, y, z):
        return Matrix([x, y, z, p]).to_4x4().transposed()

    # https://github.com/nortikin/sverchok/blob/master/nodes/generator/basic_3pt_arc.py
    # This function is taken from Sverchok, licensed under GPL v2-or-later.
    # This is a combination of the make_verts and make_edges function.
    def create_circle_segments(self, Angle, Vertices, Radius):
        if Angle < 360:
            theta = Angle / (Vertices - 1)
        else:
            theta = Angle / Vertices
        listVertX = []
        listVertY = []
        for i in range(Vertices):
            listVertX.append(Radius * cos(radians(theta * i)))
            listVertY.append(Radius * sin(radians(theta * i)))

        if Angle < 360 and self.mode_ == 0:
            sigma = radians(Angle)
            listVertX[-1] = Radius * cos(sigma)
            listVertY[-1] = Radius * sin(sigma)
        elif Angle < 360 and self.mode_ == 1:
            listVertX.append(0.0)
            listVertY.append(0.0)

        points = list((x, y, 0) for x, y in zip(listVertX, listVertY))

        listEdg = [(i, i + 1) for i in range(Vertices - 1)]

        if Angle < 360 and self.mode_ == 1:
            listEdg.append((0, Vertices))
            listEdg.append((Vertices - 1, Vertices))
        else:
            listEdg.append((Vertices - 1, 0))

        return points, listEdg


class PolylineDecorator(tool.Blender.ViewportDecorator):
    # draw_methods declares only the always-bound handler so the base's
    # __init_subclass__ validation passes; the override install below
    # conditionally registers up to four more handlers based on ui_only.
    draw_methods = (("draw_input_ui", "POST_PIXEL"),)
    event = None
    input_type = None
    input_ui = None
    angle_snap_mat = None
    angle_snap_loc = None
    use_default_container = False
    instructions = None
    snap_info = None
    tool_state = None
    relating_type = None
    polyline_points = None

    @classmethod
    def install(cls, context, ui_only=False):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_input_ui, (context,), "WINDOW", "POST_PIXEL"))
        if not ui_only:
            cls.handlers.append(
                SpaceView3D.draw_handler_add(handler.draw_snap_point, (context,), "WINDOW", "POST_PIXEL")
            )
            cls.handlers.append(
                SpaceView3D.draw_handler_add(
                    handler.select_and_draw_measurements_text, (context,), "WINDOW", "POST_PIXEL"
                )
            )
            cls.handlers.append(
                SpaceView3D.draw_handler_add(
                    handler.select_and_draw_measurements_poly, (context,), "WINDOW", "POST_VIEW"
                )
            )
            cls.handlers.append(SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

    @classmethod
    def update(
        cls,
        event: bpy.types.Event,
        tool_state: tool.Polyline.ToolState,
        input_ui: tool.Polyline.PolylineUI,
        snapping_point: Vector,
    ) -> None:
        cls.event = event
        cls.tool_state = tool_state
        cls.input_ui = input_ui

    @classmethod
    def set_angle_axis_line(cls, start: Vector, end: Vector) -> None:
        cls.axis_start = start
        cls.axis_end = end

    def calculate_measurement_x_y_and_z(self, context: bpy.types.Context) -> None:
        if len(self.polyline_points) == 0 or len(self.polyline_points) > 2:
            return None, None

        start = self.polyline_points[0]
        if len(self.polyline_points) == 1:
            end = tool.Model.get_polyline_props().snap_mouse_point[0]
        else:
            end = self.polyline_points[1]

        x_axis = (Vector((start.x, start.y, start.z)), Vector((end.x, start.y, start.z)))
        y_axis = (Vector((end.x, start.y, start.z)), Vector((end.x, end.y, start.z)))
        z_axis = (Vector((end.x, end.y, start.z)), Vector((end.x, end.y, end.z)))
        x_middle = (x_axis[1] + x_axis[0]) / 2
        y_middle = (y_axis[1] + y_axis[0]) / 2
        z_middle = (z_axis[1] + z_axis[0]) / 2

        return (x_axis, y_axis, z_axis), (x_middle, y_middle, z_middle)

    @classmethod
    def calculate_polygon(cls, points: list[Vector]) -> dict[str, Any]:
        bm = bmesh.new()

        new_verts = [bm.verts.new(v) for v in points]
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(points) - 1)]

        bm.verts.index_update()
        bm.edges.index_update()

        new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)

        bm.verts.index_update()
        bm.edges.index_update()
        verts = [v.co for v in bm.verts]
        edges = [[v.index for v in e.verts] for e in bm.edges]
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

        bm.free()

        return {"verts": verts, "edges": edges, "tris": tris}

    def shader_config(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.decorator_color = self.addon_prefs.decorations_colour
        self.decorator_color_special = self.addon_prefs.decorator_color_special
        self.decorator_color_selected = self.addon_prefs.decorator_color_selected
        self.decorator_color_error = self.addon_prefs.decorator_color_error
        self.decorator_color_unselected = self.addon_prefs.decorator_color_unselected
        self.decorator_color_background = self.addon_prefs.decorator_color_background
        theme = context.preferences.themes.items()[0][1]
        self.decorator_color_object_active = (*theme.view_3d.object_active, 1)  # unwrap color values and adds alpha=1
        self.decorator_color_x_axis = (*theme.user_interface.axis_x, 1)
        self.decorator_color_y_axis = (*theme.user_interface.axis_y, 1)
        self.decorator_color_z_axis = (*theme.user_interface.axis_z, 1)

        gpu.state.blend_set("ALPHA")
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.point_size_set(6)

    def draw_input_ui(self, context: bpy.types.Context) -> None:
        texts = {
            "D": "Distance: ",
            "A": "Angle: ",
            "X": "X coord: ",
            "Y": "Y coord: ",
            "Z": "Z coord:",
            "AREA": "Area:",
        }
        try:
            assert self.event
            mouse_pos = self.event.mouse_region_x, self.event.mouse_region_y
        except:
            mouse_pos = (None, None)

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 0
        font_size = tool.Blender.scale_font_size()
        offset = tool.Blender.scale_font_size() * 1.5
        line_height = tool.Blender.scale_font_size() * 1.25
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour
        color_highlight = self.addon_prefs.decorator_color_special
        new_line = 0
        for i, (key, field_name) in enumerate(texts.items()):
            formatted_value = None
            if self.input_ui:
                # Controls which options are displayed in the UI
                if key not in self.input_ui.input_options:
                    continue
                new_line += line_height
                if self.tool_state and key != self.tool_state.input_type:
                    formatted_value = self.input_ui.get_formatted_value(key)
                else:
                    formatted_value = self.input_ui.get_text_value(key)

            if formatted_value is None:
                continue
            if self.tool_state and key == self.tool_state.input_type:
                blf.color(self.font_id, *color_highlight)
            else:
                blf.color(self.font_id, *color)
            blf.position(self.font_id, mouse_pos[0] + offset, mouse_pos[1] - (new_line), 0)
            blf.draw(self.font_id, field_name + formatted_value)
        blf.disable(self.font_id, blf.SHADOW)

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

    def draw_measurements_text(self, context):
        region = bpy.context.region
        rv3d = region.data
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 1
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        font_size = tool.Blender.scale_font_size()
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour

        blf.color(self.font_id, *color)

        screen_coords = {}

        for i in range(len(self.polyline_points)):
            if i < 1 and self.measure_type == "POLY_AREA":
                continue
            if i == 0:
                continue
            dim_text_pos = (Vector(self.polyline_points[i].position) + Vector(self.polyline_points[i - 1].position)) / 2
            dim_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, dim_text_pos)
            if dim_text_coords:
                formatted_value = self.polyline_points[i].dim
                text = "d: " + formatted_value
                screen_coords[f"distance_{i}"] = (Vector(dim_text_coords), text)

            if i == 1:
                continue
            angle_text_pos = Vector(self.polyline_points[i - 1].position)
            angle_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, angle_text_pos)
            if angle_text_coords:
                text = "a: " + self.polyline_points[i].angle
                screen_coords[f"angle_{i}"] = (Vector(angle_text_coords), text)

        if self.measure_type == "SINGLE":
            axis_line, axis_line_center = self.calculate_measurement_x_y_and_z(context)
            for i, dim_text_pos in enumerate(axis_line_center):
                dim_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, dim_text_pos)
                if dim_text_coords:
                    value = round((axis_line[i][1] - axis_line[i][0]).length, 4)
                    direction = axis_line[i][1] - axis_line[i][0]
                    if (i == 0 and direction.x < 0) or (i == 1 and direction.y < 0) or (i == 2 and direction.z < 0):
                        value = -value
                    prefix = "xyz"[i]
                    formatted_value = tool.Polyline.format_input_ui_units(value)
                    text = f"{prefix}: {formatted_value}"
                    screen_coords[f"xyz_{i}"] = (Vector(dim_text_coords), text)

        # Area and Length text
        polyline_verts = [Vector((p.x, p.y, p.z)) for p in self.polyline_points]

        # Area
        if self.measure_type == "POLY_AREA" and self.polyline_data.area:
            if len(polyline_verts) < 3:
                blf.disable(self.font_id, blf.SHADOW)
                return
            center = sum(polyline_verts, Vector()) / len(polyline_verts)
            if polyline_verts[0] == polyline_verts[-1]:
                center = sum(polyline_verts[:-1], Vector()) / len(polyline_verts[:-1])
            area_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, center)
            if area_text_coords:
                value = self.polyline_data.area
                text = f"area: {value}"
                text_length = blf.dimensions(self.font_id, text)
                area_text_coords = list(area_text_coords)
                area_text_coords[0] -= text_length[0] / 2
                screen_coords["area"] = (Vector(area_text_coords), text)

        # Length
        if self.measure_type in {"POLYLINE", "POLY_AREA"}:
            if len(polyline_verts) < 3:
                blf.disable(self.font_id, blf.SHADOW)
                return
            total_length_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, polyline_verts[-1])
            if total_length_text_coords:
                value = self.polyline_data.total_length
                text = f"length: {value}"
                screen_coords["length"] = (Vector(total_length_text_coords), text)

        self.adjust_overlapping_labels(screen_coords)

        for label_key, (screen_co, text) in screen_coords.items():
            blf.position(self.font_id, screen_co.x, screen_co.y, 0)
            blf.color(self.font_id, 1, 1, 1, 1)
            text_length = blf.dimensions(self.font_id, text)
            self.draw_text_background(context, screen_co, text_length)
            blf.draw(self.font_id, text)

        blf.disable(self.font_id, blf.SHADOW)

    def adjust_overlapping_labels(self, screen_coords):
        font_id = self.font_id
        text_dimensions = {}

        for label_key, (screen_co, text) in screen_coords.items():
            text_dimensions[label_key] = blf.dimensions(font_id, text)

        if text_dimensions:
            first_height = next(iter(text_dimensions.values()))[1]
            min_spacing = max(2, first_height * 0.3)
        else:
            min_spacing = 2

        label_keys = list(screen_coords.keys())
        for pass_num in range(3):  # 3 passes to try to optimize complex overlaps
            for i in range(len(label_keys)):
                for j in range(i + 1, len(label_keys)):
                    key1, key2 = label_keys[i], label_keys[j]
                    co1, _ = screen_coords[key1]
                    co2, _ = screen_coords[key2]
                    dim1 = text_dimensions[key1]
                    dim2 = text_dimensions[key2]

                    bounds1 = {
                        "left": co1.x - min_spacing,
                        "right": co1.x + dim1[0] + min_spacing,
                        "top": co1.y + dim1[1] + min_spacing,
                        "bottom": co1.y - min_spacing,
                    }
                    bounds2 = {
                        "left": co2.x - min_spacing,
                        "right": co2.x + dim2[0] + min_spacing,
                        "top": co2.y + dim2[1] + min_spacing,
                        "bottom": co2.y - min_spacing,
                    }

                    if (
                        bounds1["left"] < bounds2["right"]
                        and bounds1["right"] > bounds2["left"]
                        and bounds1["bottom"] < bounds2["top"]
                        and bounds1["top"] > bounds2["bottom"]
                    ):
                        x_overlap = min(bounds1["right"], bounds2["right"]) - max(bounds1["left"], bounds2["left"])
                        y_overlap = min(bounds1["top"], bounds2["top"]) - max(bounds1["bottom"], bounds2["bottom"])

                        separation_multiplier = 1.25

                        # Move labels in the direction requiring less movement
                        if x_overlap < y_overlap:
                            separation_distance = (x_overlap / 2 + min_spacing) * separation_multiplier
                            if co1.x < co2.x:
                                co1.x -= separation_distance
                                co2.x += separation_distance
                            else:
                                co1.x += separation_distance
                                co2.x -= separation_distance
                        else:
                            separation_distance = (y_overlap / 2 + min_spacing) * separation_multiplier
                            if co1.y < co2.y:
                                co1.y -= separation_distance
                                co2.y += separation_distance
                            else:
                                co1.y += separation_distance
                                co2.y -= separation_distance

    def draw_measurements_poly(self, context):
        self.shader_config(context)
        polyline_verts: list[Vector] = []
        polyline_edges: list[list[int]] = []
        for point_prop in self.polyline_points:
            point = Vector((point_prop.x, point_prop.y, point_prop.z))
            polyline_verts.append(point)

        for i in range(len(polyline_verts) - 1):
            polyline_edges.append([i, i + 1])

        # Lines for X, Y, Z of single measure
        if self.polyline_data and self.polyline_data.measurement_type == "SINGLE":
            axis, _ = self.calculate_measurement_x_y_and_z(context)
            x_axis, y_axis, z_axis = axis
            self.draw_batch("LINES", [*x_axis], self.decorator_color_x_axis, [(0, 1)])
            self.draw_batch("LINES", [*y_axis], self.decorator_color_y_axis, [(0, 1)])
            self.draw_batch("LINES", [*z_axis], self.decorator_color_z_axis, [(0, 1)])

        # Area highlight
        if self.polyline_data:
            area = self.polyline_data.area.split(" ")[0]
            if self.polyline_data.measurement_type == "POLY_AREA" and area:
                if float(area) > 0:
                    tris = self.calculate_polygon(polyline_verts)["tris"]
                    self.draw_batch(
                        "TRIS", polyline_verts, tool.Blender.transparent_color(self.decorator_color_special), tris
                    )

        # Draw polyline with selected points
        self.line_shader.uniform_float("lineWidth", 2.0)
        self.draw_batch("POINTS", polyline_verts, self.decorator_color_special)
        if len(polyline_verts) > 1:
            self.draw_batch("LINES", polyline_verts, self.decorator_color_special, polyline_edges)

    def get_polylines_data(self, context):
        self.measure_type = tool.Project.get_measure_tool_settings().measurement_type
        polyline_props = tool.Model.get_polyline_props()
        self.polyline_data = polyline_props.insertion_polyline
        self.measure_data = polyline_props.measurement_polyline

    def select_and_draw_measurements_text(self, context):
        self.get_polylines_data(context)
        if self.polyline_data:
            polyline_props = tool.Model.get_polyline_props()
            self.polyline_data = polyline_props.insertion_polyline[0]
            self.polyline_points = self.polyline_data.polyline_points
            self.draw_measurements_text(context)

        if self.measure_data:
            for polyline_data in self.measure_data:
                self.polyline_data = polyline_data
                self.measure_type = polyline_data.measurement_type
                self.polyline_points = self.polyline_data.polyline_points
                self.draw_measurements_text(context)

    def select_and_draw_measurements_poly(self, context):
        self.get_polylines_data(context)
        if self.polyline_data:
            polyline_props = tool.Model.get_polyline_props()
            self.polyline_data = polyline_props.insertion_polyline[0]
            self.polyline_points = self.polyline_data.polyline_points
            self.draw_measurements_poly(context)

        if self.measure_data:
            for polyline_data in self.measure_data:
                self.polyline_data = polyline_data
                self.measure_type = polyline_data.measurement_type
                self.polyline_points = self.polyline_data.polyline_points
                self.draw_measurements_poly(context)

    def draw_snap_point(self, context):
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 1.2)
        theme = context.preferences.themes.items()[0][1]
        decorator_color_object_active = (*theme.view_3d.object_active, 1)  # unwrap color values and adds alpha=1

        region = context.region
        rv3d = region.data

        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        try:
            snap_prop = polyline_props.snap_mouse_ref[0]
            mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
        except:
            pass

        coords = view3d_utils.location_3d_to_region_2d(region, rv3d, mouse_point)
        if not coords:
            return
        padding = 8
        verts = []
        edges = []
        if snap_prop.snap_type in ["Edge", "Edge Intersection", "Vertex"]:
            p1 = (coords[0] - padding, coords[1] + padding)
            p2 = (coords[0] + padding, coords[1] + padding)
            p3 = (coords[0] + padding, coords[1] - padding)
            p4 = (coords[0] - padding, coords[1] - padding)
            verts = [p1, p2, p3, p4]
            if snap_prop.snap_type == "Edge":
                edges = [[0, 1], [1, 3], [3, 2], [2, 0]]
            elif snap_prop.snap_type == "Edge Intersection":
                edges = [[0, 2], [1, 3]]
            else:
                edges = [[0, 1], [1, 2], [2, 3], [3, 0]]
        elif snap_prop.snap_type == "Edge Center":
            p1 = (coords[0], coords[1] + padding)
            p2 = (coords[0] + padding, coords[1] - padding)
            p3 = (coords[0] - padding, coords[1] - padding)
            verts = [p1, p2, p3]
            edges = [[0, 1], [1, 2], [2, 0]]
        elif snap_prop.snap_type == "Face":
            draw_circle_2d(coords, decorator_color_object_active, padding)
            return
        else:
            return

        self.draw_batch("LINES", verts, decorator_color_object_active, edges)

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

        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        # Point related to the mouse
        mouse_point = [Vector((snap_prop.x, snap_prop.y, snap_prop.z))]

        # Plane Method or Default Container
        if tool.Ifc.get():
            default_container_elevation = tool.Root.get_default_container_elevation()
        else:
            default_container_elevation = 0.0
        projection_point = []
        if not self.tool_state:
            pass
        else:
            if self.tool_state.plane_method:
                plane_origin = self.tool_state.plane_origin
                axis1 = None
                axis2 = None
                if self.tool_state.plane_method == "XY":
                    projection_point = [Vector((snap_prop.x, snap_prop.y, self.tool_state.plane_origin.z))]
                    axis1 = [
                        (plane_origin.x - 10000, plane_origin.y, plane_origin.z),
                        (plane_origin.x + 10000, plane_origin.y, plane_origin.z),
                    ]
                    axis2 = [
                        (plane_origin.x, plane_origin.y - 10000, plane_origin.z),
                        (plane_origin.x, plane_origin.y + 100000, plane_origin.z),
                    ]
                    axis_color1 = decorator_color_x_axis
                    axis_color2 = decorator_color_y_axis
                elif self.tool_state.plane_method == "XZ":
                    projection_point = [Vector((snap_prop.x, self.tool_state.plane_origin.y, snap_prop.z))]
                    axis1 = [
                        (plane_origin.x - 10000, plane_origin.y, plane_origin.z),
                        (plane_origin.x + 10000, plane_origin.y, plane_origin.z),
                    ]
                    axis2 = [
                        (plane_origin.x, plane_origin.y, plane_origin.z - 10000),
                        (plane_origin.x, plane_origin.y, plane_origin.z + 100000),
                    ]
                    axis_color1 = decorator_color_x_axis
                    axis_color2 = decorator_color_z_axis
                elif self.tool_state.plane_method == "YZ":
                    projection_point = [Vector((self.tool_state.plane_origin.x, snap_prop.y, snap_prop.z))]
                    axis1 = [
                        (plane_origin.x, plane_origin.y - 10000, plane_origin.z),
                        (plane_origin.x, plane_origin.y + 10000, plane_origin.z),
                    ]
                    axis2 = [
                        (plane_origin.x, plane_origin.y, plane_origin.z - 10000),
                        (plane_origin.x, plane_origin.y, plane_origin.z + 100000),
                    ]
                    axis_color1 = decorator_color_y_axis
                    axis_color2 = decorator_color_z_axis
                else:
                    return
                # When a point is above the plane it projects the point
                # to the plane and creates a line
                if snap_prop.snap_type != "Plane":
                    if self.tool_state.use_default_container and snap_prop.z != 0:
                        projection_point = [Vector((snap_prop.x, snap_prop.y, default_container_elevation))]
                    self.line_shader.uniform_float("lineWidth", 1.0)
                    self.draw_batch("POINTS", projection_point, decorator_color_unselected)
                    edges = [[0, 1]]
                    self.draw_batch("LINES", mouse_point + projection_point, decorator_color_unselected, edges)

                if axis1 and axis2:
                    axis1 = [tuple(tool.Polyline.use_transform_orientations(Vector(v))) for v in axis1]
                    axis2 = [tuple(tool.Polyline.use_transform_orientations(Vector(v))) for v in axis2]
                    self.line_shader.uniform_float("lineWidth", 1.5)
                    self.draw_batch("LINES", axis1, highlight_color(axis_color1), [(0, 1)])
                    self.draw_batch("LINES", axis2, highlight_color(axis_color2), [(0, 1)])

        # Create polyline with selected points
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        if polyline_data:
            polyline_data = polyline_props.insertion_polyline[0]
            polyline_points = polyline_data.polyline_points
        else:
            polyline_points = []
        self.polyline_points = polyline_points
        polyline_verts: list[Vector] = []
        polyline_edges: list[list[int]] = []
        for point_prop in polyline_points:
            point = Vector((point_prop.x, point_prop.y, point_prop.z))
            polyline_verts.append(point)

        for i in range(len(polyline_verts) - 1):
            polyline_edges.append([i, i + 1])

        # Line for angle axis snap
        if snap_prop.snap_type == "Axis":
            axis_color = decorator_color
            if math.isclose(self.axis_start.y, self.axis_end.y, rel_tol=0.001) and math.isclose(
                self.axis_start.z, self.axis_end.z, rel_tol=0.001
            ):
                axis_color = decorator_color_x_axis
            if math.isclose(self.axis_start.x, self.axis_end.x, rel_tol=0.001) and math.isclose(
                self.axis_start.z, self.axis_end.z, rel_tol=0.001
            ):
                axis_color = decorator_color_y_axis
            if math.isclose(self.axis_start.x, self.axis_end.x, rel_tol=0.001) and math.isclose(
                self.axis_start.y, self.axis_end.y, rel_tol=0.001
            ):
                axis_color = decorator_color_z_axis

            self.line_shader.uniform_float("lineWidth", 0.75)
            self.draw_batch("LINES", [self.axis_start, self.axis_end], axis_color, [(0, 1)])

        # Mouse points
        if snap_prop.snap_type in ["Plane", "Axis", "Mix"]:
            self.draw_batch("POINTS", mouse_point, decorator_color_unselected)

        # Line between last polyline point and mouse
        self.line_shader.uniform_float("lineWidth", 2.0)
        edges = [[0, 1]]
        if polyline_verts:
            if snap_prop.snap_type != "Plane" and projection_point:
                self.draw_batch("LINES", [polyline_verts[-1]] + projection_point, decorator_color_selected, edges)
            else:
                self.draw_batch("LINES", [polyline_verts[-1]] + mouse_point, decorator_color_selected, edges)

        # Draw polyline with selected points
        self.line_shader.uniform_float("lineWidth", 2.0)
        self.draw_batch("POINTS", polyline_verts, decorator_color_unselected)
        if len(polyline_verts) > 1:
            self.draw_batch("LINES", polyline_verts, decorator_color_unselected, polyline_edges)


class ProductDecorator(tool.Blender.ViewportDecorator):
    draw_method = "draw_product_preview"
    preview_mode: Literal["PROFILE_VERTICAL", "PROFILE_HORIZONTAL", "LAYER2", "LAYER3", "GENERIC"]
    relating_type = None
    obj_data: dict[str, list] = {}
    obj_matrix_i = None

    @classmethod
    def install(cls, context):
        from bonsai.bim.module.geometry.decorator import ItemDecorator

        if cls.is_installed:
            cls.uninstall()

        props = tool.Model.get_model_props()

        handler = cls()
        if (
            (props.relating_type_id)
            and (relating_type := tool.Ifc.get().by_id(int(props.relating_type_id)))
            and (relating_type_obj := tool.Ifc.get_object(relating_type))
        ):
            handler.relating_type = relating_type
            if tool.Model.get_usage_type(relating_type) == "PROFILE":
                if relating_type.is_a() in {"IfcColumnType", "IfcPileType"}:
                    handler.preview_mode = "PROFILE_VERTICAL"
                else:
                    handler.preview_mode = "PROFILE_HORIZONTAL"
            elif tool.Model.get_usage_type(relating_type) == "LAYER2":
                handler.preview_mode = "LAYER2"
            elif tool.Model.get_usage_type(relating_type) == "LAYER3":
                handler.preview_mode = "LAYER3"
            else:
                handler.preview_mode = "GENERIC"
                if relating_type_obj.data:
                    handler.obj_data = ItemDecorator.get_obj_data(relating_type_obj)
                    handler.obj_data["raw_verts"] = [Vector(v) for v in handler.obj_data["verts"]]
                    handler.obj_matrix_i = relating_type_obj.matrix_world.inverted()

        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_product_preview, (context,), "WINDOW", "POST_VIEW")
        )
        cls.is_installed = True

    def draw_product_preview(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        decorator_color = self.addon_prefs.decorator_color_special
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []

        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        else:
            return

        if self.preview_mode == "LAYER2":
            data = self.get_wall_preview_data()
        elif self.preview_mode == "LAYER3":
            data = self.get_slab_preview_data()
        elif self.preview_mode == "PROFILE_VERTICAL":
            data = self.get_vertical_profile_preview_data()
        elif self.preview_mode == "PROFILE_HORIZONTAL":
            data = self.get_horizontal_profile_preview_data()
        elif self.preview_mode == "GENERIC":
            data = self.get_generic_preview_data()
        if data:
            self.draw_batch("LINES", data["verts"], decorator_color, data["edges"])
            self.draw_batch("TRIS", data["verts"], tool.Blender.transparent_color(decorator_color), data["tris"])

    def get_wall_preview_data(self):
        relating_type = self.relating_type
        # Get properties from object type
        model_props = tool.Model.get_model_props()
        direction_sense = model_props.direction_sense
        direction = 1
        if direction_sense == "NEGATIVE":
            direction = -1

        layers = tool.Model.get_material_layer_parameters(relating_type)
        if not layers["thickness"]:
            return
        thickness = layers["thickness"]
        thickness *= direction

        offset_type = model_props.offset_type_vertical
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        offset = model_props.offset * unit_scale

        height = float(model_props.extrusion_depth)
        rl = float(model_props.rl1)
        x_angle = float(model_props.x_angle)
        if x_angle > radians(90) or x_angle < radians(-90):
            height *= -1
        angle_distance = height * tan(x_angle)
        thickness *= 1 / cos(x_angle)

        data = {}
        data["verts"] = []

        # Verts
        polyline_vertices: list[Vector] = []
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        if len(polyline_points) < 2:
            data = []
            return
        for point in polyline_points:
            polyline_vertices.append(Vector((point.x, point.y, point.z)))

        is_closed = False
        if (
            polyline_vertices[0].x == polyline_vertices[-1].x
            and polyline_vertices[0].y == polyline_vertices[-1].y
            and polyline_vertices[0].z == polyline_vertices[-1].z
        ):
            is_closed = True
            polyline_vertices.pop(-1)  # Remove the last point. The edges are going to inform that the shape is closed.

        bm_base = tool.Model.create_bmesh_from_vertices(polyline_vertices, is_closed)
        base_vertices = tool.Cad.offset_edges(bm_base, offset)
        offset_base_verts = tool.Cad.offset_edges(bm_base, thickness + offset)
        top_vertices = tool.Cad.offset_edges(bm_base, angle_distance + offset)
        offset_top_verts = tool.Cad.offset_edges(bm_base, angle_distance + thickness + offset)
        if is_closed:
            base_vertices.append(base_vertices[0])
            offset_base_verts.append(offset_base_verts[0])
            top_vertices.append(top_vertices[0])
            offset_top_verts.append(offset_top_verts[0])

        if offset_base_verts is not None:
            for v in base_vertices:
                data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

            for v in offset_base_verts[::-1]:
                data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

            for v in top_vertices:
                data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

            for v in offset_top_verts[::-1]:
                data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

        bm_base.free()

        # Edges and Tris
        points = []
        side_edges_1 = []
        side_edges_2 = []
        base_edges = []

        for i in range(len(data["verts"])):
            points.append(Vector(data["verts"][i]))

        n = len(points) // 2
        bottom_side_1 = [[i, (i + 1) % (n)] for i in range((n - 1) // 2)]
        bottom_side_2 = [[i, (i + 1) % (n)] for i in range(n // 2, n - 1)]
        bottom_connections = [[i, n - i - 1] for i in range(n // 2)]
        bottom_loop = bottom_connections + bottom_side_1 + bottom_side_2
        side_edges_1.extend(bottom_side_1)
        side_edges_2.extend(bottom_side_2)
        base_edges.extend(bottom_loop)

        upper_side_1 = [[i + n for i in edges] for edges in bottom_side_1]
        upper_side_2 = [[i + n for i in edges] for edges in bottom_side_2]
        upper_loop = [[i + n for i in edges] for edges in bottom_loop]
        side_edges_1.extend(upper_side_1)
        side_edges_2.extend(upper_side_2)
        base_edges.extend(upper_loop)

        loops = [side_edges_1, side_edges_2, base_edges]

        data["edges"] = []
        data["tris"] = []
        for i, group in enumerate(loops):
            bm = bmesh.new()

            new_verts = [bm.verts.new(v) for v in points]
            new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in group]

            bm.verts.index_update()
            bm.edges.index_update()

            if i == 2:
                new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)
            new_faces = bmesh.ops.bridge_loops(bm, edges=bm.edges, use_pairs=True, use_cyclic=True)

            bm.verts.index_update()
            bm.edges.index_update()
            edges = [[v.index for v in e.verts] for e in bm.edges]
            tris = [[l.vert.index for l in loop] for loop in bm.calc_loop_triangles()]
            data["edges"].extend(edges)
            data["tris"].extend(tris)

        data["edges"] = list(set(tuple(e) for e in data["edges"]))
        data["tris"] = list(set(tuple(t) for t in data["tris"]))
        return data

    def get_slab_preview_data(self):
        relating_type = self.relating_type
        model_props = tool.Model.get_model_props()
        x_angle = 0 if tool.Cad.is_x(model_props.x_angle, 0, tolerance=0.001) else model_props.x_angle
        direction_sense = model_props.direction_sense
        direction = 1
        if direction_sense == "NEGATIVE":
            direction = -1

        layers = tool.Model.get_material_layer_parameters(relating_type)
        if not layers["thickness"]:
            return
        thickness = layers["thickness"] * abs(1 / cos(x_angle))
        thickness *= direction

        offset_type = model_props.offset_type_horizontal
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        offset = model_props.offset * abs(1 / cos(x_angle)) * unit_scale

        data = {}
        data["verts"] = []
        # Verts
        polyline_vertices: list[Vector] = []
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        if len(polyline_points) < 3:
            data = []
            return
        for point in polyline_points:
            polyline_vertices.append(Vector((point.x, point.y, point.z)))
        if x_angle:
            # Get vertices relative to the first polyline point as origin
            local_vertices = [v - Vector(polyline_vertices[0]) for v in polyline_vertices]
            # Make the transformation relative to the x_angle
            transformed_vertices = [Vector((v.x, v.y * (1 / cos(x_angle)), v.z)) for v in local_vertices]
            # Convert back to world origin
            polyline_vertices = [v + Vector(polyline_vertices[0]) for v in transformed_vertices]
        if offset != 0:
            polyline_vertices = [v + Vector((0, 0, offset)) for v in polyline_vertices]
        is_closed = True
        if (
            polyline_vertices[0].x == polyline_vertices[-1].x
            and polyline_vertices[0].y == polyline_vertices[-1].y
            and polyline_vertices[0].z == polyline_vertices[-1].z
        ):
            polyline_vertices.pop(-1)  # Remove the last point. The edges are going to inform that the shape is closed.
        bm = tool.Model.create_bmesh_from_vertices(polyline_vertices, is_closed)
        bm.verts.ensure_lookup_table()
        if x_angle:
            rot_mat = Matrix.Rotation(x_angle, 3, "X")
            if abs(x_angle) > (pi / 2):
                rot_mat = rot_mat @ Matrix.Scale(-1, 3, (0, 1, 0))
            bmesh.ops.rotate(bm, cent=Vector(bm.verts[0].co), verts=bm.verts, matrix=rot_mat)
        new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)
        new_faces = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
        new_verts = [e for e in new_faces["geom"] if isinstance(e, bmesh.types.BMVert)]
        new_faces = bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, thickness))
        bm.verts.index_update()
        bm.edges.index_update()
        verts = [tuple(v.co) for v in bm.verts]
        edges = [[v.index for v in e.verts] for e in bm.edges]
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]
        data["verts"] = verts
        data["edges"] = edges
        data["tris"] = tris
        return data

    def get_vertical_profile_preview_data(self) -> dict[str, Any]:
        relating_type = self.relating_type
        material = ifcopenshell.util.element.get_material(relating_type)
        try:
            profile = material.MaterialProfiles[0].Profile
        except:
            return {}

        model_props = tool.Model.get_model_props()
        extrusion_depth = model_props.extrusion_depth
        cardinal_point = model_props.cardinal_point
        rot_mat = Quaternion()
        if relating_type.is_a("IfcBeamType"):
            y_rot = Quaternion((0.0, 1.0, 0.0), radians(90))
            z_rot = Quaternion((0.0, 0.0, 1.0), radians(90))
            rot_mat = y_rot @ z_rot
        # Get profile data
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, profile)

        verts = shape.verts
        if not verts:
            raise RuntimeError(f"Profile shape has no vertices, it probably is invalid: '{profile}'.")

        edges = shape.edges

        grouped_verts = [[verts[i], verts[i + 1], 0] for i in range(0, len(verts), 3)]
        grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

        # Create offsets based on cardinal point
        min_x = min(v[0] for v in grouped_verts)
        max_x = max(v[0] for v in grouped_verts)
        min_y = min(v[1] for v in grouped_verts)
        max_y = max(v[1] for v in grouped_verts)

        x_offset = (max_x - min_x) / 2
        y_offset = (max_y - min_y) / 2

        match cardinal_point:
            case "1":
                grouped_verts = [(v[0] - x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
            case "2":
                grouped_verts = [(v[0], v[1] + y_offset, v[2]) for v in grouped_verts]
            case "3":
                grouped_verts = [(v[0] + x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
            case "4":
                grouped_verts = [(v[0] - x_offset, v[1], v[2]) for v in grouped_verts]
            case "5":
                grouped_verts = [(v[0], v[1], v[2]) for v in grouped_verts]
            case "6":
                grouped_verts = [(v[0] + x_offset, v[1], v[2]) for v in grouped_verts]
            case "7":
                grouped_verts = [(v[0] - x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]
            case "8":
                grouped_verts = [(v[0], v[1] - y_offset, v[2]) for v in grouped_verts]
            case "9":
                grouped_verts = [(v[0] + x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]

        # Create extrusion bmesh
        bm = bmesh.new()

        grouped_verts.append(grouped_verts[0])  # Close profile
        new_verts = [bm.verts.new(v) for v in grouped_verts]
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(grouped_verts) - 1)]

        bm.verts.index_update()
        bm.edges.index_update()

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

        new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)

        new_faces = bmesh.ops.extrude_face_region(bm, geom=bm.faces, use_dissolve_ortho_edges=True)
        new_verts = [e for e in new_faces["geom"] if isinstance(e, bmesh.types.BMVert)]
        new_faces = bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, extrusion_depth))

        bm.verts.index_update()
        bm.edges.index_update()
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

        # Calculate rotation, mouse position, angle and cardinal point
        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
        data = {}

        verts = [tuple(v.co) for v in bm.verts]
        verts = [tuple(rot_mat @ Vector(v)) for v in verts]
        verts = [tuple(Vector(v) + mouse_point) for v in verts]
        min_z = min(v.co.z for v in bm.verts)
        max_z = max(v.co.z for v in bm.verts)
        # Add axis verts
        verts.append(tuple(mouse_point))
        verts.append(tuple(mouse_point + Vector((0, 0, max_z))))
        # Add only profile edges
        edges = []
        for edge in bm.edges:
            if (edge.verts[0].co.z == min_z and edge.verts[1].co.z == min_z) or (
                edge.verts[0].co.z == max_z and edge.verts[1].co.z == max_z
            ):
                edges.append(edge)
        # Add axis edge
        edges = [(edge.verts[0].index, edge.verts[1].index) for edge in edges]
        edges.append((len(verts) - 1, len(verts) - 2))
        data["verts"] = verts
        data["edges"] = edges
        data["tris"] = tris

        bm.free()
        return data

    def get_horizontal_profile_preview_data(self) -> dict[str, Any]:
        relating_type = self.relating_type
        material = ifcopenshell.util.element.get_material(relating_type)
        try:
            profile_curve = material.MaterialProfiles[0].Profile
        except:
            return {}

        model_props = tool.Model.get_model_props()
        cardinal_point = model_props.cardinal_point

        polyline_verts = []
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        if len(polyline_points) < 2:
            return {}
        for point in polyline_points:
            polyline_verts.append(Vector((point.x, point.y, point.z)))
        polyline_edges = [(i, i + 1) for i in range(len(polyline_verts) - 1)]

        # Get profile shape
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, profile_curve)

        verts = shape.verts
        if not verts:
            raise RuntimeError(f"Profile shape has no vertices, it probably is invalid: '{profile_curve}'.")

        edges = shape.edges

        grouped_verts = [[verts[i], verts[i + 1], 0] for i in range(0, len(verts), 3)]
        grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

        # Create offsets based on cardinal point
        min_x = min(v[0] for v in grouped_verts)
        max_x = max(v[0] for v in grouped_verts)
        min_y = min(v[1] for v in grouped_verts)
        max_y = max(v[1] for v in grouped_verts)

        x_offset = (max_x - min_x) / 2
        y_offset = (max_y - min_y) / 2

        match cardinal_point:
            case "1":
                grouped_verts = [(v[0] - x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
            case "2":
                grouped_verts = [(v[0], v[1] + y_offset, v[2]) for v in grouped_verts]
            case "3":
                grouped_verts = [(v[0] + x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
            case "4":
                grouped_verts = [(v[0] - x_offset, v[1], v[2]) for v in grouped_verts]
            case "5":
                grouped_verts = [(v[0], v[1], v[2]) for v in grouped_verts]
            case "6":
                grouped_verts = [(v[0] + x_offset, v[1], v[2]) for v in grouped_verts]
            case "7":
                grouped_verts = [(v[0] - x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]
            case "8":
                grouped_verts = [(v[0], v[1] - y_offset, v[2]) for v in grouped_verts]
            case "9":
                grouped_verts = [(v[0] + x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]

        data: dict[str, Any] = {}
        data["verts"] = []
        data["edges"] = []
        data["tris"] = []

        grouped_verts = [(v) for v in grouped_verts]

        all_bm = bmesh.new()
        for i in range(len(polyline_verts) - 1):
            mesh = bpy.data.meshes.new("TempMesh")
            # Create the initial mesh from the profile verts
            bm = tool.Model.create_bmesh_from_vertices(grouped_verts, is_closed=True)
            bm.verts.ensure_lookup_table()
            # Creates the clipping plane formed by two segments.
            # The first one is for the profile start, based on the current and previous segment of the polyline.
            # The second is for the profile end, based on the current and the next segment.
            if i == 0:
                d = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
                clip_start = d
            else:
                d1 = (polyline_verts[i] - polyline_verts[i - 1]).normalized()
                d2 = (polyline_verts[i] - polyline_verts[i + 1]).normalized()
                clip_start = (d1 - d2).normalized()

            if i == len(polyline_verts) - 2:
                d = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
                clip_end = d
            else:
                d1 = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
                d2 = (polyline_verts[i + 1] - polyline_verts[i + 2]).normalized()
                clip_end = (d1 - d2).normalized()

            # Rotates the profile face to the right direction
            direction = polyline_verts[i + 1] - polyline_verts[i]
            position = polyline_verts[i]
            rotation_matrix = direction.to_track_quat("Z", "Y").to_matrix().to_4x4()
            bmesh.ops.transform(bm, verts=bm.verts, matrix=rotation_matrix)
            bmesh.ops.translate(bm, verts=bm.verts, vec=position)
            bmesh.ops.translate(bm, verts=bm.verts, vec=-direction)

            # Extrude and move the new face
            last_face = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
            new_verts = [e for e in last_face["geom"] if isinstance(e, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=new_verts, vec=direction * 3)
            # Apply the cutting planes
            cut = bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=polyline_verts[i],
                plane_no=clip_start,
                clear_inner=True,
            )
            bm.verts.index_update()
            bm.edges.index_update()
            cut = bmesh.ops.bisect_plane(
                bm,
                geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=polyline_verts[i + 1],
                plane_no=clip_end,
                clear_outer=True,
            )

            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
            all_bm.from_mesh(mesh)
            bpy.data.meshes.remove(bpy.data.meshes["TempMesh"])

        # It's necessary to add the mesh to an object to get the expected result.
        mesh = bpy.data.meshes.new("TempMesh2")
        all_bm.to_mesh(mesh)
        all_bm.free()
        obj = bpy.data.objects.new("TempObj", mesh)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bpy.data.meshes.remove(bpy.data.meshes["TempMesh2"])

        verts = [tuple(v.co) for v in bm.verts]
        edges = [[v.index for v in e.verts] for e in bm.edges]
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]
        data["verts"] = verts
        data["edges"] = edges
        data["tris"] = tris
        bm.free()
        return data

    def get_generic_preview_data(self):
        if not (data := self.obj_data):
            return
        relating_type = self.relating_type
        model_props = tool.Model.get_model_props()
        if relating_type.is_a("IfcDoorType"):
            rl = float(model_props.rl1)
        elif relating_type.is_a("IfcWindowType"):
            rl = float(model_props.rl2)
        else:
            rl = 0
        polyline_props = tool.Model.get_polyline_props()
        snap_prop = polyline_props.snap_mouse_point[0]
        default_container_elevation = tool.Root.get_default_container_elevation()
        mouse_point = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
        snap_obj = bpy.data.objects.get(snap_prop.snap_object)
        snap_element = tool.Ifc.get_entity(snap_obj)
        rot_mat = Matrix()
        if relating_type.is_a() in ["IfcDoorType", "IfcWindowType"] and snap_element and snap_element.is_a("IfcWall"):
            layers = tool.Model.get_material_layer_parameters(snap_element)
            axes = tool.Model.get_wall_axis(snap_obj, layers=layers)
            axis_base = axes["base"]
            axis_side = axes["side"]
            point_on_base_axis = tool.Cad.point_on_edge(mouse_point, axis_base)
            point_on_side_axis = tool.Cad.point_on_edge(mouse_point, axis_side)
            if (point_on_base_axis - mouse_point).length_squared <= (point_on_side_axis - mouse_point).length_squared:
                # mouse is snapped to the base axis, the preview looks exactly like the placed door / window
                rot_mat = snap_obj.matrix_world
            else:
                # mouse is snapped to the side axis, the preview is inverted, rotate it now and correct x position later
                rot_mat = (
                    (snap_obj.matrix_world.to_quaternion() @ Quaternion(Vector((0, 0, 1)), radians(180)))
                    .to_matrix()
                    .to_4x4()
                )

            mouse_point.z = snap_obj.matrix_world.translation.z

        if snap_element and (container := ifcopenshell.util.element.get_container(snap_element)):
            container_obj = tool.Ifc.get_object(container)
            mouse_point.z = container_obj.location.z

        obj_type = tool.Ifc.get_object(relating_type)

        subcontexts = tool.Drawing.get_active_drawing_subcontexts()
        if not subcontexts:
            subcontexts = [("Model", "Body", "MODEL_VIEW")]

        active_context = tool.Geometry.get_active_representation_context(obj_type)
        active_context_params = tool.Geometry.get_subcontext_parameters(active_context)
        for subcontext in subcontexts:
            if subcontext == active_context_params:
                break

            representation = ifcopenshell.util.representation.get_representation(relating_type, *subcontext)
            if representation:
                bonsai.core.geometry.switch_representation(
                    tool.Ifc,
                    tool.Geometry,
                    obj_type,
                    representation,
                )
                bpy.context.view_layer.update()
                break

        translate_mouse = Matrix.Translation(mouse_point)
        translate_rl = Matrix.Translation((0.0, 0.0, rl))
        combined_m = translate_mouse @ rot_mat @ translate_rl @ self.obj_matrix_i
        data["verts"] = [tuple(combined_m @ v) for v in data["raw_verts"]]
        return data


class WallAxisDecorator(tool.Blender.ViewportDecorator):
    draw_method = "draw_wall_axis"

    def draw_wall_axis(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element and element.is_a("IfcWall"):
                layers = tool.Model.get_material_layer_parameters(element)
                axis = tool.Model.get_wall_axis(obj, layers)
                side = [tuple(list(v) + [obj.location.z]) for v in axis["side"]]
                self.draw_batch("LINES", side, unselected_elements_color, [(0, 1)])
                base = [tuple(list(v) + [obj.location.z]) for v in axis["base"]]
                self.draw_batch("LINES", base, special_elements_color, [(0, 1)])
                reference = [tuple(list(v) + [obj.location.z]) for v in axis["reference"]]
                self.draw_batch("LINES", reference, selected_elements_color, [(0, 1)])

                direction = Vector(base[0]) - Vector(side[0])
                perpendicular = Vector((direction.y, -direction.x, 0))
                perpendicular = perpendicular.normalized() * 0.1
                arrow_base = Vector(side[0]) + direction.normalized() * 0.05
                v3 = arrow_base + perpendicular
                v4 = arrow_base - perpendicular
                arrow = [base[0], side[0], v3, v4]
                self.draw_batch("LINES", arrow, unselected_elements_color, [(0, 1), (1, 2), (1, 3)])


class SlabDirectionDecorator(tool.Blender.ViewportDecorator):
    draw_method = "draw_wall_axis"

    def draw_wall_axis(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        dir = [(0, 0, 0), (0, 0.5, 0), (-0.25, 0.15, 0), (0.25, 0.15, 0)]
        base = [(-2, 0, 0), (2, 0, 0)]
        obj = context.active_object
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if element and (element.is_a("IfcSlab") or element.is_a("IfcRoof")):
            dir = [obj.matrix_world @ Vector(d) for d in dir]
            base = [obj.matrix_world @ Vector(d) for d in base]
            self.draw_batch("LINES", dir, selected_elements_color, [(0, 1), (1, 2), (1, 3)])
            self.draw_batch("LINES", base, selected_elements_color, [(0, 1)])


class FaceAreaDecorator(tool.Blender.ViewportDecorator):
    draw_method = "draw_face_area"

    def draw_face_area(self, context):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")
        decorator_color = self.addon_prefs.decorator_color_special

        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        for i, polyline in enumerate(polyline_data):
            vertices = []
            for point in polyline.polyline_points:
                vertices.append((point.x, point.y, point.z))
            data = PolylineDecorator.calculate_polygon(vertices)
            if data:
                self.draw_batch("POINTS", data["verts"], decorator_color)
                self.draw_batch("LINES", data["verts"], decorator_color, data["edges"])
                self.draw_batch(
                    "TRIS", data["verts"], tool.Blender.transparent_color(decorator_color, alpha=0.5), data["tris"]
                )


class BoundingBoxDecorator(tool.Blender.ViewportDecorator):
    draw_methods = (
        ("draw_bounding_box_wire_cube", "POST_VIEW"),
        ("draw_dimension_text", "POST_PIXEL"),
    )

    def __init__(self):
        context = bpy.context
        theme = context.preferences.themes.items()[0][1]
        self.decorator_color_x_axis = (*theme.user_interface.axis_x, 1)
        self.decorator_color_y_axis = (*theme.user_interface.axis_y, 1)
        self.decorator_color_z_axis = (*theme.user_interface.axis_z, 1)
        self.decorator_color_wire = (*theme.view_3d.bone_solid, 1)
        self.decorator_color_special = tool.Blender.get_addon_preferences().decorator_color_special

    @staticmethod
    def get_combined_bounding_box_corners(objects):

        if not objects:
            return None, None, None
        if len(objects) == 1:
            obj = objects[0]
            corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        else:
            all_corners = []
            for obj in objects:
                if hasattr(obj, "bound_box"):
                    all_corners.extend([obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box])
            min_corner = mathutils.Vector(
                (min(v.x for v in all_corners), min(v.y for v in all_corners), min(v.z for v in all_corners))
            )
            max_corner = mathutils.Vector(
                (max(v.x for v in all_corners), max(v.y for v in all_corners), max(v.z for v in all_corners))
            )
            corners = [
                mathutils.Vector((min_corner.x, min_corner.y, min_corner.z)),
                mathutils.Vector((min_corner.x, min_corner.y, max_corner.z)),
                mathutils.Vector((min_corner.x, max_corner.y, max_corner.z)),
                mathutils.Vector((min_corner.x, max_corner.y, min_corner.z)),
                mathutils.Vector((max_corner.x, min_corner.y, min_corner.z)),
                mathutils.Vector((max_corner.x, min_corner.y, max_corner.z)),
                mathutils.Vector((max_corner.x, max_corner.y, max_corner.z)),
                mathutils.Vector((max_corner.x, max_corner.y, min_corner.z)),
            ]
        edges = [
            (0, 1, "Z"),
            (1, 2, "Y"),
            (2, 3, "Z"),
            (3, 0, "Y"),
            (4, 5, "Z"),
            (5, 6, "Y"),
            (6, 7, "Z"),
            (7, 4, "Y"),
            (0, 4, "X"),
            (1, 5, "X"),
            (2, 6, "X"),
            (3, 7, "X"),
        ]
        axis_colors = {
            "X": (0.956, 0.282, 0.322, 1),
            "Y": (0.565, 0.812, 0.125, 1),
            "Z": (0.196, 0.529, 0.929, 1),
        }
        return corners, edges, axis_colors

    @staticmethod
    def find_closest_trihedron(corners, edges, region, rv3d):

        min_y = float("inf")
        best_origin = 0
        for idx, corner in enumerate(corners):
            screen_co = location_3d_to_region_2d(region, rv3d, corner)
            if screen_co is not None and screen_co.y < min_y:
                min_y = screen_co.y
                best_origin = idx
        trihedron = [
            {"X": (0, 4), "Y": (0, 3), "Z": (0, 1)},
            {"X": (1, 5), "Y": (1, 2), "Z": (1, 0)},
            {"X": (2, 6), "Y": (2, 1), "Z": (2, 3)},
            {"X": (3, 7), "Y": (3, 0), "Z": (3, 2)},
            {"X": (4, 0), "Y": (4, 7), "Z": (4, 5)},
            {"X": (5, 1), "Y": (5, 6), "Z": (5, 4)},
            {"X": (6, 2), "Y": (6, 5), "Z": (6, 7)},
            {"X": (7, 3), "Y": (7, 4), "Z": (7, 6)},
        ]
        return trihedron[best_origin]

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

    def draw_bounding_box_wire_cube(self, context):

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        selected_objects = [obj for obj in bpy.context.selected_objects if hasattr(obj, "bound_box")]
        if not selected_objects:
            return
        corners, edges, axis_colors = self.get_combined_bounding_box_corners(selected_objects)
        region = bpy.context.region
        rv3d = bpy.context.region_data
        gpu.state.line_width_set(2.0)
        for i1, i2, axis in edges:
            self.draw_batch("LINES", [corners[i1], corners[i2]], self.decorator_color_wire)
        closest_indices = self.find_closest_trihedron(corners, edges, region, rv3d)
        for axis in "XYZ":
            pair = closest_indices[axis]
            if pair is not None:
                i1, i2 = pair
                color = getattr(self, f"decorator_color_{axis.lower()}_axis")
                self.draw_batch("LINES", [corners[i1], corners[i2]], color)

    def draw_dimension_text(self, context):
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        selected_objects = [obj for obj in bpy.context.selected_objects if hasattr(obj, "bound_box")]
        if not selected_objects:
            return
        corners, edges, axis_colors = self.get_combined_bounding_box_corners(selected_objects)
        if not corners:
            return
        dims = mathutils.Vector(
            (
                (corners[4] - corners[0]).length,
                (corners[3] - corners[0]).length,
                (corners[1] - corners[0]).length,
            )
        )
        region = bpy.context.region
        rv3d = bpy.context.region_data

        addon_prefs = tool.Blender.get_addon_preferences()
        font_id = 0
        font_size = tool.Blender.scale_font_size()
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)
        color = addon_prefs.decorations_colour
        blf.color(font_id, *color)

        closest_indices = self.find_closest_trihedron(corners, edges, region, rv3d)

        screen_coords = {}
        for axis_idx, axis in enumerate("XYZ"):
            pair = closest_indices[axis]
            if pair is not None:
                i1, i2 = pair
                offset_factor = 0.6 - (axis_idx * 0.1)
                center = corners[i1].lerp(corners[i2], offset_factor)
                value = getattr(dims, axis.lower())
                screen_co = location_3d_to_region_2d(region, rv3d, center)
                if screen_co is not None:
                    screen_coords[axis] = (screen_co, value)

        self.adjust_overlapping_labels(screen_coords)

        for axis, (screen_co, value) in screen_coords.items():
            blf.position(font_id, screen_co.x, screen_co.y, 0)
            blf.color(font_id, 1, 1, 1, 1)
            value_str = f"D{axis.lower()}: " + format_distance(value, hide_units=False)
            text_length = blf.dimensions(font_id, value_str)
            self.draw_text_background(context, screen_co, text_length)
            blf.draw(font_id, value_str)

        blf.disable(font_id, blf.SHADOW)

    def adjust_overlapping_labels(self, screen_coords):
        font_id = 0
        text_dimensions = {}
        for axis, (screen_co, value) in screen_coords.items():
            value_str = f"D{axis.lower()}: " + format_distance(value, hide_units=False)
            text_dimensions[axis] = blf.dimensions(font_id, value_str)

        min_spacing = 5

        axes = list(screen_coords.keys())
        for i in range(len(axes)):
            for j in range(i + 1, len(axes)):
                axis1, axis2 = axes[i], axes[j]
                co1, _ = screen_coords[axis1]
                co2, _ = screen_coords[axis2]
                dim1 = text_dimensions[axis1]
                dim2 = text_dimensions[axis2]

                bounds1 = {
                    "left": co1.x - min_spacing,
                    "right": co1.x + dim1[0] + min_spacing,
                    "top": co1.y + dim1[1] + min_spacing,
                    "bottom": co1.y - min_spacing,
                }
                bounds2 = {
                    "left": co2.x - min_spacing,
                    "right": co2.x + dim2[0] + min_spacing,
                    "top": co2.y + dim2[1] + min_spacing,
                    "bottom": co2.y - min_spacing,
                }

                if (
                    bounds1["left"] < bounds2["right"]
                    and bounds1["right"] > bounds2["left"]
                    and bounds1["bottom"] < bounds2["top"]
                    and bounds1["top"] > bounds2["bottom"]
                ):

                    x_overlap = min(bounds1["right"], bounds2["right"]) - max(bounds1["left"], bounds2["left"])
                    y_overlap = min(bounds1["top"], bounds2["top"]) - max(bounds1["bottom"], bounds2["bottom"])

                    if x_overlap < y_overlap:
                        if co1.x < co2.x:
                            co1.x -= x_overlap / 2 + min_spacing
                            co2.x += x_overlap / 2 + min_spacing
                        else:
                            co1.x += x_overlap / 2 + min_spacing
                            co2.x -= x_overlap / 2 + min_spacing
                    else:
                        if co1.y < co2.y:
                            co1.y -= y_overlap / 2 + min_spacing
                            co2.y += y_overlap / 2 + min_spacing
                        else:
                            co1.y += y_overlap / 2 + min_spacing
                            co2.y -= y_overlap / 2 + min_spacing


def compute_mep_join_location():
    """Midpoint between the closest endpoint pair of two selected MEP
    segments — the world location where a connecting fitting (bend /
    transition) would land. Returns ``None`` when prerequisites aren't met
    (wrong cardinality, mixed non-MEP)."""
    selected = list(tool.Blender.get_selected_objects())
    if len(selected) != 2:
        return None
    for obj in selected:
        element = tool.Ifc.get_entity(obj)
        if element is None or not tool.System.is_mep_element(element):
            return None
    a_start, a_end = tool.Model.get_flow_segment_axis(selected[0])
    b_start, b_end = tool.Model.get_flow_segment_axis(selected[1])
    pairs = [(a_start, b_start), (a_start, b_end), (a_end, b_start), (a_end, b_end)]
    closest = min(pairs, key=lambda p: (p[0] - p[1]).length)
    return (closest[0] + closest[1]) * 0.5


class MEPSegmentExtendPreviewDecorator(tool.Blender.ViewportDecorator):
    """Preview line for the MEP segment extend-to-cursor gizmo. Renders one
    line from the segment's current end to the cursor's projection on the
    segment's local Z axis when the extend icon is hovered. Self-gates every
    draw on the viewport gizmo toggle and the per-feature ``extend`` pref."""

    draw_method = "draw_line"

    LINE_WIDTH = 1.5
    LINE_ALPHA = 0.8

    def draw_line(self, context: bpy.types.Context) -> None:
        if not tool.Blender.are_viewport_gizmos_enabled():
            return
        prefs = tool.Blender.get_addon_preferences()

        active = context.active_object
        if active is None:
            return
        selected = list(tool.Blender.get_selected_objects())
        if active not in selected or len(selected) != 1:
            return

        element = tool.Ifc.get_entity(active)
        if element is None:
            return

        from bonsai.bim.module.model.mep import (
            GizmoDuctSegmentEdition,
            GizmoPipeSegmentEdition,
        )

        if tool.Parametric.is_pipe_segment(element):
            gizmo_prefs = getattr(prefs.gizmos, "pipe_segment", None)
            gizmo_cls = GizmoPipeSegmentEdition
        elif tool.Parametric.is_duct_segment(element):
            gizmo_prefs = getattr(prefs.gizmos, "duct_segment", None)
            gizmo_cls = GizmoDuctSegmentEdition
        else:
            return
        if gizmo_prefs is None or not getattr(gizmo_prefs, "enabled", True):
            return
        if not self._cursor_icon_hovered(gizmo_cls, "extend_gizmo", context):
            return

        current_length = max(c[2] for c in active.bound_box) if active.bound_box else 0.0
        line = self._compute_extend_preview_line(active.matrix_world, context.scene.cursor.location, current_length)
        if line is None:
            return
        start_world, end_world = line
        color = tuple(prefs.decorator_color_selected[:3])
        draw_polyline_segments(
            context,
            [(tuple(start_world), tuple(end_world))],
            color,
            self.LINE_ALPHA,
            self.LINE_WIDTH,
        )

    @staticmethod
    def _compute_extend_preview_line(
        matrix_world: Matrix,
        cursor_world: Vector,
        current_length: float,
    ) -> tuple[Vector, Vector] | None:
        """Returns ``(current_end_world, target_end_world)`` or ``None`` when
        no extend would happen (degenerate segment, or cursor on the existing
        end). Target follows the cursor's raw local-Z projection unbounded —
        the line stays visible past the segment origin (negative local Z)
        because the user expects to see where they're pointing even when the
        operator would floor it."""
        if current_length <= 0:
            return None
        cursor_local = matrix_world.inverted() @ cursor_world
        if abs(cursor_local.z - current_length) < 1e-6:
            return None
        current_end_world = matrix_world @ Vector((0.0, 0.0, current_length))
        target_end_world = matrix_world @ Vector((0.0, 0.0, cursor_local.z))
        return current_end_world, target_end_world


class BendPreviewDecorator(tool.Blender.ViewportDecorator):
    """GPU preview lines for the bend-creation flow.

    Polls on ``scene.BIMPreviewProperties.bend.is_active`` and renders the
    centerline + leg projections returned by ``mep.compute_bend_preview_polylines``.
    The two leg lines (segment → tangent point) show how each segment will
    be shortened; the arc polyline approximates the bend curve. On invalid
    geometry, draws the two rejected axes in warning colour instead so the
    user sees why the bend cannot be placed.

    Installed once per Blender session from ``bim/handler.py:load_post``.
    Cheap to leave running because the first thing ``draw`` does is check
    ``is_active`` and return when False.
    """

    LINE_WIDTH_LEG = 1.5
    LINE_WIDTH_ARC = 2.5
    LINE_ALPHA = 0.7

    def draw(self, context: bpy.types.Context) -> None:
        scene = context.scene
        preview = getattr(scene, "BIMPreviewProperties", None)
        props = preview.bend if preview is not None else None
        if props is None or not props.is_active:
            return
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return
        try:
            start_element = ifc_file.by_id(props.start_segment_id)
            end_element = ifc_file.by_id(props.end_segment_id)
        except Exception:
            return
        start_obj = tool.Ifc.get_object(start_element) if start_element else None
        end_obj = tool.Ifc.get_object(end_element) if end_element else None
        if start_obj is None or end_obj is None:
            return

        # Late import: decorator.py loads at addon enable but mep.py imports
        # this module for the extend preview, so a module-level import would
        # cycle.
        from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

        preview = cached_compute_bend_preview_polylines(
            start_obj, end_obj, props.start_length, props.end_length, props.radius
        )
        prefs = tool.Blender.get_addon_preferences()

        if not preview["valid"]:
            warning_color = tuple(prefs.decorator_color_error[:3])
            axes = preview.get("invalid_axes") or []
            if axes:
                segments = [(tuple(a), tuple(b)) for a, b in axes]
                draw_polyline_segments(context, segments, warning_color, self.LINE_ALPHA, self.LINE_WIDTH_ARC)
            return

        leg_color = tuple(prefs.decorations_colour[:3])
        arc_color = tuple(prefs.decorator_color_selected[:3])

        leg_a_far, leg_a_end = preview["leg_a"]
        leg_b_far, leg_b_end = preview["leg_b"]
        draw_polyline_segments(
            context,
            [(tuple(leg_a_far), tuple(leg_a_end)), (tuple(leg_b_far), tuple(leg_b_end))],
            leg_color,
            self.LINE_ALPHA,
            self.LINE_WIDTH_LEG,
        )

        arc = preview["arc"]
        if len(arc) >= 2:
            arc_segments = [(tuple(arc[i]), tuple(arc[i + 1])) for i in range(len(arc) - 1)]
            draw_polyline_segments(context, arc_segments, arc_color, self.LINE_ALPHA, self.LINE_WIDTH_ARC)


class WallFilletPreviewDecorator(tool.Blender.ViewportDecorator):
    """GPU preview lines for the wall-fillet flow.

    Polls on ``scene.BIMPreviewProperties.wall_fillet.is_active`` and renders
    the leg projections + arc + radial construction lines returned by
    ``tool.Wall.compute_wall_fillet_geometry``. The two leg lines show how
    each wall will be shortened to its tangent point; the arc approximates
    the rounded corner; the two construction lines (arc center to each
    tangent point) visually pin the radius.

    Installed once per Blender session from ``bim/handler.py:load_post``
    and uninstalled in ``bim/module/model/__init__.py:unregister``."""

    LINE_WIDTH_LEG = 1.5
    LINE_WIDTH_ARC = 2.5
    LINE_WIDTH_CONSTRUCTION = 1.0
    LINE_ALPHA = 0.7
    CONSTRUCTION_ALPHA = 0.4

    def draw(self, context: bpy.types.Context) -> None:
        scene = context.scene
        preview_props = getattr(scene, "BIMPreviewProperties", None)
        props = preview_props.wall_fillet if preview_props is not None else None
        if props is None or not props.is_active:
            return
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return
        try:
            wall_a = ifc_file.by_id(props.wall_a_id)
            wall_b = ifc_file.by_id(props.wall_b_id)
        except Exception:
            return
        wall_a_obj = tool.Ifc.get_object(wall_a) if wall_a else None
        wall_b_obj = tool.Ifc.get_object(wall_b) if wall_b else None
        if wall_a_obj is None or wall_b_obj is None:
            return

        geom = tool.Wall.compute_wall_fillet_geometry(wall_a_obj, wall_b_obj, props.radius)
        if geom is None:
            return

        prefs = tool.Blender.get_addon_preferences()
        warning_color = tuple(prefs.decorator_color_error[:3])

        if not geom["valid"]:
            # Degenerate geometry paints red: invalid_radius shows legs+arc
            # past the wall ends; invalid_axes shows the parallel/collinear
            # axes.
            if geom.get("invalid_radius"):
                tangent_a = geom.get("tangent_a")
                tangent_b = geom.get("tangent_b")
                ref_a = tool.Wall.get_world_reference_line(wall_a_obj)
                ref_b = tool.Wall.get_world_reference_line(wall_b_obj)
                if tangent_a is not None and tangent_b is not None and ref_a is not None and ref_b is not None:
                    far_a = self._far_endpoint(ref_a, geom["intersection"])
                    far_b = self._far_endpoint(ref_b, geom["intersection"])
                    legs = [
                        (tuple(far_a), tuple(tangent_a)),
                        (tuple(far_b), tuple(tangent_b)),
                    ]
                    draw_polyline_segments(context, legs, warning_color, self.LINE_ALPHA, self.LINE_WIDTH_LEG)
                arc = geom.get("arc") or []
                if len(arc) >= 2:
                    arc_segments = [(tuple(arc[i]), tuple(arc[i + 1])) for i in range(len(arc) - 1)]
                    draw_polyline_segments(context, arc_segments, warning_color, self.LINE_ALPHA, self.LINE_WIDTH_ARC)
            elif geom.get("invalid_axes"):
                axes = geom["invalid_axes"]
                segments = [(tuple(a), tuple(b)) for a, b in axes]
                draw_polyline_segments(context, segments, warning_color, self.LINE_ALPHA, self.LINE_WIDTH_ARC)
            return

        leg_color = tuple(prefs.decorations_colour[:3])
        arc_color = tuple(prefs.decorator_color_selected[:3])

        # Resolved against the IFC reference line, not mesh bounds, so trimmed
        # walls and openings don't shift the leg endpoints.
        ref_a = tool.Wall.get_world_reference_line(wall_a_obj)
        ref_b = tool.Wall.get_world_reference_line(wall_b_obj)
        if ref_a is not None and ref_b is not None and geom["intersection"] is not None:
            far_a = self._far_endpoint(ref_a, geom["intersection"])
            far_b = self._far_endpoint(ref_b, geom["intersection"])
            legs = [
                (tuple(far_a), tuple(geom["tangent_a"])),
                (tuple(far_b), tuple(geom["tangent_b"])),
            ]
            draw_polyline_segments(context, legs, leg_color, self.LINE_ALPHA, self.LINE_WIDTH_LEG)

        arc = geom["arc"]
        if len(arc) >= 2:
            arc_segments = [(tuple(arc[i]), tuple(arc[i + 1])) for i in range(len(arc) - 1)]
            draw_polyline_segments(context, arc_segments, arc_color, self.LINE_ALPHA, self.LINE_WIDTH_ARC)

        # Dim construction lines from arc_center to each tangent point so
        # the radius reads as concrete during drag.
        arc_center = geom.get("arc_center")
        if arc_center is not None:
            construction = [
                (tuple(arc_center), tuple(geom["tangent_a"])),
                (tuple(arc_center), tuple(geom["tangent_b"])),
            ]
            draw_polyline_segments(
                context, construction, arc_color, self.CONSTRUCTION_ALPHA, self.LINE_WIDTH_CONSTRUCTION
            )

    @staticmethod
    def _far_endpoint(reference_line, intersection):
        """Endpoint of ``reference_line`` furthest from ``intersection``."""
        p1, p2 = reference_line
        d1 = (p1.x - intersection[0]) ** 2 + (p1.y - intersection[1]) ** 2 + (p1.z - intersection[2]) ** 2
        d2 = (p2.x - intersection[0]) ** 2 + (p2.y - intersection[1]) ** 2 + (p2.z - intersection[2]) ** 2
        return p2 if d2 >= d1 else p1


class _DoorSwingArc(NamedTuple):
    """Parameters for one swing-arc draw call in door-local space."""

    hinge_x: float
    hinge_y: float
    panel_width: float
    x_mirror: bool


def _visible_arcs(door_type: str, overall_width: float, lining_offset: float) -> list[_DoorSwingArc]:
    """Arc specs for the parametric door swing visualisation, agnostic of
    edit-mode state so the readonly preview and the editor view stay aligned.

    Empty only for sliding-door types; unknown ``door_type`` values fall
    through to a single left-hinged arc."""
    if "SLIDING" in door_type:
        return []
    is_double = "DOUBLE_DOOR" in door_type
    is_right_single = door_type.endswith("RIGHT") and not is_double
    arcs = [
        _DoorSwingArc(
            hinge_x=overall_width if is_right_single else 0.0,
            hinge_y=lining_offset,
            panel_width=overall_width / 2 if is_double else overall_width,
            x_mirror=is_right_single,
        )
    ]
    if is_double:
        arcs.append(
            _DoorSwingArc(
                hinge_x=overall_width,
                hinge_y=lining_offset,
                panel_width=overall_width / 2,
                x_mirror=True,
            )
        )
    return arcs


# Unit quarter-arc samples shared with the edit-mode swing gizmo so the
# readonly arc traces the same curve. Re-scaled per draw via the per-arc
# transform.
_DOOR_SWING_ARC_ANGLE_MIN_RAD = math.radians(DOOR_SWING_ANGLE_MIN)
_DOOR_SWING_ARC_ANGLE_RANGE_RAD = math.radians(DOOR_SWING_ANGLE_MAX) - _DOOR_SWING_ARC_ANGLE_MIN_RAD
_DOOR_SWING_ARC_UNIT_POINTS: tuple[Vector, ...] = tuple(
    Vector(
        (
            math.cos(_DOOR_SWING_ARC_ANGLE_MIN_RAD + _DOOR_SWING_ARC_ANGLE_RANGE_RAD * (_i / ARC_SEGMENTS)),
            math.sin(_DOOR_SWING_ARC_ANGLE_MIN_RAD + _DOOR_SWING_ARC_ANGLE_RANGE_RAD * (_i / ARC_SEGMENTS)),
            0.0,
        )
    )
    for _i in range(ARC_SEGMENTS + 1)
)


class DoorSwingReadonlyDecorator(tool.Blender.ViewportDecorator):
    """Always-on swing-arc preview for the active Bonsai-parametric IfcDoor
    when it is not currently in parametric edit mode. Matches the visual
    contract of the parametric door's swing-arc gizmos so the hinge side
    and opening direction can be read without entering edit mode.

    Silent-skip cases (no draw, no error):

    - active object missing / not selected / not an IfcDoor;
    - door is mid-edit (the swing gizmo is already painting the arc);
    - door has no ``BBIM_Door`` pset (legacy import, never edited in Bonsai)."""

    LINE_WIDTH = 1.5
    LINE_ALPHA = 0.8

    def draw(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        if obj is None or not obj.select_get():
            return
        element = tool.Ifc.get_entity(obj)
        if element is None or not element.is_a("IfcDoor"):
            return
        props = getattr(obj, "BIMDoorProperties", None)
        if props is not None and props.is_editing:
            return
        pset = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Door")
        if not pset:
            return
        data = pset.get("data_dict")
        if not data:
            return
        door_type = data.get("door_type", "")
        overall_width_project = data.get("overall_width", 0.0)
        lining_offset_project = (data.get("lining_properties") or {}).get("lining_offset", 0.0)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        overall_width = overall_width_project * si_conversion
        lining_offset = lining_offset_project * si_conversion
        specs = _visible_arcs(door_type, overall_width, lining_offset)
        if not specs:
            return
        prefs = tool.Blender.get_addon_preferences()
        main_color = tuple(prefs.decorator_color_special[:3])
        mw = obj.matrix_world
        segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        for spec in specs:
            x_flip = Matrix.Scale(-1, 4, (1, 0, 0)) if spec.x_mirror else Matrix.Identity(4)
            transform = (
                Matrix.Translation(Vector((spec.hinge_x, spec.hinge_y, 0.0)))
                @ Matrix.Scale(spec.panel_width, 4)
                @ x_flip
            )
            world_main = mw @ transform
            pts = [world_main @ p for p in _DOOR_SWING_ARC_UNIT_POINTS]
            for i in range(len(pts) - 1):
                segments.append((tuple(pts[i]), tuple(pts[i + 1])))
        draw_polyline_segments(context, segments, main_color, self.LINE_ALPHA, self.LINE_WIDTH)


_BBOX_EDGES = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
)  # fmt: skip


def bbox_world_edges(
    obj: bpy.types.Object,
) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    """Return world-space (start, end) tuples for the 12 edges of ``obj``'s
    bounding box. Empty list if the object has no bound_box (e.g. Empties)."""
    if not obj.bound_box:
        return []
    mw = obj.matrix_world
    corners = [mw @ Vector(c) for c in obj.bound_box]
    return [(tuple(corners[a]), tuple(corners[b])) for a, b in _BBOX_EDGES]


def draw_polyline_segments(
    context: bpy.types.Context,
    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    color_rgb: tuple[float, float, float],
    alpha: float,
    line_width: float,
) -> None:
    """Render ``segments`` as one anti-aliased LINES batch in world space."""
    if not segments:
        return
    verts: list[tuple[float, float, float]] = []
    indices: list[tuple[int, int]] = []
    for start, end in segments:
        base = len(verts)
        verts.append(start)
        verts.append(end)
        indices.append((base, base + 1))
    if not tool.Blender.validate_shader_batch_data(verts, indices):
        return
    region = getattr(context, "region", None)
    if region is None:
        return
    shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
    shader.bind()
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", line_width)
    shader.uniform_float("color", (*color_rgb, alpha))
    batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=indices)
    gpu.state.blend_set("ALPHA")
    batch.draw(shader)
    gpu.state.blend_set("NONE")


_BBOX_HIGHLIGHT_LINE_WIDTH = 1.8
_BBOX_HIGHLIGHT_LINE_ALPHA = 0.8


class _ConnectedNetworkPathDecorator(tool.Blender.ViewportDecorator):
    """Shared scaffolding for "BFS-walk a connected IFC network from a selected
    seed and overlay its schematic path" viewport decorators.

    Subclasses implement three hooks:

        ``_is_seed_element(element)``: True if ``element`` can seed a walk
        ``_walk(start_element)``: list of network elements reachable from the seed
        ``_build_geometry(connected)``: ``(lines, free_points, connection_points)``
          for one walk pass; free dots render in the base selected color,
          connection dots in the "special" slot so junctions stand out

    Lifecycle each redraw: gate on ``BIMModelProperties.show_paths`` (the
    shared toggle for all network-path overlays), find the first selected
    seed element, walk the network (cached per seed-GUID per IFC file), and
    render lines + connection-node dots. Geometry is memoised through a
    ``TokenCache`` keyed on the decorator-cache token, so depsgraph / undo /
    redo / load all invalidate the resolved world-space pass without
    re-walking.

    Install / uninstall is driven by the central addon-load handler and
    by the toggle's ``update`` callback, so flipping the property takes
    effect immediately without a Blender restart."""

    # Network-path lines + junction dots render in ``decorator_color_selected``
    # (Bonsai's palette slot for "what the user is currently inspecting"); free
    # endpoints (dangling chain tips) switch to ``decorator_color_special`` so
    # the end of the line stands apart from interior junctions at a glance.
    LINE_WIDTH = 1.3
    LINE_ALPHA = 0.85
    # Sized larger than LINE_WIDTH so connection nodes read as discrete
    # points rather than line thickenings.
    DOT_SIZE = 4.0
    # Squared distance under which two emitted dots are treated as the same
    # connection node. In Blender units (typically meters), 1e-4 m ≈ 0.1 mm
    # — below the precision at which two IFC reference-line endpoints would
    # ever be authored as "the same join" but not so tight that float drift
    # from coordinate composition misses a real coincidence.
    CONNECTION_EPS_SQ = 1e-4 * 1e-4

    def __init__(self) -> None:
        # Walk cache keyed on (start_guid, ifc_file, geom_gen). Stores STEP
        # integer ids rather than ``entity_instance`` references — re-resolved
        # via ``ifc_file.by_id`` on each cache hit. Structurally rules out
        # the dangling-SWIG-handle class of bug: an entity removed between
        # frames either bumps geom_gen (cache miss → re-walk) or fails to
        # re-resolve (handled below by re-walking). Compare ``ifc_file`` with
        # ``is`` (not id()) so a GC-recycled id() can't produce a false hit.
        self._cached_start_guid: str | None = None
        self._cached_ifc_file: Any = None
        self._cached_geom_gen: int = -1
        self._cached_walk_ids: list[int] = []
        # Geometry cache: shared TokenCache. Key folds in geom_gen so IFC
        # mutations that don't surface via the depsgraph still flush the
        # resolved world-space lines and dots.
        self._geom_cache: TokenCache[
            tuple[
                list[tuple[tuple[float, float, float], tuple[float, float, float]]],
                list[tuple[float, float, float]],
                list[tuple[float, float, float]],
            ]
        ] = TokenCache()
        # One-shot guards so a corrupted walk or build surfaces in the console
        # once per decorator instance instead of every redraw.
        self._walk_failure_logged: bool = False
        self._build_failure_logged: bool = False
        # Short-circuit re-running a known-broken walk or build for the same
        # seed every frame; cleared the moment the user picks a different seed.
        self._failed_seed_guid: str | None = None

    _ABSTRACT_HOOKS = ("_is_seed_element", "_walk", "_build_geometry")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Pin the template-method contract at class-definition time, mirroring
        # ViewportDecorator's draw_method check: a subclass that forgets to
        # override one of the three hooks would otherwise pass class creation
        # and only raise NotImplementedError on the first walk — deferred long
        # past the offending declaration.
        missing = [
            name for name in cls._ABSTRACT_HOOKS if getattr(cls, name) is getattr(_ConnectedNetworkPathDecorator, name)
        ]
        if missing:
            raise TypeError(f"{cls.__name__}: must override abstract hook(s) {sorted(missing)}")

    def _is_seed_element(self, element: Any) -> bool:
        raise NotImplementedError

    def _walk(self, start_element: Any) -> list[Any]:
        raise NotImplementedError

    def _build_geometry(
        self,
        connected: list[Any],
    ) -> tuple[
        list[tuple[tuple[float, float, float], tuple[float, float, float]]],
        list[tuple[float, float, float]],
        list[tuple[float, float, float]],
    ]:
        """Resolve world-space line segments + dots for one walk pass. Returns
        ``(lines, free_points, connection_points)`` — free dots get the base
        selected color, connection dots get the special color so junctions
        between two consecutive elements pop out. Never raises; skips
        degenerate elements."""
        raise NotImplementedError

    @classmethod
    def _partition_points_by_coincidence(
        cls,
        points: list[tuple[float, float, float]],
        lines: Sequence[tuple[tuple[float, float, float], tuple[float, float, float]]] = (),
    ) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
        """Split ``points`` into ``(free, connection)``. A point is "connection"
        when (a) at least one other point in the list lies within
        ``CONNECTION_EPS_SQ`` (corner / end-to-end joins), or (b) it lies within
        ``CONNECTION_EPS_SQ`` of the interior of any segment in ``lines``
        (T-junctions / ATPATH joins, where one wall's end lands on another
        wall's axis interior rather than its endpoint). Connection points
        dedupe to one representative each so coincident dots don't stack the
        same color."""
        eps_sq = cls.CONNECTION_EPS_SQ
        n = len(points)
        shared = [False] * n
        for i in range(n):
            xi, yi, zi = points[i]
            for j in range(i + 1, n):
                xj, yj, zj = points[j]
                dx, dy, dz = xi - xj, yi - yj, zi - zj
                if dx * dx + dy * dy + dz * dz <= eps_sq:
                    shared[i] = True
                    shared[j] = True
        for i, point in enumerate(points):
            if shared[i]:
                continue
            if cls._point_touches_any_segment_interior(point, lines, eps_sq):
                shared[i] = True
        free: list[tuple[float, float, float]] = []
        connection: list[tuple[float, float, float]] = []
        seen_connection: list[tuple[float, float, float]] = []
        for i, point in enumerate(points):
            if not shared[i]:
                free.append(point)
                continue
            for existing in seen_connection:
                dx, dy, dz = point[0] - existing[0], point[1] - existing[1], point[2] - existing[2]
                if dx * dx + dy * dy + dz * dz <= eps_sq:
                    break
            else:
                seen_connection.append(point)
                connection.append(point)
        return free, connection

    @staticmethod
    def _point_touches_any_segment_interior(
        point: tuple[float, float, float],
        lines: Sequence[tuple[tuple[float, float, float], tuple[float, float, float]]],
        eps_sq: float,
    ) -> bool:
        """True iff ``point`` lies within ``sqrt(eps_sq)`` of the interior of
        any segment in ``lines``. Endpoints are excluded so a point cannot
        match its own owning segment via either of that segment's tips — the
        endpoint-coincidence pass already handles those cases. The qualifying
        projection must land strictly inside the segment (``0 < t < 1``) AND
        sit further than ``eps`` from either tip, catching ATPATH/T-junction
        joins without false-flagging walls that share a corner."""
        px, py, pz = point
        for (ax, ay, az), (bx, by, bz) in lines:
            dxa, dya, dza = px - ax, py - ay, pz - az
            if dxa * dxa + dya * dya + dza * dza <= eps_sq:
                continue
            dxb, dyb, dzb = px - bx, py - by, pz - bz
            if dxb * dxb + dyb * dyb + dzb * dzb <= eps_sq:
                continue
            ex, ey, ez = bx - ax, by - ay, bz - az
            seg_len_sq = ex * ex + ey * ey + ez * ez
            if seg_len_sq <= eps_sq:
                continue
            t = (dxa * ex + dya * ey + dza * ez) / seg_len_sq
            if t <= 0.0 or t >= 1.0:
                continue
            qx, qy, qz = ax + t * ex, ay + t * ey, az + t * ez
            dx, dy, dz = px - qx, py - qy, pz - qz
            if dx * dx + dy * dy + dz * dz <= eps_sq:
                return True
        return False

    def draw(self, context: bpy.types.Context) -> None:
        model_props = tool.Model.get_model_props()
        if not getattr(model_props, "show_paths", False):
            return
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return

        start_element = None
        active = context.active_object
        if active is not None:
            element = tool.Ifc.get_entity(active)
            if element is not None and self._is_seed_element(element):
                start_element = element
        if start_element is None:
            for obj in context.selected_objects or []:
                if obj is active:
                    continue
                element = tool.Ifc.get_entity(obj)
                if element is None or not self._is_seed_element(element):
                    continue
                start_element = element
                break
        if start_element is None:
            self._cached_start_guid = None
            self._cached_walk = []
            return

        start_guid = start_element.GlobalId
        if start_guid == self._failed_seed_guid:
            return
        current_geom_gen = tool.Parametric.get_geom_generation()
        connected: list[Any] | None = None
        if (
            start_guid == self._cached_start_guid
            and ifc_file is self._cached_ifc_file
            and current_geom_gen == self._cached_geom_gen
            and self._cached_walk_ids
        ):
            try:
                connected = [ifc_file.by_id(eid) for eid in self._cached_walk_ids]
            except RuntimeError:
                # An entity was removed without bumping geom_gen — rare but
                # possible from non-operator code paths. Force a re-walk
                # rather than feeding a stale handle to _build_geometry.
                connected = None
        if connected is None:
            try:
                connected = self._walk(start_element)
            except Exception:
                if not self._walk_failure_logged:
                    import traceback

                    traceback.print_exc()
                    self._walk_failure_logged = True
                self._cached_walk_ids = []
                self._failed_seed_guid = start_guid
                return
            self._cached_start_guid = start_guid
            self._cached_ifc_file = ifc_file
            self._cached_geom_gen = current_geom_gen
            self._cached_walk_ids = [e.id() for e in connected]
        if not connected:
            return

        prefs = tool.Blender.get_addon_preferences()
        line_color = tuple(prefs.decorator_color_selected[:3])
        # Junction dots get the "selected" palette slot (green by default) so
        # they read as the currently-inspected network's spine; free endpoints
        # get the "special" slot (blue by default) so dangling line ends stand
        # apart from junctions at a glance.
        connection_color = line_color
        free_color = tuple(prefs.decorator_color_special[:3])

        try:
            lines, free_points, connection_points = self._geom_cache.get_or_compute(
                (start_guid, id(ifc_file), current_geom_gen),
                lambda: self._build_geometry(connected),
            )
        except Exception:
            if not self._build_failure_logged:
                import traceback

                traceback.print_exc()
                self._build_failure_logged = True
            self._failed_seed_guid = start_guid
            return

        if lines:
            _stroke_lines_alpha(context, lines, line_color, self.LINE_WIDTH, self.LINE_ALPHA)

        if free_points or connection_points:
            # POINTS via UNIFORM_COLOR; point_size_set only affects the next batch.
            point_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
            point_shader.bind()
            gpu.state.point_size_set(self.DOT_SIZE)
            gpu.state.blend_set("ALPHA")
            if free_points:
                point_shader.uniform_float("color", (*free_color, self.LINE_ALPHA))
                batch = batch_for_shader(point_shader, "POINTS", {"pos": free_points})
                batch.draw(point_shader)
            if connection_points:
                point_shader.uniform_float("color", (*connection_color, self.LINE_ALPHA))
                batch = batch_for_shader(point_shader, "POINTS", {"pos": connection_points})
                batch.draw(point_shader)
            gpu.state.blend_set("NONE")


class MEPSystemPathDecorator(_ConnectedNetworkPathDecorator):
    """Schematic-path overlay for the selected MEP element's connected
    distribution system.

    Walk: BFS through ``IfcRelConnectsPorts`` from the first selected MEP
    element. Segments render as one axis line + endpoint dots. Fittings
    render as:

    - 2-port (transition, coupler, bend): one line port-to-port, keeping
      the schematic continuous through the fitting. The "spider from
      origin" pattern produces V-shaped flares when the fitting's local
      origin is offset from its ports.
    - 3+-port (tee, cross, branching): spider from origin to each port.
      Drawing all N*(N-1)/2 port pairs would clutter the view at high N
      (N=4 → 6 lines); the spider gives one line per port.
    - 0-port / 1-port: degenerate, no lines (dots still emit)."""

    def _is_seed_element(self, element: Any) -> bool:
        return tool.System.is_mep_element(element)

    def _walk(self, start_element: Any) -> list[Any]:
        return tool.System.walk_connected_mep_elements(start_element)

    def _build_geometry(
        self,
        connected: list[Any],
    ) -> tuple[
        list[tuple[tuple[float, float, float], tuple[float, float, float]]],
        list[tuple[float, float, float]],
        list[tuple[float, float, float]],
    ]:
        lines: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        port_positions: list[tuple[float, float, float]] = []
        for element in connected:
            if element and element.is_a("IfcFlowSegment"):
                if not tool.Geometry.has_axis_representation(element):
                    continue
                obj = tool.Ifc.get_object(element)
                if obj is None:
                    continue
                start_world, end_world = tool.Model.get_flow_segment_axis(obj)
                lines.append((tuple(start_world), tuple(end_world)))
                # Segment ports sit at the two axis endpoints — emit dots so
                # the connection node is visible whether the neighbour is a
                # fitting (also emits) or another segment (doesn't).
                port_positions.append(tuple(start_world))
                port_positions.append(tuple(end_world))
            elif element.is_a("IfcFlowFitting"):
                obj = tool.Ifc.get_object(element)
                if obj is None:
                    continue
                ports = tool.System.get_ports(element)
                port_world_positions = [tool.System.get_port_world_position(p) for p in ports]
                if len(port_world_positions) == 2:
                    lines.append((tuple(port_world_positions[0]), tuple(port_world_positions[1])))
                elif len(port_world_positions) >= 3:
                    origin = obj.matrix_world.translation
                    for port_pos in port_world_positions:
                        lines.append((tuple(origin), tuple(port_pos)))
                for port_pos in port_world_positions:
                    port_positions.append(tuple(port_pos))
        free_points, connection_points = self._partition_points_by_coincidence(port_positions)
        return lines, free_points, connection_points


class WallSystemPathDecorator(_ConnectedNetworkPathDecorator):
    """Schematic-path overlay for the selected wall's connected wall network.

    Walk: BFS through ``IfcRelConnectsPathElements`` from the first selected
    wall. Each wall renders as one reference-line segment + a dot at each
    axis endpoint. Endpoints are classified by IFC topology — every wall in
    the walked set inspects its ``IfcRelConnectsPathElements`` rels filtered
    to walls in the same set, and uses ``Relating*``/``Related*ConnectionType``
    (ATSTART / ATEND / ATPATH) to decide which endpoint participates. ATPATH
    rels also emit a connection dot at the canonical join location (a T-meets
    point sits on the through-wall's interior, not at any endpoint). The
    framework's geometric classifier is bypassed for walls because authoring
    tolerance and post-edit float drift commonly exceed the 0.1 mm coincidence
    threshold, so T-junctions otherwise fell into the free bucket."""

    def _is_seed_element(self, element: Any) -> bool:
        return element.is_a("IfcWall") and tool.Geometry.has_axis_representation(element)

    def _walk(self, start_element: Any) -> list[Any]:
        return tool.Wall.walk_connected_walls(start_element)

    def _build_geometry(
        self,
        connected: list[Any],
    ) -> tuple[
        list[tuple[tuple[float, float, float], tuple[float, float, float]]],
        list[tuple[float, float, float]],
        list[tuple[float, float, float]],
    ]:
        lines: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        refs: dict[int, tuple[tuple[float, float, float], tuple[float, float, float]]] = {}
        for element in connected:
            obj = tool.Ifc.get_object(element)
            if obj is None:
                continue
            ref = tool.Wall.get_world_reference_line(obj)
            if ref is None:
                continue
            p1, p2 = tuple(ref[0]), tuple(ref[1])
            refs[element.id()] = (p1, p2)
            lines.append((p1, p2))

        free_points, connection_points = self._classify_endpoints_from_rels(connected, refs)
        connection_points = self._dedupe_close_points(connection_points, self.CONNECTION_EPS_SQ)
        return lines, free_points, connection_points

    @staticmethod
    def _classify_endpoints_from_rels(
        connected: Sequence[Any],
        refs: dict[int, tuple[tuple[float, float, float], tuple[float, float, float]]],
    ) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
        """For each wall in ``connected`` with a reference line in ``refs``,
        classify its endpoints by walking its ``IfcRelConnectsPathElements``
        rels filtered to walls also in ``refs``. ATSTART side present →
        reference-line start is a connection; ATEND side present → reference-
        line end is a connection; otherwise free. ATPATH side present → emit
        an extra connection dot at the canonical join via
        ``tool.Wall.path_connection_location_world``. Returns
        ``(free, connection)`` un-deduped."""
        free_points: list[tuple[float, float, float]] = []
        connection_points: list[tuple[float, float, float]] = []
        for element in connected:
            self_seg = refs.get(element.id())
            if self_seg is None:
                continue
            sides: set[str] = set()
            atpath_dots: list[tuple[float, float, float]] = []
            for rel in getattr(element, "ConnectedTo", []) or ():
                if not rel.is_a("IfcRelConnectsPathElements"):
                    continue
                other = rel.RelatedElement
                other_seg = refs.get(other.id()) if other is not None else None
                if other_seg is None:
                    continue
                self_type = rel.RelatingConnectionType
                other_type = rel.RelatedConnectionType
                sides.add(self_type)
                if self_type == "ATPATH":
                    join = tool.Wall.path_connection_location_world(self_seg, self_type, other_seg, other_type)
                    atpath_dots.append(tuple(join))
            for rel in getattr(element, "ConnectedFrom", []) or ():
                if not rel.is_a("IfcRelConnectsPathElements"):
                    continue
                other = rel.RelatingElement
                other_seg = refs.get(other.id()) if other is not None else None
                if other_seg is None:
                    continue
                self_type = rel.RelatedConnectionType
                other_type = rel.RelatingConnectionType
                sides.add(self_type)
                if self_type == "ATPATH":
                    join = tool.Wall.path_connection_location_world(self_seg, self_type, other_seg, other_type)
                    atpath_dots.append(tuple(join))
            p1, p2 = self_seg
            (connection_points if "ATSTART" in sides else free_points).append(p1)
            (connection_points if "ATEND" in sides else free_points).append(p2)
            connection_points.extend(atpath_dots)
        return free_points, connection_points

    @staticmethod
    def _dedupe_close_points(
        points: Sequence[tuple[float, float, float]],
        eps_sq: float,
    ) -> list[tuple[float, float, float]]:
        """Drop later occurrences of points within ``sqrt(eps_sq)`` of an
        earlier one. Used to collapse overlapping connection dots so an ATPATH
        join computed at the same point as a neighbour's wall endpoint
        renders once."""
        result: list[tuple[float, float, float]] = []
        for point in points:
            for existing in result:
                dx, dy, dz = point[0] - existing[0], point[1] - existing[1], point[2] - existing[2]
                if dx * dx + dy * dy + dz * dz <= eps_sq:
                    break
            else:
                result.append(point)
        return result
