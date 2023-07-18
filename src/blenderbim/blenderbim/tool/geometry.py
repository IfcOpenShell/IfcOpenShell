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
import struct
import hashlib
import logging
import numpy as np
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.style
import blenderbim.core.spatial
import blenderbim.tool as tool
import blenderbim.bim.import_ifc
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


class Geometry(blenderbim.core.tool.Geometry):
    @classmethod
    def change_object_data(cls, obj, data, is_global=False):
        if is_global:
            if obj.mode == "EDIT":
                raise Exception("user_remap is not supported in EDIT mode")
            obj.data.user_remap(data)
        else:
            obj.data = data

    @classmethod
    def clear_cache(cls, element):
        cache = IfcStore.get_cache()
        if cache:
            cache.remove(element.GlobalId)

    @classmethod
    def clear_modifiers(cls, obj):
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

    @classmethod
    def clear_scale(cls, obj):
        if (obj.scale - Vector((1.0, 1.0, 1.0))).length > 1e-4:
            if obj.data.users == 1:
                context_override = {}
                context_override["object"] = context_override["active_object"] = obj
                context_override["selected_objects"] = context_override["selected_editable_objects"] = [obj]
                bpy.ops.object.transform_apply(context_override, location=False, rotation=False, scale=True)
            else:
                obj.scale = Vector((1.0, 1.0, 1.0))

    @classmethod
    def delete_data(cls, data):
        bpy.data.meshes.remove(data)

    @classmethod
    def delete_ifc_object(cls, obj):
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        if element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            return blenderbim.core.drawing.remove_drawing(tool.Ifc, tool.Drawing, drawing=element)
        if element.is_a("IfcRelSpaceBoundary"):
            ifcopenshell.api.run("boundary.remove_boundary", tool.Ifc.get(), boundary=element)
            return bpy.data.objects.remove(obj)

        collection = obj.BIMObjectProperties.collection
        if collection:
            parent = ifcopenshell.util.element.get_aggregate(element)
            if not parent:
                parent = ifcopenshell.util.element.get_container(element)
            if parent:
                parent_obj = tool.Ifc.get_object(parent)
                if parent_obj:
                    parent_collection = parent_obj.BIMObjectProperties.collection
                    for child in collection.children:
                        parent_collection.children.link(child)
            bpy.data.collections.remove(collection)
        if getattr(element, "FillsVoids", None):
            bpy.ops.bim.remove_filling(filling=element.id())

        if element.is_a("IfcOpeningElement"):
            if element.HasFillings:
                for rel in element.HasFillings:
                    bpy.ops.bim.remove_filling(filling=rel.RelatedBuildingElement.id())
            else:
                if element.VoidsElements:
                    bpy.ops.bim.remove_opening(opening_id=element.id())
        else:
            is_spatial = element.is_a() in ("IfcSpatialElement", "IfcSpatialStructureElement")
            if getattr(element, "HasOpenings", None):
                for rel in element.HasOpenings:
                    bpy.ops.bim.remove_opening(opening_id=rel.RelatedOpeningElement.id())
            for port in ifcopenshell.util.system.get_ports(element):
                blenderbim.core.system.remove_port(tool.Ifc, tool.System, port=port)
            ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
            if is_spatial:
                blenderbim.core.spatial.load_container_manager(tool.Spatial)
        try:
            obj.name
            bpy.data.objects.remove(obj)
        except:
            pass

    @classmethod
    def does_representation_id_exist(cls, representation_id):
        try:
            tool.Ifc.get().by_id(representation_id)
            return True
        except:
            return False

    @classmethod
    def duplicate_object_data(cls, obj):
        if obj.data:
            return obj.data.copy()

    @classmethod
    def get_active_representation(cls, obj):
        if obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.ifc_definition_id:
            return tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)

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
        if element.is_a("IfcAnnotation"):
            if element.ObjectType == "TEXT":
                return "IfcTextLiteral"
            elif element.ObjectType == "TEXT_LEADER":
                return "IfcGeometricCurveSet/IfcTextLiteral"

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
    def get_mesh_checksum(cls, mesh):
        data_bytes = b""
        if isinstance(mesh, bpy.types.Mesh):
            vertices = mesh.vertices[:]
            edges = mesh.edges[:]
            faces = mesh.polygons[:]

            # Convert mesh data to bytes
            for v in vertices:
                data_bytes += struct.pack("3f", *v.co)
            for e in edges:
                data_bytes += struct.pack("2i", *e.vertices)
            for f in faces:
                data_bytes += struct.pack("%di" % len(f.vertices), *f.vertices)
        elif isinstance(mesh, bpy.types.Curve):
            splines = mesh.splines[:]

            for spline in splines:
                if spline.type == "BEZIER":
                    for bezier_point in spline.bezier_points:
                        data_bytes += struct.pack("3f", *bezier_point.co)
                        data_bytes += struct.pack("3f", *bezier_point.handle_left)
                        data_bytes += struct.pack("3f", *bezier_point.handle_right)
                else:
                    for point in spline.points:
                        data_bytes += struct.pack("4f", *point.co)

        hasher = hashlib.sha1()
        hasher.update(data_bytes)
        return hasher.hexdigest()

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
    def get_representation_id(cls, representation):
        return representation.id()

    @classmethod
    def get_representation_name(cls, representation):
        return f"{representation.ContextOfItems.id()}/{representation.id()}"

    @classmethod
    def get_styles(cls, obj):
        return [tool.Style.get_style(s.material) for s in obj.material_slots if s.material]

    # TODO: multiple Literals?
    @classmethod
    def get_text_literal(cls, representation):
        texts = [i for i in representation.Items if i.is_a("IfcTextLiteral")]
        if texts:
            return texts[0]

    @classmethod
    def get_total_representation_items(cls, obj):
        return max(1, len(obj.material_slots))

    @classmethod
    def has_data_users(cls, data):
        return data.users != 0

    @classmethod
    def has_geometric_data(cls, obj):
        if not obj.data:
            return False
        if isinstance(obj.data, bpy.types.Mesh):
            return bool(obj.data.vertices)
        elif isinstance(obj.data, bpy.types.Curve):
            return bool(obj.data.splines)
        return False

    @classmethod
    def import_representation(cls, obj, representation, apply_openings=True):
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        element = tool.Ifc.get_entity(obj)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.WELD_VERTICES, True)

        context = representation.ContextOfItems
        if context.ContextIdentifier == "Body" and context.TargetView == "MODEL_VIEW":
            if element.is_a("IfcTypeProduct") or not apply_openings:
                shape = ifcopenshell.geom.create_shape(settings, representation)
            else:
                shape = ifcopenshell.geom.create_shape(settings, element)
        else:
            settings.set(settings.INCLUDE_CURVES, True)
            shape = ifcopenshell.geom.create_shape(settings, representation)

        ifc_importer = blenderbim.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()

        if element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            mesh = ifc_importer.create_camera(element, shape)
        if element.is_a("IfcAnnotation") and ifc_importer.is_curve_annotation(element):
            mesh = ifc_importer.create_curve(element, shape)
        elif shape:
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
        return not all([tool.Cad.is_x(o, 1.0) for o in obj.scale]) or obj in IfcStore.edited_objs

    @classmethod
    def is_mapped_representation(cls, representation):
        return representation.RepresentationType == "MappedRepresentation"

    @classmethod
    def is_meshlike(cls, representation):
        if ifcopenshell.util.representation.resolve_representation(representation).RepresentationType in (
            "AdvancedBrep",
            "Annotation2D",
            "Annotation3D",
            "BoundingBox",
            "Brep",
            "Curve",
            "Curve2D",
            "Curve3D",
            "FillArea",
            "GeometricCurveSet",
            "GeometricSet",
            "Point",
            "PointCloud",
            "Surface",
            "Surface2D",
            "Surface3D",
            "SurfaceModel",
            "Tessellation",
        ):
            return True
        return False

    @classmethod
    def is_profile_based(cls, data):
        return data.BIMMeshProperties.subshape_type == "PROFILE"

    @classmethod
    def is_swept_profile(cls, representation):
        return ifcopenshell.util.representation.resolve_representation(representation).RepresentationType in (
            "SweptSolid",
        )

    @classmethod
    def is_type_product(cls, element):
        return element.is_a("IfcTypeProduct")

    @classmethod
    def link(cls, element, obj):
        obj.BIMMeshProperties.ifc_definition_id = element.id()

    @classmethod
    def record_object_materials(cls, obj):
        obj.data.BIMMeshProperties.material_checksum = str([s.id() for s in cls.get_styles(obj) if s])

    @classmethod
    def record_object_position(cls, obj):
        # These are recorded separately because they have different numerical tolerances
        obj.BIMObjectProperties.location_checksum = repr(np.array(obj.matrix_world.translation).tobytes())
        obj.BIMObjectProperties.rotation_checksum = repr(np.array(obj.matrix_world.to_3x3()).tobytes())

    @classmethod
    def remove_connection(cls, connection):
        tool.Ifc.get().remove(connection)

    @classmethod
    def rename_object(cls, obj, name):
        obj.name = name

    @classmethod
    def replace_object_with_empty(cls, obj):
        element = tool.Ifc.get_entity(obj)
        name = obj.name
        tool.Ifc.unlink(obj=obj, element=element)
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
    def run_style_add_style(cls, obj=None):
        return blenderbim.core.style.add_style(tool.Ifc, tool.Style, obj=obj)

    @classmethod
    def select_connection(cls, connection):
        obj = tool.Ifc.get_object(connection.RelatingElement)
        if obj:
            obj.select_set(True)
        obj = tool.Ifc.get_object(connection.RelatedElement)
        if obj:
            obj.select_set(True)

    @classmethod
    def should_force_faceted_brep(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep

    @classmethod
    def should_force_triangulation(cls):
        return bpy.context.scene.BIMGeometryProperties.should_force_triangulation

    @classmethod
    def should_generate_uvs(cls, obj):
        if tool.Ifc.get().schema == "IFC2X3":
            return False
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == "TEX_COORD" and node.outputs["UV"].links:
                        return True
                    elif node.type == "UVMAP" and node.outputs["UV"].links and node.uv_map:
                        return True
        return False

    @classmethod
    def should_use_presentation_style_assignment(cls):
        return bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
