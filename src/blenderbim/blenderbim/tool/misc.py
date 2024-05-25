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
import bmesh
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.root
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
    def get_storey_height_in_si(cls, storey, total_storeys):
        building = ifcopenshell.util.element.get_aggregate(storey)
        related_objects = []
        for rel in building.IsDecomposedBy:
            if rel.is_a("IfcRelAggregates"):
                for element in rel.RelatedObjects:
                    if element.is_a("IfcBuildingStorey"):
                        related_objects.append((element, ifcopenshell.util.placement.get_storey_elevation(element)))
        related_objects = sorted(related_objects, key=lambda e: e[1])
        storey_elevation = None
        for i, related_object in enumerate(related_objects):
            if related_object[0] == storey:
                storey_elevation = related_object[1]
                break
        if i + total_storeys < len(related_objects):
            next_storey_elevation = related_objects[i + total_storeys][1]
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
    def run_root_copy_class(cls, obj=None):
        return blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)

    @classmethod
    def scale_object_to_height(cls, obj, height):
        absolute_bound_box = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        max_z = max([c[2] for c in absolute_bound_box])
        min_z = min([c[2] for c in absolute_bound_box])
        current_absolute_height = max_z - min_z
        scale_factor = height / current_absolute_height
        obj.matrix_world @= Matrix.Scale(
            scale_factor, 4, obj.matrix_world.inverted().to_quaternion() @ Vector((0, 0, 1))
        )
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    @classmethod
    def mark_object_as_edited(cls, obj):
        IfcStore.edited_objs.add(obj)

    @classmethod
    def split_objects_with_cutter(
        cls, objs: list[bpy.types.Object], cutter: bpy.types.Object
    ) -> list[bpy.types.Object]:
        cutter_mesh = cutter.data

        bm = bmesh.new()
        bm.from_mesh(cutter_mesh)
        bm_flipped = bm.copy()
        for f in bm_flipped.faces:
            f.normal_flip()

        new_objs = []
        for obj in objs:
            if obj.type != "MESH" or obj == cutter:
                continue
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()

            for collection in obj.users_collection:
                collection.objects.link(new_obj)

            mod = new_obj.modifiers.new(type="BOOLEAN", name="Boolean")
            mod.object = cutter
            with bpy.context.temp_override(object=new_obj):
                bpy.ops.object.modifier_apply(modifier="Boolean")

            bm_flipped.to_mesh(cutter_mesh)

            mod = obj.modifiers.new(type="BOOLEAN", name="Boolean")
            mod.object = cutter
            with bpy.context.temp_override(object=obj):
                bpy.ops.object.modifier_apply(modifier="Boolean")

            bm.to_mesh(cutter_mesh)

            new_objs.append(new_obj)

        bm.to_mesh(cutter_mesh)
        bm.free()
        bm_flipped.free()
        return new_objs
