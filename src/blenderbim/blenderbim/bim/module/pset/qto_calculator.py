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

from mathutils import Vector
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

    def angle_between_vectors(self, v1, v2):
        return np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))

    # Thanks to @Gorgious56 - the following script should decrease the time to complete by at least 5%
    # def calculate_net_lateral_area_np(object, angle_a=45, angle_b=135):
    #     z_axis = (0, 0, 1)
    #     area = 0

    #     mesh = object.data
    #     areas = np.zeros(shape=len(mesh.polygons), dtype=float)
    #     bad_areas = np.zeros(shape=len(mesh.polygons), dtype=bool)
    #     normals = np.zeros(shape=3 * len(mesh.polygons), dtype=float)
    #     mesh.polygons.foreach_get("normal", normals)
    #     normals.shape = (len(mesh.polygons), 3)  # Reshape to get a list of 3D vectors

    #     angles_to_z_axis = np.array([math.degrees(np.arccos(np.clip(np.dot(z_axis, normal), -1.0, 1.0))) for normal in normals])

    #     bad_areas = angles_to_z_axis < angle_a
    #     bad_areas += angles_to_z_axis > angle_b

    #     mesh.polygons.foreach_get("area", areas)
    #     areas *= 1 - bad_areas

    # return sum(areas)

    def get_gross_side_area(self, obj, angle_a: int = 45, angle_b: int = 135):
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
                    opening_area += self.get_net_side_area(open_obj, angle_a=angle_a, angle_b=angle_b)
                else:
                    continue

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(self.angle_between_vectors(z_axis, normal_vector))

            if angle_to_z_axis < angle_a or angle_to_z_axis > angle_b:
                continue
            area += polygon.area
        return area+opening_area
    
    def get_net_side_area(self, obj, angle_a: int = 45, angle_b: int = 135):
        z_axis = (0, 0, 1)
        area = 0
        polygons = obj.data.polygons

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(self.angle_between_vectors(z_axis, normal_vector))

            if angle_to_z_axis < angle_a or angle_to_z_axis > angle_b:
                continue
            area += polygon.area
        return area

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
            angle_to_z_axis = math.degrees(self.angle_between_vectors(z_axis, normal_vector))

            if angle_to_z_axis < angle:
                area += polygon.area
        return area + opening_area

    def get_net_top_area(self, obj, angle: int = 45):
        z_axis = (0, 0, 1)
        area = 0
        polygons = obj.data.polygons

        for polygon in polygons:
            normal_vector = (polygon.normal.x, polygon.normal.y, polygon.normal.z)
            angle_to_z_axis = math.degrees(self.angle_between_vectors(z_axis, normal_vector))

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


# Following code is here temporarily to test newly created functions:
import bpy

qto = QtoCalculator()
# # test = qto.get_net_projected_area(bpy.context.active_object, "x")
# # test2 = qto.get_net_projected_area(bpy.context.active_object, "y")
# # net = qto.get_projected_area(bpy.context.active_object, "z", False)
# # gross = qto.get_projected_area(bpy.context.active_object, "z", True)
# # grossarea = qto.get_gross_top_area(bpy.context.active_object)
# # netarea = qto.get_net_top_area(bpy.context.active_object)
grossarea = qto.get_gross_side_area(bpy.context.active_object)
netarea = qto.get_net_side_area(bpy.context.active_object)

print(netarea, grossarea)
