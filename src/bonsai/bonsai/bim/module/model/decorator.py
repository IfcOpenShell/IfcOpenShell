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

import blf
import gpu
import gpu_extras
import bmesh
import bonsai.tool as tool
from math import sin, cos, radians, degrees, atan2, acos
from bpy.types import SpaceView3D
import math
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
from typing import Union
from bonsai.bim.module.drawing.helper import format_distance


def transparent_color(color, alpha=0.1):
    color = [i for i in color]
    color[3] = alpha
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
                is_arc, group_index = tool.Blender.bmesh_check_vertex_in_groups(vertex, deform_layer, arc_groups)
                if is_arc:
                    arcs.setdefault(group_index, []).append(vertex)
                    special_vertex_indices[vertex.index] = group_index

                is_circle, group_index = tool.Blender.bmesh_check_vertex_in_groups(vertex, deform_layer, circle_groups)
                if is_circle:
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

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_snap_point, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_measurements, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_input_ui, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_product_preview, (context,), "WINDOW", "POST_VIEW")
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

    # @classmethod
    # def set_axis_rectangle(cls, corners):
    #     cls.axis_rectangle = [*corners]

    @classmethod
    def set_tool_state(cls, tool_state):
        cls.tool_state = tool_state

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_product_preview(self, context):
        decorator_color = self.addon_prefs.decorations_colour
        polyline = context.scene.BIMPolylineProperties.polyline_point
        prop = context.scene.BIMPolylineProperties.product_preview
        points = []
        edges = []
        for i in range(len(prop)):
            points.append(Vector((prop[i].x, prop[i].y, prop[i].z)))
        n = len(points) // 2
        bottom_loop = [[i, (i + 1) % (n)] for i in range(n)]
        edges.extend(bottom_loop)
        upper_loop = [[i + n for i in edges] for edges in bottom_loop]
        edges.extend(upper_loop)
        connections = [[i, j] for i, j in zip(range(n), range(n, n * 2))]
        edges.extend(connections)

        self.line_shader.uniform_float("lineWidth", 0.5)
        if len(points) > 1:
            self.draw_batch("LINES", points, decorator_color, edges)

    def draw_input_ui(self, context):
        texts = {
            "D": "Distance: ",
            "A": "Angle: ",
            "X": "X coord: ",
            "Y": "Y coord: ",
            "Z": "Z coord:",
            "AREA": "Area: ",
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
        measurement_prop = context.scene.BIMPolylineProperties.polyline_measurement

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 1
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        font_size = tool.Blender.scale_font_size(12)
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour

        blf.color(self.font_id, *color)
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

        coords = view3d_utils.location_3d_to_region_2d(region, rv3d, mouse_point)
        padding = 6
        verts = []
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
        gpu.state.point_size_set(10)

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        # Point related to the mouse
        mouse_point = [Vector((snap_prop.x, snap_prop.y, snap_prop.z))]

        try:
            snap_ref = context.scene.BIMPolylineProperties.snap_mouse_ref[0]
            ref_point = [Vector((snap_ref.x, snap_ref.y, snap_ref.z))]
        except:
            ref_point = None

        default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
        projection_point = []
        if self.tool_state and self.tool_state.use_default_container:
            # When a point is above the plane it projects the point
            # to the plane and creates a line
            if snap_prop.snap_type != "Plane" and snap_prop.z != 0:
                self.line_shader.uniform_float("lineWidth", 1.0)
                projection_point = [Vector((snap_prop.x, snap_prop.y, default_container_elevation))]
                self.draw_batch("POINTS", projection_point, decorator_color_unselected)
                edges = [[0, 1]]
                self.draw_batch("LINES", mouse_point + projection_point, (1.0, 0.6, 0.0, 1.0), edges)

        # Create polyline with selected points
        polyline_data = context.scene.BIMPolylineProperties.polyline_point
        polyline_points = []
        polyline_edges = []
        for point_prop in polyline_data:
            point = Vector((point_prop.x, point_prop.y, point_prop.z))
            polyline_points.append(point)

        for i in range(len(polyline_points) - 1):
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

        # try:
        #     self.draw_batch("TRIS", self.axis_rectangle, (1, 1, 1, 0.1), [(0, 1, 3), (0, 2, 3)])
        # except:
        #     pass

        # Area highlight
        # if "AREA" in list(self.input_panel.keys()): # TODO Change to input_ui
        #     if self.input_panel["AREA"] and float(self.input_panel["AREA"]) > 0: # TODO Change to input_ui
        #         edges = []
        #         for i in range(1, len(polyline_points) - 1):
        #             edges.append((0, i, i + 1))
        #         self.draw_batch("TRIS", polyline_points, (0, 1, 0, 0.1), edges)

        # Mouse points
        if snap_prop.snap_type in ["Plane"]:
            self.draw_batch("POINTS", mouse_point, decorator_color)

        if ref_point:
            self.draw_batch("POINTS", ref_point, decorator_color_object_active)

        # Line between last polyline point and mouse
        edges = [[0, 1]]
        if polyline_points:
            if snap_prop.snap_type != "Plane" and projection_point:
                self.draw_batch("LINES", [polyline_points[-1]] + projection_point, decorator_color, edges)
            else:
                self.draw_batch("LINES", [polyline_points[-1]] + mouse_point, decorator_color, edges)

        # Draw polyline with selected points
        self.line_shader.uniform_float("lineWidth", 2.0)
        self.draw_batch("POINTS", polyline_points, decorator_color_special)
        if len(polyline_points) > 1:
            self.draw_batch("LINES", polyline_points, decorator_color_special, polyline_edges)
