# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import gpu
import bmesh
import blenderbim.tool as tool
from math import sin, cos, radians
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from typing import Union


ERROR_ELEMENTS_COLOR = (1, 0.2, 0.322, 1)  # RED
UNSPECIAL_ELEMENT_COLOR = (0.2, 0.2, 0.2, 1)  # GREY


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
        self.addon_prefs = context.preferences.addons["blenderbim"].preferences
        selected_elements_color = self.addon_prefs.decorator_color_selected
        unselected_elements_color = self.addon_prefs.decorator_color_unselected
        special_elements_color = self.addon_prefs.decorator_color_special

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
        self.draw_batch("LINES", all_vertices, UNSPECIAL_ELEMENT_COLOR, arc_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, preview_edges)
        self.draw_batch("LINES", all_vertices, special_elements_color, roof_angle_edges)

        self.draw_batch("POINTS", unselected_vertices, transparent_color(unselected_elements_color, 0.5))
        self.draw_batch("POINTS", error_vertices, ERROR_ELEMENTS_COLOR)
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

        self.draw_batch("POINTS", arc_centroids, UNSPECIAL_ELEMENT_COLOR)
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

        self.draw_batch("POINTS", circle_centroids, UNSPECIAL_ELEMENT_COLOR)
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
