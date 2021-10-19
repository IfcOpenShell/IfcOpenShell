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
import logging
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.import_ifc
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


class Geometry(blenderbim.core.tool.Geometry):
    @classmethod
    def change_object_data(cls, obj, data, is_global=False):
        if is_global:
            obj.data.user_remap(data)
        else:
            obj.data = data

    @classmethod
    def clear_dynamic_voids(cls, obj):
        for modifier in obj.modifiers:
            if modifier.type == "BOOLEAN" and "IfcOpeningElement" in modifier.name:
                obj.modifiers.remove(modifier)

    @classmethod
    def create_dynamic_voids(cls, obj):
        element = tool.Ifc.get_entity(obj)
        for rel in element.HasOpenings:
            opening_obj = tool.Ifc.get_object(rel.RelatedOpeningElement)
            if not opening_obj:
                continue
            modifier = obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
            modifier.operation = "DIFFERENCE"
            modifier.object = opening_obj
            modifier.solver = "EXACT"
            modifier.use_self = True

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
    def get_representation_data(cls, representation):
        return bpy.data.meshes.get(cls.get_representation_name(representation))

    @classmethod
    def get_representation_name(cls, representation):
        return f"{representation.ContextOfItems.id()}/{representation.id()}"

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
    def import_representation(cls, obj, representation, enable_dynamic_voids=False):
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        element = tool.Ifc.get_entity(obj)
        settings = ifcopenshell.geom.settings()

        if representation.ContextOfItems.ContextIdentifier == "Body":
            if element.is_a("IfcTypeProduct") or enable_dynamic_voids:
                shape = ifcopenshell.geom.create_shape(settings, representation)
            else:
                shape = ifcopenshell.geom.create_shape(settings, element)
        else:
            settings.set(settings.INCLUDE_CURVES, True)
            shape = ifcopenshell.geom.create_shape(settings, representation)

        ifc_importer = blenderbim.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        mesh = ifc_importer.create_mesh(element, shape)
        ifc_importer.material_creator.load_existing_materials()
        ifc_importer.material_creator.create(element, obj, mesh)
        return mesh

    @classmethod
    def is_body_representation(cls, representation):
        return representation.ContextOfItems.ContextIdentifier == "Body"

    @classmethod
    def link(cls, element, obj):
        obj.BIMMeshProperties.ifc_definition_id = element.id()

    @classmethod
    def rename_object(cls, obj, name):
        obj.name = name

    @classmethod
    def resolve_mapped_representation(cls, representation):
        if representation.RepresentationType == "MappedRepresentation":
            return cls.resolve_mapped_representation(representation.Items[0].MappingSource.MappedRepresentation)
        return representation

    @classmethod
    def should_force_faceted_brep(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep

    @classmethod
    def should_force_triangulation(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_triangulation

    @classmethod
    def should_use_presentation_style_assignment(cls):
        return bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
