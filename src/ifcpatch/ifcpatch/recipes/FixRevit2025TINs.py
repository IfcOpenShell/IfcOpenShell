# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.


import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import logging
from typing import Optional


class Patcher:
    def __init__(
        self, file: None, logger: logging.Logger, filepath: str, is_solid: bool = True, should_create_edges: bool = True
    ):
        """Fix missing or spot-coordinate bugged TINs loading in Revit

        TINs exported from 12D or Civil 3D may contain dense or highly obtuse
        triangles.  Although these will load in Revit, you will not be able to
        use Revit's Spot Coordinate or Spot Elevation tool.

        See bug: https://github.com/Autodesk/revit-ifc/issues/511

        If `is_solid` is enabled, we assume the surface is represented as a
        solid (e.g. I have come across surfaces which are extruded by 1mm from
        Civil 3D). The solution will delete any faces with a Z normal less
        than 0.5. In case the mesh has any side faces or thickness, this should
        leave only the top surface which is relevant for spot coordinates and
        elevations.

        Vertices closer than 10mm will also be merged to prevent dense
        portions of the TIN at a minor sacrifice of surveying accuracy. It will
        also triangulate all meshes to prevent non-coplanar surfaces, and
        delete any obtuse triangles where one of their XY angles is less than
        0.3 degrees.  Therefore the result will contain some minor "holes" in
        the TIN, but these holes will only be in dense triangles that Revit
        can't handle anyway and won't affect most coordination tasks.

        After that, it will:

        1. Reassign everything to an IfcGeographicElement
        2. Detect boundary edges and create an edge-only IfcVirtualElement.
            Good for clean viz in Revit.
        3. Create a copy of the object which has no sharp faces. This will
            allow Revit's spot coordinate tool to work on any arbitrary face
            surface. Note that Revit cannot snap to edges or vertices on this
            object.
        4. Create a copy of the obejct which has one artifically injected sharp
            face. This trick allows Revit's spot coordinate tool to snap to
            edges and points. However, Revit cannot sample an arbitrary
            surface. By combining this object with the previous object, you get
            the best of both worlds.

        If you're thinking that this overlapping, Z-fighting, duplication of
        objects with arbitrary almost-degenerate triangles being added is a
        horrific abomination in the world of software workarounds, you are
        absolutely correct.

        This is a variation of FixRevitTINs which has been tested on Revit <=
        2023. I've tested this one on Revit 2025 (the behaviour has changed).

        Note that you may may want to run other tools like
        OffsetObjectPlacements or ResetAbsoluteCoordinates to fix large
        coordinates as these can also cause issues in Revit (such as inaccuracy
        or inability to use the Spot Coordinate / Elevation tool).

        This patch is designed to work on any TIN-like export, typically coming
        from civil software. It also requires you to run it using Blender, as
        the geometric modification uses the Blender geometry engine.

        `filepath` argument is required for this recipe, `file` argument is
        ignored.

        :param filepath: The filepath of the IFC model. This is required to
            load into Bonsai.
        :param is_solid: If true, assume a thickness and delete anything that
            isn't the top face.
        :param should_create_edges: If true, a new IfcVirtualElement is created
            representing the perimeter of the objects. This allows you to to
            hide regular surface edges in Revit and only use the perimeter edge
            for visualisation.
        :filter_glob filepath: *.ifc;*.ifczip;*.ifcxml

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "recipe": "FixRevit2025TINs", "arguments": []})
        """
        self.file = file
        self.filepath = filepath
        self.logger = logger
        self.is_solid = is_solid
        self.should_create_edges = should_create_edges

    def patch(self) -> None:
        import bpy
        import bmesh
        import bonsai.tool as tool
        import ifcopenshell.util.shape_builder

        bpy.context.scene.BIMProjectProperties.should_use_native_meshes = True
        bpy.ops.bim.load_project(filepath=self.filepath)

        old_history_size = tool.Ifc.get().history_size
        old_undo_steps = bpy.context.preferences.edit.undo_steps
        tool.Ifc.get().history_size = 0
        bpy.context.preferences.edit.undo_steps = 0

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id or not obj.data:
                continue
            if not obj.data.polygons:
                continue
            element = tool.Ifc.get_entity(obj)
            element.PredefinedType = "USERDEFINED"
            element.ObjectType = "TIN"
            element = ifcopenshell.util.schema.reassign_class(tool.Ifc.get(), element, "IfcGeographicElement")

            bm = bmesh.new()
            bm.from_mesh(obj.data)
            faces_to_delete = []
            if self.is_solid:
                for face in bm.faces:
                    global_normal = obj.matrix_world.to_3x3() @ face.normal
                    if global_normal.z < 0.5:
                        faces_to_delete.append(face)
            bmesh.ops.delete(bm, geom=faces_to_delete, context="FACES_ONLY")
            bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()

            if self.should_create_edges:
                self.create_edges(obj)

            self.create_face_sampleable_object(obj)
            self.create_edge_sampleable_object(obj)

        tool.Ifc.get().history_size = old_history_size
        bpy.context.preferences.edit.undo_steps = old_undo_steps

        self.file = tool.Ifc.get()

    def create_edges(self, obj):
        import bpy
        import bmesh
        import bonsai.tool as tool
        import ifcopenshell.util.element
        import ifcopenshell.util.representation
        import ifcopenshell.api.root
        import ifcopenshell.api.type
        import ifcopenshell.api.spatial
        import ifcopenshell.api.geometry

        element = tool.Ifc.get_entity(obj)
        data = obj.data
        bm = bmesh.new()
        bm.from_mesh(data)

        bm.faces.ensure_lookup_table()

        if self.is_solid:
            faces_to_delete = []
            for face in bm.faces:
                if face.normal.z < 0.5:
                    faces_to_delete.append(face)
            bmesh.ops.delete(bm, geom=faces_to_delete, context="FACES_ONLY")

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)

        edges_to_delete = []
        bm.faces.ensure_lookup_table()
        for edge in bm.edges:
            if len(edge.link_faces) != 1:
                edges_to_delete.append(edge)

        bmesh.ops.delete(bm, geom=edges_to_delete, context="EDGES_FACES")
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            vert.co.z += 0.003

        mesh = bpy.data.meshes.new("Mesh")
        bm.to_mesh(mesh)

        obj = bpy.data.objects.new("Perimeter", mesh)
        bpy.context.scene.collection.objects.link(obj)
        with bpy.context.temp_override(**tool.Blender.get_viewport_context()):
            tool.Blender.select_and_activate_single_object(bpy.context, obj)
            bpy.ops.object.convert(target="CURVE")

        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

        if self.file.schema == "IFC2X3":
            curves = self.create_curves_from_curve_ifc2x3(is_2d=False, curve_object_data=obj.data)
        else:
            curves = self.create_curves_from_curve(is_2d=False, curve_object_data=obj.data)

        representation = tool.Ifc.get().createIfcShapeRepresentation(
            context, context.ContextIdentifier, "Curve3D", curves
        )

        element2 = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=element)
        element2.Name += "-boundary"
        element2.ObjectType = "TINBOUNDARY"
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element2, representation)
        ifcopenshell.util.schema.reassign_class(tool.Ifc.get(), element2, "IfcVirtualElement")
        bm.free()

    def create_face_sampleable_object(self, obj):
        # No sharp faces
        import bpy
        import bmesh
        import bonsai.tool as tool
        import ifcopenshell.util.element
        import ifcopenshell.util.representation
        import ifcopenshell.api.root
        import ifcopenshell.api.type
        import ifcopenshell.api.spatial
        import ifcopenshell.api.geometry
        from math import degrees

        print("working on ", obj.name)
        element = tool.Ifc.get_entity(obj)
        data = obj.data
        bm = bmesh.new()
        bm.from_mesh(data)

        bm.faces.ensure_lookup_table()

        angle_threshold = 0.3
        for polygon in bm.faces:
            try:
                v1, v2, v3 = [v.co for v in polygon.verts]
                d1 = degrees((v2 - v1).angle(v3 - v1))
                d2 = degrees((v3 - v2).angle(v1 - v2))
                d3 = degrees((v1 - v3).angle(v2 - v3))
                if d1 < angle_threshold or d2 < angle_threshold or d3 < angle_threshold:
                    print("removing", d1, d2, d3, polygon)
                    bm.faces.remove(polygon)
            except:
                print("removing", polygon)
                bm.faces.remove(polygon)

        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        verts = [v.co / self.unit_scale for v in bm.verts]
        faces = [[v.index for v in p.verts] for p in bm.faces]
        item = builder.mesh(verts, faces)
        representation = builder.get_representation(context, [item])
        element2 = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=element)
        element2.Name += "-face-sample"
        print("new", element2, element)
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element2, representation)

        bm.free()

    def create_edge_sampleable_object(self, obj):
        # This is crazy but we need a sharp face per island
        import bpy
        import bmesh
        import bonsai.tool as tool
        import ifcopenshell.util.element
        import ifcopenshell.util.representation
        import ifcopenshell.api.root
        import ifcopenshell.api.type
        import ifcopenshell.api.spatial
        import ifcopenshell.api.geometry
        from math import degrees, radians, sin
        from mathutils import Matrix

        # Get the active object (assumed to have a mesh)
        mesh = obj.data

        # Create a BMesh representation
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # First purge existing sharp edges (don't ask me why, really don't)
        bm.faces.ensure_lookup_table()
        angle_threshold = 0.3
        for polygon in bm.faces:
            try:
                # v1, v2, v3 = [v.co.to_2d() for v in polygon.verts]
                v1, v2, v3 = [v.co for v in polygon.verts]
                d1 = degrees((v2 - v1).angle(v3 - v1))
                d2 = degrees((v3 - v2).angle(v1 - v2))
                d3 = degrees((v1 - v3).angle(v2 - v3))
                if d1 < angle_threshold or d2 < angle_threshold or d3 < angle_threshold:
                    print("removing", d1, d2, d3, polygon)
                    bm.faces.remove(polygon)
            except:
                print("removing", polygon)
                bm.faces.remove(polygon)
        bm.faces.ensure_lookup_table()

        # Now we add our own.

        # A set to mark faces that have been visited
        visited_faces = set()

        def get_island(start_face):
            """Return the connected set of faces (a 'mesh island') starting from start_face."""
            island = set()
            stack = [start_face]
            while stack:
                f = stack.pop()
                if f in island:
                    continue
                island.add(f)
                for edge in f.edges:
                    # For every face sharing this edge, add to the stack
                    for f2 in edge.link_faces:
                        if f2 not in island:
                            stack.append(f2)
            return island

        # Loop over all faces and process each island once
        islands_count = 0
        for face in bm.faces:
            if face in visited_faces:
                continue

            # Get the connected component (island) containing this face
            island = get_island(face)
            visited_faces |= island  # mark all island faces as visited
            islands_count += 1

            boundary_edge = None
            for face in island:
                for edge in face.edges:
                    # Count how many faces in the island use this edge.
                    count = sum(1 for f in edge.link_faces if f in island)
                    if count == 1:
                        boundary_edge = edge
                        break
                if boundary_edge:
                    break

            # If no boundary edge is found, skip this island.
            if boundary_edge is None:
                continue

            # Use the two vertices of the boundary edge as A and B.
            A, B = boundary_edge.verts[0], boundary_edge.verts[1]

            # THIRD ATTEMPT

            # Use the normal from the boundary face (i.e. the single linked face of the boundary edge)
            base_face = boundary_edge.link_faces[0]
            plane_normal = (
                base_face.normal.copy()
            )  # This normal defines the plane in which we'll construct the triangle

            # Compute the edge AB vector and its length.
            AB_vec = B.co - A.co
            d = AB_vec.length
            if d == 0:
                continue  # degenerate edge

            # --- Desired angles for the new triangle (in degrees) ---
            # This is the crazy degenerate triangle
            angle_A_deg = 0.004  # angle at vertex A
            angle_B_deg = 1.146  # angle at vertex B
            angle_C_deg = 178.85  # angle at vertex C (note: 180 - (0.004 + 1.146) = 178.85)

            # Convert angles to radians.
            angle_A = radians(angle_A_deg)
            angle_B = radians(angle_B_deg)
            angle_C = radians(angle_C_deg)

            # --- Use the law of sines to compute the new triangle's side lengths ---
            # In triangle ABC, with AB opposite angle C:
            #       AB / sin(angle_C) = AC / sin(angle_B) = BC / sin(angle_A)
            # We'll compute AC (from A) as it is needed to place the new vertex.
            AC_length = d * sin(angle_B) / sin(angle_C)

            # --- Determine the direction for AC in the triangle's plane ---
            # Starting at A, the direction of AB is our baseline.
            u = AB_vec.normalized()

            # To get the direction for AC, rotate u by angle_A about the plane_normal.
            rot_mat = Matrix.Rotation(angle_A, 3, plane_normal)
            dA = u.copy()
            dA.rotate(rot_mat)

            # Compute the position for the new vertex C.
            C_co = A.co + AC_length * dA

            # --- Create the new vertex and triangle face in the BMesh ---
            new_vert = bm.verts.new(C_co)
            bm.verts.index_update()  # update indices if needed

            # Create the new triangle face from vertices A, B, and new_vert.
            # (The order of vertices may be adjusted if you need a specific winding.)
            try:
                new_face = bm.faces.new((A, B, new_vert))
                visited_faces.add(new_face)
                print("added new face")
            except ValueError:
                # Face already exists or some error occurred
                print("Could not create face on island", islands_count)

        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        verts = [v.co / self.unit_scale for v in bm.verts]
        faces = [[v.index for v in p.verts] for p in bm.faces]
        item = builder.mesh(verts, faces)
        representation = builder.get_representation(context, [item])
        element = tool.Ifc.get_entity(obj)
        element2 = ifcopenshell.api.root.copy_class(tool.Ifc.get(), product=element)
        element2.Name += "-edge-sample"
        print("new", element2, element)
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element2, representation)

        bm.free()

        print("Added a triangle to", islands_count, "mesh island(s).")
        return

    def create_curves_from_curve_ifc2x3(
        self, is_2d: bool = False, curve_object_data=None
    ) -> list[ifcopenshell.entity_instance]:
        import bonsai.tool as tool

        dim = (lambda v: v.xy) if is_2d else (lambda v: v.xyz)
        results = []
        for spline in curve_object_data.splines:
            points = spline.bezier_points[:] + spline.points[:]
            if spline.use_cyclic_u:
                points.append(points[0])
            ifc_points = [self.create_cartesian_point(*dim(point.co)) for point in points]
            results.append(tool.Ifc.get().createIfcPolyline(ifc_points))
        return results

    def create_curves_from_curve(
        self, is_2d: bool = False, curve_object_data=None
    ) -> list[ifcopenshell.entity_instance]:
        import bonsai.tool as tool
        import numpy as np

        dim = (lambda v: v.xy) if is_2d else (lambda v: v.xyz)
        to_units = lambda v: np.array([self.convert_si_to_unit(i) for i in v])
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        results = []

        for spline in curve_object_data.splines:
            points = spline.bezier_points[:] + spline.points[:]

            points = [to_units(dim(p.co)) for p in points]
            closed_polyline = spline.use_cyclic_u and len(points) > 1
            results.append(builder.polyline(points, closed=closed_polyline))

        return results

    def create_cartesian_point(
        self, x: float, y: float, z: Optional[float] = None, is_model_coords: bool = True
    ) -> ifcopenshell.entity_instance:
        """Create IfcCartesianPoint.

        x, y, z coords are provided in SI units.
        """
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_curves_from_mesh(self, geom_data) -> list[ifcopenshell.entity_instance]:
        curves = []
        points = self.create_cartesian_point_list_from_vertices(geom_data.vertices)
        edge_loops = []
        previous_edge = None
        edge_loop = []
        for i, edge in enumerate(geom_data.edges):
            if previous_edge is None:
                edge_loop = [self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1))]
            elif edge.vertices[0] == previous_edge.vertices[1]:
                edge_loop.append(self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1)))
            else:
                edge_loops.append(edge_loop)
                edge_loop = [self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1))]
            previous_edge = edge
        edge_loops.append(edge_loop)
        for edge_loop in edge_loops:
            curves.append(self.file.createIfcIndexedPolyCurve(points, edge_loop))
        return curves

    def create_curves_from_mesh_ifc2x3(self, geom_data) -> list[ifcopenshell.entity_instance]:
        curves = []
        points = [self.create_cartesian_point(v.co.x, v.co.y, v.co.z) for v in geom_data.vertices]
        edge_loops = []
        previous_edge = None
        edge_loop = []
        for i, edge in enumerate(geom_data.edges):
            if previous_edge is None:
                edge_loop = [edge.vertices]
            elif edge.vertices[0] == previous_edge.vertices[1]:
                edge_loop.append(edge.vertices)
            else:
                edge_loops.append(edge_loop)
                edge_loop = [edge.vertices]
            previous_edge = edge
        edge_loops.append(edge_loop)
        for edge_loop in edge_loops:
            loop_points = [points[p[0]] for p in edge_loop]
            loop_points.append(points[edge_loop[-1][1]])
            curves.append(self.file.createIfcPolyline(loop_points))
        return curves

    def create_cartesian_point_list_from_vertices(self, vertices) -> ifcopenshell.entity_instance:
        import numpy as np
        from ifcopenshell.util.shape_builder import ifc_safe_vector_type

        # Catch values as floats to benefit from fast buffer copy.
        coords = np.empty(len(vertices) * 3, dtype="f")
        vertices.foreach_get("co", coords)
        coords = coords.reshape(-1, 3)
        coords_class = "IfcCartesianPointList3D"
        return self.file.create_entity(coords_class, ifc_safe_vector_type(self.convert_si_to_unit(coords)))

    def convert_si_to_unit(self, co):
        return co / self.unit_scale
