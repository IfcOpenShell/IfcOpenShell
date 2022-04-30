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


import sys
import bpy
import bmesh
from mathutils import Vector, geometry
from mathutils.geometry import intersect_line_line as LineIntersect
from mathutils.geometry import intersect_point_line as PtLineIntersect


class CAD_prefs:
    VTX_PRECISION = 1.0e-5
    VTX_DOUBLES_THRSHLD = 0.0001


class Cad:
    @classmethod
    def point_on_edge(cls, p, edge):
        """
        > p:        vector
        > edge:     tuple of 2 vectors
        < returns:  True / False if a point happens to lie on an edge
        """
        pt, _percent = PtLineIntersect(p, *edge)
        on_line = (pt - p).length < CAD_prefs.VTX_PRECISION
        return on_line and (0.0 <= _percent <= 1.0)

    @classmethod
    def line_from_edge_intersect(cls, edge1, edge2):
        """
        > takes 2 tuples, each tuple contains 2 vectors
        - prepares input for sending to intersect_line_line
        < returns output of intersect_line_line
        """
        [p1, p2], [p3, p4] = edge1, edge2
        return LineIntersect(p1, p2, p3, p4)

    @classmethod
    def get_intersection(cls, edge1, edge2):
        """
        > takes 2 tuples, each tuple contains 2 vectors
        < returns the point halfway on line. See intersect_line_line
        """
        line = cls.line_from_edge_intersect(edge1, edge2)
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
        line = cls.line_from_edge_intersect(edge1, edge2)
        if line:
            return (line[0] - line[1]).length < CAD_prefs.VTX_PRECISION

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
        < returns:
        pt, 2 vector tuple: returns closest vector to pt

        if both points in e are equally far from pt, then v1 is returned.
        """
        if isinstance(e, tuple) and all([isinstance(co, Vector) for co in e]):
            v1, v2 = e
            distance_test = (v1 - pt).length <= (v2 - pt).length
            return v1 if distance_test else v2

        print("received {0}, check expected input in docstring ".format(e))

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
        res = [point_on_edge(pt, edge) for edge in [edges[:2], edges[2:]]]
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
        return [idx for edge, idx in zip(edges, idxs) if cls.point_on_edge(pt, edge)]

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
