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
    def clear_modifiers(cls, obj):
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

    @classmethod
    def clear_scale(cls, obj):
        if obj.scale != Vector((1.0, 1.0, 1.0)):
            if obj.data.users == 1:
                context_override = {}
                context_override["object"] = context_override["active_object"] = obj
                context_override["selected_objects"] = context_override["selected_editable_objects"] = [obj]
                bpy.ops.object.transform_apply(context_override, location=False, rotation=False, scale=True)
            else:
                obj.scale = Vector((1.0, 1.0, 1.0))

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
    def delete_data(cls, data):
        bpy.data.meshes.remove(data)

    @classmethod
    def does_object_have_mesh_with_faces(cls, obj):
        return bool(isinstance(obj.data, bpy.types.Mesh) and len(obj.data.polygons))

    @classmethod
    def duplicate_object_data(cls, obj):
        return obj.data.copy()

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
    def get_element_type(cls, element):
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_elements_of_type(cls, type):
        return ifcopenshell.util.element.get_types(type)

    @classmethod
    def get_ifc_representation_class(cls, element, representation):
        material = ifcopenshell.util.element.get_material(element)
        if material and material.is_a("IfcMaterialProfileSetUsage"):
            return "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"

        extruded_areas = [e for e in tool.Ifc.get().traverse(representation) if e.is_a() == "IfcExtrudedAreaSolid"]

        if len(extruded_areas) != 1:
            return  # It's too complex for us to derive topologically right now

        profile_def = extruded_areas[0].SweptArea

        if profile_def.is_a() == "IfcRectangleProfileDef":
            return "IfcExtrudedAreaSolid/IfcRectangleProfileDef"
        elif profile_def.is_a() == "IfcCircleProfileDef":
            return "IfcExtrudedAreaSolid/IfcCircleProfileDef"
        return "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"

    @classmethod
    def get_object_data(cls, obj):
        return obj.data

    @classmethod
    def get_object_materials_without_styles(cls, obj):
        return [
            s.material for s in obj.material_slots if s.material and not s.material.BIMMaterialProperties.ifc_style_id
        ]

    @classmethod
    def get_profile_set_usage(cls, element):
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return material

    @classmethod
    def get_representation_data(cls, representation):
        return bpy.data.meshes.get(cls.get_representation_name(representation))

    @classmethod
    def get_representation_name(cls, representation):
        return f"{representation.ContextOfItems.id()}/{representation.id()}"

    @classmethod
    def get_total_representation_items(cls, obj):
        return max(1, len(obj.material_slots))

    @classmethod
    def has_data_users(cls, data):
        return data.users != 0

    @classmethod
    def import_representation(cls, obj, representation, enable_dynamic_voids=False):
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        element = tool.Ifc.get_entity(obj)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.WELD_VERTICES, True)

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
    def import_representation_parameters(cls, data):
        props = data.BIMMeshProperties
        elements = tool.Ifc.get().traverse(tool.Ifc.get().by_id(props.ifc_definition_id))
        props.ifc_parameters.clear()
        for element in elements:
            if element.is_a("IfcRepresentationItem") or element.is_a("IfcParameterizedProfileDef"):
                for i in range(0, len(element)):
                    if element.attribute_type(i) == "DOUBLE":
                        new = props.ifc_parameters.add()
                        new.name = "{}/{}".format(element.is_a(), element.attribute_name(i))
                        new.step_id = element.id()
                        new.type = element.attribute_type(i)
                        new.index = i
                        if element[i]:
                            new.value = element[i]

    @classmethod
    def is_body_representation(cls, representation):
        return representation.ContextOfItems.ContextIdentifier == "Body"

    @classmethod
    def is_box_representation(cls, representation):
        return representation.ContextOfItems.ContextIdentifier == "Box"

    @classmethod
    def is_edited(cls, obj):
        return list(obj.scale) != [1.0, 1.0, 1.0] or obj in IfcStore.edited_objs

    @classmethod
    def is_mapped_representation(cls, representation):
        return representation.RepresentationType == "MappedRepresentation"

    @classmethod
    def is_type_product(cls, element):
        return element.is_a("IfcTypeProduct")

    @classmethod
    def link(cls, element, obj):
        obj.BIMMeshProperties.ifc_definition_id = element.id()

    @classmethod
    def rename_object(cls, obj, name):
        obj.name = name

    @classmethod
    def replace_object_with_empty(cls, obj):
        element = tool.Ifc.get_entity(obj)
        name = obj.name
        tool.Ifc.unlink(obj)
        obj.name = ifcopenshell.guid.new()
        new_obj = bpy.data.objects.new(name, None)
        if element:
            tool.Ifc.link(element, new_obj)
        for collection in obj.users_collection:
            collection.objects.link(new_obj)
        new_obj.matrix_world = obj.matrix_world
        bpy.data.objects.remove(obj)

    @classmethod
    def resolve_mapped_representation(cls, representation):
        if representation.RepresentationType == "MappedRepresentation":
            return cls.resolve_mapped_representation(representation.Items[0].MappingSource.MappedRepresentation)
        return representation

    @classmethod
    def run_geometry_update_representation(cls, obj=None):
        bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="")

    @classmethod
    def should_force_faceted_brep(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep

    @classmethod
    def should_force_triangulation(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_triangulation

    @classmethod
    def should_use_presentation_style_assignment(cls):
        return bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
