import bpy
import bmesh
import ifcopenshell
import ifcopenshell.util.unit
from math import pi
from mathutils import Vector, Matrix


class Helper:
    def __init__(self, file):
        self.file = file
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

    # We can detect a rectangular extrusion by picking any face, then find an
    # edge that shares a single vertex only with that face to find the extrusion
    # edge. A face with the normal facing down is prioritised. A limited
    # dissolve ensure that faces are quads and not tris.
    def auto_detect_rectangle_profile_extruded_area_solid(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 5, verts=bm.verts, edges=bm.edges)

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
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 5, verts=bm.verts, edges=bm.edges)

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
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 5, verts=bm.verts, edges=bm.edges)

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

    def detect_extrusion_edge(self, bm, profile_face):
        bm.edges.ensure_lookup_table()
        extrusion = None
        face_verts_set = set(profile_face.verts)
        for edge in bm.edges:
            unshared_verts = set(edge.verts) - face_verts_set
            if len(unshared_verts) == 1:
                if unshared_verts.pop() == edge.verts[1]:
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

    def create_rectangle_profile_def(self, mesh, profile_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        xdim = self.convert_si_to_unit(
            (mesh.vertices[profile_indices[0]].co - mesh.vertices[profile_indices[1]].co).length
        )
        ydim = self.convert_si_to_unit(
            (mesh.vertices[profile_indices[1]].co - mesh.vertices[profile_indices[2]].co).length
        )
        curve = self.file.createIfcRectangleProfileDef("AREA", None, None, xdim, ydim)
        return {"curve_ucs": curve_ucs, "curve": curve}

    def create_circle_profile_def(self, mesh, profile_indices):
        curve_ucs = self.get_curve_profile_coordinate_system(mesh, profile_indices)
        radius = self.convert_si_to_unit(
            abs((mesh.vertices[profile_indices[0]].co - mesh.vertices[profile_indices[int(len(profile_indices) / 2)]].co).length) / 2
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
