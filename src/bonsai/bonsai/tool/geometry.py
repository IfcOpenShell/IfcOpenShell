# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import struct
import hashlib
import logging
import numpy as np
import numpy.typing as npt
import multiprocessing
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.grid
import ifcopenshell.api.style
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
import ifcopenshell.util.system
import ifcopenshell.util.unit
import bonsai.core.tool
import bonsai.core.drawing
import bonsai.core.geometry
import bonsai.core.spatial
import bonsai.core.style
import bonsai.core.system
import bonsai.tool as tool
import bonsai.bim.helper
import bonsai.bim.import_ifc
from collections import defaultdict
from math import radians, pi
from mathutils import Vector, Matrix
from bonsai.bim.ifc import IfcStore
from typing import Union, Iterable, Optional, Literal, Iterator, List, TYPE_CHECKING, get_args, Generator
from typing_extensions import TypeIs

if TYPE_CHECKING:
    from bonsai.bim.prop import Attribute


class Geometry(bonsai.core.tool.Geometry):
    @classmethod
    def change_object_data(cls, obj: bpy.types.Object, data: bpy.types.ID, is_global: bool = False) -> None:
        if is_global:
            cls.replace_object_data_globally(obj.data, data)
        else:
            obj.data = data

    @classmethod
    def replace_object_data_globally(cls, old_data: bpy.types.ID, new_data: bpy.types.ID) -> None:
        if getattr(old_data, "is_editmode", None):
            raise Exception("user_remap is not supported for meshes in EDIT mode")
        old_data.user_remap(new_data)

    @classmethod
    def clear_cache(cls, element: ifcopenshell.entity_instance) -> None:
        cache = IfcStore.get_cache()
        if cache and hasattr(element, "GlobalId"):
            cache.remove(element.GlobalId)

    @classmethod
    def clear_modifiers(cls, obj: bpy.types.Object) -> None:
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

    @classmethod
    def clear_scale(cls, obj: bpy.types.Object) -> None:
        """Apply and clear object scale.

        If it's a mesh object, scale will be applied to it's mesh.
        Note that clearing scale has no impact on cameras.
        """
        if cls.is_scaled(obj):
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
    def delete_data(cls, data: bpy.types.Mesh) -> None:
        # Try except is faster than isinstance
        try:
            bpy.data.meshes.remove(data)
        except TypeError:
            try:
                bpy.data.curves.remove(data)
            except TypeError:
                bpy.data.cameras.remove(data)

    @classmethod
    def is_locked(cls, element: ifcopenshell.entity_instance) -> bool:
        if element.is_a("IfcProject"):
            return True
        elif tool.Root.is_spatial_element(element) and bpy.context.scene.BIMSpatialDecompositionProperties.is_locked:
            return True
        elif (
            element.is_a("IfcPositioningElement") or element.is_a("IfcGrid") or element.is_a("IfcGridAxis")
        ) and bpy.context.scene.BIMGridProperties.is_locked:
            return True
        return False

    @classmethod
    def lock_object(cls, obj: bpy.types.Object) -> None:
        obj.lock_location = (True, True, True)
        obj.lock_rotation = (True, True, True)
        obj.lock_rotation_w = True
        obj.lock_rotations_4d = True
        obj.lock_scale = (True, True, True)

    @classmethod
    def unlock_object(cls, obj: bpy.types.Object) -> None:
        obj.lock_location = (False, False, False)
        obj.lock_rotation = (False, False, False)
        obj.lock_rotation_w = False
        obj.lock_rotations_4d = False
        obj.lock_scale = (False, False, False)

    @classmethod
    def lock_scale(cls, obj: bpy.types.Object) -> None:
        obj.lock_scale = (True, True, True)

    @classmethod
    def unlock_scale(cls, obj: bpy.types.Object) -> None:
        obj.lock_scale = (False, False, False)

    @classmethod
    def unlock_scale_object_with_openings(cls, obj: bpy.types.Object) -> None:
        element = tool.Ifc.get_entity(obj)
        queue = {element}
        while queue:
            element = queue.pop()
            if getattr(element, "HasOpenings", None):
                # Part still has openings, keep it locked.
                continue
            obj = tool.Ifc.get_object(element)
            cls.unlock_scale(obj)
            queue.update(new_parts := set(ifcopenshell.util.element.get_parts(element)))

    @classmethod
    def delete_ifc_item(cls, obj: bpy.types.Object) -> None:
        props = bpy.context.scene.BIMGeometryProperties
        if len(props.item_objs) == 1:
            return
        for i, item_obj in enumerate(props.item_objs):
            if item_obj.obj == obj:
                props.item_objs.remove(i)
                break
        item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        cls.remove_representation_item(item)
        cls.reload_representation(props.representation_obj)
        bpy.data.objects.remove(obj)

    @classmethod
    def delete_ifc_object(cls, obj: bpy.types.Object) -> None:
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            return bonsai.core.drawing.remove_drawing(tool.Ifc, tool.Drawing, drawing=element)
        elif element.is_a("IfcRelSpaceBoundary"):
            ifcopenshell.api.run("boundary.remove_boundary", tool.Ifc.get(), boundary=element)
            return bpy.data.objects.remove(obj)
        elif element.is_a("IfcGridAxis"):
            is_last_axis = False
            # Deleting the last W axis is OK
            if ((grid := element.PartOfU) and len(grid[0].UAxes) == 1) or (
                (grid := element.PartOfV) and len(grid[0].VAxes) == 1
            ):
                is_last_axis = True
            if is_last_axis:
                return
            ifcopenshell.api.run("grid.remove_grid_axis", tool.Ifc.get(), axis=element)
            return bpy.data.objects.remove(obj)
        elif element.is_a("IfcGrid"):
            axes = list(element.UAxes or []) + list(element.VAxes or []) + list(element.WAxes or [])
            for axis in axes:
                if axis_obj := tool.Ifc.get_object(axis):
                    bpy.data.objects.remove(axis_obj)
                ifcopenshell.api.grid.remove_grid_axis(tool.Ifc.get(), axis=axis)

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
            is_spatial = tool.Root.is_spatial_element(element)
            if getattr(element, "HasOpenings", None):
                for rel in element.HasOpenings:
                    bpy.ops.bim.remove_opening(opening_id=rel.RelatedOpeningElement.id())
            for port in ifcopenshell.util.system.get_ports(element):
                bonsai.core.system.remove_port(tool.Ifc, tool.System, port=port)
            ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)

            if isinstance(obj.data, bpy.types.Mesh) and not tool.Ifc.get_entity_by_id(
                obj.data.BIMMeshProperties.ifc_definition_id
            ):
                tool.Blender.remove_data_block(obj.data)

            if is_spatial:
                bonsai.core.spatial.import_spatial_decomposition(tool.Spatial)
        try:
            obj.name
            if bpy.context.scene.BIMGeometryProperties.representation_obj == obj:
                bpy.context.scene.BIMGeometryProperties.representation_obj = None
            bpy.data.objects.remove(obj)
        except:
            pass

    @classmethod
    def dissolve_triangulated_edges(cls, obj: bpy.types.Object) -> None:
        # AdvancedBreps may contain non-faceted, curved faces (e.g. as part of
        # a cylinder) so dissolving edges should not be allowed.
        mesh_element = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        if (
            mesh_element.is_a("IfcShapeRepresentation")
            and ifcopenshell.util.representation.resolve_representation(mesh_element).RepresentationType
            == "AdvancedBrep"
        ) or mesh_element.is_a("IfcAdvancedBrep"):
            return
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
    def apply_item_ids_as_vertex_groups(cls, obj: bpy.types.Object) -> None:
        """Save mesh-object item_ids as vertex groups in format 'ios_item_id_xxxx'.

        Since ios_item_ids are item ids for original faces (triangulated),
        this method should be used before `dissolve_triangulated_edges`."""

        mesh = obj.data
        assert isinstance(mesh, bpy.types.Mesh)
        # I guess, they're already applied.
        if "ios_item_ids" not in mesh:
            return

        # Just to be safe.
        if "ios_edges" not in mesh:
            raise Exception("Triangulated edges are already dissolved, cannot aply item ids.")

        polygon_verts = np.empty(len(mesh.polygons) * 3, dtype="I")
        mesh.polygons.foreach_get("vertices", polygon_verts)
        polygon_verts = polygon_verts.reshape(-1, 3)

        ios_item_ids: list[int] = mesh["ios_item_ids"]
        vertices_by_item_ids = defaultdict(list[int])
        for i, item_id in enumerate(ios_item_ids):
            # .tolist() as VertexGroup.add() is not ready for uints.
            vertices_by_item_ids[item_id].extend(polygon_verts[i].tolist())

        for item_id, verts in vertices_by_item_ids.items():
            vg = obj.vertex_groups.new(name=f"ios_item_id_{item_id}")
            vg.add(verts, weight=1.0, type="ADD")

        del mesh["ios_item_ids"]

    @classmethod
    def does_representation_id_exist(cls, representation_id: int) -> bool:
        try:
            tool.Ifc.get().by_id(representation_id)
            return True
        except:
            return False

    @classmethod
    def duplicate_object_data(cls, obj: bpy.types.Object) -> Union[bpy.types.ID, None]:
        if obj.data:
            return obj.data.copy()

    @classmethod
    def generate_2d_box_mesh(cls, obj: bpy.types.Object, axis: Literal["X", "Y", "Z"] = "Z") -> bpy.types.Mesh:
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
    def generate_3d_box_mesh(cls, obj: bpy.types.Object) -> bpy.types.Mesh:
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
    def generate_outline_mesh(cls, obj: bpy.types.Object, axis: Literal["+Z", "-Y"] = "+Z") -> bpy.types.Mesh:
        def get_visible_faces(
            obj: bpy.types.Object, bm: bmesh.types.BMesh, axis: Literal["+Z", "-Y"] = "+Z"
        ) -> list[bmesh.types.BMFace]:
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

        def get_contour_edges(visible_faces: list[bmesh.types.BMFace]) -> list[bmesh.types.BMEdge]:
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

        def get_crease_edges(visible_faces: list[bmesh.types.BMFace], threshold: float) -> list[bmesh.types.BMEdge]:
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
    def get_active_representation(cls, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
        """< IfcShapeRepresentation or None"""
        if obj.data and hasattr(obj.data, "BIMMeshProperties") and obj.data.BIMMeshProperties.ifc_definition_id:
            return tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)

    @classmethod
    def get_data_representation(cls, data: bpy.types.Mesh) -> ifcopenshell.entity_instance | None:
        if hasattr(data, "BIMMeshProperties") and data.BIMMeshProperties.ifc_definition_id:
            return tool.Ifc.get().by_id(data.BIMMeshProperties.ifc_definition_id)

    @classmethod
    def get_active_representation_context(cls, obj: bpy.types.Object) -> ifcopenshell.entity_instance:
        active_representation = tool.Geometry.get_active_representation(obj)
        if active_representation:
            return active_representation.ContextOfItems
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_subcontext_parameters(
        cls, subcontext: ifcopenshell.entity_instance
    ) -> tuple[Union[str, None], Union[str, None], Union[str, None]]:
        return (
            subcontext.ContextType,
            subcontext.ContextIdentifier,
            getattr(subcontext, "TargetView", None),
        )

    @classmethod
    def get_representations_iter(cls, element: ifcopenshell.entity_instance) -> Iterator[ifcopenshell.entity_instance]:
        return ifcopenshell.util.representation.get_representations_iter(element)

    @classmethod
    def get_representation_by_context(
        cls, element: ifcopenshell.entity_instance, context: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.representation.get_representation(element, context)

    @classmethod
    def get_cartesian_point_offset(cls, obj: bpy.types.Object) -> npt.NDArray[np.float64] | None:
        if (
            obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT"
            and obj.BIMObjectProperties.cartesian_point_offset
        ):
            return np.array(tuple(map(float, obj.BIMObjectProperties.cartesian_point_offset.split(","))))

    @classmethod
    def get_element_type(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_elements_of_type(cls, type: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_types(type)

    @classmethod
    def get_ifc_representation_class(
        cls, element: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
    ) -> Union[str, None]:
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
    def get_material_checksum(cls, obj: bpy.types.Object) -> str:
        return str([s.id() for s in cls.get_styles(obj) if s])

    @classmethod
    def get_mesh_checksum(cls, mesh: Union[bpy.types.Mesh, bpy.types.Curve]) -> str:
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
    def get_object_data(cls, obj: bpy.types.Object) -> Union[bpy.types.ID, None]:
        return obj.data

    @classmethod
    def get_object_materials_without_styles(cls, obj: bpy.types.Object) -> list[bpy.types.Material]:
        return [
            s.material for s in obj.material_slots if s.material and not s.material.BIMStyleProperties.ifc_definition_id
        ]

    @classmethod
    def get_profile_set_usage(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return material

    @classmethod
    def get_representation_data(cls, representation: ifcopenshell.entity_instance) -> Union[bpy.types.Mesh, None]:
        return bpy.data.meshes.get(cls.get_representation_name(representation))

    @classmethod
    def get_representation_id(cls, representation: ifcopenshell.entity_instance) -> int:
        return representation.id()

    @classmethod
    def get_representation_name(cls, representation: ifcopenshell.entity_instance) -> str:
        return tool.Loader.get_mesh_name(representation.ContextOfItems.id(), representation.id())

    @classmethod
    def get_styles(
        cls, obj: bpy.types.Object, only_assigned_to_faces: bool = False
    ) -> list[Union[ifcopenshell.entity_instance, None]]:
        styles = [tool.Ifc.get_entity(s.material) for s in obj.material_slots if s.material]
        if not only_assigned_to_faces:
            return styles

        usage_count = [0] * len(obj.material_slots)
        if not usage_count:  # if there are no materials, polygons will still use index 0
            return []

        for poly in obj.data.polygons:
            usage_count[poly.material_index] += 1

        # remove usages for empty material slots
        for i, slot in reversed(list(enumerate(obj.material_slots))):
            if not slot.material:
                del usage_count[i]

        styles = [style for style, usage in zip(styles, usage_count, strict=True) if usage > 0]
        return styles

    # TODO: multiple Literals?
    @classmethod
    def get_text_literal(
        cls, representation: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        texts = [i for i in representation.Items if i.is_a("IfcTextLiteral")]
        if texts:
            return texts[0]

    @classmethod
    def get_total_representation_items(cls, obj: bpy.types.Object) -> int:
        return max(1, len(obj.material_slots))

    @classmethod
    def has_data_users(cls, data: bpy.types.ID) -> bool:
        return data.users != 0

    @classmethod
    def has_geometric_data(cls, obj: bpy.types.Object) -> bool:
        if not obj.data:
            return False
        if isinstance(obj.data, bpy.types.Mesh):
            return bool(obj.data.vertices)
        elif isinstance(obj.data, bpy.types.Curve):
            return bool(obj.data.splines)
        return False

    @classmethod
    def has_material_style_override(cls, element: ifcopenshell.entity_instance) -> bool:
        if element.is_a("IfcTypeProduct"):
            return False
        own_material = ifcopenshell.util.element.get_material(element, should_inherit=False)
        if own_material:
            # Material usages just inherit the style from the type material, so can't override it.
            if own_material.is_a("IfcMaterialUsageDefinition"):
                return False
            own_material = ifcopenshell.util.element.get_materials(element, should_inherit=False)[0]
            inherited_style = cls.get_inherited_material_style(element)
            style = tool.Material.get_style(own_material) if own_material else None
            if inherited_style != style:
                return True
        return False

    @classmethod
    def reimport_element_representations(
        cls, obj: bpy.types.Object, representation: ifcopenshell.entity_instance, apply_openings: bool = True
    ) -> None:
        element = tool.Ifc.get_entity(obj)
        assert element

        elements = set()
        element_types = set()
        representation = ifcopenshell.util.representation.resolve_representation(representation)
        context = representation.ContextOfItems
        for mapped_element in ifcopenshell.util.element.get_elements_by_representation(tool.Ifc.get(), representation):
            if mapped_element.is_a("IfcTypeProduct"):
                element_types.add(mapped_element)
            else:
                elements.add(mapped_element)
                if element_type := ifcopenshell.util.element.get_type(mapped_element):
                    element_types.add(element_type)

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        settings = ifcopenshell.geom.settings()
        settings.set("weld-vertices", True)
        settings.set("apply-default-materials", False)
        settings.set("layerset-first", True)
        settings.set("keep-bounding-boxes", True)
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)

        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()

        # TODO support fallbacks like for point clouds

        settings.set("context-ids", [context.id()])
        if not apply_openings:
            settings.set("disable-opening-subtractions", True)

        shape = None
        if elements:
            iterator = ifcopenshell.geom.iterator(
                settings, tool.Ifc.get(), multiprocessing.cpu_count(), include=elements
            )
        else:
            iterator = None  # For example, when switching representation of a type with no occurrences
        meshes = {}
        if iterator and iterator.initialize():
            while True:
                shape = iterator.get()
                element = tool.Ifc.get().by_id(shape.id)
                if obj := tool.Ifc.get_object(element):
                    mesh_name = tool.Loader.get_mesh_name_from_shape(shape.geometry)
                    mesh = meshes.get(mesh_name)
                    if mesh is None:
                        # Duplicate code
                        representation = tool.Ifc.get().by_id(int(shape.geometry.id.split("-")[0]))
                        if element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
                            mesh = tool.Loader.create_camera(element, representation, shape)
                        elif element.is_a("IfcAnnotation") and ifc_importer.is_curve_annotation(element):
                            mesh = ifc_importer.create_curve(element, shape)
                        elif shape:
                            cartesian_point_offset = cls.get_cartesian_point_offset(obj)
                            if cartesian_point_offset is None:
                                cartesian_point_offset = False
                            mesh = ifc_importer.create_mesh(
                                element, shape, cartesian_point_offset=cartesian_point_offset
                            )
                            ifc_importer.material_creator.load_existing_materials()
                            shape_has_openings = cls.does_shape_has_openings(shape)
                            ifc_importer.material_creator.create(element, obj, mesh, shape_has_openings)
                            mesh.BIMMeshProperties.has_openings_applied = apply_openings
                            if not shape_has_openings:
                                tool.Loader.load_indexed_colour_map(representation, mesh)
                        tool.Loader.link_mesh(shape, mesh)
                        meshes[mesh_name] = mesh

                    old_mesh = obj.data
                    if type(old_mesh) == type(mesh):
                        cls.change_object_data(obj, mesh, is_global=False)
                    else:
                        obj = cls.recreate_object_with_data(obj, mesh, is_global=False)
                    cls.record_object_materials(obj)
                    if not cls.has_data_users(old_mesh):
                        cls.delete_data(old_mesh)
                    cls.clear_modifiers(obj)
                    cls.clear_cache(element)

                if not iterator.next():
                    break

        for element in element_types:
            if obj := tool.Ifc.get_object(element):
                if representation := ifcopenshell.util.representation.get_representation(element, context):
                    geometry = ifcopenshell.geom.create_shape(settings, representation)
                    mesh_name = tool.Loader.get_mesh_name_from_shape(geometry)
                    mesh = meshes.get(mesh_name)
                    if mesh is None:
                        # Duplicate code
                        representation = tool.Ifc.get().by_id(int(geometry.id.split("-")[0]))
                        if geometry:
                            mesh = ifc_importer.create_mesh(element, geometry)
                            ifc_importer.material_creator.load_existing_materials()
                            shape_has_openings = False
                            ifc_importer.material_creator.create(element, obj, mesh, shape_has_openings)
                            mesh.BIMMeshProperties.has_openings_applied = apply_openings
                            if not shape_has_openings:
                                tool.Loader.load_indexed_colour_map(representation, mesh)
                        tool.Loader.link_mesh(geometry, mesh)
                        meshes[mesh_name] = mesh

                    old_mesh = obj.data
                    if type(old_mesh) == type(mesh):
                        cls.change_object_data(obj, mesh, is_global=False)
                    else:
                        obj = cls.recreate_object_with_data(obj, mesh, is_global=False)
                    cls.record_object_materials(obj)
                    if not cls.has_data_users(old_mesh):
                        cls.delete_data(old_mesh)
                    cls.clear_modifiers(obj)
                    cls.clear_cache(element)

    @classmethod
    def does_shape_has_openings(
        cls, shape: Union[ifcopenshell.geom.ShapeElementType, ifcopenshell.geom.ShapeType]
    ) -> bool:
        return "openings" in getattr(shape, "geometry", shape).id

    @classmethod
    def import_representation_parameters(cls, data: bpy.types.Mesh) -> None:
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
    def is_body_representation(cls, representation: ifcopenshell.entity_instance) -> bool:
        return representation.ContextOfItems.ContextIdentifier == "Body"

    @classmethod
    def is_box_representation(cls, representation: ifcopenshell.entity_instance) -> bool:
        return representation.ContextOfItems.ContextIdentifier == "Box"

    @classmethod
    def is_data_supported_for_adding_representation(cls, data: Union[bpy.types.ID, None]) -> TypeIs[
        Union[
            bpy.types.Mesh,
            bpy.types.Curve,
            bpy.types.Camera,
        ]
    ]:
        supported_types = (
            bpy.types.Mesh,
            bpy.types.Curve,
            bpy.types.Camera,
        )
        if not data:
            return False
        return isinstance(data, supported_types)

    TYPES_WITH_MESH_PROPERTIES = Union[
        bpy.types.Mesh,
        bpy.types.Curve,
        bpy.types.Camera,
        bpy.types.PointLight,
    ]

    @classmethod
    def has_mesh_properties(
        cls, data: Union[bpy.types.ID, None], supported_types=get_args(TYPES_WITH_MESH_PROPERTIES)
    ) -> TypeIs[TYPES_WITH_MESH_PROPERTIES]:
        if not data:
            return False
        return isinstance(data, supported_types)

    @classmethod
    def is_scaled(cls, obj: bpy.types.Object) -> bool:
        return not all([tool.Cad.is_x(o, 1.0) for o in obj.scale])

    @classmethod
    def is_mapped_representation(cls, representation: ifcopenshell.entity_instance) -> bool:
        return representation.RepresentationType == "MappedRepresentation"

    @classmethod
    def is_meshlike(cls, representation: ifcopenshell.entity_instance) -> bool:
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
    def is_meshlike_item(cls, item: ifcopenshell.entity_instance) -> bool:
        return item.is_a("IfcTessellatedItem") or item.is_a("IfcManifoldSolidBrep")

    @classmethod
    def is_curvelike_item(cls, item: ifcopenshell.entity_instance) -> bool:
        return (
            item.is_a("IfcPolyline")
            or item.is_a("IfcCompositeCurve")
            or item.is_a("IfcIndexedPolyCurve")
            or item.is_a("IfcCircle")
        )

    @classmethod
    def is_movable(cls, item: ifcopenshell.entity_instance) -> bool:
        return item.is_a("IfcSweptAreaSolid")

    @classmethod
    def is_profile_based(cls, data: bpy.types.Mesh) -> bool:
        return data.BIMMeshProperties.subshape_type == "PROFILE"

    @classmethod
    def is_swept_profile(cls, representation: ifcopenshell.entity_instance) -> bool:
        return ifcopenshell.util.representation.resolve_representation(representation).RepresentationType in (
            "SweptSolid",
        )

    @classmethod
    def is_representation_item(cls, obj: bpy.types.Object) -> bool:
        return bool(
            (data := obj.data)
            and isinstance(data, Geometry.TYPES_WITH_MESH_PROPERTIES)
            and (ifc_id := data.BIMMeshProperties.ifc_definition_id)
            and tool.Ifc.get().by_id(ifc_id).is_a("IfcRepresentationItem")
        )

    @classmethod
    def is_text_literal(cls, representation: ifcopenshell.entity_instance) -> bool:
        items = ifcopenshell.util.representation.resolve_items(representation)
        return bool([i for i in items if i["item"].is_a("IfcTextLiteral")])

    @classmethod
    def is_type_product(cls, element: ifcopenshell.entity_instance) -> bool:
        return element.is_a("IfcTypeProduct")

    @classmethod
    def link(cls, element: ifcopenshell.entity_instance, obj: bpy.types.Mesh) -> None:
        tool.Ifc.link(element, obj)

    @classmethod
    def record_object_materials(cls, obj: bpy.types.Object) -> None:
        obj.data.BIMMeshProperties.material_checksum = cls.get_material_checksum(obj)

    @classmethod
    def record_object_position(cls, obj: bpy.types.Object) -> None:
        # These are recorded separately because they have different numerical tolerances
        obj.BIMObjectProperties.location_checksum = repr(np.array(obj.matrix_world.translation).tobytes())
        obj.BIMObjectProperties.rotation_checksum = repr(np.array(obj.matrix_world.to_3x3()).tobytes())

    @classmethod
    def remove_connection(cls, connection: ifcopenshell.entity_instance) -> None:
        tool.Ifc.get().remove(connection)

    @classmethod
    def rename_object(cls, obj: bpy.types.Object, name: str) -> None:
        obj.name = name

    @classmethod
    def recreate_object_with_data(
        cls, obj: bpy.types.Object, data: Union[bpy.types.ID, None], is_global: bool = False
    ) -> bpy.types.Object:
        """Recreate a Blender object with the provided `data`.

        This method is useful when an object should no longer have associated
        data (in Blender, you cannot simply assign .data to None).
        Or if object is an empty and should now have a data.

        The object's original data is not handled by this method and should be
        processed separately to avoid leaving orphan data.

        Original `obj` is deleted and becomes invalid and should be replaced
        with an object returned by this method.

        :param is_global: Whether all `obj` occurrences should also be recreated
        with the provided `data`. Works only if `obj` is an IfcTypeProduct.
        :return: The newly recreated object.
        """
        element = tool.Ifc.get_entity(obj)
        name = obj.name
        if element:
            if is_global and element.is_a("IfcTypeProduct"):
                ocurrences = ifcopenshell.util.element.get_types(element)
                for occurrence in ocurrences:
                    cls.recreate_object_with_data(tool.Ifc.get_object(occurrence), data)

            tool.Ifc.unlink(element=element)

        obj.name = ifcopenshell.guid.new()
        new_obj = bpy.data.objects.new(name, data)

        if element:
            tool.Ifc.link(element, new_obj)
        for collection in obj.users_collection:
            collection.objects.link(new_obj)
        new_obj.matrix_world = obj.matrix_world
        bpy.data.objects.remove(obj)
        return new_obj

    @classmethod
    def resolve_mapped_representation(
        cls, representation: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        if representation.RepresentationType == "MappedRepresentation":
            return cls.resolve_mapped_representation(representation.Items[0].MappingSource.MappedRepresentation)
        return representation

    @classmethod
    def unresolve_type_representation(
        cls, representation: ifcopenshell.entity_instance, occurence: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        if not ifcopenshell.util.element.get_type(occurence):
            return representation

        if representation.RepresentationType == "MappedRepresentation":
            return representation

        context = representation.ContextOfItems
        for mapped_representation in occurence.Representation.Representations:
            if mapped_representation.ContextOfItems != context:
                continue
            if cls.resolve_mapped_representation(mapped_representation) == representation:
                return mapped_representation

        raise Exception(
            f"Couldn't find any representation matching type representation {representation} in occurrence {occurence}."
        )

    @classmethod
    def run_geometry_update_representation(cls, obj: bpy.types.Object) -> None:
        bpy.ops.bim.update_representation(obj=obj.name, ifc_representation_class="")

    @classmethod
    def run_style_add_style(cls, obj: bpy.types.Material) -> ifcopenshell.entity_instance:
        return bonsai.core.style.add_style(tool.Ifc, tool.Style, obj=obj)

    @classmethod
    def select_connection(cls, connection: ifcopenshell.entity_instance) -> None:
        obj = tool.Ifc.get_object(connection.RelatingElement)
        if obj:
            obj.select_set(True)
        obj = tool.Ifc.get_object(connection.RelatedElement)
        if obj:
            obj.select_set(True)

    @classmethod
    def should_force_faceted_brep(cls) -> bool:
        return bpy.context.scene.BIMGeometryProperties.should_force_faceted_brep

    @classmethod
    def should_force_triangulation(cls) -> bool:
        return bpy.context.scene.BIMGeometryProperties.should_force_triangulation

    @classmethod
    def should_generate_uvs(cls, obj: bpy.types.Object) -> bool:
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
    def should_use_presentation_style_assignment(cls) -> bool:
        return bpy.context.scene.BIMGeometryProperties.should_use_presentation_style_assignment

    @classmethod
    def get_model_representations(cls) -> list[ifcopenshell.entity_instance]:
        return tool.Ifc.get().by_type("IfcShapeRepresentation")

    @classmethod
    def flip_object(cls, obj: bpy.types.Object, flip_local_axes: str) -> None:
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
    def reload_representation(cls, obj_or_objs: Union[bpy.types.Object, Iterable[bpy.types.Object]]) -> None:
        """Reload object/objects active representation.

        Ensures that same representations won't be reloaded multiple times.
        """
        objs = obj_or_objs if isinstance(obj_or_objs, Iterable) else [obj_or_objs]
        ifc_file = tool.Ifc.get()

        # Find all objects that use the same representation
        # as there are possibility that some of them have openings
        # (each representation with opening has a unique Mesh)
        # and therefore reloading Mesh of it's type or occurrence
        # might not be enough.
        elements = set()
        for obj in objs:
            representation = tool.Geometry.get_active_representation(obj)
            if not representation:
                continue
            representation = tool.Geometry.resolve_mapped_representation(representation)
            elements.update(ifcopenshell.util.element.get_elements_by_representation(ifc_file, representation))

        # Filter out unique meshes to avoid
        # reloading the same representation multiple times.
        meshes_to_objects: dict[bpy.types.Mesh, bpy.types.Object] = {}
        for element in elements:
            # Some objects may not exist if they are filtered out, or are unloaded (e.g. openings)
            if (obj := tool.Ifc.get_object(element)) and obj.data:
                meshes_to_objects[obj.data] = obj

        for obj in meshes_to_objects.values():
            cls._reload_representation(obj)

    @classmethod
    def _reload_representation(cls, obj: bpy.types.Object) -> None:
        """Reload representation only for this object.

        Be careful as this method won't reload representation for related objects
        that use the same representation but have different meshes
        (e.g. because of the openings).
        In the most cases just use reload_representation
        as it will handle those complications by itself.
        """
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        bonsai.core.geometry.switch_representation(
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
    def switch_from_representation(cls, obj: bpy.types.Object, representation: ifcopenshell.entity_instance) -> None:
        """Switch object representation to any other besides `representation`.

        If no other representation present, will replace object with an empty.
        Method assumes that `obj` does have a current representation (it could be not `representation`).
        """
        element = tool.Ifc.get_entity(obj)
        assert element

        active_representation = tool.Geometry.get_active_representation(obj)
        active_representation = tool.Geometry.resolve_mapped_representation(active_representation)
        if active_representation != representation:
            return

        new_representation = None
        for r in cls.get_representations_iter(element):
            r = tool.Geometry.resolve_mapped_representation(r)
            if r != representation:
                new_representation = r
                break

        # `representation` is the only representation for object.
        if new_representation is None:
            cls.recreate_object_with_data(obj, None)
            return

        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=new_representation,
            should_reload=False,
            should_sync_changes_first=False,
            is_global=True,
        )

    @classmethod
    def remove_representation_item(cls, representation_item: ifcopenshell.entity_instance) -> None:
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
            consider_inverses.remove(styled_item)
            ifc_file.remove(styled_item)
        if layer and len(layer.Items) == 1:
            consider_inverses.remove(layer)
            ifc_file.remove(layer)
        if colour:
            consider_inverses.remove(colour)
            ifcopenshell.util.element.remove_deep2(ifc_file, colour)
        if texture:
            consider_inverses.remove(texture)
            ifcopenshell.util.element.remove_deep2(ifc_file, texture)

        for shape_aspect in shape_aspects:
            cls.remove_representation_items_from_shape_aspect([representation_item], shape_aspect)

        representation.Items = tuple(set(representation.Items) - {representation_item})
        also_consider = list(consider_inverses)
        ifcopenshell.util.element.remove_deep2(ifc_file, representation_item, also_consider=also_consider)

    @classmethod
    def create_shape_aspect(
        cls,
        product_shape: ifcopenshell.entity_instance,
        base_representation: ifcopenshell.entity_instance,
        items: list[ifcopenshell.entity_instance],
        previous_shape_aspect: Optional[ifcopenshell.entity_instance] = None,
    ) -> ifcopenshell.entity_instance:
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
    def remove_representation_items_from_shape_aspect(
        cls, representation_items: list[ifcopenshell.entity_instance], shape_aspect: ifcopenshell.entity_instance
    ) -> None:
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
    def add_representation_item_to_shape_aspect(
        cls, representation_items: list[ifcopenshell.entity_instance], shape_aspect: ifcopenshell.entity_instance
    ) -> None:
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
    def get_shape_aspect_representation(
        cls,
        shape_aspect: ifcopenshell.entity_instance,
        base_representation: ifcopenshell.entity_instance,
        create_new: bool = False,
    ) -> Union[ifcopenshell.entity_instance, None]:
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
    def add_shape_aspect_representation(
        cls, shape_aspect: ifcopenshell.entity_instance, base_representation: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        shape_aspect_representation = tool.Ifc.get().createIfcShapeRepresentation(
            ContextOfItems=base_representation.ContextOfItems,
            RepresentationIdentifier=base_representation.RepresentationIdentifier,
            RepresentationType=base_representation.RepresentationType,
        )
        shape_aspect.ShapeRepresentations = shape_aspect.ShapeRepresentations + (shape_aspect_representation,)
        return shape_aspect_representation

    @classmethod
    def get_shape_aspect_representation_for_item(
        cls, shape_aspect: ifcopenshell.entity_instance, representation_item: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        ifc_file = tool.Ifc.get()
        for inverse in ifc_file.get_inverse(representation_item):
            if inverse.is_a("IfcShapeRepresentation"):
                if inverse.OfShapeAspect:
                    if inverse.OfShapeAspect[0] == shape_aspect:
                        return inverse

    @classmethod
    def get_shape_aspect_styles(
        cls,
        element: ifcopenshell.entity_instance,
        shape_aspect: ifcopenshell.entity_instance,
        representation_item: ifcopenshell.entity_instance,
    ) -> list[ifcopenshell.entity_instance]:
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
    def delete_opening_object_placement(cls, placement: ifcopenshell.entity_instance) -> None:
        model = tool.Ifc.get()
        ifcopenshell.util.element.remove_deep2(model, placement)

    @classmethod
    def get_blender_offset_type(cls, obj: bpy.types.Object) -> Optional[str]:
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            if (result := obj.BIMObjectProperties.blender_offset_type) == "NONE":
                result = obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
            return result

    @classmethod
    def has_geometry_without_styles(cls, mesh: bpy.types.Mesh) -> bool:
        """Check if mesh has geometry without styles.

        Detects geometry without styles based on how
        MaterialCreator works - will check if either
        mesh has no material slots or has an empty material slot.
        """
        return not mesh.materials or any(m is None for m in mesh.materials)

    @classmethod
    def get_representation_styles(
        cls, representation: ifcopenshell.entity_instance
    ) -> set[ifcopenshell.entity_instance]:
        """Return a set of styles assigned to the representation directly."""

        styles = set()

        # Get all stylable representation items.
        items = []
        for item in representation.Items:
            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            if item.is_a("IfcBooleanResult"):
                operand = item.FirstOperand
                while True:
                    items.append(operand)
                    if operand.is_a("IfcBooleanResult"):
                        operand = operand.FirstOperand
                    else:
                        break
            items.append(item)

        for item in items:
            if not item.StyledByItem:
                continue
            current_styles = list(item.StyledByItem[0].Styles)
            while current_styles:
                style = current_styles.pop()
                if style.is_a("IfcPresentationStyle"):
                    styles.add(style)
                elif style.is_a("IfcPresentationStyleAssignment"):
                    current_styles.extend(style.Styles)

        return styles

    @classmethod
    def get_inherited_material_style(
        cls, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        if element.is_a("IfcTypeProduct"):
            return
        element_type = ifcopenshell.util.element.get_type(element)
        if not element_type:
            return
        materials = ifcopenshell.util.element.get_materials(element_type)
        if not materials:
            return
        material_style = tool.Material.get_style(materials[0])
        return material_style

    @classmethod
    def should_use_immediate_representation(cls, element: ifcopenshell.entity_instance, apply_openings: bool) -> bool:
        use_immediate_repr = apply_openings and bool(getattr(element, "HasOpenings", None))
        use_immediate_repr = use_immediate_repr or cls.has_material_style_override(element)
        return use_immediate_repr

    @classmethod
    def get_openings(cls, element: ifcopenshell.entity_instance) -> Generator[ifcopenshell.entity_instance, None, None]:
        """Get element openings as IfcRelVoidsElements.

        Use `.RelatedOpeningElement` to get the opening element.
        """
        for element in getattr(element, "HasOpenings", ()):
            yield element

        if aggregate := ifcopenshell.util.element.get_aggregate(element):
            yield from cls.get_openings(aggregate)

    @classmethod
    def has_openings(cls, element: ifcopenshell.entity_instance) -> bool:
        return bool(next(cls.get_openings(element), False))

    @classmethod
    def get_elements_by_representation(
        cls, representation: ifcopenshell.entity_instance
    ) -> set[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_elements_by_representation(tool.Ifc.get(), representation)

    @classmethod
    def sync_item_positions(cls) -> None:
        props = bpy.context.scene.BIMGeometryProperties
        if not props.representation_obj:
            return
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        rep_obj = props.representation_obj

        coordinate_offset = cls.get_cartesian_point_offset(rep_obj)
        rep_matrix = np.array(rep_obj.matrix_world.copy())
        if coordinate_offset is not None:
            rep_matrix[:, 3][0:3] -= coordinate_offset
        rep_matrix_i = np.linalg.inv(rep_matrix)

        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        has_changed = False

        for item_obj in props.item_objs:
            if not (obj := item_obj.obj):
                continue
            item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
            if is_swept_area := item.is_a("IfcSweptAreaSolid"):
                if not tool.Ifc.is_moved(obj):
                    continue
                has_changed = True
                old_position = item.Position

                if is_swept_area and np.allclose(np.array(rep_matrix), np.array(obj.matrix_world), atol=1e-4):
                    if old_position:
                        item.Position = None
                        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_position)
                    continue

                position = rep_matrix_i @ np.array(obj.matrix_world)
                position[:, 3][0:3] /= unit_scale
                item.Position = builder.create_axis2_placement_3d_from_matrix(position)
                if old_position:
                    ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), old_position)

        if has_changed:
            cls.reload_representation(rep_obj)
            tool.Root.reload_item_decorator()

    @classmethod
    def import_item_attributes(cls, obj: bpy.types.Object) -> None:
        props = obj.data.BIMMeshProperties
        props.item_attributes.clear()
        item = tool.Ifc.get().by_id(props.ifc_definition_id)
        allowed_attributes = [
            a.name()
            for a in item.wrapped_data.declaration().as_entity().all_attributes()
            if a.type_of_attribute()._is("IfcLengthMeasure")
        ]

        def callback(attr_name: str, *_) -> Union[None, Literal[False]]:
            if attr_name not in allowed_attributes:
                return False
            return None

        bonsai.bim.helper.import_attributes2(item, props.item_attributes, callback=callback)

    @classmethod
    def update_item_attributes(cls, obj: bpy.types.Object) -> None:
        props = obj.data.BIMMeshProperties
        item = tool.Ifc.get().by_id(props.ifc_definition_id)
        for attribute in props.item_attributes:
            setattr(item, attribute.name, attribute.get_value())

    @classmethod
    def import_item(cls, obj: bpy.types.Object) -> None:
        props = bpy.context.scene.BIMGeometryProperties
        rep_obj = props.representation_obj
        tool.Loader.settings.contexts = ifcopenshell.util.representation.get_prioritised_contexts(tool.Ifc.get())
        tool.Loader.settings.context_settings = tool.Loader.create_settings()
        tool.Loader.settings.gross_context_settings = tool.Loader.create_settings(is_gross=True)
        item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        obj.data.clear_geometry()

        geometry = tool.Loader.create_generic_shape(item)
        if (cartesian_point_offset := cls.get_cartesian_point_offset(rep_obj)) is not None:
            verts_array = np.array(geometry.verts)
            offset = np.array([-cartesian_point_offset[0], -cartesian_point_offset[1], -cartesian_point_offset[2]])
            offset_verts = verts_array + np.tile(offset, len(verts_array) // 3)
            verts = offset_verts.tolist()
        else:
            verts = geometry.verts
        tool.Loader.convert_geometry_to_mesh(geometry, obj.data, verts=verts)

        if ios_materials := list(obj.data["ios_materials"]):
            material = tool.Ifc.get_object(tool.Ifc.get().by_id(ios_materials[0]))
            obj.data.materials.append(material)

        obj.matrix_world = rep_obj.matrix_world.copy()

        if is_swept_area := item.is_a("IfcSweptAreaSolid"):
            position = item.Position
            # Positional is optional only for SweptAreaSolid.
            if position or not is_swept_area:
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                position = ifcopenshell.util.placement.get_axis2placement(position)
                position[:, 3][0:3] *= unit_scale
                item_matrix = np.array(rep_obj.matrix_world.copy())
                if cartesian_point_offset is not None:
                    item_matrix[:, 3][0:3] -= cartesian_point_offset
                item_matrix = Matrix(item_matrix @ position)

                transformation = obj.matrix_world.inverted() @ item_matrix
                transformation_i = transformation.inverted()

                obj.matrix_world = item_matrix
                obj.data.transform(transformation_i)
            cls.record_object_position(obj)

    @classmethod
    def disable_item_mode(cls) -> None:
        props = bpy.context.scene.BIMGeometryProperties
        if props.representation_obj:
            props.representation_obj.hide_set(False)
            cls.unlock_object(props.representation_obj)
            tool.Blender.set_active_object(props.representation_obj)
            cls.sync_item_positions()
            props.is_changing_mode = True
            if props.mode != "OBJECT":
                props.mode = "OBJECT"
            props.is_changing_mode = False
        props.representation_obj = None

    @classmethod
    def edit_meshlike_item(cls, obj: bpy.types.Object) -> None:
        item = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        if obj.data.BIMMeshProperties.mesh_checksum == cls.get_mesh_checksum(obj.data):
            return
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        rep_obj = bpy.context.scene.BIMGeometryProperties.representation_obj
        if (coordinate_offset := cls.get_cartesian_point_offset(rep_obj)) is not None:
            verts = [((np.array(v.co) + coordinate_offset) / unit_scale).tolist() for v in obj.data.vertices]
        else:
            verts = [v.co / unit_scale for v in obj.data.vertices]

        faces = [p.vertices[:] for p in obj.data.polygons]
        if item.is_a("IfcAdvancedBrep"):
            new_item = builder.faceted_brep(verts, faces)
        else:
            new_item = builder.mesh(verts, faces)
        for inverse in tool.Ifc.get().get_inverse(item):
            ifcopenshell.util.element.replace_attribute(inverse, item, new_item)
        ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), item)
        obj.data.BIMMeshProperties.ifc_definition_id = new_item.id()
        cls.reload_representation(bpy.context.scene.BIMGeometryProperties.representation_obj)

    @classmethod
    def split_by_loose_parts(cls, obj: bpy.types.Object) -> List[bpy.types.Mesh]:
        # Before .copy() since it also copies the selection.
        selection = tool.Blender.get_objects_selection(bpy.context)

        dup_obj = obj.copy()
        dup_obj.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(dup_obj)

        tool.Blender.select_and_activate_single_object(bpy.context, dup_obj)

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")

        results = []
        for obj in bpy.context.selected_objects:
            results.append(obj.data)
            bpy.data.objects.remove(obj)

        # Preserve original selection.
        tool.Blender.set_objects_selection(*selection)
        return results

    @classmethod
    def reload_representation_item_ids(cls, representation: ifcopenshell.entity_instance, data: bpy.types.Mesh) -> None:
        data["ios_item_ids"] = [i["item"].id() for i in ifcopenshell.util.representation.resolve_items(representation)]

    @classmethod
    def export_mesh_to_tessellation(cls, obj: bpy.types.Object, ifc_context) -> ifcopenshell.entity_instance:
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(tool.Ifc.get())
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        items = []
        meshes = cls.split_by_loose_parts(obj)
        for mesh in meshes:
            verts = [v.co / unit_scale for v in mesh.vertices]
            faces = [p.vertices[:] for p in mesh.polygons]
            item = builder.mesh(verts, faces)
            items.append(item)
            material_index = mesh.polygons[0].material_index
            if materials := list(mesh.materials):
                material = materials[material_index]
                if not (style := tool.Ifc.get_entity(material)):
                    style = ifcopenshell.api.run("style.add_style", tool.Ifc.get(), name=material.name)
                    if material.use_nodes:
                        ifc_class = "IfcSurfaceStyleRendering"
                        attributes = tool.Style.get_surface_rendering_attributes(material)
                    else:
                        ifc_class = "IfcSurfaceStyleShading"
                        attributes = tool.Style.get_surface_shading_attributes(material)
                    ifcopenshell.api.style.add_surface_style(
                        tool.Ifc.get(), style=style, ifc_class=ifc_class, attributes=attributes
                    )
                    tool.Ifc.link(style, material)
                    material.use_fake_user = True
                ifcopenshell.api.style.assign_item_style(tool.Ifc.get(), item=item, style=style)
            bpy.data.meshes.remove(mesh)
        return builder.get_representation(ifc_context, items)
