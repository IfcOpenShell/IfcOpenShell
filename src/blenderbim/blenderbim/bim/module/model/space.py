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
import ifcopenshell
import ifcopenshell.util.element
import blenderbim.tool as tool
import blenderbim.core.spatial as core
import blenderbim.core.type
from math import pi
from mathutils import Vector, Matrix
from shapely import Polygon, MultiPolygon


class GenerateSpace(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_space"
    bl_label = "Generate Space"
    bl_options = {"REGISTER"}
    bl_description = "Create a space from the cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        return tool.Ifc.get_entity(collection_obj)

    def _execute(self, context):
        # This works as a 2.5 extruded polygon based on a cutting plane. Note
        # that rooms exclude walls (i.e. not to wall midpoint or exterior /
        # exterior edge.

        def msg(self, context):
            self.layout.label(text="NO ACTIVE STOREY")

        props = context.scene.BIMModelProperties
        relating_type_id = props.relating_type_id
        relating_type = None
        if relating_type_id:
            relating_type = tool.Ifc.get().by_id(int(relating_type_id))
            if not relating_type.is_a("IfcSpaceType"):
                relating_type = None

        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        if not collection_obj:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return
        spatial_element = tool.Ifc.get_entity(collection_obj)
        if not spatial_element:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return

#       core.generate_space(tool.Ifc, tool.Spatial)






        active_obj = bpy.context.active_object
        element = None
        if bpy.context.selected_objects and active_obj:
            element = tool.Ifc.get_entity(active_obj)
            mat = active_obj.matrix_world
            local_bbox_center = 0.125 * sum((Vector(b) for b in active_obj.bound_box), Vector())
            global_bbox_center = mat @ local_bbox_center
            x = global_bbox_center.x
            y = global_bbox_center.y
            z = (mat @ Vector(active_obj.bound_box[0])).z

            h = active_obj.dimensions.z
        else:
            x, y = context.scene.cursor.location.xy
            z = collection_obj.matrix_world.translation.z
            mat = Matrix()
            mat.translation = (x, y, z)
            h = 3

        calculation_rl = context.scene.BIMModelProperties.rl3
        self.cut_point = collection_obj.matrix_world.translation.copy() + Vector((0, 0, calculation_rl))
        self.cut_normal = Vector((0, 0, 1))
        boundary_lines = []

        gross_settings = ifcopenshell.geom.settings()
        gross_settings.set(gross_settings.DISABLE_OPENING_SUBTRACTIONS, True)

        for obj in bpy.context.visible_objects:
            visible_element = tool.Ifc.get_entity(obj)

            if (
                not visible_element
                or obj.type != "MESH"
                or not self.is_bounding_class(visible_element)
                or not tool.Drawing.is_intersecting_plane(obj, self.cut_point, self.cut_normal)
            ):
                continue

            old_mesh = None
            if visible_element.HasOpenings:
                new_mesh = self.create_mesh(ifcopenshell.geom.create_shape(gross_settings, visible_element))
                old_mesh = obj.data
                obj.data = new_mesh

            local_cut_point = obj.matrix_world.inverted() @ self.cut_point
            local_cut_normal = obj.matrix_world.inverted().to_quaternion() @ self.cut_normal
            verts, edges = tool.Drawing.bisect_mesh_with_plane(obj, local_cut_point, local_cut_normal)

            if old_mesh:
                obj.data = old_mesh
                bpy.data.meshes.remove(new_mesh)

            for edge in edges or []:
                boundary_lines.append(
                    shapely.LineString(
                        [Vector((round(x, 3) for x in verts[edge[0]])), Vector((round(x, 3) for x in verts[edge[1]]))]
                    )
                )

        unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
        closed_polygons = shapely.polygonize(unioned_boundaries.geoms)

        space_polygon = None
        for polygon in closed_polygons.geoms:
            if shapely.contains_xy(polygon, x, y):
                space_polygon = shapely.force_3d(polygon)

        if not space_polygon:
            return

        bm = bmesh.new()
        bm.verts.index_update()
        bm.edges.index_update()

        mat_invert = mat.inverted()
        new_verts = [bm.verts.new(mat_invert @ Vector([v[0], v[1], z])) for v in space_polygon.exterior.coords[0:-1]]
        [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
        bm.edges.new((new_verts[len(new_verts) - 1], new_verts[0]))

        for interior in space_polygon.interiors:
            new_verts = [bm.verts.new(mat_invert @ Vector([v[0], v[1], z])) for v in interior.coords[0:-1]]
            [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
            bm.edges.new((new_verts[len(new_verts) - 1], new_verts[0]))

        bm.verts.index_update()
        bm.edges.index_update()

        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.triangle_fill(bm, edges=bm.edges)
        bmesh.ops.dissolve_limit(bm, angle_limit=pi / 180 * 5, verts=bm.verts, edges=bm.edges)

        extrusion = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
        extruded_verts = [g for g in extrusion["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=[0.0, 0.0, h], verts=extruded_verts)

        mesh = bpy.data.meshes.new(name="Space")
        bm.to_mesh(mesh)
        bm.free()

        if element and element.is_a("IfcSpace"):
            mesh.name = active_obj.data.name
            mesh.BIMMeshProperties.ifc_definition_id = active_obj.data.BIMMeshProperties.ifc_definition_id
            tool.Geometry.change_object_data(active_obj, mesh, is_global=True)
            tool.Ifc.edit(active_obj)
        else:
            if relating_type:
                name = tool.Model.generate_occurrence_name(relating_type, "IfcSpace")
            else:
                name = "Space"
            obj = bpy.data.objects.new("Space", mesh)
            obj.matrix_world = mat
            collection.objects.link(obj)
            bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcSpace")
            element = tool.Ifc.get_entity(obj)
            if relating_type:
                blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

    def is_bounding_class(self, element):
        for ifc_class in ["IfcWall", "IfcColumn", "IfcMember", "IfcVirtualElement", "IfcPlate"]:
            if element.is_a(ifc_class):
                return True
        return False

    def create_mesh(self, shape):
        geometry = shape.geometry
        mesh = bpy.data.meshes.new("tmp")
        verts = geometry.verts
        if geometry.faces:
            num_vertices = len(verts) // 3
            total_faces = len(geometry.faces)
            loop_start = range(0, total_faces, 3)
            num_loops = total_faces // 3
            loop_total = [3] * num_loops
            num_vertex_indices = len(geometry.faces)

            mesh.vertices.add(num_vertices)
            mesh.vertices.foreach_set("co", verts)
            mesh.loops.add(num_vertex_indices)
            mesh.loops.foreach_set("vertex_index", geometry.faces)
            mesh.polygons.add(num_loops)
            mesh.polygons.foreach_set("loop_start", loop_start)
            mesh.polygons.foreach_set("loop_total", loop_total)
            mesh.polygons.foreach_set("use_smooth", [0] * total_faces)
            mesh.update()
        return mesh


class GenerateSpacesFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_spaces_from_walls"
    bl_label = "Generate Spaces From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Generate spaces from selected walls. The active object must be a wall"

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element:
            return context.selected_objects and element.is_a("IfcWall")

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        container = tool.Spatial.get_container(element)

        if not active_obj:
            self.report({"ERROR"}, "No active object. Please select a wall")
            return

        element = tool.Ifc.get_entity(active_obj)
        if element and not element.is_a("IfcWall"):
            return self.report({"ERROR"}, "The active object is not a wall. Please select a wall.")

        if not container:
            self.report({"ERROR"}, "The wall is not contained.")

        if not bpy.context.selected_objects:
            self.report({"ERROR"}, "No selected objects found. Please select walls.")
            return

        core.generate_spaces_from_walls(tool.Ifc, tool.Spatial, tool.Collector)

class ToggleSpaceVisibility(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_space_visibility"
    bl_label = "Toggle Space Visibility"
    bl_options = {"REGISTER"}
    bl_description = "Change the space visibility"

    def execute(cls, context):
        core.toggle_space_visibility(tool.Ifc, tool.Spatial)
        return {"FINISHED"}

