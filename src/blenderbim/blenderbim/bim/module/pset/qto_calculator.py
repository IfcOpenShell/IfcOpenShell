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
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import blenderbim.tool as tool
import ifcopenshell
from blenderbim.bim.module.pset.calc_quantity_function_mapper import mapper


class QtoCalculator:

    def __init__(self):
        self.mapping_dict = {}
        for key in mapper.keys():
            self.mapping_dict[key] = dict(mapper[key].items())

        for key in self.mapping_dict.keys():
            for item in self.mapping_dict[key].keys():
                if self.mapping_dict[key][item]:
                    if isinstance(self.mapping_dict[key][item], str):
                        self.mapping_dict[key][item] = eval("self." + self.mapping_dict[key][item])
                    if isinstance(self.mapping_dict[key][item], dict):
                        self.mapping_dict[key][item] = eval("self." + self.mapping_dict[key][item]["function_name"])
                else:
                    self.mapping_dict[key][item] = None

    def calculate_quantity(self, qto_name, quantity_name, obj):
        string = "self.mapping_dict[qto_name][quantity_name](obj"
        if isinstance(mapper[qto_name][quantity_name], dict):
            args = mapper[qto_name][quantity_name]["args"]
        else:
            args = ""
        string += args
        string += ")"
        return eval(string)

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
            return self.get_net_perimeter(obj)
        elif "area" in prop_name and ("footprint" in prop_name or "section" in prop_name or "floor" in prop_name):
            return self.get_net_footprint_area(obj)
        elif "area" in prop_name and "side" in prop_name:
            return self.get_side_area(obj)
        elif "area" in prop_name:
            return self.get_total_surface_area(obj)
        elif "volume" in prop_name and "gross" in prop_name:
            return self.get_gross_volume(obj)
        elif "volume" in prop_name :
            return self.get_net_volume(obj)

    def get_units(self, o, vg_index):
        return len([v for v in o.data.vertices if vg_index in [g.group for g in v.groups]])

    def get_linear_length(self, o):
        """_summary_: Returns the length of the longest edge of the object bounding box

        :param blender-object o: Blender Object
        :return float: Length
        """
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
        """_summary_: Returns the width of the object bounding box

        :param blender-object o: blender object
        :return float: width
        """
        x = (Vector(o.bound_box[4]) - Vector(o.bound_box[0])).length
        y = (Vector(o.bound_box[3]) - Vector(o.bound_box[0])).length
        return min(x, y)

    def get_height(self, o):
        """_summary_: Returns the height of the object bounding box

        :param blender-object o: blender object
        :return float: height
        """
        return (Vector(o.bound_box[1]) - Vector(o.bound_box[0])).length

    def get_net_perimeter(self, o):
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

    def get_gross_perimeter(self, o):
        element = tool.Ifc.get_entity(o)
        mesh = self.get_gross_element_mesh(element)
        gross_obj = bpy.data.objects.new("GrossObj", mesh)
        gross_perimeter = self.get_net_perimeter(gross_obj)
        self.delete_obj(gross_obj)
        return gross_perimeter

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
        """_summary_: Returns the area of the footprint of the object, excluding any holes

        :param blender-object o: blender object
        :return float: footprint area
        """
        area = 0
        for polygon in self.get_lowest_polygons(o):
            area += polygon.area
        return area

    def get_gross_footprint_area(self, o):
        """_summary_: Returns the area of the footprint of the object, without related opening and excluding any holes

        :param blender-object o: blender object
        :return float: footprint area"""
        element = tool.Ifc.get_entity(o)
        mesh = self.get_gross_element_mesh(element)
        gross_obj = bpy.data.objects.new("GrossObj", mesh)
        gross_footprint_area = self.get_net_footprint_area(gross_obj)
        self.delete_obj(gross_obj)
        return gross_footprint_area

    def get_net_roofprint_area(self, o):
        # Is roofprint the right word? Couldn't think of anything better - vulevukusej
        """_summary_: Returns the area of the net roofprint of the object, excluding any holes

        :param blender-object o: Blender Object
        :return float: Area
        """
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

    def get_net_volume(self, o):
        o_mesh = bmesh.new()
        o_mesh.from_mesh(o.data)
        volume = o_mesh.calc_volume()
        self.delete_bmesh(o_mesh)
        return volume

    def get_gross_volume(self, o):
        element = tool.Ifc.get_entity(o)
        if not element:
            print(f"Object {o.name} hasn't an IFC instance so gross volume is equal to net volume")
            return self.get_net_volume

        mesh = self.get_gross_element_mesh(element)
        bm = self.get_bmesh_from_mesh(mesh)

        gross_volume = bm.calc_volume()

        self.delete_bmesh(bm)
        self.delete_mesh(mesh)

        return gross_volume

    # The following is @Moult's older code.  Keeping it here just in case the bmesh function is buggy. -vulevukusej

    # def get_volume(self, o, vg_index=None):
    # volume = 0
    # ob_mat = o.matrix_world
    # me = o.data
    # me.calc_loop_triangles()
    # for tf in me.loop_triangles:
    #     tfv = tf.vertices
    #     if len(tf.vertices) == 3:
    #         tf_tris = ((me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),)
    #     else:
    #         tf_tris = (
    #             (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),
    #             (
    #                 me.vertices[tfv[2]],
    #                 me.vertices[tfv[3]],
    #                 me.vertices[tfv[0]],
    #             ),
    #         )

    #     for tf_iter in tf_tris:
    #         v1 = ob_mat @ tf_iter[0].co
    #         v2 = ob_mat @ tf_iter[1].co
    #         v3 = ob_mat @ tf_iter[2].co

    #         volume += v1.dot(v2.cross(v3)) / 6.0
    # return volume

    def get_opening_type(self, opening, obj):
        """_summary_: Returns the opening type - OPENING / RECESS

        :param blender-object opening: blender opening object
        :param blender-object obj: blender object
        :return string: "OPENING" or "RECESS"
        """
        polygons = opening.data.polygons
        ray_intersections = 0

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            polygon_centre = (polygon.center.x, polygon.center.y, polygon.center.z)
            if obj.ray_cast(polygon_centre, normal_vector)[0]:
                ray_intersections += 1

        # If an odd number of face-normal vectors intersect with the object, then the void is a recess, otherwise it's an opening
        return "OPENING" if ray_intersections % 2 == 0 else "RECESS"

    def get_opening_area(
        self, obj, angle_z1: int = 45, angle_z2: int = 135, min_area: int = 0, ignore_recesses: bool = False
    ):
        """_summary_: Returns the lateral area of the openings in the object.

        :param obj: blender object
        :param int angle_z1: Angle measured from the positive z-axis to the normal-vector of the opening area. Openings with a normal_vector lower than this value will be ignored, defaults to 45
        :param int angle_z2: Angle measured from the positive z-axis to the normal-vector of the opening area. Openings with a normal_vector greater than this value will be ignored,defaults to 135
        :param float min_area: Minimum opening area to consider.  Values lower than this will be ignored, defaults to 0
        :param bool ignore_recesses: Toggle whether recess areas should be considered, defaults to False
        :return float: Opening Area
        """
        total_opening_area = 0
        ifc = tool.Ifc.get()
        ifc_element = ifc.by_id(obj.BIMObjectProperties.ifc_definition_id)
        if len(openings := ifc_element.HasOpenings) != 0:
            for opening in openings:
                opening_id = opening.RelatedOpeningElement.GlobalId
                ifc_opening_element = ifc.by_guid(opening_id)
                #bl_opening_obj = tool.Ifc.get_object(ifc_opening_element)
                #mesh = bpy.data.meshes.new('myMesh')
                mesh = self.get_gross_element_mesh(ifc_opening_element)

                bl_opening_obj = bpy.data.objects.new("MyObject", mesh)

                opening_type = (
                    ifc_opening_element.PredefinedType
                    if ifc_opening_element.PredefinedType is not None
                    else self.get_opening_type(bl_opening_obj, obj)
                )

                if ignore_recesses and opening_type == "RECESS":
                    continue

                bl_OBB_opening_object = self.get_OBB_object(bl_opening_obj)
                opening_area = self.get_lateral_area(
                    #self.get_OBB_object(bl_opening_obj), angle_z1=angle_z1, angle_z2=angle_z2, exclude_end_areas=True
                    bl_OBB_opening_object, angle_z1=angle_z1, angle_z2=angle_z2, exclude_end_areas=True
                )
                if opening_area >= min_area:
                    total_opening_area += opening_area

                self.delete_obj(bl_opening_obj)
                self.delete_mesh(mesh)
                self.delete_obj(bl_OBB_opening_object)

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
        """_summary_

        :param blender-object obj: blender object, bpy.types.Object
        :param bool subtract_openings: Toggle whether opening-areas should be subtracted, defaults to True
        :param bool exclude_end_areas: , defaults to False
        :param bool exclude_side_areas: , defaults to False
        :param int angle_z1: Angle measured from the positive z-axis to the normal-vector of the area. Openings with a normal_vector lower than this value will be ignored, defaults to 45
        :param int angle_z2: Angle measured from the positive z-axis to the normal-vector of the area. Openings with a normal_vector greater than this value will be ignored, defaults to 135
        :return float: Lateral Area
        """
        x_axis = [1, 0, 0]
        y_axis = [0, 1, 0]
        z_axis = [0, 0, 1]
        area = 0
        total_opening_area = (
            0 if subtract_openings else self.get_opening_area(obj, angle_z1=angle_z1, angle_z2=angle_z2)
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

    def get_half_lateral_area(
       self,
        obj,
        subtract_openings: bool = True,
        exclude_end_areas: bool = False,
        exclude_side_areas: bool = False,
        angle_z1: int = 45,
        angle_z2: int = 135,
    ):
        """_summary_:
        :param blender-object obj: blender object, bpy.types.Object
        :param bool subtract_openings: Toggle whether opening-areas should be subtracted, defaults to True
        :param bool exclude_end_areas: , defaults to False
        :param bool exclude_side_areas: , defaults to False
        :param int angle_z1: Angle measured from the positive z-axis to the normal-vector of the area. Openings with a normal_vector lower than this value will be ignored, defaults to 45
        :param int angle_z2: Angle measured from the positive z-axis to the normal-vector of the area. Openings with a normal_vector greater than this value will be ignored, defaults to 135
        :return float: Lateral Area / 2
        """
        return self.get_lateral_area(obj, subtract_openings, exclude_end_areas, exclude_side_areas, angle_z1, angle_z2)/2

    def get_gross_top_area(self, obj, angle: int = 45):
        """_summary_: Returns the gross top area of the object.

        :param blender-object obj: blender object
        :param int angle: Angle measured from the positive z-axis to the normal-vector of the area. Values lower than this will be ignored, defaults to 45
        :return float: Gross Top Area
        """

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

    # curently net top area is larger then projected area, because its taking into account internal polygons, or window sills
    def get_net_top_area(self, obj, angle: int = 45, ignore_internal: bool = True):
        """_summary_: Returns the net top area of the object.

        :param blender-object obj: blender object
        :param int angle: Angle measured from the positive z-axis to the normal-vector of the area. Values lower than this will be ignored, defaults to 45
        :param bool ignore_internal: Toggle whether internal areas should be subtracted (Like window sills), defaults to True
        :return float: Net Top Area
        """
        z_axis = (0, 0, 1)
        area = 0
        polygons = obj.data.polygons

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(polygon.normal.rotation_difference(Vector(z_axis)).angle)

            if angle_to_z_axis < angle:
                # offset the raycast, otherwise the raycast will always collide with the object.
                offset = polygon.center+Vector((0,0,0.01))
                if ignore_internal and obj.ray_cast(offset, (0,0,1))[0]:
                    continue
                area += polygon.area

        return area

    def get_projected_area(self, obj, projection_axis: str = "z", is_gross: bool = True):
        """_summary_: Returns the projected area of the object.

        :param blender-object obj: blender object
        :param str projection_axis: Axis to project the area onto. Can be "X", "Y" or "Z"
        :param bool is_gross: if True, the projected area will include openings, if False, the projected area will exclude openings
        :return float: Projected Area
        """

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
                a = getattr(odata.vertices[loop.vertex_index].co, axes[0])
                b = getattr(odata.vertices[loop.vertex_index].co, axes[1])
                polygon_tuples.append((a, b))

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
        """_summary_: Returns the Oriented-Bounding-Box (OBB) of the object.

        :param blender-object obj: Blender Object
        :return blender-object: OBB of the Object
        """
        ifc_id = obj.BIMObjectProperties.ifc_definition_id
        bbox = obj.bound_box
        # matrix transformation to go from obj coordinates to world coordinates:
        obb = [Vector(v) for v in bbox]
        obb_mesh = bpy.data.meshes.new(f"OBB_{ifc_id}")

        # list of faces, with each tuple referring to an vertex-index in obb
        faces = [
            (0, 1, 2, 3),
            (7, 6, 5, 4),
            (5, 6, 2, 1),
            (0, 3, 7, 4),
            (0, 4, 5, 1),
            (2, 6, 7, 3),
        ]

        obb_mesh.from_pydata(vertices=obb, edges=[], faces=faces)
        # obb_mesh.transform(obj.matrix_world)

        # create a new object from the mesh
        new_OBB_object = bpy.data.objects.new(f"OBB_{ifc_id}", obb_mesh)
        new_OBB_object.matrix_world = obj.matrix_world

        # create new collection for QtoCalculator
        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        if not bpy.context.scene.collection.children.get(collection.name):
            bpy.context.scene.collection.children.link(collection)

        # add object to scene collection and then hide them.
        collection.objects.get(new_OBB_object.name, collection.objects.link(new_OBB_object))
        new_OBB_object.hide_set(True)

        return new_OBB_object

    def get_AABB_object(self, obj):
        """_summary_: Returns the Axis-Aligned-Bounding-Box (AABB) of the object.

        :param blender-object obj: Blender Object
        :return blender-object: AABB of the Object
        """
        ifc_id = obj.BIMObjectProperties.ifc_definition_id
        aabb_mesh = bpy.data.meshes.new(f"OBB_{ifc_id}")

        x = [v.co.x for v in obj.data.vertices]
        y = [v.co.y for v in obj.data.vertices]
        z = [v.co.z for v in obj.data.vertices]

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
            (7, 6, 5, 4),
            (5, 6, 2, 1),
            (0, 3, 7, 4),
            (0, 4, 5, 1),
            (2, 6, 7, 3),
        ]

        aabb_mesh.from_pydata(vertices=vertices, edges=[], faces=faces)
        aabb_mesh.update()

        # create a new object from the mesh
        new_AABB_object = bpy.data.objects.new(f"OBB_{ifc_id}", aabb_mesh)
        new_AABB_object.matrix_world = obj.matrix_world

          # create new collection for QtoCalculator
        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        if not bpy.context.scene.collection.children.get(collection.name):
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
        """_summary_: Returns the object bisected by two planes.

        :param blender-object obj: Blender Object
        :param tuple(x,y,z) plane_co_pos: Point on upper bisection plane. Example: (0,0,0)
        :param tuple(x,y,z) plane_no_pos: Tuple describing the normal vector of the upper bisection plane. Example: (0,0,1)
        :param tuple(x,y,z) plane_co_neg: Point on lower bisection plane. Example: (0,0,0)
        :param tuple(x,y,z) plane_no_neg: Tuple describing the normal vector of the lower bisection plane. Example: (0,0,-1)
        :return _type_: _description_
        """
        ifc_id = obj.BIMObjectProperties.ifc_definition_id

        bis_obj = obj.copy()
        bis_obj.data = obj.data.copy()
        bis_obj.name = f"Bisected_{ifc_id}"

        collection = bpy.data.collections.get("QtoCalculator", bpy.data.collections.new("QtoCalculator"))
        if not bpy.context.scene.collection.children.get(collection.name):
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

    def get_total_contact_area(self, obj, class_filter: str = ["IfcElement"]):
        """_summary_: Returns the total contact area of the object with other objects.

        :param blender-object obj: Blender Object
        :param list [] class_filter: A list of classes used to filter the objects to be considered for the calculation. Example: ["IfcWall"] or ["IfcWall", "IfcSlab"]
        :return float: Total contact area of the object with other objects.
        """
        total_contact_area = 0
        touching_objects = self.get_touching_objects(obj, class_filter)

        for o in touching_objects:
            total_contact_area += self.get_contact_area(obj, o)

        return total_contact_area

    def get_touching_objects(self, obj, class_filter):
        """_summary_: Returns a list of objects that are touching the object.

        :param blender-object obj: Blender Object
        :param list [] class_filter: A list of classes used to filter the objects to be considered for the calculation. Example: ["IfcWall"] or ["IfcWall", "IfcSlab"]
        :return list: List of touching objects
        """
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
            blender_o = tool.Ifc.get_object(o)
            if blender_o == obj:
                continue
            o_mesh = bmesh.new()
            try:
                o_mesh.from_mesh(blender_o.data)
            except:
                # i'm too tired to debug this properly.  Not sure what causes this error. @vulevukusej
                continue
            o_mesh.transform(blender_o.matrix_world)
            o_tree = BVHTree.FromBMesh(o_mesh)

            if len(obj_tree.overlap(o_tree)) > 0:
                touching_objects.append(blender_o)

        # return the objects to their original states
        blender_o.rotation_euler[0] -= math.radians(0.001)
        blender_o.rotation_euler[1] -= math.radians(0.001)
        bpy.context.evaluated_depsgraph_get().update()

        return touching_objects

    def get_contact_area(self, object1, object2):
        """_summary_: Returns the contact area between two objects.

        :param blender-object obj: Blender Object
        :param blender-object obj: Blender Object
        :return float: contact area between the two objects.
        """
        # list of tuples, each tuple containing the index of the polygon in object1 and object2 that are touching
        total_area = 0

        for poly1 in object1.data.polygons:
            for poly2 in object2.data.polygons:
                total_area += self.get_intersection_between_polygons(object1, poly1, object2, poly2)
        return total_area

    def get_intersection_between_polygons(self, object1, poly1, object2, poly2):
        """_summary_: Returns the intersection between two polygons.

        :param blender-object object1: Blender Object
        :param blender-polygon poly1: Blender Polygon
        :param blender-object object1: Blender Object
        :param blender-polygon poly1: Blender Polygon
        :return float: intersection area of the two polygons.
        """
        # get normal vectors according to world axis
        normal1 = object1.rotation_euler.to_matrix() @ poly1.normal
        center1 = object1.matrix_world @ poly1.center
        normal2 = object2.rotation_euler.to_matrix() @ poly2.normal
        center2 = object2.matrix_world @ poly2.center

        angle_between_normals = normal1.rotation_difference(normal2).angle

        if math.degrees(angle_between_normals) < 178:
            return 0

        # touching polygons should be coplanar:
        plane_intersection = mathutils.geometry.intersect_plane_plane(
                center1,
                normal1,
                center2,
                normal2
            )

        # sometimes coplanar planes will interesect far off into the distance.  This is a crude way of filtering out those intersections.
        if plane_intersection[0] is None or (plane_intersection[0] - center1).magnitude > 20:
            return 0

        # calculate rotation between face and vertical Z-axis.  This makes it easier to calculate intersection area later
        rotation_to_z = normal1.rotation_difference(Vector((0, 0, 1)))
        center_of_rotation = center1

        # rotation around face.center in world space / https://blender.stackexchange.com/a/12324/130742
        trans_matrix = Matrix.Translation(center_of_rotation) @ rotation_to_z.to_matrix().to_4x4()

        pgon1 = self.create_shapely_polygon(object1, poly1, trans_matrix)
        pgon2 = self.create_shapely_polygon(object2, poly2, trans_matrix)

        try:
            return pgon1.intersection(pgon2).area
        except:
            # TopologicalError - Generated Geometry might be invalid
            return 0

    def create_shapely_polygon(self, obj, polygon, trans_matrix):
        """_summary_: Create a shapely polygon

        :param blender-object obj: Blender Object
        :param blender-polygon polygon: Blender Polygon
        :param matrix trans_matrix: Matrix that rotates the polygon to face upwards
        :return Shapely Polygon: Shapely Polygon
        """
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

    def get_gross_element_mesh(self, element):
        settings = ifcopenshell.geom.settings()
        settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
        shape = ifcopenshell.geom.create_shape(settings, element)
        faces = shape.geometry.faces
        verts = shape.geometry.verts

        mesh = bpy.data.meshes.new("myBeautifulMesh")

        num_vertices = len(verts) // 3
        total_faces = len(faces)
        loop_start = range(0, total_faces, 3)
        num_loops = total_faces // 3
        loop_total = [3] * num_loops
        num_vertex_indices = len(faces)

        mesh.vertices.add(num_vertices)
        mesh.vertices.foreach_set("co", verts)
        mesh.loops.add(num_vertex_indices)
        mesh.loops.foreach_set("vertex_index", faces)
        mesh.polygons.add(num_loops)
        mesh.polygons.foreach_set("loop_start", loop_start)
        mesh.polygons.foreach_set("loop_total", loop_total)
        mesh.update()

        # An alternative to foreach is
        # mesh.from_pydata(grouped_verts, edges, grouped_faces)
        # look at import_ifc.py in blenderbim

        return mesh

    def get_bmesh_from_mesh(self, mesh):
        bm = bmesh.new()
        bm.from_mesh(mesh)
        #bm.to_mesh(mesh)
        return bm

    def delete_mesh(self, mesh):
        mesh.user_clear()
        bpy.data.meshes.remove(mesh)

    def delete_bmesh(self, bm):
        bmesh.ops.delete(bm)
        bm.free()

    def delete_obj(self, obj):
        bpy.data.objects.remove(obj, do_unlink = True)

