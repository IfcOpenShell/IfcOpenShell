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
    mouse_pos = None
    input_panel = None
    input_type = None
    angle_snap_mat = None
    angle_snap_loc = None
    use_default_container = False
    instructions = None
    snap_info = None
 
    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_input_panel, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_on_screen_menu, (context,), "WINDOW", "POST_PIXEL"))
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

    @classmethod
    def set_mouse_position(cls, event):
        cls.mouse_pos = event.mouse_region_x, event.mouse_region_y

    @classmethod
    def set_input_panel(cls, input_panel, input_type):
        cls.input_panel = input_panel
        cls.input_type = input_type

    @classmethod
    def set_angle_axis_line(cls, start, end):
        cls.axis_start = start
        cls.axis_end = end

    @classmethod
    def set_axis_rectangle(cls, corners):
        cls.axis_rectangle = [*corners]

    @classmethod
    def set_use_default_container(cls, value=False):
        cls.use_default_container = value

    @classmethod
    def set_plane(cls, plane_origin, plane_normal):
        cls.plane_origin = plane_origin
        cls.plane_normal = plane_normal

    @classmethod
    def set_instructions(cls, instructions):
        cls.instructions = instructions

    @classmethod
    def set_snap_info(cls, snap_info):
        cls.snap_info = snap_info

    @classmethod
    def calculate_distance_and_angle(cls, context, is_input_on):

        try:
            polyline_data = context.scene.BIMModelProperties.polyline_point
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_data[len(polyline_data) - 1]
        except:
            last_point_data = None
            second_to_last_point_data = None
            default_container_elevation = 0

        snap_prop = context.scene.BIMModelProperties.snap_mouse_point[0]

        if last_point_data:
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        else:
            last_point = Vector((0, 0, 0))

        if is_input_on:
            snap_vector = Vector(
                (float(cls.input_panel["X"]), float(cls.input_panel["Y"]), default_container_elevation)
            )
        else:
            if cls.use_default_container:
                snap_vector = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
            else:
                snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        second_to_last_point = None
        if len(polyline_data) > 1:
            second_to_last_point_data = polyline_data[len(polyline_data) - 2]
            second_to_last_point = Vector(
                (second_to_last_point_data.x, second_to_last_point_data.y, second_to_last_point_data.z)
            )
        else:
            # Creates a fake "second to last" point away from the first point but in the same x axis
            # this allows to calculate the angle relative to x axis when there is only one point
            second_to_last_point = Vector((last_point.x - 1000, last_point.y, last_point.z))

        distance = (snap_vector - last_point).length
        if distance > 0:
            angle = tool.Cad.angle_3_vectors(snap_vector, last_point, second_to_last_point, degrees=True)
            if cls.input_panel:
                cls.input_panel["X"] = str(round(snap_vector.x, 4))
                cls.input_panel["Y"] = str(round(snap_vector.y, 4))
                if "Z" in list(cls.input_panel.keys()):
                    cls.input_panel["Z"] = str(round(snap_vector.z, 4))
                cls.input_panel["D"] = str(round(distance, 4))
                cls.input_panel["A"] = str(round(angle, 4))

                return cls.input_panel

        return cls.input_panel

    @classmethod
    def calculate_area(cls, context):
        try:
            polyline_data = context.scene.BIMModelProperties.polyline_point
        except:
            return cls.input_panel

        if len(polyline_data) < 3:
            return cls.input_panel

        points = []
        for data in polyline_data:
            points.append(Vector((data.x, data.y, data.z)))

        if points[0] == points[-1]:
            points = points[1:]

        # TODO move this to CAD
        # Calculate the normal vector of the plane formed by the first three vertices
        v1, v2, v3 = points[:3]
        normal = (v2 - v1).cross(v3 - v1).normalized()

        # Check if all points are coplanar
        is_coplanar = True
        tolerance = 1e-6  # Adjust this value as needed
        for v in points:
            if abs((v - v1).dot(normal)) > tolerance:
                is_coplanar = False

        if is_coplanar:
            area = 0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                area += points[i].cross(points[j]).dot(normal)

            area = abs(area) / 2
        else:
            area = 0

        if "AREA" in list(cls.input_panel.keys()):
            cls.input_panel["AREA"] = str(round(area, 4))
        return cls.input_panel


    @classmethod
    def calculate_x_y_and_z(cls, context):
        try:
            polyline_data = context.scene.BIMModelProperties.polyline_point
            last_point_data = polyline_data[len(polyline_data) - 1]
        except:
            return

        snap_prop = context.scene.BIMModelProperties.snap_mouse_point[0]
        snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
        last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        second_to_last_point = None
        if len(polyline_data) > 1:
            second_to_last_point_data = polyline_data[len(polyline_data) - 2]
            second_to_last_point = Vector(
                (second_to_last_point_data.x, second_to_last_point_data.y, second_to_last_point_data.z)
            )
        else:
            # Creates a fake "second to last" point away from the first point but in the same x axis
            # this allows to calculate the angle relative to x axis when there is only one point
            second_to_last_point = Vector((last_point.x - 10, last_point.y, last_point.z))

        distance = float(cls.input_panel["D"])

        if distance < 0 or distance > 0:
            angle_rad = radians(180 - float(cls.input_panel["A"]))
            ref_vec = second_to_last_point - last_point
            dir_vec = last_point - snap_vector

            rot_axis = ref_vec.cross(dir_vec)
            rot_axis.normalize()
            rot_axis = Vector((abs(rot_axis.x), abs(rot_axis.y), abs(rot_axis.z)))

            rot_mat = Matrix.Rotation(angle_rad, 3, rot_axis)

            ref_vec.normalize()
            coords = ((ref_vec @ rot_mat) * distance) + last_point

            x = coords[0]
            y = coords[1]
            z = coords[2]
            if cls.input_panel:
                cls.input_panel["X"] = str(round(x, 4))
                cls.input_panel["Y"] = str(round(y, 4))
                if "Z" in list(cls.input_panel.keys()):
                    cls.input_panel["Z"] = str(round(z, 4))

                return cls.input_panel

        return cls.input_panel

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_input_panel(self, context):
        texts = {"D": "Distance:", "A": "Angle:", "X": "X coord:", "Y": "Y coord:", "Z": "Z coord:",  "AREA": "Area:"}

        unit_system = tool.Drawing.get_unit_system()
        if unit_system == "IMPERIAL":
            precision = context.scene.DocProperties.imperial_precision
            factor = 3.28084
        else:
            precision = None
            factor = 1

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 0
        blf.size(self.font_id, 12)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour
        color_highlight = self.addon_prefs.decorator_color_special
        offset = 20
        new_line = 20
        for i, (key, value) in enumerate(self.input_panel.items()):

            if key != "A" and key != self.input_type:
                value = float(value)
                if context.scene.unit_settings.length_unit == 'MILLIMETERS':
                    value = value * 1000
                formatted_value = format_distance(value*factor, precision=precision, suppress_zero_inches=True, in_unit_length=True)
            else:
                formatted_value = value

            if key not in list(texts.keys()):
                continue
            if key == self.input_type:
                blf.color(self.font_id, *color_highlight)
            else:
                blf.color(self.font_id, *color)
            blf.position(self.font_id, self.mouse_pos[0] + offset, self.mouse_pos[1] - (new_line * i), 0)
            blf.draw(self.font_id, texts[key] + formatted_value)

    def draw_measurements(self, context):
        region = context.region
        rv3d = region.data
        measurement_prop = context.scene.BIMModelProperties.polyline_measurement


        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 1
        blf.size(self.font_id, 12)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour


        blf.color(self.font_id, *color)
        for i in range(len(measurement_prop)):
            if i == 0:
                continue
            pos_dim = (Vector(measurement_prop[i].position) + Vector(measurement_prop[i-1].position)) / 2
            coords_dim = view3d_utils.location_3d_to_region_2d(region, rv3d, pos_dim)

            unit_system = tool.Drawing.get_unit_system()
            if unit_system == "IMPERIAL":
                precision = context.scene.DocProperties.imperial_precision
                factor = 3.28084
            else:
                precision = None
                factor = 1

            value = measurement_prop[i].dim            
            value = float(value)
            if context.scene.unit_settings.length_unit == 'MILLIMETERS':
                value = value * 1000
            formatted_value = format_distance(value*factor, precision=precision, suppress_zero_inches=True, in_unit_length=True)
            
            blf.position(self.font_id, coords_dim[0], coords_dim[1], 0)
            blf.draw(self.font_id, "d: " + formatted_value)

            pos_angle = measurement_prop[i-1].position
            coords_angle = view3d_utils.location_3d_to_region_2d(region, rv3d, pos_angle)
            blf.position(self.font_id, coords_angle[0], coords_angle[1], 0)
            blf.draw(self.font_id, "a: " + measurement_prop[i].angle)

    def draw_on_screen_menu(self, context):
        region = context.region

        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 2
        blf.size(self.font_id, 12)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorations_colour
        blf.color(self.font_id, *color)

        text_w, text_h = blf.dimensions(0, self.instructions)
        position = (region.width / 2) - (text_w / 2)
        blf.position(self.font_id, position, 10, 0)
        blf.draw(self.font_id, self.instructions)

        text_w, text_h = blf.dimensions(0, self.snap_info)
        position = (region.width / 2) - (text_w / 2)
        blf.position(self.font_id, position, 30, 0)
        blf.draw(self.font_id, self.snap_info)

    
    def __call__(self, context):

        self.addon_prefs = tool.Blender.get_addon_preferences()
        decorator_color = self.addon_prefs.decorations_colour
        decorator_color_special = self.addon_prefs.decorator_color_special
        decorator_color_selected = self.addon_prefs.decorator_color_selected
        decorator_color_error = self.addon_prefs.decorator_color_error
        decorator_color_unselected = self.addon_prefs.decorator_color_unselected
        decorator_color_background = self.addon_prefs.decorator_color_background

        gpu.state.blend_set("ALPHA")
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.point_size_set(10)

        snap_prop = context.scene.BIMModelProperties.snap_mouse_point[0]
        # Point related to the mouse
        mouse_point = [Vector((snap_prop.x, snap_prop.y, snap_prop.z))]

        try:
            snap_ref = context.scene.BIMModelProperties.snap_mouse_ref[0]
            ref_point = [Vector((snap_ref.x, snap_ref.y, snap_ref.z))]
        except:
            ref_point = None

        if snap_prop.snap_type in ["Face", "Plane"]:
            self.draw_batch("POINTS", mouse_point, decorator_color_unselected)
        else:
            self.draw_batch("POINTS", mouse_point, (1.0, 0.6, 0.0, 1.0))

        if ref_point:
            self.draw_batch("POINTS", ref_point, (1.0, 0.6, 0.0, 1.0))

        default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
        projection_point = []
        if self.use_default_container:
            # When a point is above the plane it projects the point
            # to the plane and creates a line
            if snap_prop.snap_type != "Plane" and snap_prop.z != 0:
                self.line_shader.uniform_float("lineWidth", 1.0)
                projection_point = [Vector((snap_prop.x, snap_prop.y, default_container_elevation))]
                self.draw_batch("POINTS", projection_point, decorator_color_unselected)
                edges = [[0, 1]]
                self.draw_batch("LINES", mouse_point + projection_point, (1.0, 0.6, 0.0, 1.0), edges)

        # Polyline with selected points
        polyline_data = context.scene.BIMModelProperties.polyline_point
        polyline_points = []
        polyline_edges = []
        for point_prop in polyline_data:
            point = Vector((point_prop.x, point_prop.y, point_prop.z))
            polyline_points.append(point)

        for i in range(len(polyline_points) - 1):
            polyline_edges.append([i, i + 1])

        self.line_shader.uniform_float("lineWidth", 2.0)
        self.draw_batch("POINTS", polyline_points, decorator_color_selected)
        if len(polyline_points) > 1:
            self.draw_batch("LINES", polyline_points, decorator_color_selected, polyline_edges)

        # Line between last polyline point and mouse
        edges = [[0, 1]]
        if polyline_points:
            if snap_prop.snap_type != "Plane" and projection_point:
                self.draw_batch("LINES", [polyline_points[-1]] + projection_point, decorator_color_unselected, edges)
            else:
                self.draw_batch("LINES", [polyline_points[-1]] + mouse_point, decorator_color_unselected, edges)

        # Line for angle axis snap
        if snap_prop.snap_type == "Axis":
            self.line_shader.uniform_float("lineWidth", 0.75)
            self.draw_batch("LINES", [self.axis_start, self.axis_end], decorator_color_unselected, [(0, 1)])

        try:
            self.draw_batch("TRIS", self.axis_rectangle, (1, 1, 1, 0.1), [(0, 1, 3), (0, 2, 3)])
        except:
            pass

        # Area highlight
        if "AREA" in list(self.input_panel.keys()):
            if self.input_panel["AREA"] and float(self.input_panel["AREA"]) > 0:
                edges = []
                for i in range(1, len(polyline_points) - 1):
                    edges.append((0, i, i + 1))
                self.draw_batch("TRIS", polyline_points, (0, 1, 0, 0.1), edges)
