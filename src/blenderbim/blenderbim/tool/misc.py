# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector, Matrix
from blenderbim.bim.ifc import IfcStore


class Misc(blenderbim.core.tool.Misc):
    @classmethod
    def get_object_storey(cls, obj):
        storey = ifcopenshell.util.element.get_container(tool.Ifc.get_entity(obj))
        if storey and storey.is_a("IfcBuildingStorey"):
            return storey

    @classmethod
    def get_storey_elevation_in_si(cls, storey):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        elevation = ifcopenshell.util.placement.get_storey_elevation(storey)
        return elevation * unit_scale

    @classmethod
    def get_storey_height_in_si(cls, storey):
        building = ifcopenshell.util.element.get_aggregate(storey)
        related_objects = []
        for rel in building.IsDecomposedBy:
            if rel.is_a("IfcRelAggregates"):
                for element in rel.RelatedObjects:
                    if element.is_a("IfcBuildingStorey"):
                        related_objects.append((element, ifcopenshell.util.placement.get_storey_elevation(element)))
        related_objects = sorted(related_objects, key=lambda e: e[1])
        storey_elevation = None
        next_storey_elevation = None
        for related_object in related_objects:
            if related_object[0] == storey:
                storey_elevation = related_object[1]
            elif storey_elevation is not None:
                next_storey_elevation = related_object[1]
                break
        if next_storey_elevation:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            return (next_storey_elevation - storey_elevation) * unit_scale

    @classmethod
    def set_object_origin_to_bottom(cls, obj):
        absolute_bound_box = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        min_z = min([c[2] for c in absolute_bound_box])
        new_origin = obj.matrix_world.translation.copy()
        new_origin[2] = min_z
        obj.data.transform(
            Matrix.Translation(
                (obj.matrix_world.inverted().to_quaternion() @ (obj.matrix_world.translation - new_origin))
            )
        )
        obj.matrix_world.translation = new_origin

    @classmethod
    def move_object_to_elevation(cls, obj, elevation):
        obj.matrix_world.translation[2] = elevation

    @classmethod
    def scale_object_to_height(cls, obj, height):
        absolute_bound_box = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        max_z = max([c[2] for c in absolute_bound_box])
        min_z = min([c[2] for c in absolute_bound_box])
        current_absolute_height = max_z - min_z
        scale_factor = height / current_absolute_height
        obj.matrix_world @= Matrix.Scale(scale_factor, 4, obj.matrix_world.to_quaternion() @ Vector((0, 0, 1)))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    @classmethod
    def mark_object_as_edited(cls, obj):
        IfcStore.edited_objs.add(obj)
