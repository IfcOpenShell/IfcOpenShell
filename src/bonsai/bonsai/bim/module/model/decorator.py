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

import bpy
import blf
import bpy
import gpu
import gpu_extras
import bmesh
import ifcopenshell
import bonsai.tool as tool
import math
from math import sin, cos, radians
from bpy.types import SpaceView3D
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
from typing import Union
from bonsai.bim.module.drawing.helper import format_distance
from itertools import chain


def transparent_color(color, alpha=0.1):
    color = [i for i in color]
    color[3] = alpha
    return color


def highlight_color(color, alpha=0.1):
    color = [i + (1 - i) * 0.5 for i in color]
    return color


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
        """mutates original bm (triangulates it)
        so the triangulation edges will be shown too
        """
        traingulated_bm = bm
        bmesh.ops.triangulate(traingulated_bm, faces=traingulated_bm.faces)

        face_indices = [[v.index for v in f.verts] for f in traingulated_bm.faces]
        faces_color = transparent_color(self.addon_prefs.decorator_color_special)
        self.draw_batch("TRIS", vertices_coords, faces_color, face_indices)

    def __call__(self, context, get_custom_bmesh=None, draw_faces=False, exit_edit_mode_callback=None):
        self.addon_prefs = tool.Blender.get_addon_preferences()
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special
        error_elements_color = self.addon_prefs.decorator_color_error
        background_elements_color = self.addon_prefs.decorator_color_background

        obj = context.active_object

        if obj.mode != "EDIT":
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

        self.draw_batch("POINTS", unselected_vertices, transparent_color(unselected_elements_color, 0.5))
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


class PolylineDecorator:
    is_installed = False
    handlers = []
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
                SpaceView3D.draw_handler_add(handler.draw_measurements, (context,), "WINDOW", "POST_PIXEL")
            )
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

    @classmethod
    def update(cls, event, tool_state, input_ui, snapping_point):
        cls.event = event
        cls.tool_state = tool_state
        cls.input_ui = input_ui

    @classmethod
    def set_input_ui(cls, input_ui):
        cls.input_ui = input_ui

    @classmethod
    def set_angle_axis_line(cls, start, end):
        cls.axis_start = start
        cls.axis_end = end

    def calculate_measurement_x_y_and_z(self, context):
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []

        if len(polyline_points) == 0 or len(polyline_points) > 2:
            return None, None

        start = polyline_points[0]
        if len(polyline_points) == 1:
            end = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        else:
            end = polyline_points[1]

        x_axis = (Vector((start.x, start.y, start.z)), Vector((end.x, start.y, start.z)))
        y_axis = (Vector((end.x, start.y, start.z)), Vector((end.x, end.y, start.z)))
        z_axis = (Vector((end.x, end.y, start.z)), Vector((end.x, end.y, end.z)))
        x_middle = (x_axis[1] + x_axis[0]) / 2
        y_middle = (y_axis[1] + y_axis[0]) / 2
        z_middle = (z_axis[1] + z_axis[0]) / 2

        return (x_axis, y_axis, z_axis), (x_middle, y_middle, z_middle)

    @classmethod
    def calculate_polygon(self, points):
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

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_input_ui(self, context):
        texts = {
            "D": "Distance: ",
            "A": "Angle: ",
            "X": "X coord: ",
            "Y": "Y coord: ",
            "Z": "Z coord:",
            "AREA": "Area:",
        }
        try:
            mouse_pos = self.event.mouse_region_x, self.event.mouse_region_y
        except:
            mouse_pos = (None, None)

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 0
        font_size = tool.Blender.scale_font_size(12)
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour
        color_highlight = self.addon_prefs.decorator_color_special
        offset = 20
        new_line = 0
        for i, (key, field_name) in enumerate(texts.items()):
            formatted_value = None
            if self.input_ui:
                # Controls which options are displayed in the UI
                if key not in self.input_ui.input_options:
                    continue
                new_line += 20
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

    def draw_measurements(self, context):
        region = context.region
        rv3d = region.data
        measure_type = context.scene.MeasureToolSettings.measurement_type
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        if not polyline_data:
            return
        else:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
        polyline_points = polyline_data.polyline_points

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 1
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        font_size = tool.Blender.scale_font_size(12)
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour

        blf.color(self.font_id, *color)
        for i in range(len(polyline_points)):
            if i == 0:
                continue
            dim_text_pos = (Vector(polyline_points[i].position) + Vector(polyline_points[i - 1].position)) / 2
            dim_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, dim_text_pos)

            formatted_value = polyline_points[i].dim

            blf.position(self.font_id, dim_text_coords[0], dim_text_coords[1], 0)
            text = "d: " + formatted_value
            text_length = blf.dimensions(self.font_id, text)
            self.draw_text_background(context, dim_text_coords, text_length)
            blf.draw(self.font_id, text)

            if i == 1:
                continue
            angle_text_pos = Vector(polyline_points[i - 1].position)
            angle_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, angle_text_pos)
            blf.position(self.font_id, angle_text_coords[0], angle_text_coords[1], 0)
            text = "a: " + polyline_points[i].angle
            text_length = blf.dimensions(self.font_id, text)
            self.draw_text_background(context, angle_text_coords, text_length)
            blf.draw(self.font_id, text)

        if measure_type == "SINGLE":
            axis_line, axis_line_center = self.calculate_measurement_x_y_and_z(context)
            for i, dim_text_pos in enumerate(axis_line_center):
                dim_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, dim_text_pos)
                blf.position(self.font_id, dim_text_coords[0], dim_text_coords[1], 0)
                value = round((axis_line[i][1] - axis_line[i][0]).length, 4)
                direction = axis_line[i][1] - axis_line[i][0]
                if (i == 0 and direction.x < 0) or (i == 1 and direction.y < 0) or (i == 2 and direction.z < 0):
                    value = -value
                prefix = "xyz"[i]
                formatted_value = tool.Polyline.format_input_ui_units(value)
                text = f"{prefix}: {formatted_value}"
                text_length = blf.dimensions(self.font_id, text)
                self.draw_text_background(context, dim_text_coords, text_length)
                blf.draw(self.font_id, text)

        # Area and Length text
        polyline_verts = [Vector((p.x, p.y, p.z)) for p in polyline_points]

        # Area
        if measure_type == "POLY_AREA" and polyline_data.area:
            if len(polyline_verts) < 3:
                return
            center = sum(polyline_verts, Vector()) / len(polyline_verts)  # Center between all polyline points
            if polyline_verts[0] == polyline_verts[-1]:
                center = sum(polyline_verts[:-1], Vector()) / len(
                    polyline_verts[:-1]
                )  # Doesn't use the last point if is a closed polyline
            area_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, center)
            value = polyline_data.area
            text = f"area: {value}"
            text_length = blf.dimensions(self.font_id, text)
            area_text_coords[0] -= text_length[0] / 2  # Center text horizontally
            blf.position(self.font_id, area_text_coords[0], area_text_coords[1], 0)
            self.draw_text_background(context, area_text_coords, text_length)
            blf.draw(self.font_id, text)

        # Length
        if measure_type in {"POLYLINE", "POLY_AREA"}:
            if len(polyline_verts) < 3:
                return
            total_length_text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, polyline_verts[-1])
            blf.position(self.font_id, total_length_text_coords[0], total_length_text_coords[1], 0)
            value = polyline_data.total_length
            text = f"length: {value}"
            text_length = blf.dimensions(self.font_id, text)
            self.draw_text_background(context, total_length_text_coords, text_length)
            blf.draw(self.font_id, text)

        blf.disable(self.font_id, blf.SHADOW)

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

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        try:
            snap_prop = context.scene.BIMPolylineProperties.snap_mouse_ref[0]
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

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
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
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        if polyline_data:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
            polyline_points = polyline_data.polyline_points
        else:
            polyline_points = []
        polyline_verts = []
        polyline_edges = []
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

        # Lines for X, Y, Z of single measure
        if polyline_data and polyline_data.measurement_type == "SINGLE":
            axis, _ = self.calculate_measurement_x_y_and_z(context)
            x_axis, y_axis, z_axis = axis
            self.draw_batch("LINES", [*x_axis], decorator_color_x_axis, [(0, 1)])
            self.draw_batch("LINES", [*y_axis], decorator_color_y_axis, [(0, 1)])
            self.draw_batch("LINES", [*z_axis], decorator_color_z_axis, [(0, 1)])

        # Area highlight
        if polyline_data:
            area = polyline_data.area.split(" ")[0]
            if polyline_data.measurement_type == "POLY_AREA" and area:
                if float(area) > 0:
                    tris = self.calculate_polygon(polyline_verts)["tris"]
                    self.draw_batch("TRIS", polyline_verts, transparent_color(decorator_color_special), tris)

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


