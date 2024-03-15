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
import struct
import hashlib
import logging
import numpy as np
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.style
import blenderbim.core.spatial
import blenderbim.core.geometry
import blenderbim.tool as tool
import blenderbim.bim.import_ifc
from math import radians, pi
from mathutils import Vector, Matrix
from blenderbim.bim.ifc import IfcStore
from typing import List


class Geometry(blenderbim.core.tool.Geometry):
    @classmethod
    def change_object_data(cls, obj, data, is_global=False):
        if is_global:
            cls.replace_object_data_globally(obj.data, data)
        else:
            obj.data = data

    @classmethod
    def replace_object_data_globally(cls, old_data, new_data):
        if getattr(old_data, "is_editmode", None):
            raise Exception("user_remap is not supported for meshes in EDIT mode")
        old_data.user_remap(new_data)

    @classmethod
    def clear_cache(cls, element):
        cache = IfcStore.get_cache()
        if cache and hasattr(element, "GlobalId"):
            cache.remove(element.GlobalId)

    @classmethod
    def clear_modifiers(cls, obj):
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

    @classmethod
    def clear_scale(cls, obj):
        # Note that clearing scale has no impact on cameras.
        if (obj.scale - Vector((1.0, 1.0, 1.0))).length > 1e-4:
            if not obj.data:
                location, rotation, _ = obj.matrix_world.decompose()
                obj.matrix_world = Matrix.Translation(location) @ rotation.to_matrix().to_4x4()
                obj.matrix_world.normalize()
            elif obj.data.users == 1:
                context_override = {}
                context_override["object"] = context_override["active_object"] = obj
                context_override["selected_objects"] = context_override["selected_editable_objects"] = [obj]
                with bpy.context.temp_override(**context_override):
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
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
                    for child_object in collection.objects:
                        parent_collection.objects.link(child_object)
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
            is_spatial = element.is_a("IfcSpatialElement") or element.is_a("IfcSpatialStructureElement")
            if getattr(element, "HasOpenings", None):
                for rel in element.HasOpenings:
                    bpy.ops.bim.remove_opening(opening_id=rel.RelatedOpeningElement.id())
            for port in ifcopenshell.util.system.get_ports(element):
                blenderbim.core.system.remove_port(tool.Ifc, tool.System, port=port)
            ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)

            if isinstance(obj.data, bpy.types.Mesh) and not tool.Ifc.get_entity_by_id(
                obj.data.BIMMeshProperties.ifc_definition_id
            ):
                tool.Blender.remove_data_block(obj.data)

            if is_spatial:
                blenderbim.core.spatial.load_container_manager(tool.Spatial)
        try:
            obj.name
            bpy.data.objects.remove(obj)
        except:
            pass

    @classmethod
    def dissolve_triangulated_edges(cls, obj):
        if obj.data and "ios_edges" in obj.data:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            edges_to_keep = set(map(frozenset, obj.data["ios_edges"]))
            edges_to_dissolve = []
            for edge in bm.edges:
                if frozenset([vert.index for vert in edge.verts]) not in edges_to_keep:
                    edges_to_dissolve.append(edge)
            bmesh.ops.dissolve_edges(bm, edges=edges_to_dissolve)
            bm.to_mesh(obj.data)
            bm.free()
            del obj.data["ios_edges"]

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
    def generate_2d_box_mesh(cls, obj, axis="Z"):
        bm = bmesh.new()
        verts = [Vector(corner) for corner in obj.bound_box]
        if axis == "Z":
            verts = [verts[i] for i in [0, 4, 7, 3]]
            for v in verts:
                v.z = 0
        elif axis == "Y":
            verts = [verts[i] for i in [0, 4, 5, 1]]
            for v in verts:
                v.y = 0
        elif axis == "X":
            verts = [verts[i] for i in [4, 7, 6, 5]]
            for v in verts:
                v.x = 0
        bm.faces.new([bm.verts.new(v) for v in verts])

        mesh = bpy.data.meshes.new(name="tmp")
        bm.to_mesh(mesh)
        bm.free()
        return mesh

    @classmethod
    def generate_3d_box_mesh(cls, obj):
        bm = bmesh.new()
        verts = [bm.verts.new(Vector(corner)) for corner in obj.bound_box]

        bm.faces.new([verts[i] for i in [0, 3, 7, 4]])
        bm.faces.new([verts[i] for i in [0, 1, 2, 3]])
        bm.faces.new([verts[i] for i in [0, 4, 5, 1]])
        bm.faces.new([verts[i] for i in [4, 7, 6, 5]])
        bm.faces.new([verts[i] for i in [7, 3, 2, 6]])
        bm.faces.new([verts[i] for i in [1, 5, 6, 2]])

        mesh = bpy.data.meshes.new(name="tmp")
        bm.to_mesh(mesh)
        bm.free()
        return mesh

    @classmethod
    def generate_outline_mesh(cls, obj, axis="+Z"):
        def get_visible_faces(obj, bm, axis="+Z"):
            # A visible face is any face with the normal facing the axis and
            # its centroid not obscured (tested via raycasting) by any other
            # face.
            distance = max(obj.dimensions.xyz)
            if axis == "+Z":
                max_z = max([co[2] for co in obj.bound_box]) + 0.002
                direction = Vector((0, 0, -1))
            elif axis == "-Y":
                min_y = max([co[2] for co in obj.bound_box]) - 0.002
                direction = Vector((0, 1, 0))
            depsgraph = bpy.context.evaluated_depsgraph_get()
            visible_faces = []
            face_offset = obj.matrix_world.to_quaternion() @ Vector((0, 0, distance))
            global_direction = obj.matrix_world.to_quaternion() @ direction
            for face in bm.faces:
                if direction.dot(face.normal) > 0:
                    continue
                if axis == "+Z":
                    face_centroid_at_max = Vector((*face.calc_center_median().xy, max_z))
                elif axis == "-Y":
                    centroid = face.calc_center_median()
                    face_centroid_at_max = Vector((centroid.x, min_y, centroid.z))
                face_centroid_at_max = obj.matrix_world @ face_centroid_at_max
                hit, loc, norm, idx, o, mw = bpy.context.scene.ray_cast(
                    depsgraph, face_centroid_at_max, global_direction, distance=distance
                )
                if o != obj or idx == face.index:
                    visible_faces.append(face)
            return visible_faces

        def get_contour_edges(visible_faces):
            # A contour is any edge where one face is visible and the other isn't.
            contour_edges = []
            for face in visible_faces:
                for edge in face.edges:
                    total_linked_faces = len(edge.link_faces)
                    if total_linked_faces == 1:
                        contour_edges.append(edge)
                    elif total_linked_faces == 2:
                        other_face = edge.link_faces[0] if edge.link_faces[1] == face else edge.link_faces[1]
                        if other_face not in visible_faces:
                            contour_edges.append(edge)
            return contour_edges

        def get_crease_edges(visible_faces, threshold):
            # A crease is any edge with a face angle greater than a threshold.
            crease_edges = []
            for face in visible_faces:
                for edge in face.edges:
                    if len(edge.link_faces) == 2:
                        angle = edge.link_faces[0].normal.angle(edge.link_faces[1].normal)
                        if abs(angle) > threshold:
                            crease_edges.append(edge)
            return crease_edges

        # Calculate outline edges
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        visible_faces = get_visible_faces(obj, bm, axis=axis)
        outline_edges = set(get_contour_edges(visible_faces))
        outline_edges.update(get_crease_edges(visible_faces, radians(60)))

        # Copy outline edges to new bmesh
        bm.to_mesh(obj.data)
        bm_new = bmesh.new()
        vert_map = {}

        for edge in outline_edges:
            verts = []
            for vert in edge.verts:
                if vert not in vert_map:
                    new_vert = bm_new.verts.new(vert.co)
                    vert_map[vert] = new_vert
                verts.append(vert_map[vert])
            bm_new.edges.new(verts)

        # Flatten along axis in new bmesh
        for vert in bm_new.verts:
            if axis == "+Z":
                vert.co.z = 0
            elif axis == "-Y":
                vert.co.y = 0

        # Convert new bmesh to new mesh
        new_mesh = bpy.data.meshes.new("tmp")
        bm_new.to_mesh(new_mesh)

        bm_new.free()
        bm.free()

        return new_mesh

    @classmethod
    def get_active_representation(cls, obj):
        """< IfcShapeRepresentation or None"""
        if obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.ifc_definition_id:
            return tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)

    @classmethod
    def get_active_representation_context(cls, obj):
        active_representation = tool.Geometry.get_active_representation(obj)
        if active_representation:
            return active_representation.ContextOfItems
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_subcontext_parameters(cls, subcontext):
        return (
            subcontext.ContextType,
            subcontext.ContextIdentifier,
            getattr(subcontext, "TargetView", None),
        )

    @classmethod
    def get_representation_by_context(cls, element, context):
        if element.is_a("IfcProduct") and element.Representation:
            for r in element.Representation.Representations:
                if r.ContextOfItems == context:
                    return r
        elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
            for r in element.RepresentationMaps:
                if r.MappedRepresentation.ContextOfItems == context:
                    return r.MappedRepresentation

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
    def get_styles(cls, obj, only_assigned_to_faces=False):
        styles = [tool.Style.get_style(s.material) for s in obj.material_slots if s.material]
        if not only_assigned_to_faces:
            return styles

        usage_count = [0] * len(obj.material_slots)
        if not usage_count:  # if there are no materials, polygons will still use index 0
            return []
        for poly in obj.data.polygons:
            usage_count[poly.material_index] += 1
        styles = [style for style, usage in zip(styles, usage_count, strict=True) if usage > 0]
        return styles

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

        if element.is_a("IfcTypeProduct"):
            # You may only specify a single representation when creating shapes for types
            try:
                shape = ifcopenshell.geom.create_shape(settings, representation)
            except:
                settings.set(settings.INCLUDE_CURVES, True)
                shape = ifcopenshell.geom.create_shape(settings, representation)
        else:
            if not apply_openings:
                settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)

            if context.ContextIdentifier == "Body" and context.TargetView == "MODEL_VIEW":
                try:
                    shape = ifcopenshell.geom.create_shape(settings, element, representation)
                except:
                    settings.set(settings.INCLUDE_CURVES, True)
                    shape = ifcopenshell.geom.create_shape(settings, element, representation)
            else:
                settings.set(settings.INCLUDE_CURVES, True)
                shape = ifcopenshell.geom.create_shape(settings, element, representation)

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
            mesh.BIMMeshProperties.has_openings_applied = apply_openings

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
    def is_text_literal(cls, representation):
        items = ifcopenshell.util.representation.resolve_items(representation)
        return bool([i for i in items if i["item"].is_a("IfcTextLiteral")])

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
    def unresolve_type_representation(cls, representation, occurence):
        if not ifcopenshell.util.element.get_type(occurence):
            return representation

        if representation.RepresentationType == "MappedRepresentation":
            return representation

        for mapped_representation in occurence.Representation.Representations:
            if cls.resolve_mapped_representation(mapped_representation) == representation:
                return mapped_representation

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

    @classmethod
    def get_model_representations(cls):
        return tool.Ifc.get().by_type("IfcShapeRepresentation")

    @classmethod
    def flip_object(cls, obj, flip_local_axes):
        assert len(flip_local_axes) == 2, "flip_local_axes must be two axes to flip"
        rotation_axis = next(i for i in "XYZ" if i not in flip_local_axes)
        rotation_axis_i = "XYZ".index(rotation_axis)

        bb_data = tool.Blender.get_object_bounding_box(obj)
        # min max points of rotated plane of origin based bounding box
        min_point = Vector([min(i, 0) for i in bb_data["min_point"]])
        max_point = Vector([max(i, 0) for i in bb_data["max_point"]])
        # keep it in rotated plane only
        max_point[rotation_axis_i] = min_point[rotation_axis_i]

        # to compensate for flipped two axes
        # we adjust new max point to match previous min point (or vice versa)
        original_min_point = obj.matrix_world @ min_point
        obj.matrix_world = obj.matrix_world @ Matrix.Rotation(pi, 4, rotation_axis)
        new_max_point = obj.matrix_world @ max_point
        obj.matrix_world.translation += original_min_point - new_max_point

        bpy.context.view_layer.update()

    @classmethod
    def reload_representation(cls, obj):
        """reload `obj` active representation"""
        if not obj.data:
            return
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        blenderbim.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=True,
            is_global=True,
            should_sync_changes_first=False,
            apply_openings=True,
        )

    @classmethod
    def remove_representation_item(cls, representation_item):
        # NOTE: we assume it's not the last representation item
        # otherwise we probably would need to remove representation too
        # NOTE: a lot of shared code with `geometry.remove_representation`
        ifc_file = tool.Ifc.get()
        shape_aspects = []

        consider_inverses = []
        styled_item, colour, texture, layer = None, None, None, None
        [consider_inverses.append(styled_item := t) for t in representation_item.StyledByItem]
        # IFC2X3 is using LayerAssignments
        for t in (
            representation_item.LayerAssignment
            if hasattr(representation_item, "LayerAssignment")
            else representation_item.LayerAssignments
        ):
            consider_inverses.append(layer := t)
        # IfcTessellatedFaceSet
        [consider_inverses.append(colour := t) for t in getattr(representation_item, "HasColours", [])]
        [consider_inverses.append(texture := t) for t in getattr(representation_item, "HasTextures", [])]

        for inverse in ifc_file.get_inverse(representation_item):
            if inverse.is_a("IfcShapeRepresentation"):
                if inverse.OfShapeAspect:
                    shape_aspects.append(inverse.OfShapeAspect[0])
                else:
                    representation = inverse

        if styled_item:
            ifc_file.remove(styled_item)
        if layer and len(layer.Items) == 1:
            ifc_file.remove(styled_item)
        if colour:
            ifcopenshell.util.element.remove_deep2(ifc_file, colour)
        if texture:
            ifcopenshell.util.element.remove_deep2(ifc_file, texture)

        for shape_aspect in shape_aspects:
            cls.remove_representation_items_from_shape_aspect([representation_item], shape_aspect)

        representation.Items = tuple(set(representation.Items) - {representation_item})
        also_consider = list(consider_inverses)
        ifcopenshell.util.element.remove_deep2(ifc_file, representation_item, also_consider=also_consider)

    @classmethod
    def create_shape_aspect(cls, product_shape, base_representation, items, previous_shape_aspect=None):
        """
        > `product_shape` - IfcProductDefinitionShape or IfcRepresentationMap\n
        > `base_representation` - base representation to get context attributes from\n
        > `items` - representation items\n
        > `previous_shape_aspect` - (optional) previous shape aspect, if provided\n
        items will be removed the previous shape aspect first\n

        < IfcShapeAspect
        """

        if previous_shape_aspect is not None:
            cls.remove_representation_items_from_shape_aspect(items, previous_shape_aspect)

        shape_aspect = tool.Ifc.get().createIfcShapeAspect(
            PartOfProductDefinitionShape=product_shape, ShapeRepresentations=()
        )
        # keep IfcShapeAspect and IfcShapeRepresentation valid
        rep = tool.Geometry.add_shape_aspect_representation(shape_aspect, base_representation)
        rep.Items = items

        return shape_aspect

    @classmethod
    def remove_representation_items_from_shape_aspect(cls, representation_items, shape_aspect):
        ifc_file = tool.Ifc.get()
        # as shape aspect might have multiple representations
        # it's easier to find it from the item
        for inverse in ifc_file.get_inverse(representation_items[0]):
            if inverse.is_a("IfcShapeRepresentation") and shape_aspect in inverse.OfShapeAspect:
                representation = inverse
                break

        # removing last item would make representation invalid
        if len(representation.Items) == len(representation_items):
            # removing last representation would make shape aspect invalid.
            # remove shape aspect first otherwise remove_representation won't remove it because of the inverse
            if len(shape_aspect.ShapeRepresentations) == 1:
                ifc_file.remove(shape_aspect)
            tool.Ifc.run("geometry.remove_representation", representation=representation)
        else:
            items = set(representation.Items) - set(representation_items)
            representation.Items = tuple(items)

    @classmethod
    def add_representation_item_to_shape_aspect(cls, representation_items, shape_aspect):
        """NOTE: we assume that all items belonged to the same representation and to the same shape aspect"""
        ifc_file = tool.Ifc.get()
        previous_shape_aspect = None
        for inverse in ifc_file.get_inverse(representation_items[0]):
            if inverse.is_a("IfcShapeRepresentation"):
                if inverse.OfShapeAspect:
                    # item is already added to the shape aspect
                    if inverse.OfShapeAspect[0] == shape_aspect:
                        return
                    previous_shape_aspect = inverse.OfShapeAspect[0]
                else:
                    base_representation = inverse

        # remove item from previous shape aspect
        if previous_shape_aspect:
            cls.remove_representation_items_from_shape_aspect(representation_items, previous_shape_aspect)
        shape_aspect_representation = cls.get_shape_aspect_representation(
            shape_aspect, base_representation, create_new=True
        )
        shape_aspect_representation.Items = shape_aspect_representation.Items + tuple(representation_items)

    @classmethod
    def get_shape_aspect_representation(cls, shape_aspect, base_representation, create_new=False):
        for representation in shape_aspect.ShapeRepresentations:
            if (
                representation.ContextOfItems == base_representation.ContextOfItems
                and representation.RepresentationIdentifier == base_representation.RepresentationIdentifier
                and representation.RepresentationType == base_representation.RepresentationType
            ):
                return representation

        if not create_new:
            return None

        return cls.add_shape_aspect_representation(shape_aspect, base_representation)

    @classmethod
    def add_shape_aspect_representation(cls, shape_aspect, base_representation):
        shape_aspect_representation = tool.Ifc.get().createIfcShapeRepresentation(
            ContextOfItems=base_representation.ContextOfItems,
            RepresentationIdentifier=base_representation.RepresentationIdentifier,
            RepresentationType=base_representation.RepresentationType,
        )
        shape_aspect.ShapeRepresentations = shape_aspect.ShapeRepresentations + (shape_aspect_representation,)
        return shape_aspect_representation

    @classmethod
    def get_shape_aspect_representation_for_item(cls, shape_aspect, representation_item):
        ifc_file = tool.Ifc.get()
        for inverse in ifc_file.get_inverse(representation_item):
            if inverse.is_a("IfcShapeRepresentation"):
                if inverse.OfShapeAspect:
                    if inverse.OfShapeAspect[0] == shape_aspect:
                        return inverse

    @classmethod
    def get_shape_aspect_styles(cls, element, shape_aspect, representation_item) -> List[ifcopenshell.entity_instance]:
        """update `representation_item` style based on styles connected to the `shape_aspect`
        through material constituents with the same name
        """
        if not shape_aspect.Name:
            return []

        # get material connected to the shape aspect with material constituent name
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if not material or not material.is_a("IfcMaterialConstituentSet") or not material.MaterialConstituents:
            return []

        matching_constituent = next((c for c in material.MaterialConstituents if c.Name == shape_aspect.Name), None)
        if matching_constituent is None:
            return []

        constituent_material = matching_constituent.Material
        if not constituent_material.HasRepresentation:
            return []

        # get shape aspect representation for item
        shape_aspect_representation = cls.get_shape_aspect_representation_for_item(shape_aspect, representation_item)

        # get the styles for this context
        material_representation = None
        for r in constituent_material.HasRepresentation[0].Representations:
            if r.ContextOfItems == shape_aspect_representation.ContextOfItems:
                material_representation = r
                break

        if material_representation is None:
            return []

        styles = [s for s in tool.Ifc.get().traverse(material_representation) if s.is_a("IfcPresentationStyle")]
        return styles

    @classmethod
    def delete_opening_object_placement(cls, placement):
        model = tool.Ifc.get()
        ifcopenshell.util.element.remove_deep2(model, placement)
