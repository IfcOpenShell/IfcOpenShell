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
import blenderbim.core.type
from math import pi
from mathutils import Vector, Matrix
from shapely import Polygon


class GenerateSpace(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_space"
    bl_label = "Generate Space"
    bl_options = {"REGISTER"}
    bl_description = "Create a space from the cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        collection = context.view_layer.active_layer_collection.collection
        collection_obj = bpy.data.objects.get(collection.name)
        return tool.Ifc.get_entity(collection_obj)

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # layered walls (i.e. prismatic) in the currently active storey (though
        # we can easily extend it to include other "bounding" elements). For
        # now we generate rooms that exclude walls (i.e. not to wall midpoint
        # or exterior / interior edge).

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
        collection_obj = bpy.data.objects.get(collection.name)
        if not collection_obj:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return
        spatial_element = tool.Ifc.get_entity(collection_obj)
        if not spatial_element:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return

        active_obj = bpy.context.active_object
        element = None
        if bpy.context.selected_objects and active_obj:
            element = tool.Ifc.get_entity(active_obj)
            x, y, z = active_obj.matrix_world.translation.xyz
            mat = active_obj.matrix_world
            h = active_obj.dimensions.z
        else:
            x, y = context.scene.cursor.location.xy
            z = collection_obj.matrix_world.translation.z
            mat = Matrix()
            mat[0][3], mat[1][3], mat[2][3] = x, y, z
            h = 3

        boundary_elements = []
        for subelement in ifcopenshell.util.element.get_decomposition(spatial_element):
            if subelement.is_a("IfcWall") and tool.Model.get_usage_type(subelement) == "LAYER2":
                boundary_elements.append(subelement)

        boundary_lines = []
        for boundary_element in boundary_elements:
            obj = tool.Ifc.get_object(boundary_element)
            if not obj:
                continue
            axis = self.get_wall_axis(obj)
            for ypos in ["miny", "maxy"]:
                start, end = axis[ypos]
                offset = (end - start).normalized() * 0.3  # Offset wall lines by 300mm
                boundary_lines.append(shapely.LineString([start - offset, end + offset]))

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

    def get_wall_axis(self, obj):
        x_values = [v[0] for v in obj.bound_box]
        y_values = [v[1] for v in obj.bound_box]
        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)
        return {
            "miny": [
                (obj.matrix_world @ Vector((min_x, min_y, 0.0))).to_2d(),
                (obj.matrix_world @ Vector((max_x, min_y, 0.0))).to_2d(),
            ],
            "maxy": [
                (obj.matrix_world @ Vector((min_x, max_y, 0.0))).to_2d(),
                (obj.matrix_world @ Vector((max_x, max_y, 0.0))).to_2d(),
            ],
        }


class GenerateSpacesFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_spaces_from_walls"
    bl_label = "Generate Spaces From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Generate spaces from selected walls. The active object must be a wall."

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        return context.selected_objects and element.is_a("IfcWall")

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active objct must be a wall and
        # have to be selected walls
        props = context.scene.BIMModelProperties

        active_obj = bpy.context.active_object
        if not active_obj:
            self.report({'ERROR'}, "No active object. Please select a wall")
            return

        element = None
        element = tool.Ifc.get_entity(active_obj)
        if not element.is_a("IfcWall"):
            self.report({'ERROR'}, "The active object is not a wall. Please select a wall.")
            return

        collection = active_obj.users_collection[0]
        collection_obj = bpy.data.objects.get(collection.name)
        if not collection_obj:
            self.report({'ERROR'}, "No collection found. Please insert one.")
            return

        spatial_element = tool.Ifc.get_entity(collection_obj)
        if not spatial_element:
            self.report({'ERROR'}, "The collection hasn't an ifc space entity. Please provide one.")
            return

        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "No selected objects found. Please select walls.")
            return

        x, y, z = active_obj.matrix_world.translation.xyz
        mat = active_obj.matrix_world
        h = active_obj.dimensions.z

        boundary_elements = []
        for obj in bpy.context.selected_objects:
            subelement = tool.Ifc.get_entity(obj)
            if subelement.is_a("IfcWall"):
                boundary_elements.append(subelement)

        polys = []
        for boundary_element in boundary_elements:
            obj = tool.Ifc.get_object(boundary_element)
            if not obj:
                continue
            points = []
            base = self.get_obj_base_points(obj)
            for index in ["low_left", "low_right", "high_right", "high_left"]:
                point = base[index]
                points.append(point)

            polys.append(Polygon(points))

        model = tool.Ifc.get()

        project_unit = ifcopenshell.util.unit.get_project_unit(model, "LENGTHUNIT")
        prefix=getattr(project_unit, "Prefix", None)

        tolerance = 0.03

        converted_tolerance = ifcopenshell.util.unit.convert(
                                                        value = tolerance,
                                                        from_prefix = None,
                                                        from_unit = "METRE",
                                                        to_prefix = prefix,
                                                        to_unit = project_unit.Name,
                                                        )


        union = shapely.ops.unary_union(polys).buffer(converted_tolerance, cap_style = 2, join_style = 2)

        i=0
        for linear_ring in union.interiors:
            poly = Polygon(linear_ring)

            poly = poly.buffer(converted_tolerance, single_sided=True, cap_style = 2, join_style = 2)

            bm = bmesh.new()
            bm.verts.index_update()
            bm.edges.index_update()

            mat_invert = mat.inverted()

            new_verts = [bm.verts.new(mat_invert @ Vector([v[0], v[1], 0])) for v in poly.exterior.coords[0:-1]]
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

            bmesh.ops.recalc_face_normals(bm, faces = bm.faces)

            name = "Space" + str(i)
            mesh = bpy.data.meshes.new(name = name)
            bm.to_mesh(mesh)
            bm.free()

            obj = bpy.data.objects.new(name, mesh)
            obj.matrix_world = mat
            collection.objects.link(obj)

            bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcSpace")
            i+=1

        return {"FINISHED"}


    def get_obj_base_points(self, obj):
        x_values = [(obj.matrix_world @ Vector(v)).x for v in obj.bound_box]
        y_values = [(obj.matrix_world @ Vector(v)).y for v in obj.bound_box]
        return {
            "low_left": (x_values[0], y_values[0]),
            "high_left": (x_values[3], y_values[3]),
            "low_right": (x_values[4], y_values[4]),
            "high_right": (x_values[7], y_values[7]),
        }