# # Following code is here temporarily to test newly created functions:

#qto = QtoCalculator()
#o = bpy.context.active_object
#sel = bpy.context.selected_objects
#
#nl = '\n'
# print(
#     f"get_linear_length: {qto.get_linear_length(o)}{nl}{nl}"
#     f"get_width: {qto.get_width(o)}{nl}{nl}"
#     f"get_height: {qto.get_height(o)}{nl}{nl}"
#     f"get_perimeter: {qto.get_perimeter(o)}{nl}{nl}"
#     f"get_lowest_polygons: {qto.get_lowest_polygons(o)}{nl}{nl}"
#     f"get_highest_polygons: {qto.get_highest_polygons(o)}{nl}{nl}"
#     f"get_net_footprint_area: {qto.get_net_footprint_area(o)}{nl}{nl}"
#     f"get_net_roofprint_area: {qto.get_net_roofprint_area(o)}{nl}{nl}"
#     f"get_side_area: {qto.get_side_area(o)}{nl}{nl}"
#     f"get_total_surface_area: {qto.get_total_surface_area(o)}{nl}{nl}"
#     f"get_volume: {qto.get_volume(o)}{nl}{nl}"
#     f"get_opening_area(o, angle_z1=45, angle_z2=135, min_area=0, ignore_recesses=False): {qto.get_opening_area(o, angle_z1=45, angle_z2=135, min_area=0, ignore_recesses=False)}{nl}{nl}"
#     f"get_lateral_area(o, subtract_openings=True, exclude_end_areas=False, exclude_side_areas=False, angle_z1=45, angle_z2=135): {qto.get_lateral_area(o, subtract_openings=True, exclude_end_areas=False, exclude_side_areas=False, angle_z1=45, angle_z2=135)}{nl}{nl}"
#     f"get_gross_top_area: {qto.get_gross_top_area(o, angle=45)}{nl}{nl}"
#     f"get_net_top_area(o, angle=45, ignore_internal=True): {qto.get_net_top_area(o, angle=45, ignore_internal=True)}{nl}{nl}"
#     f"get_projected_area(o, projection_axis='z', is_gross=True): {qto.get_projected_area(o, projection_axis='z', is_gross=True)}{nl}{nl}"
#     f"get_OBB_object: {qto.get_OBB_object(o)}{nl}{nl}"
#     f"get_AABB_object: {qto.get_AABB_object(o)}{nl}{nl}"
#     f"get_bisected_obj(o, plane_co_pos=(0,0,1), plane_no_pos=(0,0,1), plane_co_neg=(0,0,1), plane_no_neg=(0,0,1)): {qto.get_bisected_obj(o, plane_co_pos=(0,0,1), plane_no_pos=(0,0,1), plane_co_neg=(0,0,1), plane_no_neg=(0,0,1))}{nl}{nl}"
#     f"get_total_contact_area(o, class_filter=['IfcWall', 'IfcSlab']): {qto.get_total_contact_area(o, class_filter=['IfcWall', 'IfcSlab'])}{nl}{nl}"
#     f"get_touching_objects(o, ['IfcElement']): {qto.get_touching_objects(o, ['IfcElement'])}{nl}{nl}"
#     #f"get_contact_area: {qto.get_contact_area(o)}{nl}{nl}"
#     )


