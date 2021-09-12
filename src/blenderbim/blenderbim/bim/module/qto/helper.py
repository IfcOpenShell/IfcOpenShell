# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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


def calculate_height(obj):
    return obj.dimensions[2]


def calculate_edges_lengths(objs, context):
    return calculate_mesh_quantity(objs, context, lambda bm: sum((e.calc_length() for e in bm.edges if e.select)))


def calculate_faces_areas(objs, context):
    return calculate_mesh_quantity(objs, context, lambda bm: sum((f.calc_area() for f in bm.faces if f.select)))


def calculate_volumes(objs, context):
    return calculate_mesh_quantity(objs, context, lambda bm: bm.calc_volume())


def calculate_mesh_quantity(objs: bpy.types.Object, context, operation):
    """Get the sum of the target quantity on all passed mesh objects

    :param objs: iterable of mesh object
    :param context: current execution context
    :param operation: function which takes a single bmesh as an argument, returns a float value
    :returns float:
    """
    result = 0
    edit_mode = context.active_object.mode == "EDIT"
    for obj in objs:
        if edit_mode:
            bm = bmesh.from_edit_mesh(obj.data)
            result += operation(bm)
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            result += operation(bm)
            bm.free()
    return result


def calculate_formwork_area(objs, context):
    """
    Formwork is defined as the surface area required to cover all exposed
    surfaces of one or more objects, excluding top surfaces (i.e. that have a
    face normal with a significant Z component).
    """
    copied_objs = []
    result = 0

    for obj in objs:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        context.collection.objects.link(new_obj)
        copied_objs.append(new_obj)

    if len(objs) > 1:
        context_override = {}
        context_override["object"] = context_override["active_object"] = copied_objs[0]
        context_override["selected_objects"] = context_override["selected_editable_objects"] = copied_objs
        bpy.ops.object.join(context_override)

    copied_objs[0].name = "Formwork"
    copied_objs[0].BIMObjectProperties.ifc_definition_id = 0
    modifier = copied_objs[0].modifiers.new("Formwork", "REMESH")
    modifier.mode = "SHARP"
    # This hardcoded value may be optimised through a better understanding of the octree division.
    # These values are based off some trial and error heuristics I've learned through experience.
    max_dim = max(copied_objs[0].dimensions)
    if max_dim > 45:
        modifier.octree_depth = 9
    elif max_dim > 35:
        modifier.octree_depth = 8
    elif max_dim > 12:
        modifier.octree_depth = 7
    elif max_dim > 5:
        modifier.octree_depth = 6
    else:
        modifier.octree_depth = 5

    mesh = copied_objs[0].evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
    for polygon in mesh.polygons:
        if polygon.normal.z > 0.5:
            continue
        result += polygon.area
    return result
