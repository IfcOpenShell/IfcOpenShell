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


class GenerateSpace(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_space"
    bl_label = "Generate Space"
    bl_options = {"REGISTER"}

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
