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
from math import sin, cos, tan, radians
from bpy.types import SpaceView3D
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix, Quaternion
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
from typing import Union
from bonsai.bim.module.drawing.helper import format_distance
from bonsai.bim.module.geometry.decorator import ItemDecorator


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

        self.draw_batch("LINES", all_vertices, transparent_color(unselected_elements_color), unselected_edges)
        self.draw_batch("LINES", all_vertices, selected_elements_color, selected_edges)
        self.draw_batch("LINES", all_vertices, background_elements_color, arc_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, preview_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, roof_angle_edges)

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
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_snap_point, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_measurements, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_input_ui, (context,), "WINDOW", "POST_PIXEL"))
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

    def calculate_polygon(self, points):
        bm = bmesh.new()

        new_verts = [bm.verts.new(v) for v in points]
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(points) - 1)]

        bm.verts.index_update()
        bm.edges.index_update()

        new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)

        bm.verts.index_update()
        bm.edges.index_update()
        verts = bm.verts
        edges = bm.edges
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

        bm.free()

        return {"verts": verts, "edges": edges, "tris": tris}

    def draw_batch(self, shader_type, content_pos, color, indices=None):
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
        new_line = 20
        for i, (key, field_name) in enumerate(texts.items()):

            formatted_value = None
            if self.input_ui:
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
            blf.position(self.font_id, mouse_pos[0] + offset, mouse_pos[1] - (new_line * i), 0)
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
        if measure_type == "AREA" and polyline_data.area:
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
        if measure_type in {"POLYLINE", "AREA"}:
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
        self.line_shader.uniform_float("lineWidth", 1.0)
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
        padding = 6
        verts = []
        edges = []
        if snap_prop.snap_type in ["Edge", "Vertex"]:
            p1 = (coords[0] - padding, coords[1] + padding)
            p2 = (coords[0] + padding, coords[1] + padding)
            p3 = (coords[0] + padding, coords[1] - padding)
            p4 = (coords[0] - padding, coords[1] - padding)
            verts = [p1, p2, p3, p4]
            if snap_prop.snap_type == "Edge":
                edges = [[0, 1], [1, 3], [3, 2], [2, 0]]
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
        default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
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
            if area:
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

    def get_wall_preview_data(cls, context, relating_type):
        def create_bmesh_from_vertices(vertices):
            bm = bmesh.new()

            new_verts = [bm.verts.new(v) for v in polyline_vertices]
            if is_closed:
                new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
                new_edges.append(
                    bm.edges.new((new_verts[-1], new_verts[0]))
                )  # Add an edge between the last an first point to make it closed.
            else:
                new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]

            bm.verts.index_update()
            bm.edges.index_update()
            return bm

        # Get properties from object type
        layers = tool.Model.get_material_layer_parameters(relating_type)
        if not layers["thickness"]:
            return
        thickness = layers["thickness"]
        model_props = context.scene.BIMModelProperties
        direction_sense = model_props.direction_sense
        direction = 1
        if direction_sense == "NEGATIVE":
            direction = -1
        offset_type = model_props.offset_type
        offset = 0
        if offset_type == "CENTER":
            offset = -thickness / 2
        elif offset_type == "INTERIOR":
            offset = -thickness

        unit_system = tool.Drawing.get_unit_system()
        factor = 1
        if unit_system == "IMPERIAL":
            factor = 3.048
        if unit_system == "METRIC":
            unit_length = context.scene.unit_settings.length_unit
            if unit_length == "MILLIMETERS":
                factor = 1000

        # For the model properties, the offset value should just be converted
        # However, for the wall preview logic that follows, offset and thickness must change direction
        model_props.offset = offset * factor
        thickness *= direction
        offset *= direction

        height = float(model_props.extrusion_depth)
        rl = float(model_props.rl1)
        x_angle = float(model_props.x_angle)
        angle_distortion = height * tan(x_angle)

        wall_preview_data = {}
        wall_preview_data["verts"] = []

        # Verts
        polyline_vertices = []
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        if len(polyline_points) < 2:
            wall_preview_data = []
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

        bm_base = create_bmesh_from_vertices(polyline_vertices)
        base_vertices = tool.Cad.offset_edges(bm_base, offset)
        offset_base_verts = tool.Cad.offset_edges(bm_base, thickness + offset)
        top_vertices = tool.Cad.offset_edges(bm_base, angle_distortion + offset)
        offset_top_verts = tool.Cad.offset_edges(bm_base, angle_distortion + thickness + offset)
        if is_closed:
            base_vertices.append(base_vertices[0])
            offset_base_verts.append(offset_base_verts[0])
            top_vertices.append(top_vertices[0])
            offset_top_verts.append(offset_top_verts[0])

        if offset_base_verts is not None:
            for v in base_vertices:
                wall_preview_data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

            for v in offset_base_verts[::-1]:
                wall_preview_data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

            for v in top_vertices:
                wall_preview_data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

            for v in offset_top_verts[::-1]:
                wall_preview_data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

        bm_base.free()

        # Edges and Tris
        points = []
        side_edges_1 = []
        side_edges_2 = []
        base_edges = []

        for i in range(len(wall_preview_data["verts"])):
            points.append(Vector(wall_preview_data["verts"][i]))

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

        wall_preview_data["edges"] = []
        wall_preview_data["tris"] = []
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
            wall_preview_data["edges"].extend(edges)
            wall_preview_data["tris"].extend(tris)

        wall_preview_data["edges"] = list(set(tuple(e) for e in wall_preview_data["edges"]))
        wall_preview_data["tris"] = list(set(tuple(t) for t in wall_preview_data["tris"]))

        return wall_preview_data

    def get_product_preview_data(cls, context, relating_type):
        model_props = context.scene.BIMModelProperties
        if relating_type.is_a("IfcDoorType"):
            rl = float(model_props.rl1)
        elif relating_type.is_a("IfcWindowType"):
            rl = float(model_props.rl2)
        else:
            rl = 0
        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
        snap_obj = bpy.data.objects.get(snap_prop.snap_object)
        snap_element = tool.Ifc.get_entity(snap_obj)
        rot_mat = Quaternion()
        if snap_element and snap_element.is_a("IfcWall"):
            rot_mat = snap_obj.matrix_world.to_quaternion()

        obj_type = tool.Ifc.get_object(relating_type)
        if obj_type.data:
            data = ItemDecorator.get_obj_data(obj_type)
            data["verts"] = [tuple(obj_type.matrix_world.inverted() @ Vector(v)) for v in data["verts"]]
            data["verts"] = [tuple(rot_mat @ (Vector((v[0], v[1], (v[2] + rl)))) + mouse_point) for v in data["verts"]]
            return data

    def get_profile_preview_data(self, context, relating_type):
        material = ifcopenshell.util.element.get_material(relating_type)
        try:
            profile = material.MaterialProfiles[0].Profile
        except:
            return {}

        model_props = context.scene.BIMModelProperties
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
            raise RuntimeError("Profile shape has no vertices, it probably is invalid.")

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

        new_verts = [bm.verts.new(v) for v in grouped_verts]
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(grouped_verts) - 1)]

        bm.verts.index_update()
        bm.edges.index_update()

        new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)

        new_faces = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
        new_verts = [e for e in new_faces["geom"] if isinstance(e, bmesh.types.BMVert)]
        new_faces = bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, extrusion_depth))

        bm.verts.index_update()
        bm.edges.index_update()
        tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

        # Create bounding box
        verts = bm.verts
        i = len(verts)

        min_x = min(v.co.x for v in verts)
        max_x = max(v.co.x for v in verts)
        min_y = min(v.co.y for v in verts)
        max_y = max(v.co.y for v in verts)
        min_z = min(v.co.z for v in verts)
        max_z = max(v.co.z for v in verts)

        bbox_verts = [
            (min_x, min_y, min_z),
            (max_x, min_y, min_z),
            (max_x, max_y, min_z),
            (min_x, max_y, min_z),
            (min_x, min_y, max_z),
            (max_x, min_y, max_z),
            (max_x, max_y, max_z),
            (min_x, max_y, max_z),
        ]

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

        # Calculate rotation, mouse position, angle and cardinal point
        # TODO Angle
        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
        data = {}

        verts = [tuple(v.co) for v in verts]
        verts.extend(bbox_verts)
        verts = [tuple(rot_mat @ Vector(v)) for v in verts]
        verts = [tuple(Vector(v) + mouse_point) for v in verts]
        data["verts"] = verts
        data["edges"] = bbox_edges
        # data["edges"] = [(edge.verts[0].index, edge.verts[1].index) for edge in bm.edges]
        data["tris"] = tris

        bm.free()
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
        props = context.scene.BIMModelProperties
        relating_type_id = props.relating_type_id
        if relating_type_id:
            self.relating_type = tool.Ifc.get().by_id(int(relating_type_id))
        else:
            return

        # Wall
        if self.relating_type.is_a("IfcWallType"):
            wall_preview_data = self.get_wall_preview_data(context, self.relating_type)
            if wall_preview_data:
                self.draw_batch("LINES", wall_preview_data["verts"], decorator_color, wall_preview_data["edges"])
                self.draw_batch(
                    "TRIS", wall_preview_data["verts"], transparent_color(decorator_color), wall_preview_data["tris"]
                )

        # Mesh type products
        product_preview_data = self.get_product_preview_data(context, self.relating_type)
        if product_preview_data:
            self.draw_batch("LINES", product_preview_data["verts"], decorator_color, product_preview_data["edges"])
            self.draw_batch(
                "TRIS", product_preview_data["verts"], transparent_color(decorator_color), product_preview_data["tris"]
            )

        # Profile type products
        product_preview_data = self.get_profile_preview_data(context, self.relating_type)
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
                verts = [tuple(list(v) + [0.0]) for v in axis["reference"]]
                self.draw_batch("LINES", verts, selected_elements_color, [(0, 1)])
                verts = [tuple(list(v) + [0.0]) for v in axis["side"]]
                self.draw_batch("LINES", verts, unselected_elements_color, [(0, 1)])