class ProductDecorator:
    is_installed = False
    handlers = []
    relating_type = None

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_product_preview, (context,), "WINDOW", "POST_VIEW")
        )
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        props = bpy.context.scene.BIMProductPreviewProperties  # updated by model/polyline.py
        props.verts.clear()
        props.edges.clear()
        props.tris.clear()
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def get_product_preview_data(self, context):
        props = context.scene.BIMProductPreviewProperties
        data = {}
        data["verts"] = [(*v.value_3d,) for v in props.verts]
        data["edges"] = [(int(e.value_2d[0]), int(e.value_2d[1])) for e in props.edges]
        data["tris"] = [(int(t.value_3d[0]), int(t.value_3d[1]), int(t.value_3d[2])) for t in props.tris]
        return data

    def draw_product_preview(self, context):
        def transparent_color(color, alpha=0.1):
            color = [i for i in color]
            color[3] = alpha
            return color

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        decorator_color = self.addon_prefs.decorator_color_special
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []

        self.relating_type = None
        props = tool.Model.get_model_props()
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        else:
            return

        product_preview_data = self.get_product_preview_data(context)
        if product_preview_data:
            self.draw_batch("LINES", product_preview_data["verts"], decorator_color, product_preview_data["edges"])
            self.draw_batch(
                "TRIS", product_preview_data["verts"], transparent_color(decorator_color), product_preview_data["tris"]
            )


class WallAxisDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_wall_axis, (context,), "WINDOW", "POST_VIEW"))
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
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

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
            if element.is_a("IfcWall"):
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


class SlabDirectionDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_wall_axis, (context,), "WINDOW", "POST_VIEW"))
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
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

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


class FaceAreaDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_face_area, (context,), "WINDOW", "POST_VIEW"))
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
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_face_area(self, context):
        def transparent_color(color, alpha=0.1):
            color = [i for i in color]
            color[3] = alpha
            return color

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader.uniform_float("lineWidth", 2.0)
        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")
        decorator_color = self.addon_prefs.decorator_color_special

        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        for i, polyline in enumerate(polyline_data):
            vertices = []
            for point in polyline.polyline_points:
                vertices.append((point.x, point.y, point.z))
            data = PolylineDecorator.calculate_polygon(vertices)
            if data:
                self.draw_batch("POINTS", data["verts"], decorator_color)
                self.draw_batch("LINES", data["verts"], decorator_color, data["edges"])
                self.draw_batch("TRIS", data["verts"], transparent_color(decorator_color, alpha=0.5), data["tris"])
