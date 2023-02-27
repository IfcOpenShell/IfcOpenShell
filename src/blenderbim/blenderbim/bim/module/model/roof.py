# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


import bpy
import bmesh
import shapely
import blenderbim.tool as tool
from math import tan, radians
from mathutils import Vector, Matrix
from bpypolyskel import bpypolyskel


class GenerateHippedRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_hipped_roof"
    bl_label = "Generate Hipped Roof"
    bl_options = {"REGISTER"}
    mode: bpy.props.StringProperty(default="ANGLE")
    height: bpy.props.FloatProperty(default=1)
    angle: bpy.props.FloatProperty(default=10)

    def _execute(self, context):
        obj = bpy.context.active_object
        if not obj:
            return

        boundary_lines = []

        for edge in obj.data.edges:
            boundary_lines.append(
                shapely.LineString([obj.data.vertices[edge.vertices[0]].co, obj.data.vertices[edge.vertices[1]].co])
            )

        unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
        closed_polygons = shapely.polygonize(unioned_boundaries.geoms)

        roof_polygon = None
        biggest_area = 0
        for polygon in closed_polygons.geoms:
            area = polygon.area
            if area > biggest_area:
                roof_polygon = polygon
                biggest_area = area

        roof_polygon = shapely.force_3d(roof_polygon)

        if not shapely.is_ccw(roof_polygon):
            roof_polygon = roof_polygon.reverse()

        # Define vertices for the base footprint of the building at height 0.0
        # counterclockwise order
        verts = [Vector(v) for v in roof_polygon.exterior.coords[0:-1]]
        total_exterior_verts = len(verts)
        next_index = total_exterior_verts

        inner_loops = None
        for interior in roof_polygon.interiors:
            if inner_loops is None:
                inner_loops = []
            loop = interior.coords[0:-1]
            total_verts = len(loop)
            verts.extend([Vector(v) for v in loop])
            inner_loops.append((next_index, total_verts))
            next_index += total_verts

        unit_vectors = None  # we have no unit vectors, let them computed by polygonize()
        start_exterior_index = 0

        faces = []

        if self.mode == "HEIGHT":
            height = self.height
            angle = 0.0
        else:
            angle = tan(radians(round(self.angle, 4)))
            height = 0.0

        faces = bpypolyskel.polygonize(
            verts, start_exterior_index, total_exterior_verts, inner_loops, height, angle, faces, unit_vectors
        )

        edges = []
        mesh = bpy.data.meshes.new(name="Building_with_Roof")
        mesh.from_pydata(verts, edges, faces)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        extrusion = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
        extruded_verts = [g for g in extrusion["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=[0.0, 0.0, 0.1], verts=extruded_verts)

        bm.to_mesh(mesh)
        bm.free()

        obj.data = mesh
