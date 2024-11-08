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
import bmesh
import shapely
import mathutils
import numpy as np
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.shape
import bonsai.tool as tool
from math import pi, pow
from mathutils import Vector, Matrix, geometry
from typing import Union


class Helper:
    def __init__(self, file: ifcopenshell.file):
        self.file = file
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

    # We can detect a rectangular extrusion by picking any face, then find an
    # edge that shares a single vertex only with that face to find the extrusion
    # edge. A face with the normal facing down is prioritised. A limited
    # dissolve ensure that faces are quads and not tris.
    def auto_detect_rectangle_profile_extruded_area_solid(self, mesh: bpy.types.Mesh) -> dict:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.faces.ensure_lookup_table()
        face = None
        for face in bm.faces:
            if face.normal.z < -0.1:
                break
        profile = [l.vert.index for l in face.loops]
        extrusion = self.detect_extrusion_edge(bm, face)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        return {"profile": profile, "extrusion": extrusion}

    # After a limited dissolve, we detect the circle profile as it should be the
    # only ngon (this assumes the circle has at least a facetation of > 4 edges.
    # The extrusion direction is any edge that only shares a single vertex with
    # the profile. We prioritise the profile that has a downwards normal.
    def auto_detect_circle_profile_extruded_area_solid(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.faces.ensure_lookup_table()
        potential_faces = []
        for face in bm.faces:
            if len(face.verts) > 4:
                potential_faces.append(face)
        for face in potential_faces:
            if face.normal.z < -0.1:
                break

        profile = [l.vert.index for l in face.loops]
        extrusion = self.detect_extrusion_edge(bm, face)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        return {"profile": profile, "extrusion": extrusion}

    # After a limited dissolve, the arbitrary profile is any ngon or tri.
    # Failing that, it is equivalent to a rectangular profile. The extrusion
    # direction is any edge that only shares a single vertex with the profile.
    # We prioritise the profile that has a downwards normal.
    def auto_detect_arbitrary_closed_profile_extruded_area_solid(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.faces.ensure_lookup_table()
        potential_faces = []
        for face in bm.faces:
            total_verts = len(face.verts)
            if total_verts > 4 or total_verts == 3:
                potential_faces.append(face)

        if not potential_faces:
            potential_faces = bm.faces

        for face in potential_faces:
            if face.normal.z < -0.1:
                break

        profile = [l.vert.index for l in face.loops]
        extrusion = self.detect_extrusion_edge(bm, face)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        return {"profile": profile, "extrusion": extrusion}

    # An arbitrary closed profile with voids is similar to one without voids.
    # We start the same way with any ngon (no tri), but instead of being the entire
    # profile, it is only one of the possible faces that make up the end of our
    # extrusion. Then we find all faces with the same normal. This creates a set
    # of faces that define the end of our extrusion.  From this set of faces, we
    # need to then extract the outer loop and inner loops. First, all loops are
    # detected from the faces. Any edge that is not shared between other faces
    # in the set must be part of either an inner or outer loop. This gives us a
    # set of edges. Then, connected edges (i.e. sharing a vertex) are joined to
    # form distinct loops.  Finally, the outer loop is distinguished by being
    # the loop with the greatest area.
    def auto_detect_arbitrary_profile_with_voids_extruded_area_solid(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.faces.ensure_lookup_table()
        potential_faces = []
        for face in bm.faces:
            total_verts = len(face.verts)
            if total_verts > 4:
                potential_faces.append(face)

        for face in potential_faces:
            if face.normal.z < -0.1:
                break

        end_faces = []
        end_face_normal = face.normal
        for face in bm.faces:
            if (face.normal - end_face_normal).length < 0.001:
                end_faces.append(face)

        loop_edges = set()
        for face in end_faces:
            potential_edges = set(face.edges)
            for face2 in end_faces:
                if face == face2:
                    continue
                potential_edges -= set(face2.edges)
            loop_edges |= potential_edges

        # Create loops from edges
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

        # Determine outer loop
        max_area = 0
        outer_loop = None
        inner_loops = []

        for loop in loops:
            loop_vertices = []
            total_edges = len(loop)
            for i, edge in enumerate(loop):
                if i + 1 == total_edges and edge.verts[0] in loop[i - 1].verts:
                    loop_vertices.append(edge.verts[0])
                elif i + 1 == total_edges and edge.verts[1] in loop[i - 1].verts:
                    loop_vertices.append(edge.verts[1])
                elif edge.verts[0] in loop[i + 1].verts:
                    loop_vertices.append(edge.verts[1])
                elif edge.verts[1] in loop[i + 1].verts:
                    loop_vertices.append(edge.verts[0])

            loop_bm = bmesh.new()
            for vert in loop_vertices:
                loop_bm.verts.new(vert.co)
            face = loop_bm.faces.new(loop_bm.verts)

            loop_vertex_indices = [v.index for v in loop_vertices]
            face_area = face.calc_area()
            if face_area > max_area:
                max_area = face_area
                outer_loop = loop_vertex_indices
            inner_loops.append(loop_vertex_indices)
            loop_bm.free()

        inner_loops.remove(outer_loop)

        extrusion = self.detect_extrusion_edge(bm, end_faces[0])

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        return {"profile": outer_loop, "inner_curves": inner_loops, "extrusion": extrusion}

    # An arbitrary face with voids is similar to a profile with voids for extrusion.
    # Before we begin we check that all faces are coplanar instead of finding suitable face.
    # Then we process the same way.
    # Only 2 parameters are returned as there is no extrusion.
    def auto_detect_curve_bounded_plane(self, mesh, tolerance=0.001):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 1, verts=bm.verts, edges=bm.edges)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.faces.ensure_lookup_table()
        faces = bm.faces
        normal = faces[0].normal
        point = faces[0].verts[0].co
        for face in faces:
            pt_f = face.verts[0].co
            if (
                normal.dot(face.normal) < 1 - tolerance
                or abs(geometry.distance_point_to_plane(pt_f, point, normal)) > tolerance
            ):
                raise ValueError("All faces must be coplanar and have same orientation")

        loop_edges = set()
        for face in faces:
            potential_edges = set(face.edges)
            for face2 in faces:
                if face == face2:
                    continue
                potential_edges -= set(face2.edges)
            loop_edges |= potential_edges

        # Create loops from edges
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

        # Determine outer loop
        max_area = 0
        outer_loop = None
        inner_loops = []

        for loop in loops:
            loop_vertices = []
            total_edges = len(loop)
            for i, edge in enumerate(loop):
                if i + 1 == total_edges and edge.verts[0] in loop[i - 1].verts:
                    loop_vertices.append(edge.verts[0])
                elif i + 1 == total_edges and edge.verts[1] in loop[i - 1].verts:
                    loop_vertices.append(edge.verts[1])
                elif edge.verts[0] in loop[i + 1].verts:
                    loop_vertices.append(edge.verts[1])
                elif edge.verts[1] in loop[i + 1].verts:
                    loop_vertices.append(edge.verts[0])

            loop_bm = bmesh.new()
            for vert in loop_vertices:
                loop_bm.verts.new(vert.co)
            face = loop_bm.faces.new(loop_bm.verts)

            loop_vertex_indices = [v.index for v in loop_vertices]
            face_area = face.calc_area()
            if face_area > max_area:
                max_area = face_area
                outer_loop = loop_vertex_indices
            inner_loops.append(loop_vertex_indices)
            loop_bm.free()

        inner_loops.remove(outer_loop)

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        return {"outer_curve": outer_loop, "inner_curves": inner_loops}

    # An extrusion edge is an edge that shares a single vertex with a profile
    # face and is not on the plane of the face.
    def detect_extrusion_edge(self, bm, profile_face):
        bm.edges.ensure_lookup_table()
        extrusion = None
        face_verts_set = set(profile_face.verts)
        for edge in bm.edges:
            unshared_verts = set(edge.verts) - face_verts_set
            if len(unshared_verts) == 1:
                unshared_vert = unshared_verts.pop()
                if (
                    abs(
                        mathutils.geometry.distance_point_to_plane(
                            unshared_vert.co, profile_face.verts[0].co, profile_face.normal
                        )
                    )
                    > 1e-6
                ):
                    if unshared_vert == edge.verts[1]:
                        return [edge.verts[0].index, edge.verts[1].index]
                    return [edge.verts[1].index, edge.verts[0].index]

    def create_extruded_area_solid(self, mesh, extrusion_indices, profile_def):
        position = self.create_ifc_axis_2_placement_3d(
            profile_def["curve_ucs"]["center"], profile_def["curve_ucs"]["z_axis"], profile_def["curve_ucs"]["x_axis"]
        )
        direction = self.get_extrusion_direction(mesh, extrusion_indices, profile_def["curve_ucs"])
        unit_direction = direction.normalized()
        return self.file.createIfcExtrudedAreaSolid(
            profile_def["curve"],
            position,
            self.file.createIfcDirection((unit_direction.x, unit_direction.y, unit_direction.z)),
            self.convert_si_to_unit(direction.length),
        )

    def create_arbitrary_closed_profile_def(self, mesh, profile_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        outer_curve = self.create_polyline_from_loop(mesh, profile_indices, curve_ucs)
        curve = self.file.createIfcArbitraryClosedProfileDef("AREA", None, outer_curve)
        return {"curve_ucs": curve_ucs, "curve": curve}

    def create_arbitrary_profile_def_with_voids(self, mesh, profile_indices, inner_curve_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        outer_curve = self.create_polyline_from_loop(mesh, profile_indices, curve_ucs)
        inner_curves = [
            self.create_polyline_from_loop(mesh, curve_indices, curve_ucs) for curve_indices in inner_curve_indices
        ]
        curve = self.file.createIfcArbitraryProfileDefWithVoids("AREA", None, outer_curve, inner_curves)
        return {"curve_ucs": curve_ucs, "curve": curve}

    def create_rectangle_profile_def(self, mesh, profile_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        xdim = self.convert_si_to_unit(
            (mesh.vertices[profile_indices[0]].co - mesh.vertices[profile_indices[1]].co).length
        )
        ydim = self.convert_si_to_unit(
            (mesh.vertices[profile_indices[1]].co - mesh.vertices[profile_indices[2]].co).length
        )
        position = None
        if self.file.schema == "IFC2X3":
            position = self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint([0.0, 0.0]))
        curve = self.file.createIfcRectangleProfileDef("AREA", None, position, xdim, ydim)
        return {"curve_ucs": curve_ucs, "curve": curve}

    def create_circle_profile_def(self, mesh, profile_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        radius = self.convert_si_to_unit(
            abs(
                (
                    mesh.vertices[profile_indices[0]].co
                    - mesh.vertices[profile_indices[int(len(profile_indices) / 2)]].co
                ).length
            )
            / 2
        )
        center = Vector((0, 0))
        position = self.create_ifc_axis_2_placement_2d(center, Vector((1, 0)))
        curve = self.file.createIfcCircleProfileDef("AREA", None, position, radius)
        return {"curve_ucs": curve_ucs, "curve": curve}

    # Not used anywhere, but probably useful in the future
    def get_loop_from_v_indices(self, obj, indices):
        edges = self.get_edges_in_v_indices(obj, indices)
        loop = self.get_loop_from_edges(edges)
        loop.pop(-1)
        return loop

    def get_loop_from_edges(self, edges):
        while edges:
            currentEdge = edges.pop()
            startVert = currentEdge.vertices[0]
            endVert = currentEdge.vertices[1]
            polyLine = [startVert, endVert]
            ok = 1
            while ok:
                ok = 0
                i = len(edges)
                while i:
                    i -= 1
                    ed = edges[i]
                    if ed.vertices[0] == endVert:
                        polyLine.append(ed.vertices[1])
                        endVert = polyLine[-1]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[1] == endVert:
                        polyLine.append(ed.vertices[0])
                        endVert = polyLine[-1]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[0] == startVert:
                        polyLine.insert(0, ed.vertices[1])
                        startVert = polyLine[0]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[1] == startVert:
                        polyLine.insert(0, ed.vertices[0])
                        startVert = polyLine[0]
                        ok = 1
                        del edges[i]
            return polyLine

    def get_edges_in_v_indices(self, obj, indices):
        return [e for e in obj.data.edges if (e.vertices[0] in indices and e.vertices[1] in indices)]

    def get_curve_profile_coordinate_system(self, mesh, loop):
        profile_face = bpy.data.meshes.new("profile_face")
        profile_verts = [(mesh.vertices[p].co.x, mesh.vertices[p].co.y, mesh.vertices[p].co.z) for p in loop]
        profile_faces = [tuple(range(0, len(profile_verts)))]
        profile_face.from_pydata(profile_verts, [], profile_faces)
        center = profile_face.polygons[0].center
        if (mesh.vertices[loop[1]].co - mesh.vertices[loop[0]].co).length < 0.01:
            x_axis = (mesh.vertices[loop[0]].co - center).normalized()
        else:
            x_axis = (mesh.vertices[loop[1]].co - mesh.vertices[loop[0]].co).normalized()
        z_axis = profile_face.polygons[0].normal.normalized()
        y_axis = z_axis.cross(x_axis).normalized()
        matrix = Matrix((x_axis, y_axis, z_axis))
        matrix.normalize()
        return {
            "center": center,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "z_axis": z_axis,
            "matrix": matrix.to_4x4() @ Matrix.Translation(-center),
        }

    def convert_si_to_unit(self, co):
        return co / self.unit_scale

    def create_polyline_from_loop(self, mesh, loop, curve_ucs):
        points = []
        for point in loop:
            transformed_point = curve_ucs["matrix"] @ mesh.vertices[point].co
            points.append(self.create_cartesian_point(transformed_point.x, transformed_point.y))
        points.append(points[0])
        return self.file.createIfcPolyline(points)

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def get_extrusion_direction(self, mesh, extrusion_indices, curve_ucs):
        return curve_ucs["matrix"] @ (
            curve_ucs["center"] + (mesh.vertices[extrusion_indices[1]].co - mesh.vertices[extrusion_indices[0]].co)
        )

    def get_start_and_end_of_extrusion(self, profile_points, extrusion_edge):
        if extrusion_edge.vertices[0] in profile_points:
            return (extrusion_edge.vertices[0], extrusion_edge.vertices[1])
        return (extrusion_edge.vertices[1], extrusion_edge.vertices[0])

    def create_ifc_axis_2_placement_2d(self, point, forward):
        return self.file.createIfcAxis2Placement2D(
            self.create_cartesian_point(point.x, point.y), self.file.createIfcDirection((forward.x, forward.y))
        )

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.create_cartesian_point(point.x, point.y, point.z),
            self.file.createIfcDirection((up.x, up.y, up.z)),
            self.file.createIfcDirection((forward.x, forward.y, forward.z)),
        )
