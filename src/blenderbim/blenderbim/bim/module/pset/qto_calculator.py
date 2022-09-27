# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, Vukas Pajic <vulepajic@gmail.om>
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

import bpy, bmesh
import mathutils
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils.bvhtree import BVHTree
import numpy as np
import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import blenderbim.tool as tool


class QtoCalculator:
    def guess_quantity(self, prop_name, alternative_prop_names, obj):
        prop_name = prop_name.lower()
        alternative_prop_names = [p.lower() for p in alternative_prop_names]
        if "length" in prop_name and "width" not in alternative_prop_names and "height" not in alternative_prop_names:
            return self.get_linear_length(obj)
        elif "length" in prop_name:
            return self.get_length(obj)
        elif "width" in prop_name and "length" not in alternative_prop_names:
            return self.get_length(obj)
        elif "width" in prop_name:
            return self.get_width(obj)
        elif "height" in prop_name or "depth" in prop_name:
            return self.get_height(obj)
        elif "perimeter" in prop_name:
            return self.get_perimeter(obj)
        elif "area" in prop_name and ("footprint" in prop_name or "section" in prop_name or "floor" in prop_name):
            return self.get_footprint_area(obj)
        elif "area" in prop_name and "side" in prop_name:
            return self.get_side_area(obj)
        elif "area" in prop_name:
            return self.get_area(obj)
        elif "volume" in prop_name:
            return self.get_volume(obj)

    def get_units(self, o, vg_index):
        return len([v for v in o.data.vertices if vg_index in [g.group for g in v.groups]])

    def get_linear_length(self, o):
        x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
        y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
        z = (Vector(o.bound_box[1]) - Vector(o.bound_box[0])).length
        return max(x, y, z)

    def get_length(self, o, vg_index=None):
        if vg_index is None:
            x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
            y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
            return max(x, y)
        length = 0
        edges = [
            e
            for e in o.data.edges
            if (
                vg_index in [g.group for g in o.data.vertices[e.vertices[0]].groups]
                and vg_index in [g.group for g in o.data.vertices[e.vertices[1]].groups]
            )
        ]
        for e in edges:
            length += self.get_edge_distance(o, e)
        return length

    def get_width(self, o):
        x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
        y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
        return min(x, y)

    def get_min_width(self, o):
        x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
        y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
        return min(x, y)

    def get_height(self, o):
        return (Vector(o.bound_box[1]) - Vector(o.bound_box[0])).length

    def get_perimeter(self, o):
        parsed_edges = []
        shared_edges = []
        perimeter = 0
        for polygon in self.get_lowest_polygons(o):
            for edge_key in polygon.edge_keys:
                if edge_key in parsed_edges:
                    shared_edges.append(edge_key)
                else:
                    parsed_edges.append(edge_key)
                    perimeter += self.get_edge_key_distance(o, edge_key)
        for edge_key in shared_edges:
            perimeter -= self.get_edge_key_distance(o, edge_key)
        return perimeter

    def get_lowest_polygons(self, o):
        lowest_polygons = []
        lowest_z = None
        for polygon in o.data.polygons:
            z = round(polygon.center[2], 3)
            if lowest_z is None:
                lowest_z = z
            if z > lowest_z:
                continue
            elif z == lowest_z:
                lowest_polygons.append(polygon)
            elif z < lowest_z:
                lowest_polygons = [polygon]
                lowest_z = z
        return lowest_polygons

    def get_highest_polygons(self, o):
        highest_polygons = []
        highest_z = None
        for polygon in o.data.polygons:
            z = round(polygon.center[2], 3)
            if highest_z is None:
                highest_z = z
            if z > highest_z:
                continue
            elif z == highest_z:
                highest_polygons.append(polygon)
            elif z < highest_z:
                highest_polygons = [polygon]
                highest_z = z
        return highest_polygons

    def get_edge_key_distance(self, obj, edge_key):
        return (obj.data.vertices[edge_key[1]].co - obj.data.vertices[edge_key[0]].co).length

    def get_edge_distance(self, obj, edge):
        return (obj.data.vertices[edge.vertices[1]].co - obj.data.vertices[edge.vertices[0]].co).length

    def get_net_footprint_area(self, o):
        area = 0
        for polygon in self.get_lowest_polygons(o):
            area += polygon.area
        return area

    def get_net_top_footprint_area(self, o):
        area = 0
        for polygon in self.get_highest_polygons(o):
            area += polygon.area
        return area

    def get_side_area(self, o):
        # There are a few dumb options for this, but this seems the dumbest
        # until I get more practical experience on what works best.
        x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
        y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
        z = (Vector(o.bound_box[1]) - Vector(o.bound_box[0])).length
        return max(x * z, y * z)

    def get_total_surface_area(self, o, vg_index=None):
        if vg_index is None:
            area = 0
            for polygon in o.data.polygons:
                area += polygon.area
            return area
        area = 0
        vertices_in_vg = [v.index for v in o.data.vertices if vg_index in [g.group for g in v.groups]]
        for polygon in o.data.polygons:
            if self.is_polygon_in_vg(polygon, vertices_in_vg):
                area += polygon.area
        return area

    def is_polygon_in_vg(self, polygon, vertices_in_vg):
        for v in polygon.vertices:
            if v not in vertices_in_vg:
                return False
        return True

    def get_volume(self, o, vg_index=None):
        volume = 0
        ob_mat = o.matrix_world
        me = o.data
        me.calc_loop_triangles()
        for tf in me.loop_triangles:
            tfv = tf.vertices
            if len(tf.vertices) == 3:
                tf_tris = ((me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),)
            else:
                tf_tris = (
                    (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),
                    (
                        me.vertices[tfv[2]],
                        me.vertices[tfv[3]],
                        me.vertices[tfv[0]],
                    ),
                )

            for tf_iter in tf_tris:
                v1 = ob_mat @ tf_iter[0].co
                v2 = ob_mat @ tf_iter[1].co
                v3 = ob_mat @ tf_iter[2].co

                volume += v1.dot(v2.cross(v3)) / 6.0
        return volume

    # deprecated - Vector.rotation_difference is 20x faster
    # def angle_between_vectors(self, v1, v2):
    #     return np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))

    # Thanks to @Gorgious56 - the following script should decrease the time to complete by at least 5%
    # def calculate_net_lateral_area_np(object, angle_z1=45, angle_z2=135):
    #     z_axis = (0, 0, 1)
    #     area = 0

    #     mesh = object.data
    #     areas = np.zeros(shape=len(mesh.polygons), dtype=float)
    #     bad_areas = np.zeros(shape=len(mesh.polygons), dtype=bool)
    #     normals = np.zeros(shape=3 * len(mesh.polygons), dtype=float)
    #     mesh.polygons.foreach_get("normal", normals)
    #     normals.shape = (len(mesh.polygons), 3)  # Reshape to get a list of 3D vectors

    #     angles_to_z_axis = np.array([math.degrees(np.arccos(np.clip(np.dot(z_axis, normal), -1.0, 1.0))) for normal in normals])

    #     bad_areas = angles_to_z_axis < angle_z1
    #     bad_areas += angles_to_z_axis > angle_z2

    #     mesh.polygons.foreach_get("area", areas)
    #     areas *= 1 - bad_areas

    # return sum(areas)

    def get_opening_type(self, opening, obj):
        polygons = opening.data.polygons
        ray_intersections = 0

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            polygon_centre = (polygon.center.x, polygon.center.y, polygon.center.z)
            if obj.ray_cast(polygon_centre, normal_vector)[0]:
                ray_intersections += 1

        # If an odd number of face-normal vectors intersect with the object, then the void is a recess, otherwise it's an opening
        return "OPENING" if ray_intersections % 2 == 0 else "RECESS"

    def get_side_opening_area(
        self, obj, angle_z1: int = 45, angle_z2: int = 135, min_area: int = 0, ignore_recesses: bool = False
    ):
        total_opening_area = 0
        ifc = tool.Ifc.get()
        ifc_element = ifc.by_id(obj.BIMObjectProperties.ifc_definition_id)
        if len(openings := ifc_element.HasOpenings) != 0:
            for opening in openings:
                opening_id = opening.RelatedOpeningElement.GlobalId
                ifc_opening_element = ifc.by_guid(opening_id)
                bl_opening_obj = tool.Ifc.get_object(ifc_opening_element)

                opening_type = (
                    ifc_opening_element.PredefinedType
                    if ifc_opening_element.PredefinedType is not None
                    else self.get_opening_type(bl_opening_obj, obj)
                )

                if ignore_recesses and opening_type == "RECESS":
                    continue
                opening_area = self.get_lateral_area(
                    bl_opening_obj, subtract_openings=False, angle_z1=angle_z1, angle_z2=angle_z2
                )
                if opening_area >= min_area:
                    total_opening_area += opening_area

        return total_opening_area

    def get_lateral_area(
        self,
        obj,
        subtract_openings: bool = True,
        exclude_end_areas: bool = False,
        exclude_side_areas: bool = False,
        angle_z1: int = 45,
        angle_z2: int = 135,
    ):
        x_axis = [1, 0, 0]
        y_axis = [0, 1, 0]
        z_axis = [0, 0, 1]
        area = 0
        total_opening_area = (
            0 if subtract_openings else self.get_side_opening_area(obj, angle_z1=angle_z1, angle_z2=angle_z2)
        )
        polygons = obj.data.polygons

        for polygon in polygons:
            angle_to_z_axis = math.degrees(polygon.normal.rotation_difference(Vector(z_axis)).angle)
            if angle_to_z_axis < angle_z1 or angle_to_z_axis > angle_z2:
                continue
            if exclude_end_areas:
                angle_to_x_axis = math.degrees(polygon.normal.rotation_difference(Vector(x_axis)).angle)
                if angle_to_x_axis < 45 or angle_to_x_axis > 135:
                    continue
            if exclude_side_areas:
                angle_to_y_axis = math.degrees(polygon.normal.rotation_difference(Vector(y_axis)).angle)
                if angle_to_y_axis < 45 or angle_to_y_axis > 135:
                    continue
            area += polygon.area
        return area + total_opening_area

    def get_gross_top_area(self, obj, angle: int = 45):
        z_axis = (0, 0, 1)
        area = 0
        opening_area = 0
        polygons = obj.data.polygons

        ifc = tool.Ifc.get()
        ifc_element = ifc.by_id(obj.BIMObjectProperties.ifc_definition_id)

        if len(openings := ifc_element.HasOpenings) != 0:
            for opening in openings:
                if opening.RelatedOpeningElement.PredefinedType == "OPENING":
                    opening_id = opening.RelatedOpeningElement.GlobalId

                    entity = ifc.by_guid(opening_id)
                    open_obj = tool.Ifc.get_object(entity)
                    opening_area += self.get_net_top_area(open_obj, angle=angle)
                else:
                    continue

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(polygon.normal.rotation_difference(Vector(z_axis)).angle)

            if angle_to_z_axis < angle:
                area += polygon.area
        return area + opening_area

    def get_net_top_area(self, obj, angle: int = 45):
        z_axis = (0, 0, 1)
        area = 0
        polygons = obj.data.polygons

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(polygon.normal.rotation_difference(Vector(z_axis)).angle)

            if angle_to_z_axis < angle:
                area += polygon.area
        return area

    def get_projected_area(self, obj, projection_axis: str, is_gross: bool):
        odata = obj.data
        polygons = obj.data.polygons
        shapely_polygons = []

        axes = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}[projection_axis]

        for polygon in polygons:
            if getattr(polygon.normal, projection_axis) == 0:
                continue
            polygon_tuples = []

            for loop_index in polygon.loop_indices:
                loop = odata.loops[loop_index]
                v1_coord_a = getattr(odata.vertices[loop.vertex_index].co, axes[0])
                v1_coord_b = getattr(odata.vertices[loop.vertex_index].co, axes[1])
                polygon_tuples.append((v1_coord_a, v1_coord_b))

            pgon = Polygon(polygon_tuples)
            shapely_polygons.append(pgon)

        projected_polygon = unary_union(shapely_polygons)
        if is_gross:
            void_area = 0
            voids = projected_polygon.interiors
            for void in voids:
                void_polygon = Polygon(void)
                void_area += void_polygon.area
            return projected_polygon.area + void_area
        return projected_polygon.area

    def get_OBB_object(self, obj):
        ifc_id = obj.BIMObjectProperties.ifc_definition_id
        bbox = obj.bound_box
        # matrix transformation to go from obj coordinates to world coordinates:
        obb = [obj.matrix_world @ Vector(v) for v in bbox]
        obb_mesh = bpy.data.meshes.new(f"OBB_{ifc_id}")

        # list of faces, with each tuple referring to an vertex-index in obb
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (1, 2, 6, 5),
            (0, 3, 7, 4),
            (1, 5, 4, 0),
            (2, 6, 7, 3),
        ]

        obb_mesh.from_pydata(vertices=obb, edges=[], faces=faces)
        obb_mesh.update()

        # create a new object from the mesh
        new_OBB_object = bpy.data.objects.new(f"OBB_{ifc_id}", obb_mesh)

        # create new collection for QtoCalculator
        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        bpy.context.scene.collection.children.link(collection)

        # add object to scene collection and then hide them.
        collection.objects.link(new_OBB_object)
        new_OBB_object.hide_set(True)

        return new_OBB_object

    def get_AABB_object(self, obj):
        ifc_id = obj.BIMObjectProperties.ifc_definition_id
        aabb_mesh = bpy.data.meshes.new(f"OBB_{ifc_id}")

        x = [(obj.matrix_world @ x.co).x for x in obj.data.vertices]
        y = [(obj.matrix_world @ y.co).y for y in obj.data.vertices]
        z = [(obj.matrix_world @ z.co).z for z in obj.data.vertices]

        min_x, max_x, min_y, max_y, min_z, max_z = min(x), max(x), min(y), max(y), min(z), max(z)

        vertices = [
            (min_x, min_y, min_z),
            (min_x, min_y, max_z),
            (min_x, max_y, max_z),
            (min_x, max_y, min_z),
            (max_x, min_y, min_z),
            (max_x, min_y, max_z),
            (max_x, max_y, max_z),
            (max_x, max_y, min_z),
        ]

        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (1, 2, 6, 5),
            (0, 3, 7, 4),
            (1, 5, 4, 0),
            (2, 6, 7, 3),
        ]

        aabb_mesh.from_pydata(vertices=vertices, edges=[], faces=faces)
        aabb_mesh.update()

        # create a new object from the mesh
        new_AABB_object = bpy.data.objects.new(f"OBB_{ifc_id}", aabb_mesh)

        # create new collection for QtoCalculator
        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        bpy.context.scene.collection.children.link(collection)

        # add object to scene collection and then hide them.
        collection.objects.link(new_AABB_object)
        new_AABB_object.hide_set(True)

        return new_AABB_object

    def get_bisected_obj(
        self,
        obj,
        plane_co_pos,
        plane_no_pos,
        plane_co_neg,
        plane_no_neg,
    ):
        ifc_id = obj.BIMObjectProperties.ifc_definition_id

        bis_obj = obj.copy()
        bis_obj.data = obj.data.copy()
        bis_obj.name = f"Bisected_{ifc_id}"

        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        bpy.context.scene.collection.children.link(collection)
        collection.objects.link(bis_obj)

        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = bis_obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.mesh.bisect(plane_co=plane_co_pos, plane_no=plane_no_pos, use_fill=True, clear_outer=True)

        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(plane_co=plane_co_neg, plane_no=plane_no_neg, use_fill=True, clear_outer=True)
        bpy.ops.object.editmode_toggle()
        bis_obj.hide_set(True)

        return bis_obj
    
    def get_total_contact_area(self, obj, class_filter):
        total_contact_area = 0
        touching_objects = self.get_touching_objects(obj, class_filter)
        
        for o in touching_objects:
            total_contact_area += self.get_contact_area(obj, o)
        
    def get_touching_objects(self, obj, class_filter):
        # rotate the object ever so slightly, otherwise bvhtree.overlap won't work properly.  https://blender.stackexchange.com/a/275244/130742
        # I still prefer using bhvtree over ifcclash simply because of the considerable speed improvement @vulevukusej
        obj.rotation_euler[0] += math.radians(0.001)
        obj.rotation_euler[1] += math.radians(0.001)
        bpy.context.evaluated_depsgraph_get().update()

        obj_mesh = bmesh.new()
        obj_mesh.from_mesh(obj.data)
        obj_mesh.transform(obj.matrix_world)
        obj_tree = BVHTree.FromBMesh(obj_mesh)

        touching_objects = []
        filtered_objects = []
        
        ifc = tool.Ifc.get()
        for f in class_filter:
            filtered_objects += ifc.by_type(f)
        
        for o in filtered_objects:
            blender_o = tool.Ifc.get_object(o.id())
            if o == obj:
                continue
            o_mesh = bmesh.new()
            try:
                o_mesh.from_mesh(o.data)
            except:
                #i'm too tired to debug this properly.  Not sure what causes this error. @vulevukusej
                continue
            o_mesh.transform(o.matrix_world)
            o_tree = BVHTree.FromBMesh(o_mesh)

            if len(obj_tree.overlap(o_tree)) > 0:
                touching_objects.append(o)

        # return the objects to their original states
        o.rotation_euler[0] -= math.radians(0.001)
        o.rotation_euler[1] -= math.radians(0.001)
        bpy.context.evaluated_depsgraph_get().update()

        return touching_objects
        
    def get_contact_area(self, object1, object2):
        total_area = (
            0  # list of tuples, each tuple containing the index of the polygon in object1 and object2 that are touching
        )

        for poly1 in object1.data.polygons:
            for poly2 in object2.data.polygons:
                return self.polygon_intersection_area(object1, poly1, object2, poly2)
        return total_area
            

    def get_intersection_between_polygons(self, object1, poly1, object2, poly2):

        # touching polygons should be coplanar:
        if (
            mathutils.geometry.intersect_plane_plane(
                object1.matrix_world @ poly1.center,
                object1.matrix_world @ poly1.normal,
                object2.matrix_world @ poly2.center,
                object2.matrix_world @ poly2.normal,
            )[0]
            is None
        ):
            return 0

        # get normal vectors according to world axis
        ref_normal = object1.rotation_euler.to_matrix() @ poly1.normal
        cont_normal = object2.rotation_euler.to_matrix() @ poly2.normal
        angle_between_normals = ref_normal.rotation_difference(cont_normal).angle

        # calculate rotation between face and vertical Z-axis.  This makes it easier to calculate intersection area later
        rotation_to_z = ref_normal.rotation_difference(Vector((0, 0, 1)))
        center_of_rotation = object1.matrix_world @ poly1.center

        # rotation around face.center in world space / https://blender.stackexchange.com/a/12324/130742
        trans_matrix = Matrix.Translation(center_of_rotation) @ rotation_to_z.to_matrix().to_4x4()

        pgon1 = self.create_shapely_polygon(object1, poly1, trans_matrix)
        pgon2 = self.create_shapely_polygon(object2, poly2, trans_matrix)

        return pgon1.intersection(pgon2).area

    def create_shapely_polygon(self, obj, polygon, trans_matrix):
        polygon_tuples = []
        odata = obj.data
        for loop_index in polygon.loop_indices:
            loop = odata.loops[loop_index]
            coords = obj.matrix_world @ odata.vertices[loop.vertex_index].co
            rotated_coords = trans_matrix @ coords
            x = rotated_coords.x
            y = rotated_coords.y
            polygon_tuples.append((x, y))
        return Polygon(polygon_tuples)


    # 1 and 3
    def polygon_intersection_area(self, object1, polygon1, object2, polygon2):
        # polygons should be coplanar:
        if (
            mathutils.geometry.intersect_plane_plane(
                polygon1.center, polygon1.normal, polygon2.center, polygon2.normal
            )[0]
            is None
        ):
            return 0

        intersection = self.get_combined_poly(object1, polygon1, object2, polygon2)
        return intersection.area

# # Following code is here temporarily to test newly created functions:

# o1 = bpy.data.objects["Cube"]
# o2 = bpy.data.objects["Cube.001"]

# poly1 = o1.data.polygons[1]
# poly2 = o2.data.polygons[3]

# qto = QtoCalculator()
# o = bpy.context.active_object

# print(qto.get_touching_objects(o, ["IfcWall", "IfcSlab"]))
# #
