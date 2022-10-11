# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


import sys
import bpy
import math
import bmesh
import mathutils.geometry
from mathutils import Vector, Matrix, geometry


VTX_PRECISION = 1.0e-5


class Cad:
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
        """
        if signed:
            a = (edge1[1] - edge1[0]).angle_signed(edge2[1] - edge2[0])
        else:
            a = (edge1[1] - edge1[0]).angle(edge2[1] - edge2[0])
        return math.degrees(a) if degrees else a

    @classmethod
    def is_x(cls, value, x, tolerance=None):
        """
        > takes a value and a target of x, either as a single value x or an interable of values
        < returns if the value is equivalent to x within a tolerance
        """
        if tolerance is None:
            tolerance = VTX_PRECISION
        if isinstance(x, (list, tuple)):
            for y in x:
                if value > (y - tolerance) and value < (y + tolerance):
                    return True
            return False
        return value > (x - tolerance) and value < (x + tolerance)

    @classmethod
    def intersect_edges(cls, edge1, edge2):
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
