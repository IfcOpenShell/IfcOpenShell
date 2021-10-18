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
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


class Geometry(blenderbim.core.tool.Geometry):
    @classmethod
    def does_object_have_mesh_with_faces(cls, obj):
        return bool(isinstance(obj.data, bpy.types.Mesh) and len(obj.data.polygons))

    @classmethod
    def duplicate_object_data(cls, obj):
        obj.data = obj.data.copy()
        return obj.data

    @classmethod
    def get_object_data(cls, obj):
        return obj.data

    @classmethod
    def get_object_materials_without_styles(cls, obj):
        return [
            s.material for s in obj.material_slots if s.material and not s.material.BIMMaterialProperties.ifc_style_id
        ]

    @classmethod
    def get_representation_name(cls, context, representation):
        return f"{context.id()}/{representation.id()}"

    @classmethod
    def get_cartesian_point_coordinate_offset(cls, obj):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT":
            return Vector(
                (
                    float(props.blender_eastings),
                    float(props.blender_northings),
                    float(props.blender_orthogonal_height),
                )
            )

    @classmethod
    def get_total_representation_items(cls, obj):
        return max(1, len(obj.material_slots))

    @classmethod
    def link(cls, element, obj):
        obj.BIMMeshProperties.ifc_definition_id = element.id()

    @classmethod
    def rename_object_data(cls, data, name):
        data.name = name

    @classmethod
    def should_force_faceted_brep(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep

    @classmethod
    def should_force_triangulation(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_triangulation

    @classmethod
    def should_use_presentation_style_assignment(cls):
        return bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
