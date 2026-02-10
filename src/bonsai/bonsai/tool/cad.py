# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

# This code was originally taken from https://github.com/zeffii/mesh_tiny_cad
# which is typically bundled with Blender, licensed under GPL v2-or-later.
# Modifications are made to make the behaviour more in line with how intuitively
# CAD drafters use these tools.

# Changes include:
#
#  - Instead of AutoVTX, user explicitly chooses V, T, or X mode
#  - Instead of adding edges, existing edges are extended
#  - An arc is reconstructed from 3 points instead of a full circle
#  - You can now derive the center from an arc without generating geometry

from __future__ import annotations

import itertools
import math
import sys
from typing import TYPE_CHECKING, Union

import bmesh
import bpy
import mathutils.geometry
import numpy as np
from mathutils import Matrix, Vector, geometry

if TYPE_CHECKING:
    from bonsai.bim.module.cad.prop import BIMCadProperties


VTX_PRECISION = 1.0e-5


class Cad:
    @classmethod
    def get_cad_props(cls) -> BIMCadProperties:
        return bpy.context.scene.BIMCadProperties

    @classmethod
    def is_point_on_edge(cls, p, edge):
        """
        > p:        vector
        > edge:     tuple of 2 vectors
        < returns:  True / False if a point happens to lie on an edge
        """
        pt, _percent = mathutils.geometry.intersect_point_line(p, *edge)
        on_line = (pt - p).length < VTX_PRECISION
        return on_line and (0.0 <= _percent <= 1.0)

    @classmethod
    def point_on_edge(cls, p, edge):
        """
        > p:        vector
        > edge:     tuple of 2 vectors
        < returns:  a vector of the closest point on that edge
        """
        return mathutils.geometry.intersect_point_line(p, *edge)[0]

    @classmethod
    def edge_percent(cls, p, edge):
        """
        > takes a point, and a edge as a tuple of 2 vectors
        < returns the percentage between 0 and 1 of where the point lies on the edge
        """
        return mathutils.geometry.intersect_point_line(p, *edge)[1]

    @classmethod
    def angle_edges(cls, edge1, edge2, degrees=False, signed=False):
        """
        > takes 2 edges, each as a tuple of two vectors
        < returns the potentially signed angle as degrees or radians

        NOTE: `signed` expects both edges to be 2D (just as `Vector.angle_signed`)
        """
        if signed:
            a = (edge1[1] - edge1[0]).angle_signed(edge2[1] - edge2[0])
        else:
            a = (edge1[1] - edge1[0]).angle(edge2[1] - edge2[0])
        return math.degrees(a) if degrees else a

    @classmethod
    def angle_3_vectors(cls, v1, v2, v3, new_angle=None, degrees=False):
        """
        > takes 3 vectors. The order matters, v2 is the center point.
        < returns the signed angle as degrees or radians
        < if a new angle is provided, return the rotation vector
        """
        d1 = v1 - v2
        d2 = v3 - v2

        # Rounding avoids problems when dealing with 180 degrees
        d1 = Vector(round(c, 6) for c in d1)
        d2 = Vector(round(c, 6) for c in d2)

        d1.normalize()
        d2.normalize()

        axis = d1.cross(d2).normalized()

        # Calculate the unsigned angle between the "d1" and "d2" vectors
        try:
            a = d1.angle(d2)
        except:
            a = 0

        # Determine the sign of the angle based on the provided axis
        # If new_angle, determine the direction of the rotation
        parameter = (
            round(axis.z, 2) < 0
            or (round(axis.y, 2) == 0 and round(axis.x < 0))
            or (round(axis.x, 2) == 0 and round(axis.y > 0))
        )
        if new_angle is not None:
            rot_mat = Matrix.Rotation(new_angle, 3, axis)
            rot_vector = (d1 @ rot_mat) if parameter else (rot_mat @ d1)

            # 180 degrees special cases
            if abs(round(a, 4)) == round(math.pi, 4) and (
                rot_vector.x == 0.0
                and rot_vector.y == 0.0
                or rot_vector.x == 0.0
                and rot_vector.z == 0.0
                or rot_vector.y == 0.0
                and rot_vector.z == 0.0
            ):
                rot_vector *= -1
            return rot_vector
        else:
            sign = -1 if parameter else 1

            if degrees:
                a = math.degrees(a)

                # 180 degrees special cases
                if abs(round(a, 2)) == abs(180.00):
                    return -180.0
                return a * sign
            else:
                return a

    @classmethod
    def is_x(cls, value: float, x: float, tolerance: float | None = None) -> bool:
        """
        > takes a value and a target of x, either as a single value x or an interable of values
        < returns if the value is equivalent to x within a tolerance
        """
        if tolerance is None:
            tolerance = VTX_PRECISION
        if isinstance(x, (list, tuple)):
            for y in x:
                if (y + tolerance) > value > (y - tolerance):
                    return True
            return False
        return (x + tolerance) > value > (x - tolerance)

    @classmethod
    def normalise_angle(cls, angle: float) -> float:
        """Normalise an angle between -179 and 180"""
        angle = angle % 360
        angle = (angle + 360) % 360
        if angle > 180:
            angle -= 360
        return angle

    @classmethod
    def are_vectors_equal(cls, v1: Vector, v2: Vector, tolerance: float | None = None) -> bool:
        return cls.is_x((v2 - v1).length, 0, tolerance)

    @classmethod
    def intersect_edge_plane(cls, v1, v2, plane_co, plane_no):
        """
        > takes an edges as two vector, and a plane as origin point and normal
        < return the intersection point or None
        """
        return geometry.intersect_line_plane(v1, v2, plane_co, plane_no)

    def intersect_edge_plane_v2(v1, v2, plane_co, plane_no, eps=1e-9):
        """
        Numpy version of intersect_edge_plane
        > takes an edges as two vector, and a plane as origin point and normal
        < return the intersection point or None
        """

        # References: https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python,
        # https://stackoverflow.com/a/18543221

        p0 = np.array((v1.x, v1.y, v1.z), dtype=np.float64)
        p1 = np.array((v2.x, v2.y, v2.z), dtype=np.float64)
        pc = np.array((plane_co.x, plane_co.y, plane_co.z), dtype=np.float64)
        n = np.array((plane_no.x, plane_no.y, plane_no.z), dtype=np.float64)

        u = p1 - p0
        dot = np.dot(u, n)
        if abs(dot) < eps:
            # Line is parallel to plane (no intersection or lies in plane)
            return None

        w = pc - p0
        fac = np.dot(w, n) / dot
        p = p0 + fac * u

        return Vector(p)

    @classmethod
    def intersect_edges(
        cls, edge1: tuple[Vector, Vector], edge2: tuple[Vector, Vector]
    ) -> Union[tuple[Vector, Vector], None]:
        """
        > takes 2 tuples, each tuple contains 2 vectors
        - prepares input for sending to intersect_line_line
        < returns output of intersect_line_line
        """
        [p1, p2], [p3, p4] = edge1, edge2
        # https://developer.blender.org/T101591
        is_2d = len(p1) == 2
        if is_2d:
            p1 = p1.to_3d()
            p2 = p2.to_3d()
            p3 = p3.to_3d()
            p4 = p4.to_3d()
        results = mathutils.geometry.intersect_line_line(p1, p2, p3, p4)
        if is_2d and results:
            r1, r2 = results
            return r1.to_2d() if r1 else r1, r2.to_2d() if r2 else r2
        return results

    @classmethod
    def intersect_edges_v2(cls, edge1, edge2):
        """
        Calculate the closest points on two line segments.
        Note: This function doesn't use intersect_line_line and uses Numpy for calculations

        > edge1: tuple of two vectors (v1, v2) representing the first segment
        > edge2: tuple of two vectors (v3, v4) representing the second segment
        < returns: tuple of two vectors (C1, C2) or (None, None) if lines are parallel
        """
        # This function seems to work better than intersect_line_line
        # in orthogonal view
        # https://en.wikipedia.org/wiki/Skew_lines#Nearest_points

        is_2d = False
        # Starting and ending points
        p1, p1_end = edge1
        p2, p2_end = edge2
        if len(p1) == 2:
            is_2d = True
            p1, p1_end = p1.to_3d(), p1_end.to_3d()
            p2, p2_end = p2.to_3d(), p2_end.to_3d()

        p1 = np.array((p1.x, p1.y, p1.z), dtype=np.float64)
        p1_end = np.array((p1_end.x, p1_end.y, p1_end.z), dtype=np.float64)
        p2 = np.array((p2.x, p2.y, p2.z), dtype=np.float64)
        p2_end = np.array((p2_end.x, p2_end.y, p2_end.z), dtype=np.float64)
        # Directions
        d1 = p1_end - p1
        d2 = p2_end - p2
        d1 /= np.linalg.norm(d1) or 1  # equivalent of Vector.normalized() or Vector / Vector.length
        d2 /= np.linalg.norm(d2) or 1

        n = np.cross(d1, d2)

        # if n is zero, lines are parallel
        if abs(np.linalg.norm(n)) < 1e-6:
            return None, None

        n2 = np.cross(d2, n)
        c1 = p1 + (np.dot((p2 - p1), n2) / (np.dot(d1, n2))) * d1
        n1 = np.cross(d1, n)
        c2 = p2 + (np.dot((p1 - p2), n1) / (np.dot(d2, n1))) * d2

        if is_2d:
            return Vector(c1[:2].copy()), Vector(c2[:2].copy())
        else:
            return Vector(c1), Vector(c2)

    @classmethod
    def get_intersection(cls, edge1, edge2):
        """
        > takes 2 tuples, each tuple contains 2 vectors
        < returns the point halfway on line. See intersect_line_line
        """
        line = cls.intersect_edges(edge1, edge2)
        if line:
            return (line[0] + line[1]) / 2

    @classmethod
    def test_coplanar(cls, edge1, edge2):
        """
        the line that describes the shortest line between the two edges
        would be short if the lines intersect mathematically. If this
        line is longer than the VTX_PRECISION then they are either
        coplanar or parallel.
        """
        line = cls.intersect_edges(edge1, edge2)
        if line:
            return (line[0] - line[1]).length < VTX_PRECISION

    @classmethod
    def closest_idx(cls, pt, e):
        """
        > pt:       vector
        > e:        bmesh edge
        < returns:  returns index of vertex closest to pt.

        if both points in e are equally far from pt, then v1 is returned.
        """
        if isinstance(e, bmesh.types.BMEdge):
            ev = e.verts
            v1 = ev[0].co
            v2 = ev[1].co
            distance_test = (v1 - pt).length <= (v2 - pt).length
            return ev[0].index if distance_test else ev[1].index

        print("received {0}, check expected input in docstring ".format(e))

    @classmethod
    def closest_vector(cls, pt, e):
        """
        > pt:       vector
        > e:        2 vector tuple
        < returns either v1 or v2 in e, whichever is closest to pt

        if both points in e are equally far from pt, then v1 is returned.
        """
        if isinstance(e, tuple) and all([isinstance(co, Vector) for co in e]):
            v1, v2 = e
            distance_test = (v1 - pt).length <= (v2 - pt).length
            return v1 if distance_test else v2

    @classmethod
    def furthest_vector(cls, pt, e):
        """
        > pt:       vector
        > e:        2 vector tuple
        < returns either v1 or v2 in e, whichever is furthest from pt

        if both points in e are equally far from pt, then v1 is returned.
        """
        if isinstance(e, tuple) and all([isinstance(co, Vector) for co in e]):
            v1, v2 = e
            distance_test = (v1 - pt).length >= (v2 - pt).length
            return v1 if distance_test else v2

    @classmethod
    def closest_and_furthest_vectors(cls, pt, e):
        """
        > pt:       vector
        > e:        2 vector tuple
        < returns the two vectors closest to and furthest from pt.
        """
        if isinstance(e, tuple) and all([isinstance(co, Vector) for co in e]):
            closest = cls.closest_vector(pt, e)
            furthest = e[1] if closest == e[0] else e[0]
            return closest, furthest

    @classmethod
    def coords_tuple_from_edge_idx(cls, bm, idx):
        """bm is a bmesh representation"""
        return tuple(v.co for v in bm.edges[idx].verts)

    @classmethod
    def vectors_from_indices(cls, bm, raw_vert_indices):
        """bm is a bmesh representation"""
        return [bm.verts[i].co for i in raw_vert_indices]

    @classmethod
    def vertex_indices_from_edges_tuple(cls, bm, edge_tuple):
        """
        > bm:           is a bmesh representation
        > edge_tuple:   contains two edge indices.
        < returns the vertex indices of edge_tuple
        """

        def k(v, w):
            return bm.edges[edge_tuple[v]].verts[w].index

        return [k(i >> 1, i % 2) for i in range(4)]

    @classmethod
    def get_vert_indices_from_bmedges(cls, edges):
        """
        > bmedges:      a list of two bm edges
        < returns the vertex indices of edge_tuple as a flat list.
        """
        temp_edges = []
        print(edges)
        for e in edges:
            for v in e.verts:
                temp_edges.append(v.index)
        return temp_edges

    @classmethod
    def num_edges_point_lies_on(cls, pt, edges):
        """returns the number of edges that a point lies on."""
        res = [cls.is_point_on_edge(pt, edge) for edge in [edges[:2], edges[2:]]]
        return len([i for i in res if i])

    @classmethod
    def get_edge_direction(cls, edge):
        return (edge[1] - edge[0]).normalized()

    @classmethod
    def are_edges_parallel(cls, edge1, edge2):
        edge1_dir = edge1[1] - edge1[0]
        edge2_dir = edge2[1] - edge2[0]
        return cls.is_x(edge1_dir.cross(edge2_dir).length_squared, 0)

    @classmethod
    def are_edges_collinear(cls, edge1, edge2):
        if not cls.are_edges_parallel(edge1, edge2):
            return False
        return cls.are_edges_parallel((edge2[0], edge1[0]), edge2)

    @classmethod
    def closest_points(cls, edge1, edge2):
        """
        closest end points between `edge1` and `edge2`

        ensures returned vectors are the exact objects
        that were passed to the method with `edge1` and `edge2`

        < returns two tuples - two closest points and two other points

        first point of each tuple belongs to `edge1` and second to `edge2`
        """

        distance_squared = None
        closest_points = None
        for p1 in edge1:
            for p2 in edge2:
                cur_line = p2 - p1
                cur_distance_squared = cur_line.dot(cur_line)
                if distance_squared is None or cur_distance_squared < distance_squared:
                    closest_points = (p1, p2)
                    distance_squared = cur_distance_squared

        other_points = (
            edge1[0] if closest_points[0] == edge1[1] else edge1[1],
            edge2[0] if closest_points[1] == edge2[1] else edge2[1],
        )
        return closest_points, other_points

    @classmethod
    def find_intersecting_edges(cls, bm, pt, idx1, idx2):
        """
        > pt:           Vector
        > idx1, ix2:    edge indices
        < returns the list of edge indices where pt is on those edges
        """
        if not pt:
            return []
        idxs = [idx1, idx2]
        edges = [cls.coords_tuple_from_edge_idx(bm, idx) for idx in idxs]
        return [idx for edge, idx in zip(edges, idxs) if cls.is_point_on_edge(pt, edge)]

    @classmethod
    def duplicates(cls, indices):
        return len(set(indices)) < 4

    @classmethod
    def vert_idxs_from_edge_idx(cls, bm, idx):
        edge = bm.edges[idx]
        return edge.verts[0].index, edge.verts[1].index

    @classmethod
    def add_edges(cls, bm, pt, idxs, fdp):
        """
        this function is a disaster --
        index updates and ensure_lookup_table() are called before this function
        and after, and i've tried doing this less verbose but results tend to be
        less predictable. I'm obviously a terrible coder, but can only spend so
        much time figuring out this stuff.
        """

        v1 = bm.verts.new(pt)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.index_update()

        try:
            for e in idxs:
                bm.edges.index_update()
                v2 = bm.verts[e]
                bm.edges.new((v1, v2))

            bm.edges.index_update()
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

        except Exception as err:
            print("some failure: details")
            for l in fdp:
                print(l)

            sys.stderr.write("ERROR: %s\n" % str(err))
            print(sys.exc_info()[-1].tb_frame.f_code)
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))

    @classmethod
    def remove_earmarked_edges(cls, bm, earmarked):
        edges_select = [e for e in bm.edges if e.index in earmarked]
        bmesh.ops.delete(bm, geom=edges_select, context="EDGES")

    @classmethod
    def perform_vtx(cls, bm, pt, edges, pts, vertex_indices):
        idx1, idx2 = edges[0].index, edges[1].index
        fdp = pt, edges, pts, vertex_indices

        # this list will hold those edges that pt lies on
        edges_indices = cls.find_intersecting_edges(bm, pt, idx1, idx2)
        mode = "VTX"[len(edges_indices)]

        if mode == "V":
            cl_vert1 = cls.closest_idx(pt, edges[0])
            cl_vert2 = cls.closest_idx(pt, edges[1])
            cls.add_edges(bm, pt, [cl_vert1, cl_vert2], fdp)

        elif mode == "T":
            to_edge_idx = edges_indices[0]
            from_edge_idx = idx1 if to_edge_idx == idx2 else idx2

            cl_vert = cls.closest_idx(pt, bm.edges[from_edge_idx])
            to_vert1, to_vert2 = cls.vert_idxs_from_edge_idx(bm, to_edge_idx)
            cls.add_edges(bm, pt, [cl_vert, to_vert1, to_vert2], fdp)

        elif mode == "X":
            cls.add_edges(bm, pt, vertex_indices, fdp)

        # final refresh before returning to user.
        if edges_indices:
            cls.remove_earmarked_edges(bm, edges_indices)

        bm.edges.index_update()
        return bm

    @classmethod
    def perform_t(cls, bm, pt, target, edge, pts, vertex_indices):
        cl_vert = cls.closest_idx(pt, bm.edges[edge.index])
        bm.verts[cl_vert].co = pt
        bm.edges.index_update()
        return bm

    @classmethod
    def perform_v(cls, bm, pt, target, edge, pts, vertex_indices):
        bm = cls.perform_t(bm, pt, target, edge, pts, vertex_indices)
        bm = cls.perform_t(bm, pt, edge, target, pts, vertex_indices)
        return bm

    @classmethod
    def prioritise_active_edge(cls, bm, edges):
        return [edges[0], edges[1]] if bm.select_history.active == edges[0] else [edges[1], edges[0]]

    @classmethod
    def do_vtx_if_appropriate(cls, bm, edges, mode):
        vertex_indices = cls.get_vert_indices_from_bmedges(edges)

        # test 1, are there shared vers? if so return non-viable
        if not len(set(vertex_indices)) == 4:
            return {"SHARED_VERTEX"}

        # test 2, is parallel?
        p1, p2, p3, p4 = [bm.verts[i].co for i in vertex_indices]
        point = cls.get_intersection([p1, p2], [p3, p4])
        if not point:
            return {"PARALLEL_EDGES"}

        # test 3, coplanar edges?
        coplanar = cls.test_coplanar([p1, p2], [p3, p4])
        if not coplanar:
            return {"NON_PLANAR_EDGES"}

        edges = cls.prioritise_active_edge(bm, edges)
        # point must lie on an edge or the virtual extension of an edge
        if mode == "T":
            bm = cls.perform_t(bm, point, edges[0], edges[1], (p1, p2, p3, p4), vertex_indices)
        elif mode == "V":
            bm = cls.perform_v(bm, point, edges[0], edges[1], (p1, p2, p3, p4), vertex_indices)
        return bm

    @classmethod
    def get_center_of_arc(cls, pts, obj=None):
        """also will convert center of arc from local space of `obj` (if it's provided)"""
        mw = obj.matrix_world if obj else None
        V = Vector

        # construction
        v1, v2, v3, v4 = V(pts[0]), V(pts[1]), V(pts[1]), V(pts[2])
        edge1_mid = v1.lerp(v2, 0.5)
        edge2_mid = v3.lerp(v4, 0.5)
        axis = geometry.normal(v1, v2, v4)
        mat_rot = Matrix.Rotation(math.radians(90.0), 4, axis)

        # triangle edges
        v1_ = ((v1 - edge1_mid) @ mat_rot) + edge1_mid
        v2_ = ((v2 - edge1_mid) @ mat_rot) + edge1_mid
        v3_ = ((v3 - edge2_mid) @ mat_rot) + edge2_mid
        v4_ = ((v4 - edge2_mid) @ mat_rot) + edge2_mid

        r = geometry.intersect_line_line(v1_, v2_, v3_, v4_)
        if r:
            p1, _ = r
            cp = mw @ p1 if mw else p1
            return cp
        else:
            print("not on a circle")

    # https://github.com/nortikin/sverchok/blob/master/nodes/generator/basic_3pt_arc.py
    # This function is taken from Sverchok's generate_3PT_mode_1 function, licensed under GPL v2-or-later.
    # No functional modifications have been made.
    @classmethod
    def create_arc_segments(cls, pts=None, num_verts=20, make_edges=False):
        """
        Arc from [start - through - end]
        - call this function only if you have 3 pts,
        - do your error checking before passing to it.
        """
        num_verts -= 1
        verts, edges = [], []
        V = Vector

        # construction
        v1, v2, v3, v4 = V(pts[0]), V(pts[1]), V(pts[1]), V(pts[2])
        edge1_mid = v1.lerp(v2, 0.5)
        edge2_mid = v3.lerp(v4, 0.5)
        axis = mathutils.geometry.normal(v1, v2, v4)
        mat_rot = Matrix.Rotation(math.radians(90.0), 4, axis)

        # triangle edges
        v1_ = ((v1 - edge1_mid) @ mat_rot) + edge1_mid
        v2_ = ((v2 - edge1_mid) @ mat_rot) + edge1_mid
        v3_ = ((v3 - edge2_mid) @ mat_rot) + edge2_mid
        v4_ = ((v4 - edge2_mid) @ mat_rot) + edge2_mid

        r = mathutils.geometry.intersect_line_line(v1_, v2_, v3_, v4_)
        if r:
            # do arc
            p1, _ = r

            # find arc angle.
            a = (v1 - p1).angle((v4 - p1), 0)
            s = (2 * math.pi) - a

            interior_angle = (v1 - v2).angle(v4 - v3, 0)
            if interior_angle > 0.5 * math.pi:
                s = math.pi + 2 * (0.5 * math.pi - interior_angle)

            for i in range(num_verts + 1):
                mat_rot = Matrix.Rotation(((s / num_verts) * i), 4, axis)
                vec = ((v4 - p1) @ mat_rot) + p1
                verts.append(vec[:])
        else:
            # do straight line
            step_size = 1 / num_verts
            verts = [v1_.lerp(v4_, i * step_size)[:] for i in range(num_verts + 1)]

        if make_edges:
            edges = [(n, n + 1) for n in range(len(verts) - 1)]

        return verts, edges

    @classmethod
    def is_counter_clockwise_order(cls, A, B, C):
        """whether A-B-C located in counter-clockwise order in 2d space"""
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    @classmethod
    def sign(cls, value):
        """
        returns:
          0 if cls.is_x(value, 0)) \n
          1 if value > 0 \n
         -1 if value < 0
        """
        if cls.is_x(value, 0):
            return 0
        return 1 if value > 0 else -1

    @classmethod
    def get_basis_vector(cls, object, axis_i):
        return object.matrix_world.col[axis_i].normalized().to_3d()

    @classmethod
    def offset_edges(cls, bm, distance, mw=Matrix.Identity(4), wp=Matrix.Identity(4)):

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        edges = [e for e in bm.edges]

        if len(edges) < 1:
            return

        verts = set()
        [verts.update(e.verts) for e in edges]

        rotation = Matrix.Rotation(math.pi / 2, 2, "Z")
        rotation_i = Matrix.Rotation(-math.pi / 2, 2, "Z")

        # Create loops from edges
        loop_edges = set(edges)
        loops = []
        while loop_edges:
            edge = loop_edges.pop()
            loop = [edge]
            has_found_connected_edge = True
            while has_found_connected_edge:
                has_found_connected_edge = False
                for edge in loop_edges.copy():
                    edge_verts = set(edge.verts)
                    if edge_verts & set(loop[0].verts):
                        loop.insert(0, edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
                    elif edge_verts & set(loop[-1].verts):
                        loop.append(edge)
                        loop_edges.remove(edge)
                        has_found_connected_edge = True
            loops.append(loop)

        for loop in loops:
            all_verts = {v.index for e in loop for v in e.verts}
            possible_v1s = []
            is_closed = True
            for edge in loop:
                # If we have an open loop, start at either end instead
                v = edge.verts[0]
                if len(v.link_edges) == 1:
                    possible_v1s.append(v)
                    is_closed = False
                else:
                    for link_edge in v.link_edges:
                        if link_edge.other_vert(v).index not in all_verts:
                            possible_v1s.append(v)
                            is_closed = False
                            break
                v = edge.verts[1]
                if len(v.link_edges) == 1:
                    possible_v1s.append(v)
                    is_closed = False
                else:
                    for link_edge in v.link_edges:
                        if link_edge.other_vert(v).index not in all_verts:
                            possible_v1s.append(v)
                            is_closed = False
                            break

            # Always start at the same vertex, so that when the operator is
            # refreshed with new parameters the axes don't randomly get flipped.
            if is_closed:
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                start = bm.verts[min(all_verts)]
            else:
                start = possible_v1s[0] if possible_v1s[0].index < possible_v1s[1].index else possible_v1s[1]

            v1 = start

            new_verts = []
            processed_verts = set()
            # [v0] --> v1 --> v2
            while v1:
                if v1.index in processed_verts:
                    break

                link_verts = []
                if len(v1.link_edges) == 1:
                    v = v1.link_edges[0].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None
                else:
                    v = v1.link_edges[0].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None
                    v = v1.link_edges[1].other_vert(v1)
                    link_verts.append(v) if v.index in all_verts else None

                if len(link_verts) == 1:
                    v2 = link_verts[0]
                    v0 = None if v2.index not in processed_verts else v2
                    v2 = None if v2.index in processed_verts else v2
                else:
                    v2 = link_verts[0]
                    v0 = link_verts[1]
                    if v2.index in processed_verts:
                        if is_closed and v0.index in processed_verts:
                            v3 = start
                            v0 = v0 if v2 == v3 else v2
                            v2 = v3
                        else:
                            v0, v2 = v2, v0

                normals = []
                v1co = (wp.inverted() @ mw @ v1.co).to_2d()
                if v2:
                    v2co = (wp.inverted() @ mw @ v2.co).to_2d()
                    direction = (v2co - v1co).normalized()
                    local_direction = (rotation @ direction).normalized()
                    normals.append(local_direction)

                if v0:
                    v0co = (wp.inverted() @ mw @ v0.co).to_2d()
                    direction = (v0co - v1co).normalized()
                    local_direction = (rotation_i @ direction).normalized()
                    normals.append(local_direction)

                if len(normals) == 2:
                    # https://stackoverflow.com/a/54042831/9627415
                    new_normal = (normals[0].lerp(normals[1], 0.5)).normalized()
                    offset_length = distance / math.sqrt((1 + normals[0].dot(normals[1])) / 2)
                    offset = mw.inverted().to_quaternion() @ (wp.to_quaternion() @ (new_normal * offset_length).to_3d())
                    new_vert = v1.co + offset
                    new_verts.append(bm.verts.new(new_vert))
                else:
                    normal = (normals[0] * distance).to_3d()
                    offset = mw.inverted().to_quaternion() @ (wp.to_quaternion() @ normal)
                    new_vert = v1.co + offset
                    new_verts.append(bm.verts.new(new_vert))

                processed_verts.add(v1.index)

                if v2 in processed_verts:
                    break

                v1 = v2

        return new_verts

    @classmethod
    def region_2d_to_vector_3d_np(cls, region: bpy.types.Region, rv3d: bpy.types.RegionView3d, coord: Vector) -> Vector:
        """
        Numpy version of view3d_utils.region_2d_to_vector_3d
        Return a direction vector from the viewport at the specific 2d region
        coordinate.

        > region: region of the 3D viewport, typically bpy.context.region.
        > rv3d: 3D region data, typically bpy.context.space_data.region_3d.
        > coord: 2d coordinates relative to the region:
           (event.mouse_region_x, event.mouse_region_y) for example.
        < returns a normalized 3d vector.
        """
        view_m = np.array(rv3d.view_matrix)
        window_m = np.array(rv3d.window_matrix)
        viewinv = np.linalg.inv(view_m)

        if rv3d.is_perspective:
            # For better precision with large numbers, avoid using rv3d.perspective_matrix. See https://github.com/IfcOpenShell/IfcOpenShell/issues/7046
            # Calculate it with view_matrix and window_matrix as numpy arrays.
            pers_m = window_m @ view_m
            persinv = np.linalg.inv(pers_m)

            out = np.array(
                [(2.0 * coord[0] / region.width) - 1.0, (2.0 * coord[1] / region.height) - 1.0, -0.5, 1.0],
                dtype=np.float64,
            )

            w = out[:3].dot(persinv[3, :3]) + persinv[3, 3]

            viewinv_translation = viewinv[:3, 3]
            view_vector = (persinv.dot(out)[:3] / w) - viewinv_translation
        else:
            view_vector = -viewinv[:3, 2].copy()  # -Z column

        view_vector /= np.linalg.norm(view_vector) or 1  # equivalent to Vector.normalized()
        return Vector(view_vector)

    @classmethod
    def region_2d_to_location_3d_np(
        cls, region: bpy.types.Region, rv3d: bpy.types.RegionView3d, coord: Vector, depth_location: Vector
    ) -> Vector:
        """
        Numpy version of view3d_utils.region_2d_to_location_3d
        Return a 3d location from the region relative 2d coords, aligned with
        *depth_location*.

        > region: region of the 3D viewport, typically bpy.context.region.
        > rv3d: 3D region data, typically bpy.context.space_data.region_3d.
        > coord: 2d coordinates relative to the region:
           (event.mouse_region_x, event.mouse_region_y) for example.
        < returns a normalized 3d vector.
        """
        coord_vec = cls.region_2d_to_vector_3d_np(region, rv3d, coord)
        depth_location = np.array([depth_location[0], depth_location[1], depth_location[2]], dtype=np.float64)

        origin_start = cls.region_2d_to_origin_3d_np(region, rv3d, coord)
        origin_end = origin_start + coord_vec

        if rv3d.is_perspective:
            viewinv = np.linalg.inv(rv3d.view_matrix)
            view_vec = viewinv[:3, 2].copy()
            return cls.intersect_edge_plane_v2(
                Vector(origin_start), Vector(origin_end), Vector(depth_location), Vector(view_vec)
            )
        else:
            return cls.point_on_edge(
                Vector(depth_location),
                (Vector(origin_start), Vector(origin_end)),
            )

    @classmethod
    def region_2d_to_origin_3d_np(
        cls, region: bpy.types.Region, rv3d: bpy.types.RegionView3d, coord: Vector, *, clamp: float = None
    ) -> Vector:
        """
        Numpy version of view3d_utils.region_2d_to_origin_3d
        Return the 3d view origin from the region relative 2d coords.

        .. note::

           Orthographic views have a less obvious origin,
           the far clip is used to define the viewport near/far extents.
           Since far clip can be a very large value,
           the result may give with numeric precision issues.

           To avoid this problem, you can optionally clamp the far clip to a
           smaller value based on the data you're operating on.


        > region: region of the 3D viewport, typically bpy.context.region.
        > rv3d: 3D region data, typically bpy.context.space_data.region_3d.
        > coord: 2d coordinates relative to the region:
           (event.mouse_region_x, event.mouse_region_y) for example.
        > clamp: clamp: Clamp the maximum far-clip value used.
           (negative value will move the offset away from the view_location)
        < returns the origin of the viewpoint in 3d space.
        """

        view_m = np.array(rv3d.view_matrix)
        window_m = np.array(rv3d.window_matrix)
        viewinv = np.linalg.inv(view_m)

        if rv3d.is_perspective:
            origin_start = viewinv[:3, 3].copy()
        else:
            pers_m = window_m @ view_m  # See https://github.com/IfcOpenShell/IfcOpenShell/issues/7046
            persinv = np.linalg.inv(pers_m)

            dx = (2.0 * coord[0] / region.width) - 1.0
            dy = (2.0 * coord[1] / region.height) - 1.0

            origin_start = (persinv[:3, 0] * dx) + (persinv[:3, 1] * dy) + persinv[:3, 3]

            if clamp != 0.0:
                if rv3d.view_perspective != "CAMERA":
                    origin_offset = persinv[:3, 2].copy()  # column 2
                    if clamp is not None:
                        c = float(clamp)
                        if c < 0.0:
                            origin_offset = -origin_offset
                            c = -c
                        length = np.linalg.norm(origin_offset)
                        if length > c and length > 0.0:
                            origin_offset = (origin_offset / length) * c
                    origin_start = origin_start - origin_offset

        return Vector(origin_start)

    @classmethod
    def location_3d_to_region_2d_np(
        cls, region: bpy.types.Region, rv3d: bpy.types.RegionView3d, coord: Vector, *, default=None
    ) -> Vector:
        """
        Numpy version of view3d_utils.location_3d_to_region_2d
        Return the *region* relative 2d location of a 3d position.

        > region: region of the 3D viewport, typically bpy.context.region.
        > rv3d: 3D region data, typically bpy.context.space_data.region_3d.
        > coord: 2d coordinates relative to the region:
           (event.mouse_region_x, event.mouse_region_y) for example.
        < returns a 2d location.
        """
        pt = np.array((coord[0], coord[1], coord[2], 1.0), dtype=np.float64)
        view_m = np.array(rv3d.view_matrix)
        window_m = np.array(rv3d.window_matrix)
        pers_m = window_m @ view_m
        prj = pers_m.dot(pt)  # 4-vector
        w = prj[3]
        if w > 0.0:
            width_half = region.width / 2.0
            height_half = region.height / 2.0
            x = width_half + width_half * (prj[0] / w)
            y = height_half + height_half * (prj[1] / w)
            return Vector((float(x), float(y)))
        return default
