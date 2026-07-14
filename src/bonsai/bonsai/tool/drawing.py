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

from __future__ import annotations

import json
import logging
import math
import os
import platform
import re
import shutil
import subprocess
from collections.abc import Iterable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, Optional, Union

import bmesh
import bpy
import ifcopenshell.api
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.drawing
import ifcopenshell.api.geometry
import ifcopenshell.api.group
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import lark
import mathutils
import numpy as np
import shapely
from ifcopenshell.util.shape_builder import ShapeBuilder
from lxml import etree
from mathutils import Matrix, Vector
from shapely.ops import unary_union

import bonsai.bim.helper
import bonsai.bim.import_ifc
import bonsai.core.geometry
import bonsai.core.root
import bonsai.core.tool
import bonsai.core.type
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.drawing.prop import (
        BIMAnnotationProperties,
        BIMAssignedProductProperties,
        BIMCameraProperties,
        BIMTextProperties,
        DocProperties,
        Sheet,
    )
    from bonsai.bim.module.drawing.prop import Drawing as DrawingProperties


class Drawing(bonsai.core.tool.Drawing):
    ANNOTATION_DATA_TYPE = Literal["empty", "curve", "mesh"]
    PERSPECTIVE_CAMERA_SHIFT_PROPERTIES = ("PerspectiveShiftX", "PerspectiveShiftY")
    DOCUMENT_TYPE = Literal["SCHEDULE", "REFERENCE"]
    LocationHintLiteral = Literal["PERSPECTIVE", "ORTHOGRAPHIC", "NORTH", "SOUTH", "EAST", "WEST"]
    LOCATION_HINT_LITERALS = ("PERSPECTIVE", "ORTHOGRAPHIC", "NORTH", "SOUTH", "EAST", "WEST")
    LocationHintType = Union[LocationHintLiteral, str]

    # ObjectType: annotation_name, description, icon, data_type
    # fmt: off

    class AnnotationObjectType(NamedTuple):
        annotation_name: str
        description: str
        icon: str
        data_type: Drawing.ANNOTATION_DATA_TYPE

    ANNOTATION_TYPES_DATA: dict[str, AnnotationObjectType] = {
        "DIMENSION":     AnnotationObjectType("Dimension",        "Add dimensions annotation.\nMeasurement values can be hidden through ShowDescriptionOnly property\nof BBIM_Dimension property set", "FIXED_SIZE", "curve"),
        "ANGLE":         AnnotationObjectType("Angle",            "", "DRIVER_ROTATIONAL_DIFFERENCE", "curve"),
        "RADIUS":        AnnotationObjectType("Radius",           "", "FORWARD", "curve"),
        "DIAMETER":      AnnotationObjectType("Diameter",         "Add diameter annotation.\nMeasurement values can be hidden through ShowDescriptionOnly property\nof BBIM_Dimension property set", "ARROW_LEFTRIGHT", "curve"),
        "TEXT":          AnnotationObjectType("Text",             "", "SMALL_CAPS", "empty"),
        "TEXT_LEADER":   AnnotationObjectType("Leader",           "", "TRACKING_BACKWARDS", "curve"),
        "STAIR_ARROW":   AnnotationObjectType("Stair Arrow",      "Add stair arrow annotation.\nIf you have IfcStairFlight object selected, it will be used as a reference for the annotation", "SCREEN_BACK", "curve"),
        "PLAN_LEVEL":    AnnotationObjectType("Level (Plan)",     "", "SORTBYEXT", "curve"),
        "SECTION_LEVEL": AnnotationObjectType("Level (Section)",  "", "TRIA_DOWN", "curve"),
        "BREAKLINE":     AnnotationObjectType("Breakline",        "", "FCURVE", "mesh"),
        "SYMBOL":        AnnotationObjectType("Symbol",           "", "KEYFRAME", "empty"),
        "MULTI_SYMBOL":  AnnotationObjectType("Multi-Symbol",     "", "OUTLINER_DATA_POINTCLOUD", "mesh"),
        "LINEWORK":      AnnotationObjectType("Line",             "", "SNAP_MIDPOINT", "mesh"),
        "BATTING":       AnnotationObjectType("Batting",          "Add batting annotation.\nThickness could be changed through Thickness property of BBIM_Batting property set", "FORCE_FORCE", "mesh"),
        "REVISION_CLOUD":AnnotationObjectType("Revision Cloud",   "Add revision cloud", "VOLUME_DATA", "mesh"),
        "FILL_AREA":     AnnotationObjectType("Fill Area",        "", "NODE_TEXTURE", "mesh"),
        "FALL":          AnnotationObjectType("Fall",             "", "SORT_ASC", "curve"),
        "IMAGE":         AnnotationObjectType("Image",            "Add reference image attached to the drawing", "TEXTURE", "mesh"),
    }
    # fmt: on

    DEFAULT_SYMBOLS = [
        "rectangle-tag",
        "triangle-tag",
        "hexagon-tag",
        "capsule-tag",
        "circle-tag",
        "door-tag",
        "window-tag",
        "space-tag",
        "elevation-arrow",
        "elevation-tag",
        "section-arrow",
        "section-tag",
        "dot",
        "setout-tag",
        "setout-point",
        "control-point",
        "traverse-point",
        "spot-elevation",
    ]

    @classmethod
    def get_document_props(cls) -> DocProperties:
        assert (scene := bpy.context.scene)
        return scene.DocProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_annotation_props(cls) -> BIMAnnotationProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMAnnotationProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_text_props(cls, obj: bpy.types.Object) -> BIMTextProperties:
        return obj.BIMTextProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_camera_props(cls, camera: Union[bpy.types.Object, bpy.types.Camera]) -> BIMCameraProperties:
        """
        :param camera: Camera object or camera.
        """
        if isinstance(camera, bpy.types.Camera):
            data = camera
        else:
            assert isinstance(data := camera.data, bpy.types.Camera)
        return data.BIMCameraProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_object_assigned_product_props(cls, obj: bpy.types.Object) -> BIMAssignedProductProperties:
        return obj.BIMAssignedProductProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def canonicalise_class_name(cls, name: str) -> str:
        return re.sub("[^0-9a-zA-Z]+", "", name)

    @classmethod
    def copy_representation(cls, source: ifcopenshell.entity_instance, dest: ifcopenshell.entity_instance) -> None:
        if source.Representation:
            dest.Representation = ifcopenshell.util.element.copy_deep(
                tool.Ifc.get(), source.Representation, exclude=["IfcGeometricRepresentationContext"]
            )

    @classmethod
    def get_annotation_data_type(cls, object_type: str) -> ANNOTATION_DATA_TYPE:
        return cls.ANNOTATION_TYPES_DATA[object_type].data_type

    @classmethod
    def create_annotation_object(cls, drawing: ifcopenshell.entity_instance, object_type: str) -> bpy.types.Object:
        import bonsai.bim.module.drawing.annotation as annotation

        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        scale = 1 / float(Fraction(pset["Scale"]))
        data_type = cls.get_annotation_data_type(object_type)
        obj = annotation.Annotator.get_annotation_obj(drawing, object_type, data_type)
        if object_type == "FILL_AREA":
            obj = annotation.Annotator.add_plane_to_annotation(obj)
        elif object_type == "REVISION_CLOUD":
            obj = annotation.Annotator.add_plane_to_annotation(obj, remove_face=True)
        elif object_type == "MULTI_SYMBOL":
            obj = annotation.Annotator.add_vertex_to_annotation(obj)
        elif object_type == "TEXT_LEADER":
            co1, _, co2, _ = annotation.Annotator.get_placeholder_coords()
            obj = annotation.Annotator.add_line_to_annotation(obj, co2, co1)
        elif object_type == "PLAN_LEVEL":
            co1, co2, _, _ = annotation.Annotator.get_placeholder_coords()
            vec = co2 - co1
            if vec.length == 0:
                vec = Vector((1, 0, 0))  # Fallback to a unit vector
            else:
                vec = vec.normalized()
            scaled_length = 0.023 * scale  # 0.023 could probably be a preference
            co_end = co1 + vec * scaled_length
            obj = annotation.Annotator.add_line_to_annotation(obj, co_end, co1)
            obj.matrix_world = obj.matrix_world @ Matrix.Rotation(math.radians(-90), 4, "Z")
        elif object_type != "TEXT":
            obj = annotation.Annotator.add_line_to_annotation(obj)

        return obj

    @classmethod
    def get_annotation_drawing(cls, element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance | None:
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                for e in rel.RelatedObjects:
                    if e.ObjectType == "DRAWING":
                        return e

    @classmethod
    def exclude_annotation_from_drawing(
        cls, element: ifcopenshell.entity_instance, drawing: ifcopenshell.entity_instance
    ) -> None:
        ifc_file = tool.Ifc.get()
        pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=drawing, name="EPset_Drawing")
        exclude = ifcopenshell.util.element.get_property_definition(pset, prop="Exclude") or ""
        if exclude:
            exclude += "+"
        exclude += element.GlobalId
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Exclude": exclude})

    @classmethod
    def ensure_annotation_in_drawing_plane(
        cls, obj: bpy.types.Object, camera: Optional[bpy.types.Object] = None
    ) -> None:
        """Make sure annotation object is going to be visible in the camera view"""

        def get_camera_from_annotation_object(obj):
            entity = tool.Ifc.get_entity(obj)
            if not entity:
                return
            return tool.Ifc.get_object(cls.get_annotation_drawing(entity))

        if not camera:
            camera = get_camera_from_annotation_object(obj) or bpy.context.scene.camera

        current_pos = camera.matrix_world.inverted() @ obj.location
        current_pos.z = -camera.data.clip_start - 0.05
        current_pos = camera.matrix_world @ current_pos
        obj.location = current_pos

    ANNOTATION_TYPES_SUPPORT_SETUP = ("STAIR_ARROW", "TEXT", "REVISION_CLOUD", "FILL_AREA")

    @classmethod
    def setup_annotation_object(
        cls,
        obj: bpy.types.Object,
        object_type: str,
        related_object: Optional[bpy.types.Object] = None,
        rotation_mode: str = "NONE",
    ) -> None:
        """Finish object's adjustments after both object and entity are created"""

        if not related_object:
            related_object = bpy.context.active_object

        if not related_object or not (related_entity := tool.Ifc.get_entity(related_object)):
            return

        ifc_file = tool.Ifc.get()
        obj_entity = tool.Ifc.get_entity(obj)
        assert obj_entity
        assign_product = False

        if object_type == "STAIR_ARROW":
            if related_entity.is_a("IfcStairFlight"):
                stair, arrow = related_object, obj
                assert isinstance(stair.data, bpy.types.Mesh)
                assert isinstance(arrow.data, bpy.types.Mesh)

                # place the arrow
                # NOTE: may not work correctly in EDIT mode
                bbox = tool.Blender.get_object_bounding_box(stair)
                arrow.location = stair.matrix_world @ Vector(
                    (bbox["min_x"], (bbox["max_y"] - bbox["min_y"]) / 2, bbox["max_z"])
                )
                last_step_x = max(v.co.x for v in stair.data.vertices if tool.Cad.is_x(v.co.z - bbox["max_z"], 0))
                arrow.data.splines[0].points[0].co = Vector((0, 0, 0, 1))
                arrow.data.splines[0].points[1].co = Vector((last_step_x, 0, 0, 1))

                cls.ensure_annotation_in_drawing_plane(obj)
                assign_product = True

        elif object_type == "TEXT":
            bbox = tool.Blender.get_object_bounding_box(related_object)

            obj.location = related_object.matrix_world @ bbox["center"]
            cls.ensure_annotation_in_drawing_plane(obj)
            assign_product = True

        elif object_type == "REVISION_CLOUD":
            revised_object, cloud = related_object, obj
            assert isinstance(revised_object.data, bpy.types.Mesh)
            assert isinstance(obj.data, bpy.types.Mesh)

            verts = [np.array(revised_object.matrix_world @ v.co) for v in revised_object.data.vertices]
            verts = [(np.around(v[[0, 1]], decimals=3)).tolist() for v in verts]
            edges = [e.vertices for e in revised_object.data.edges]

            # shapely magic
            boundary_lines = [shapely.LineString([verts[v] for v in e]) for e in edges]
            unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
            all_polygons = shapely.polygonize(unioned_boundaries.geoms).geoms
            outer_shell = unary_union(all_polygons)

            bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
            new_verts = list(outer_shell.exterior.coords)
            bm_verts = [bm.verts.new(v + (0,)) for v in new_verts]
            bm_edges = [bm.edges.new([bm_verts[i], bm_verts[i + 1]]) for i in range(len(new_verts) - 1)]
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

            tool.Blender.apply_bmesh(obj.data, bm, obj)
            cloud.location = Vector((0, 0, 0))
            cls.ensure_annotation_in_drawing_plane(cloud)
            assign_product = True

        if assign_product and not cls.get_assigned_product(obj_entity):
            ifcopenshell.api.drawing.assign_product(
                ifc_file, relating_product=related_entity, related_object=obj_entity
            )

        if rotation_mode != "NONE" and related_object:
            cls.apply_annotation_rotation(obj, related_object, rotation_mode)

    @classmethod
    def apply_annotation_rotation(
        cls, tag_obj: bpy.types.Object, related_object: bpy.types.Object, rotation_mode: str
    ) -> None:
        """Apply rotation to annotation based on the selected rotation mode"""
        camera = bpy.context.scene.camera
        camera_right = camera.matrix_world.to_3x3() @ mathutils.Vector((1, 0, 0))

        if rotation_mode == "CAMERA_Horizontal":
            location = tag_obj.location.copy()
            camera_matrix = camera.matrix_world.copy()
            camera_matrix.translation = location
            tag_obj.matrix_world = camera_matrix

        elif rotation_mode == "CAMERA_Vertical":
            location = tag_obj.location.copy()
            camera_matrix = camera.matrix_world.copy()
            camera_matrix.translation = location
            rotation_90z = mathutils.Matrix.Rotation(math.pi / 2, 4, "Z")
            camera_matrix = camera_matrix @ rotation_90z
            tag_obj.matrix_world = camera_matrix

        elif rotation_mode == "LOCAL_X":
            local_x = related_object.matrix_world.to_3x3() @ mathutils.Vector((1, 0, 0))
            local_x = local_x.normalized()
            if local_x.dot(camera_right) < 0:
                local_x = -local_x

            tag_obj.rotation_euler = local_x.to_track_quat("X", "Z").to_euler()

        elif rotation_mode == "LOCAL_Y":
            local_y = related_object.matrix_world.to_3x3() @ mathutils.Vector((0, 1, 0))
            local_y = local_y.normalized()
            if local_y.dot(camera_right) < 0:
                local_y = -local_y

            tag_obj.rotation_euler = local_y.to_track_quat("X", "Z").to_euler()

        elif rotation_mode == "LOCAL_Z":
            local_z = related_object.matrix_world.to_3x3() @ mathutils.Vector((0, 0, 1))
            local_z = local_z.normalized()
            if local_z.dot(camera_right) < 0:
                local_z = -local_z

            tag_obj.rotation_euler = local_z.to_track_quat("X", "Z").to_euler()

    @classmethod
    def is_annotation_object_type(
        cls, element: ifcopenshell.entity_instance, object_types: Union[str, Sequence[str]]
    ) -> bool:
        if isinstance(object_types, str):
            object_types = [object_types]

        element_type = element.is_a()

        if element_type == "IfcAnnotation" and ifcopenshell.util.element.get_predefined_type(element) in object_types:
            return True

        if element_type == "IfcTypeProduct" and (
            applicable_object_type := cls.get_annotation_type_object_type(element)
        ):
            if applicable_object_type in object_types:
                return True

        return False

    @classmethod
    def get_annotation_type_object_type(cls, element_type: ifcopenshell.entity_instance) -> Union[str, None]:
        applicable_occurrence: Union[str, None]
        applicable_occurrence = element_type.ApplicableOccurrence
        if not applicable_occurrence or not applicable_occurrence.startswith("IfcAnnotation/"):
            return
        return applicable_occurrence.split("/", 1)[1]

    @classmethod
    def get_annotation_representation(
        cls, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        rep = ifcopenshell.util.representation.get_representation(
            element, "Plan", "Annotation"
        ) or ifcopenshell.util.representation.get_representation(element, "Model", "Annotation")
        if not rep:
            return None

        rep = tool.Geometry.resolve_mapped_representation(rep)
        return rep

    @classmethod
    def create_camera(
        cls,
        name: str,
        matrix: Matrix,
        location_hint: Union[LocationHintLiteral, int],
        target_view: ifcopenshell.util.representation.TARGET_VIEW,
    ) -> bpy.types.Object:
        camera = bpy.data.objects.new(name, (camera_data := bpy.data.cameras.new(name)))
        props = cls.get_camera_props(camera_data)
        camera_data.show_limits = True
        if location_hint == "PERSPECTIVE":
            props.camera_type = "PERSP"
        else:
            props.camera_type = "ORTHO"
        camera_data.ortho_scale = 50  # The default of 6m is too small
        camera_data.clip_start = 0.002  # 2mm is close to zero but allows any GPU-drawn lines to be visible.
        if target_view == "MODEL_VIEW":
            assert (space := tool.Blender.get_view3d_space())
            camera_data.clip_end = max(space.clip_end, 10)
        else:
            camera_data.clip_end = 10  # A slightly more reasonable default
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            props.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            props.diagram_scale = "1:100|1/100"
        camera.matrix_world = matrix
        return camera

    @classmethod
    def get_perspective_camera_shifts(cls, drawing: ifcopenshell.entity_instance) -> dict[str, float]:
        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing") or {}
        shift_x_prop, shift_y_prop = cls.PERSPECTIVE_CAMERA_SHIFT_PROPERTIES
        return {
            "shift_x": float(pset.get(shift_x_prop, 0.0) or 0.0),
            "shift_y": float(pset.get(shift_y_prop, 0.0) or 0.0),
        }

    @classmethod
    def sync_perspective_camera_shifts(cls, drawing: ifcopenshell.entity_instance, camera: bpy.types.Camera) -> None:
        if camera.type != "PERSP":
            return

        shift_x_prop, shift_y_prop = cls.PERSPECTIVE_CAMERA_SHIFT_PROPERTIES
        current_shifts = cls.get_perspective_camera_shifts(drawing)
        new_shifts = {"shift_x": float(camera.shift_x or 0.0), "shift_y": float(camera.shift_y or 0.0)}
        if tool.Cad.is_x(current_shifts["shift_x"], new_shifts["shift_x"]) and tool.Cad.is_x(
            current_shifts["shift_y"], new_shifts["shift_y"]
        ):
            return

        ifc_file = tool.Ifc.get()
        pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=drawing, name="EPset_Drawing")
        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={
                shift_x_prop: new_shifts["shift_x"],
                shift_y_prop: new_shifts["shift_y"],
            },
        )

    @classmethod
    def create_svg_schedule(cls, schedule: ifcopenshell.entity_instance) -> None:
        import bonsai.bim.module.drawing.scheduler as scheduler

        schedule_creator = scheduler.Scheduler()
        schedule_creator.schedule(
            cls.get_document_uri(schedule), cls.get_path_with_ext(cls.get_document_uri(schedule), "svg")
        )

    @classmethod
    def create_svg_sheet(cls, document: ifcopenshell.entity_instance, titleblock: str) -> str:
        import bonsai.bim.module.drawing.sheeter as sheeter

        sheet_builder = sheeter.SheetBuilder()
        uri = cls.get_document_uri(document, "LAYOUT")
        assert uri
        sheet_builder.create(uri, titleblock)
        return uri

    @classmethod
    def add_drawings(cls, sheet: ifcopenshell.entity_instance) -> None:
        import bonsai.bim.module.drawing.sheeter as sheeter

        sheet_builder = sheeter.SheetBuilder()
        drawing_references = {}
        drawing_names = []
        for reference in cls.get_document_references(sheet):
            reference_description = cls.get_reference_description(reference)
            if reference_description == "DRAWING":
                drawing_references[Path(reference.Location).stem] = reference
                drawing_names.append(Path(reference.Location).stem)
        for drawing_annotation in [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]:
            if drawing_annotation.Name in drawing_names:
                sheet_builder.add_drawing(drawing_references[drawing_annotation.Name], drawing_annotation, sheet)

    @classmethod
    def delete_collection(cls, collection: bpy.types.Collection) -> None:
        bpy.data.collections.remove(collection, do_unlink=True)

    @classmethod
    def delete_drawing_elements(cls, elements: Iterable[ifcopenshell.entity_instance]) -> None:
        for element in elements:
            obj = tool.Ifc.get_object(element)
            ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=element)
            if obj:
                obj_data = obj.data
                bpy.data.objects.remove(obj)
                if obj_data and obj_data.users == 0:  # in case we have drawing element types
                    tool.Blender.remove_data_block(obj_data)

    @classmethod
    def delete_object(cls, obj: bpy.types.Object) -> None:
        bpy.data.objects.remove(obj)

    @classmethod
    def disable_editing_drawings(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_drawings = False

    @classmethod
    def disable_editing_schedules(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_schedules = False

    @classmethod
    def disable_editing_references(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_references = False

    @classmethod
    def disable_editing_sheets(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_sheets = False

    @classmethod
    def disable_editing_text(cls, obj: bpy.types.Object) -> None:
        props = tool.Drawing.get_text_props(obj)
        obj.property_unset(tool.Blender.get_props_attribute_name(props))

    @classmethod
    def disable_editing_assigned_product(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_assigned_product_props(obj)
        props.is_editing_product = False

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        from bonsai.bim.module.geometry.data import ViewportData

        tool.Blender.select_and_activate_single_object(bpy.context, obj)
        if not obj.data:
            return
        ViewportData.load()  # Reload valid modes
        bpy.ops.bim.override_mode_set_edit()  # Enter item mode
        ViewportData.load()  # Reload valid modes
        bpy.ops.bim.override_mode_set_edit()  # Enter edit mode

    @classmethod
    def enable_editing_drawings(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_drawings = True

    @classmethod
    def enable_editing_schedules(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_schedules = True

    @classmethod
    def enable_editing_references(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_references = True

    @classmethod
    def enable_editing_sheets(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.is_editing_sheets = True

    @classmethod
    def enable_editing_text(cls, obj: bpy.types.Object) -> None:
        props = cls.get_text_props(obj)
        props.is_editing = True

    @classmethod
    def enable_editing_assigned_product(cls, obj: bpy.types.Object) -> None:
        props = cls.get_object_assigned_product_props(obj)
        props.is_editing_product = True

    @classmethod
    def ensure_unique_drawing_name(cls, name: str) -> str:
        names = [e.Name for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        while name in names:
            name += "-X"
        return name

    @classmethod
    def ensure_unique_identification(cls, identification: str) -> str:
        ids = [
            cls.get_sheet_identification(d)
            for d in tool.Ifc.get().by_type("IfcDocumentInformation")
            if d.Scope == "SHEET"
        ]
        while identification in ids:
            identification += "-X"
        return identification

    @classmethod
    def export_text_literal_attributes(cls, obj: bpy.types.Object) -> list[dict[str, Any]]:
        literals: list[dict[str, Any]] = []
        props = tool.Drawing.get_text_props(obj)
        for literal_props in props.literals:
            literal_data = bonsai.bim.helper.export_attributes(literal_props.attributes)
            alignment = literal_props.align_vertical + "-" + literal_props.align_horizontal
            if alignment == "middle-middle":
                alignment = "center"
            literal_data["BoxAlignment"] = alignment
            literals.append(literal_data)
        return literals

    @classmethod
    def export_font_size(cls, obj: bpy.types.Object) -> str:
        return float(cls.get_text_props(obj).font_size)

    @classmethod
    def export_alignment(cls, obj: bpy.types.Object) -> str:
        props = cls.get_text_props(obj)
        if (alignment := props.align_vertical + "-" + props.align_horizontal) == "middle-middle":
            return "center"
        return alignment

    @classmethod
    def export_wrap_length(cls, obj: bpy.types.Object) -> str:
        return cls.get_text_props(obj).newline_at

    @classmethod
    def export_symbol(cls, obj: bpy.types.Object) -> str:
        return cls.get_text_props(obj).get_symbol()

    @classmethod
    def create_annotation_context(
        cls, target_view: str, object_type: Optional[str] = None
    ) -> ifcopenshell.entity_instance:
        # checking PLAN target view and annotation type that doesn't require 3d
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW") and object_type not in (
            "FALL",
            "SECTION_LEVEL",
            "PLAN_LEVEL",
        ):
            parent = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan")
            if not parent:
                parent = ifcopenshell.api.context.add_context(tool.Ifc.get(), context_type="Plan")
        else:
            parent = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model")
            if not parent:
                parent = ifcopenshell.api.context.add_context(tool.Ifc.get(), context_type="Model")

        return ifcopenshell.api.context.add_context(
            tool.Ifc.get(),
            context_type=parent.ContextType,
            context_identifier="Annotation",
            target_view=target_view,
            parent=parent,
        )

    @classmethod
    def get_annotation_context(
        cls, target_view: str, object_type: Optional[str] = None
    ) -> Union[ifcopenshell.entity_instance, None]:
        # checking PLAN target view and annotation type that doesn't require 3d
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW") and object_type not in (
            "FALL",
            "SECTION_LEVEL",
            "PLAN_LEVEL",
        ):
            return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Annotation", target_view)
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Annotation", target_view)

    @classmethod
    def get_body_context(cls) -> ifcopenshell.entity_instance:
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_document_uri(
        cls, document: ifcopenshell.entity_instance, description: Optional[str] = None
    ) -> Union[str, None]:
        if getattr(document, "Location", None):
            if os.path.isabs(document.Location):
                return document.Location
            ifc_path = tool.Ifc.get_path()
            if os.path.isfile(ifc_path):
                ifc_path = os.path.dirname(ifc_path)
            return os.path.abspath(os.path.join(ifc_path, document.Location))
        if document.is_a("IfcDocumentInformation"):
            if tool.Ifc.get_schema() == "IFC2X3":
                references = document.DocumentReferences
            else:
                references = document.HasDocumentReferences
            for reference in references:
                if description and cls.get_reference_description(reference) != description:
                    continue
                location = cls.get_document_uri(reference)
                if location:
                    return location

    @classmethod
    def get_path_filename(cls, path: str) -> str:
        return os.path.splitext(os.path.basename(path))[0]

    @classmethod
    def get_path_with_ext(cls, path: str, ext: str) -> str:
        return os.path.splitext(path)[0] + f".{ext}"

    @classmethod
    def get_unit_system(cls) -> Literal["NONE", "METRIC", "IMPERIAL"]:
        return bpy.context.scene.unit_settings.system

    @classmethod
    def get_drawing_collection(cls, drawing: ifcopenshell.entity_instance) -> Union[bpy.types.Collection, None]:
        obj = tool.Ifc.get_object(drawing)
        if obj:
            return tool.Blender.get_object_bim_props(obj).collection

    @classmethod
    def get_drawing_group(cls, drawing: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        for rel in drawing.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                return rel.RelatingGroup

    @classmethod
    def get_drawing_document(cls, drawing: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        for rel in drawing.HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument"):
                return rel.RelatingDocument

    @classmethod
    def get_drawing_references(cls, drawing: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        results: set[ifcopenshell.entity_instance] = set()
        for inverse in tool.Ifc.get().get_inverse(drawing):
            if inverse.is_a("IfcRelAssignsToProduct") and inverse.RelatingProduct == drawing:
                results.update(inverse.RelatedObjects)
        return results

    @classmethod
    def get_drawing_target_view(cls, drawing: ifcopenshell.entity_instance) -> str:
        return ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {}).get("TargetView", "MODEL_VIEW")

    @classmethod
    def ensure_drawings_parent_document(cls) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        for document in ifc_file.by_type("IfcDocumentInformation"):
            if document.Name == "DRAWINGS" and document.Scope == "DRAWINGS":
                return document
        document = ifcopenshell.api.document.add_information(ifc_file)
        if ifc_file.schema == "IFC2X3":
            attributes = {"DocumentId": "DRAWINGS", "Name": "DRAWINGS", "Scope": "DRAWINGS"}
        else:
            attributes = {"Identification": "DRAWINGS", "Name": "DRAWINGS", "Scope": "DRAWINGS"}
        ifcopenshell.api.document.edit_information(ifc_file, information=document, attributes=attributes)
        return document

    @classmethod
    def ensure_drawings_parent_group(cls) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        for group in ifc_file.by_type("IfcGroup"):
            if group.Name == "DRAWINGS" and group.ObjectType == "DRAWINGS":
                return group
        group = ifcopenshell.api.group.add_group(ifc_file)
        ifcopenshell.api.group.edit_group(
            ifc_file, group=group, attributes={"Name": "DRAWINGS", "ObjectType": "DRAWINGS"}
        )
        return group

    @classmethod
    def get_group_elements(cls, group: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        for rel in group.IsGroupedBy or []:
            return rel.RelatedObjects

    @classmethod
    def get_ifc_representation_class(cls, object_type: str) -> str:
        if object_type == "TEXT":
            return "IfcTextLiteral"
        elif object_type == "TEXT_LEADER":
            return "IfcGeometricCurveSet/IfcTextLiteral"
        return ""

    @classmethod
    def get_name(cls, element: ifcopenshell.entity_instance) -> Union[str, None]:
        return element.Name

    @classmethod
    def update_camera_matrix(
        cls,
        matrix: Matrix,
        *,
        camera_dir: Vector,
        up: Vector,
    ) -> None:
        # Camera dir is actually Z-.
        camera_dir = -camera_dir
        right = up.cross(camera_dir)
        assert isinstance(right, Vector)
        matrix.col[0][:3] = right
        matrix.col[1][:3] = up
        matrix.col[2][:3] = camera_dir

    @classmethod
    def generate_drawing_matrix(
        cls,
        target_view: ifcopenshell.util.representation.TARGET_VIEW,
        location_hint: Union[LocationHintLiteral, int],
    ) -> Matrix:
        assert bpy.context.scene
        m = Matrix()
        x, y, z = (0, 0, 0) if location_hint == 0 else bpy.context.scene.cursor.matrix.translation
        X, Y, Z = m.to_3x3()
        if isinstance(location_hint, int):
            if target_view == "REFLECTED_PLAN_VIEW":
                # Flip Z axis.
                m.col[2] *= -1
            if location_hint:
                storey = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint))
                assert isinstance(storey, bpy.types.Object)
                z = storey.matrix_world.translation.z
                if target_view == "PLAN_VIEW":
                    # Keep default camera direction - Z-.
                    m.translation = (x, y, z + 1.6)
                    return m
                elif target_view == "REFLECTED_PLAN_VIEW":
                    m.translation = (x, y, z + 1.6)
                else:
                    assert False, target_view
            return m
        elif target_view == "ELEVATION_VIEW":
            m.translation = (x, y, z)
            if location_hint == "NORTH":
                cls.update_camera_matrix(m, camera_dir=-Y, up=Z)
            elif location_hint == "SOUTH":
                cls.update_camera_matrix(m, camera_dir=Y, up=Z)
            elif location_hint == "EAST":
                cls.update_camera_matrix(m, camera_dir=-X, up=Z)
            elif location_hint == "WEST":
                cls.update_camera_matrix(m, camera_dir=X, up=Z)
            return m
        elif target_view == "SECTION_VIEW":
            m.translation = (x, y, z)
            X, Y, Z = m.to_3x3()
            if location_hint == "NORTH":
                cls.update_camera_matrix(m, camera_dir=Y, up=Z)
            elif location_hint == "SOUTH":
                cls.update_camera_matrix(m, camera_dir=-Y, up=Z)
            elif location_hint == "EAST":
                cls.update_camera_matrix(m, camera_dir=X, up=Z)
            elif location_hint == "WEST":
                cls.update_camera_matrix(m, camera_dir=-X, up=Z)
            return m
        elif target_view == "MODEL_VIEW":
            assert (space := tool.Blender.get_view3d_space())
            assert (r3d := space.region_3d)
            return r3d.view_matrix.inverted()
        return m

    @classmethod
    def generate_sheet_identification(cls) -> str:
        number = len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"])
        number += 1
        return "A" + str(number).zfill(2)

    @classmethod
    def get_text_literal(
        cls, obj: bpy.types.Object, return_list: bool = False
    ) -> Union[ifcopenshell.entity_instance, None, list[ifcopenshell.entity_instance]]:
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        rep = cls.get_annotation_representation(element)
        if not rep:
            return [] if return_list else None

        items = [i for i in rep.Items if i.is_a("IfcTextLiteral")]
        if not items:
            return [] if return_list else None
        if return_list:
            return items
        return items[0]

    @classmethod
    def is_editing_sheets(cls) -> bool:
        props = tool.Drawing.get_document_props()
        return props.is_editing_sheets

    @classmethod
    def edit_text_literals(cls, obj: bpy.types.Object, literal_attributes: dict) -> None:
        if not literal_attributes:
            return
        assert (element := tool.Ifc.get_entity(obj))
        assert (rep := cls.get_annotation_representation(element))
        to_remove = [i for i in rep.Items if i.is_a("IfcTextLiteral")]
        new_literals = [cls.add_literal(**a) for a in literal_attributes]
        rep.Items = [i for i in rep.Items if not i.is_a("IfcTextLiteral")] + new_literals
        for literal in to_remove:
            ifcopenshell.util.element.remove_deep2(tool.Ifc.get(), literal)

    @classmethod
    def add_literal(cls, **attributes: str) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        builder = ShapeBuilder(ifc_file)
        origin = builder.create_axis2_placement_3d()
        ifc_literal = ifc_file.create_entity(
            "IfcTextLiteralWithExtent",
            attributes.get("Literal", "Literal"),
            origin,
            attributes.get("Path", "RIGHT"),
            ifc_file.create_entity("IfcPlanarExtent", 1000, 1000),
            attributes.get("BoxAlignment", "bottom-left"),
        )
        return ifc_literal

    @classmethod
    def get_assigned_product(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                product = rel.RelatingProduct
                if product.is_a("IfcGrid") and rel.Name:
                    for attribute in ("UAxes", "VAxes", "WAxes"):
                        for axis in getattr(product, attribute) or []:
                            if axis.AxisTag == rel.Name:
                                return axis
                return product

    @classmethod
    def get_assigned_product_workaround(
        cls, element: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        """Get all products assigned to the element.

        A workaround allowing to unassign accumulated products until we properly resolve #4014.
        In theory annotations should have more than one product assigned,
        but there's still undefined bug causing that in some cases.
        """

        assigned_products: list[ifcopenshell.entity_instance] = []
        for rel in element.HasAssignments:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            assigned_products.append(rel.RelatingProduct)

        if len(assigned_products) > 1:
            print(
                f"WARNING. Detected multiple assigned products ({len(assigned_products)}) for annotation '{element}'."
                "\nIf you can reproduce this, please report it to Bonsai developers "
                "at https://github.com/IfcOpenShell/IfcOpenShell/issues/4014."
                "\nAssigned products:\n" + "\n".join([str(p) for p in assigned_products])
            )

        return assigned_products

    @classmethod
    def import_annotations_in_group(cls, group: ifcopenshell.entity_instance) -> None:
        elements = set(
            [
                e
                for e in cls.get_group_elements(group)
                if e.is_a("IfcAnnotation") and e.ObjectType != "DRAWING" and not tool.Ifc.get_object(e)
            ]
        )
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.load_existing_meshes()
        ifc_importer.material_creator.load_existing_materials()
        ifc_importer.create_generic_elements(elements)
        ifc_importer.setup_arrays(annotations_to_import=elements)
        for obj in ifc_importer.added_data.values():
            tool.Collector.assign(obj)

    @classmethod
    def get_camera_shape_matrix(
        cls, drawing: ifcopenshell.entity_instance, shape: ifcopenshell.geom.ShapeElementType
    ) -> Matrix:
        mat = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))

        if cls.get_drawing_target_view(drawing) == "REFLECTED_PLAN_VIEW":
            mat[1][1] *= -1
        return mat

    # NOTE: EPsetDrawing pset is completely synced with BIMCameraProperties
    # but BIMCameraProperties are only synced with EPsetDrawing at drawing import
    # therefore camera props can differ from pset if the user changed them from pset.
    @classmethod
    def import_drawing(cls, drawing: ifcopenshell.entity_instance) -> bpy.types.Object:
        settings = ifcopenshell.geom.settings()

        representation = ifcopenshell.util.representation.get_representation(drawing, "Model", "Body", "MODEL_VIEW")
        assert representation

        shape = ifcopenshell.geom.create_shape(settings, drawing)
        camera = tool.Loader.create_camera(drawing, representation, shape)
        tool.Loader.link_mesh(shape, camera)
        obj = bpy.data.objects.new(tool.Loader.get_name(drawing), camera)

        cls.import_camera_props(drawing, camera)
        tool.Ifc.link(drawing, obj)

        obj.matrix_world = cls.get_camera_shape_matrix(drawing, shape)

        tool.Geometry.record_object_position(obj)
        tool.Collector.assign(obj)

        return obj

    @classmethod
    def import_temporary_drawing_camera(cls, drawing: ifcopenshell.entity_instance) -> bpy.types.Object:
        settings = ifcopenshell.geom.settings()

        representation = ifcopenshell.util.representation.get_representation(drawing, "Model", "Body", "MODEL_VIEW")
        assert representation

        shape = ifcopenshell.geom.create_shape(settings, drawing)
        camera = tool.Loader.create_camera(drawing, representation, shape)
        if obj := bpy.data.objects.get("TemporaryDrawingCamera"):
            obj.data = camera
        else:
            obj = bpy.data.objects.new(tool.Loader.get_name(drawing), camera)

        obj.matrix_world = cls.get_camera_shape_matrix(drawing, shape)
        return obj

    @classmethod
    def import_camera_props(cls, drawing: ifcopenshell.entity_instance, camera: bpy.types.Camera) -> None:
        from bonsai.bim.module.drawing.prop import get_diagram_scales

        # Temporarily clear the definition id to prevent prop update callbacks to IFC.
        camera_props = cls.get_camera_props(camera)
        update_props = camera_props.update_props
        camera_props.update_props = False

        camera_props.has_underlay = False
        camera_props.has_linework = True
        camera_props.has_annotation = True
        camera_props.target_view = "PLAN_VIEW"
        camera_props.is_nts = False
        camera.shift_x = 0.0
        camera.shift_y = 0.0

        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        if pset:
            if "TargetView" in pset:
                camera_props.target_view = pset["TargetView"]
            if "Scale" in pset:
                valid_scales = [
                    i[0] for i in get_diagram_scales(None, bpy.context) if pset["Scale"] == i[0].split("|")[-1]
                ]
                if valid_scales:
                    camera_props.diagram_scale = valid_scales[0]
                else:
                    camera_props.diagram_scale = "CUSTOM"
                    if ":" in pset["HumanScale"]:
                        numerator, denominator = pset["HumanScale"].split(":")
                    else:
                        numerator, denominator = pset["HumanScale"].split("=")
                    camera_props.custom_scale_numerator = numerator
                    camera_props.custom_scale_denominator = denominator
            if "HasUnderlay" in pset:
                camera_props.has_underlay = bool(pset["HasUnderlay"])
            if "HasLinework" in pset:
                camera_props.has_linework = bool(pset["HasLinework"])
            if "HasAnnotation" in pset:
                camera_props.has_annotation = bool(pset["HasAnnotation"])
            if "IsNTS" in pset:
                camera_props.is_nts = bool(pset["IsNTS"])
            if "DPI" in pset:
                camera_props.dpi = int(pset["DPI"])
            if "LineworkMode" in pset:
                camera_props.linework_mode = str(pset["LineworkMode"])
            if "FillMode" in pset:
                camera_props.fill_mode = str(pset["FillMode"])
            if "CutMode" in pset:
                camera_props.cut_mode = str(pset["CutMode"])
            if camera.type == "PERSP":
                shifts = cls.get_perspective_camera_shifts(drawing)
                camera.shift_x = shifts["shift_x"]
                camera.shift_y = shifts["shift_y"]

        camera_props.update_props = update_props

    drawing_selected_states: dict[int, bool] = {}

    @classmethod
    def import_drawings(cls) -> None:
        props = tool.Drawing.get_document_props()
        expanded_target_views = {d.target_view for d in props.drawings if not d.is_drawing and d.is_expanded}
        cls.drawing_selected_states.update({d.ifc_definition_id: d.is_selected for d in props.drawings if d.is_drawing})
        props.drawings.clear()
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        grouped_drawings: dict[str, list[ifcopenshell.entity_instance]] = {
            "MODEL_VIEW": [],
            "PLAN_VIEW": [],
            "SECTION_VIEW": [],
            "ELEVATION_VIEW": [],
            "REFLECTED_PLAN_VIEW": [],
        }
        for drawing in drawings:
            target_view = cls.get_drawing_target_view(drawing)
            grouped_drawings.setdefault(target_view, []).append(drawing)

        for target_view, drawings in grouped_drawings.items():
            new = props.drawings.add()
            new.name = target_view.replace("_", " ").title() + f" ({len(drawings)})"
            new.target_view = target_view
            new.is_drawing = False
            new.is_expanded = target_view in expanded_target_views

            if not new.is_expanded:
                continue

            for drawing in sorted(drawings, key=lambda x: x.Name or "Unnamed"):
                new = props.drawings.add()
                new.name = drawing.Name or "Unnamed"
                new.is_selected = cls.drawing_selected_states.setdefault(drawing.id(), True)
                new.is_drawing = True
                new.ifc_definition_id = drawing.id()  # Last, to prevent unnecessary prop callbacks

    @classmethod
    def import_documents(cls, document_type: DOCUMENT_TYPE) -> None:
        dprops = cls.get_document_props()
        if document_type == "SCHEDULE":
            documents_collection = dprops.schedules
        elif document_type == "REFERENCE":
            documents_collection = dprops.references

        documents_collection.clear()
        schedules = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == document_type]
        for schedule in schedules:
            new = documents_collection.add()
            new.ifc_definition_id = schedule.id()
            new.name = schedule.Name or "Unnamed"
            new.identification = tool.Document.get_document_information_id(schedule) or ""

    @classmethod
    def get_sheet_identification(cls, sheet: ifcopenshell.entity_instance) -> str:
        """Schema agnostic method to get IfcDocumentInformation.Identification."""
        attr = "DocumentId" if sheet.file.schema == "IFC2X3" else "Identification"
        return getattr(sheet, attr)

    @classmethod
    def import_sheets(cls) -> None:
        props = cls.get_document_props()
        expanded_sheets = {s.ifc_definition_id for s in props.sheets if s.is_expanded}
        if not hasattr(cls, "sheet_selected_states"):
            cls.sheet_selected_states = {}
        cls.sheet_selected_states.update({s.ifc_definition_id: s.is_selected for s in props.sheets if s.is_sheet})
        props.sheets.clear()
        sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
        for sheet in sorted(sheets, key=lambda s: cls.get_sheet_identification(s)):
            new = props.sheets.add()
            new.ifc_definition_id = sheet.id()
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = sheet.DocumentId
            else:
                new.identification = sheet.Identification
            new.name = sheet.Name
            new.is_sheet = True
            new.is_expanded = sheet.id() in expanded_sheets
            new.is_selected = cls.sheet_selected_states.setdefault(sheet.id(), True)

            if not new.is_expanded:
                continue

            for reference in cls.get_document_references(sheet):
                reference_description = cls.get_reference_description(reference)
                if reference_description in ("SHEET", "LAYOUT", "RASTER"):
                    # These references are an internal detail and should not be visible to users
                    continue
                new = props.sheets.add()
                new.ifc_definition_id = reference.id()
                new.is_sheet = False

                new.identification = tool.Document.get_external_reference_id(reference) or ""

                new.name = os.path.basename(reference.Location)
                new.reference_type = reference_description

    @classmethod
    def get_active_sheet(cls) -> Sheet:
        props = cls.get_document_props()
        # Will also get active sheet even if one of it's subitems selected (drawings, etc).
        return next(s for s in props.sheets[: props.active_sheet_index + 1][::-1] if s.is_sheet)

    @classmethod
    def get_active_drawing_item(cls) -> Union[DrawingProperties, None]:
        props = cls.get_document_props()
        drawing_index = props.active_drawing_index
        if len(props.drawings) > drawing_index >= 0:
            item = props.drawings[drawing_index]
            if item.is_drawing:
                return item

    @classmethod
    def get_active_sheet_item(cls, *, is_sheet: bool = False, reference_type: str = "") -> Union[Sheet, None]:
        props = cls.get_document_props()
        sheet_index = props.active_sheet_index
        if len(props.sheets) > sheet_index >= 0:
            item = props.sheets[sheet_index]
            if not is_sheet and not reference_type:
                return item
            if is_sheet:
                if item.is_sheet:
                    return item
            elif reference_type:
                if item.reference_type == reference_type:
                    return item

    @classmethod
    def import_text_attributes(cls, obj: bpy.types.Object) -> None:
        props = cls.get_text_props(obj)
        props.literals.clear()

        ifc_literals = cls.get_text_literal(obj, return_list=True)
        assert isinstance(ifc_literals, list)

        if ifc_literals:
            first_alignment = getattr(ifc_literals[0], "BoxAlignment", None) or "bottom-left"
            if first_alignment == "center":
                first_alignment = "middle-middle"
            props.align_vertical, props.align_horizontal = first_alignment.split("-")

        for ifc_literal in ifc_literals:
            literal_props = props.literals.add()
            bonsai.bim.helper.import_attributes(ifc_literal, literal_props.attributes)

            alignment = getattr(ifc_literal, "BoxAlignment", None) or "bottom-left"
            if alignment == "center":
                alignment = "middle-middle"
            literal_props.align_vertical, literal_props.align_horizontal = alignment.split("-")
            literal_props.ifc_definition_id = ifc_literal.id()

        from bonsai.bim.module.drawing.data import DecoratorData

        text_data = DecoratorData.get_text_data(obj)
        props.font_size = str(text_data["FontSize"])
        props.newline_at = text_data["Newline_At"]
        props.set_symbol(text_data["Symbol"])

    @classmethod
    def import_assigned_product(cls, obj: bpy.types.Object) -> None:
        element = tool.Ifc.get_entity(obj)
        assert element
        product = cls.get_assigned_product(element)
        props = cls.get_object_assigned_product_props(obj)
        if product:
            assert isinstance(product_obj := tool.Ifc.get_object(product), bpy.types.Object)
            props.relating_product = product_obj
        else:
            props.relating_product = None

    @classmethod
    def open_with_user_command(cls, user_command: str, path: str) -> None:
        if user_command:
            commands = json.loads(user_command)
            replacements = {"path": path}
            for command in commands:
                command[0] = shutil.which(command[0]) or command[0]
                subprocess.Popen([replacements.get(c, c) for c in command])
        else:
            if platform.system() == "Darwin":
                subprocess.call(("open", path))
            elif platform.system() == "Windows":
                os.startfile(os.path.normpath(path))
            else:
                subprocess.call(("xdg-open", path))

    @classmethod
    def open_spreadsheet(cls, uri: str) -> None:
        cls.open_with_user_command(tool.Blender.get_addon_preferences().spreadsheet_command, uri)

    @classmethod
    def open_svg(cls, uri: str) -> None:
        cls.open_with_user_command(tool.Blender.get_addon_preferences().svg_command, uri)

    @classmethod
    def open_layout_svg(cls, uri: str) -> None:
        cls.open_with_user_command(tool.Blender.get_addon_preferences().layout_svg_command, uri)

    @classmethod
    def run_root_assign_class(
        cls,
        obj=None,
        ifc_class=None,
        predefined_type=None,
        should_add_representation=True,
        context=None,
        ifc_representation_class=None,
    ) -> Union[ifcopenshell.entity_instance, None]:
        return bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def run_type_assign_type(cls, element: ifcopenshell.entity_instance, relating_type: ifcopenshell.entity_instance):
        return bonsai.core.type.assign_type(tool.Ifc, tool.Model, tool.Type, element=element, type=relating_type)

    @classmethod
    def reload_representation(cls, obj: bpy.types.Object, representation: ifcopenshell.entity_instance):
        return bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
        )

    @classmethod
    def get_representation(cls, element, context):
        return ifcopenshell.util.representation.get_representation(element, context)

    @classmethod
    def set_camera_name(cls, drawing: ifcopenshell.entity_instance, name: str) -> None:
        camera = tool.Ifc.get_object(drawing)
        if camera and camera.name != name:
            camera.name = name

    @classmethod
    def set_drawing_collection_name(
        cls, drawing: ifcopenshell.entity_instance, collection: bpy.types.Collection
    ) -> None:
        collection.name = tool.Loader.get_name(drawing)

    @classmethod
    def set_name(cls, element: ifcopenshell.entity_instance, name: str) -> None:
        element.Name = name

    @classmethod
    def show_decorations(cls) -> None:
        props = tool.Drawing.get_document_props()
        props.should_draw_decorations = True

    @classmethod
    def edit_text_font_size(cls, obj: bpy.types.Object, font_size: float) -> None:
        """updates pset `EPset_Annotation.Classes` value
        based on current font size from `obj.BIMTextProperties.font_size`
        """
        from bonsai.bim.module.drawing.data import FONT_SIZES

        props = cls.get_text_props(obj)
        element = tool.Ifc.get_entity(obj)
        assert element
        # updating text font size in EPset_Annotation.Classes
        font_size_str = next((key for key in FONT_SIZES if FONT_SIZES[key] == font_size), None)
        classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        assert isinstance(classes, Union[str, None])
        classes_split = classes.split() if classes else []

        different_font_sizes = [c for c in classes_split if c in FONT_SIZES and c != font_size_str]

        # We do need to change pset value in ifc,
        # but only if there are different font sizes in classes already
        # or if the current font size is not present in classes
        # (except regular font size because it's default).
        if different_font_sizes or (font_size_str not in classes_split and font_size_str != "regular"):
            assert font_size_str is not None
            classes_split = [c for c in classes_split if c not in FONT_SIZES] + [font_size_str]
            classes = " ".join(classes_split)

            ifc_file = tool.Ifc.get()
            pset = tool.Pset.get_element_pset(element, "EPset_Annotation")
            if not pset:
                pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="EPset_Annotation")
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Classes": classes})

    @classmethod
    def edit_text_wrap_length(cls, obj: bpy.types.Object, wrap_length: int) -> None:
        element = tool.Ifc.get_entity(obj)
        ifc_file = tool.Ifc.get()
        pset = tool.Pset.get_element_pset(element, "EPset_Annotation")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Newline_At": wrap_length})

    @classmethod
    def edit_text_symbol(cls, obj: bpy.types.Object, symbol: str) -> None:
        element = tool.Ifc.get_entity(obj)
        ifc_file = tool.Ifc.get()
        pset = tool.Pset.get_element_pset(element, "EPset_Annotation")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Symbol": symbol})

    @classmethod
    def edit_text_alignment(cls, obj: bpy.types.Object, alignment: str) -> None:
        ifc_literals = cls.get_text_literal(obj, return_list=True)
        for ifc_literal in ifc_literals or []:
            if ifc_literal.is_a("IfcTextLiteralWithExtent"):
                ifc_literal.BoxAlignment = alignment

    # TODO below this point is highly experimental prototype code with no tests

    class SheetWarningType(NamedTuple):
        warning_type: Literal["MISSING_LAYOUT", "MISSING_TITLEBLOCK"]
        message: str

        def __str__(self) -> str:
            return f"{self.warning_type:<20} - {self.message}"

    @classmethod
    def validate_sheet_files(cls, sheet: ifcopenshell.entity_instance) -> list[SheetWarningType]:
        warnings: list[tool.Drawing.SheetWarningType] = []

        layout_path = cls.get_document_uri(sheet, "LAYOUT")
        assert layout_path
        sheet_id = cls.get_sheet_identification(sheet)
        if not Path(layout_path).exists():
            warnings.append(
                cls.SheetWarningType("MISSING_LAYOUT", f"Sheet '{sheet_id}' - missing layout '{layout_path}'.")
            )

        titleblock_path = cls.get_document_uri(sheet, "TITLEBLOCK")
        assert titleblock_path
        if not Path(titleblock_path).exists():
            warnings.append(
                cls.SheetWarningType(
                    "MISSING_TITLEBLOCK", f"Sheet '{sheet_id}' - missing titleblock '{titleblock_path}'."
                )
            )
        return warnings

    @classmethod
    def does_file_exist(cls, uri: str) -> bool:
        return os.path.exists(uri)

    @classmethod
    def delete_file(cls, uri: str) -> None:
        os.remove(uri)

    @classmethod
    def move_file(cls, src: str, dest: str) -> None:
        try:
            shutil.move(src, dest)
        except:
            # Perhaps the file is locked in Windows?
            shutil.copy(src, dest)

    @classmethod
    def generate_drawing_name(
        cls,
        target_view: ifcopenshell.util.representation.TARGET_VIEW,
        location_hint: Union[LocationHintLiteral, int],
    ) -> str:
        if isinstance(location_hint, int):
            if location_hint:
                location = tool.Ifc.get().by_id(location_hint)
                target_view_ = target_view
                if target_view == "REFLECTED_PLAN_VIEW":
                    target_view_ = "RCP_VIEW"
                return (location.Name or "UNNAMED").upper() + " " + target_view_.split("_")[0]
        elif target_view in ("SECTION_VIEW", "ELEVATION_VIEW") and location_hint:
            return location_hint + " " + target_view.split("_")[0]
        elif target_view == "MODEL_VIEW" and location_hint:
            return location_hint
        return target_view

    @classmethod
    def get_default_layout_path(cls, identification: str, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        prefs = tool.Blender.get_addon_preferences()
        layouts_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "LayoutsDir") or prefs.doc.layouts_dir
        )
        return os.path.join(layouts_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_sheet_path(cls, identification: str, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        prefs = tool.Blender.get_addon_preferences()
        sheets_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "SheetsDir") or prefs.doc.sheets_dir
        )
        return os.path.join(sheets_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_titleblock_path(cls, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        prefs = tool.Blender.get_addon_preferences()
        titleblocks_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "TitleblocksDir")
            or prefs.doc.titleblocks_dir
        )
        return os.path.join(titleblocks_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_drawing_path(cls, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        prefs = tool.Blender.get_addon_preferences()
        drawings_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "DrawingsDir") or prefs.doc.drawings_dir
        )
        return os.path.join(drawings_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def sanitise_filename(cls, name: str) -> str:
        return "".join(x for x in name if (x.isalnum() or x in "._- "))

    ResourceType = Literal["Stylesheet", "Markers", "Symbols", "Patterns", "ShadingStyles"]
    RESOURCE_TYPES = ("Stylesheet", "Markers", "Symbols", "Patterns", "ShadingStyles")

    @classmethod
    def get_default_drawing_resource_path(cls, resource: ResourceType) -> Union[str, None]:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        doc_prefs = tool.Blender.get_addon_preferences().doc
        resource_path = ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", f"{resource}Path") or getattr(
            doc_prefs, f"{resource.lower()}_path"
        )
        if resource_path:
            assert isinstance(resource_path, str)
            return resource_path.replace("\\", "/")

    @classmethod
    def get_default_shading_style(cls) -> str:
        prefs = tool.Blender.get_addon_preferences()
        return prefs.doc.shadingstyle_default

    @classmethod
    def setup_shading_styles_path(cls, resource_path: str) -> None:
        resource_path = tool.Ifc.resolve_uri(resource_path)
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)
        if not os.path.exists(resource_path):
            resource_basename = os.path.basename(resource_path)
            ootb_resource = tool.Blender.get_data_dir_path(Path("assets") / resource_basename)
            if ootb_resource.is_file():
                shutil.copy(ootb_resource, resource_path)

    @classmethod
    def get_potential_reference_elements(
        cls, drawing: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        elements = []
        existing_references = set(cls.get_group_elements(cls.get_drawing_group(drawing)))
        if exclude := ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "Exclude"):
            existing_references.update(ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), exclude))

        for element in tool.Ifc.get().by_type("IfcAnnotation"):
            if element in existing_references or element == drawing:
                continue
            if element.ObjectType == "DRAWING":
                pset = ifcopenshell.util.element.get_psets(element).get("EPset_Drawing", {})
                if pset.get("TargetView", None) in ("SECTION_VIEW", "ELEVATION_VIEW") and pset.get(
                    "GlobalReferencing", False
                ):
                    elements.append(element)
        for element in tool.Ifc.get().by_type("IfcGrid"):
            if element in existing_references:
                continue
            for axis in element.UAxes + element.VAxes + (element.WAxes or tuple()):
                if axis in existing_references:
                    continue
                elements.append(axis)
        target_view = tool.Drawing.get_drawing_target_view(drawing)
        if target_view in ("SECTION_VIEW", "ELEVATION_VIEW"):
            for element in tool.Ifc.get().by_type("IfcBuildingStorey"):
                if element in existing_references:
                    continue
                elements.append(element)
        return elements

    @classmethod
    def is_auto_annotation(cls, element: ifcopenshell.entity_instance):
        return element.is_a("IfcAnnotation") and element.ObjectType in ("GRID", "SECTION", "ELEVATION", "SECTION_LEVEL")

    @classmethod
    def get_drawing_reference_annotation(
        cls, drawing: ifcopenshell.entity_instance, reference_element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, bool, None]:
        if drawing == reference_element:
            return True
        if reference_element.is_a("IfcGridAxis"):
            # We cannot associate IfcGridAxis directly, so we establish a convention:
            # IfcRelAssignsToProduct.RelatingProduct = IfcGrid
            # IfcRelAssignsToProduct.Name = IfcGridAxis.AxisTag
            grid = None
            for attribute in ("PartOfU", "PartOfV", "PartOfW"):
                if getattr(reference_element, attribute, None):
                    grid = getattr(reference_element, attribute)[0]
                    break

            for element in cls.get_group_elements(cls.get_drawing_group(drawing)):
                if not element.is_a("IfcAnnotation"):
                    continue
                for rel in element.HasAssignments:
                    if (
                        rel.is_a("IfcRelAssignsToProduct")
                        and rel.RelatingProduct == grid
                        and rel.Name == reference_element.AxisTag
                    ):
                        return element
            return
        for element in cls.get_group_elements(cls.get_drawing_group(drawing)):
            if element.is_a("IfcAnnotation"):
                for rel in element.HasAssignments:
                    if rel.is_a("IfcRelAssignsToProduct") and rel.RelatingProduct == reference_element:
                        return element

    @classmethod
    def regenerate_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        annotation: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if reference_element.is_a("IfcGridAxis"):
            return cls.regenerate_grid_axis_reference_annotation(drawing, annotation, reference_element, context)
        elif reference_element.is_a("IfcAnnotation") and reference_element.ObjectType == "DRAWING":
            target_view = ifcopenshell.util.element.get_pset(reference_element, "EPset_Drawing", "TargetView")
            if target_view == "ELEVATION_VIEW":
                return cls.regenerate_elevation_reference_annotation(drawing, annotation, reference_element, context)
            elif target_view == "SECTION_VIEW":
                return cls.regenerate_section_reference_annotation(drawing, annotation, reference_element, context)
        elif reference_element.is_a("IfcBuildingStorey"):
            return cls.regenerate_storey_annotation(drawing, annotation, reference_element, context)
        return annotation

    @classmethod
    def generate_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if reference_element.is_a("IfcGridAxis"):
            return cls.generate_grid_axis_reference_annotation(drawing, reference_element, context)
        elif reference_element.is_a("IfcAnnotation") and reference_element.ObjectType == "DRAWING":
            target_view = ifcopenshell.util.element.get_pset(reference_element, "EPset_Drawing", "TargetView")
            if target_view == "ELEVATION_VIEW":
                return cls.generate_elevation_reference_annotation(drawing, reference_element, context)
            elif target_view == "SECTION_VIEW":
                return cls.generate_section_reference_annotation(drawing, reference_element, context)
        elif reference_element.is_a("IfcBuildingStorey"):
            return cls.generate_storey_annotation(drawing, reference_element, context)

    @classmethod
    def generate_storey_points(
        cls, drawing: ifcopenshell.entity_instance, storey: ifcopenshell.entity_instance
    ) -> list | None:
        import bonsai.bim.module.drawing.helper as helper

        camera = tool.Ifc.get_object(drawing)
        if camera.data.type != "ORTHO":
            return
        if not cls.is_matrix_perpendicular(camera.matrix_world, Matrix()):
            return

        xmin, xmax, ymin, ymax = helper.ortho_view_frame(camera.data)[:4]
        rl = ifcopenshell.util.placement.get_local_placement(storey.ObjectPlacement)[2][3]

        # Convert RL from project units (feet) to meters for Blender world space
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        rl_meters = rl * unit_scale

        y = (camera.matrix_world.inverted() @ Vector((0.0, 0.0, rl_meters))).y
        if y < ymin or y > ymax:
            return

        return (Vector((xmax, y, 0.0)), Vector((xmin, y, 0.0)))

    @classmethod
    def generate_storey_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        storey: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if not (points := cls.generate_storey_points(drawing, storey)):
            return

        camera = tool.Ifc.get_object(drawing)
        mesh = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new(storey.Name or "Unnamed", mesh)
        obj.matrix_world = cls.get_default_annotation_matrix(camera)
        element = cls.run_root_assign_class(
            obj=obj, ifc_class="IfcAnnotation", predefined_type="SECTION_LEVEL", should_add_representation=False
        )
        tool.Geometry.run_edit_object_placement(obj)
        element.Name = storey.Name or "Unnamed"
        builder = ShapeBuilder(tool.Ifc.get())
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        points = [p / unit_scale for p in points]
        representation = builder.get_representation(context, [builder.polyline(points)])
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)
        return element

    @classmethod
    def regenerate_storey_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        annotation: ifcopenshell.entity_instance,
        storey: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if not (points := cls.generate_storey_points(drawing, storey)):
            return

        camera = tool.Ifc.get_object(drawing)
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, annotation)
        m = ifcopenshell.util.shape.get_shape_matrix(shape)
        mw = cls.get_default_annotation_matrix(camera)
        existing_verts = [Vector(v) for v in ifcopenshell.util.shape.get_vertices(shape.geometry)]

        new_points = None
        if not np.allclose(m, np.array(mw), atol=1e-4):
            new_points = points
        elif len(existing_verts) != 2:
            new_points = points
        else:
            existing_verts = sorted(existing_verts, key=lambda v: v.x)
            xmin, xmax = [v.x for v in existing_verts]
            y = points[0].y
            if not tool.Cad.is_x(y, existing_verts[0].y) or not tool.Cad.is_x(y, existing_verts[1].y):
                new_points = (Vector((xmax, y, 0.0)), Vector((xmin, y, 0.0)))

        if new_points:
            if representation := ifcopenshell.util.representation.get_representation(annotation, context):
                ifcopenshell.api.geometry.unassign_representation(
                    tool.Ifc.get(), product=annotation, representation=representation
                )
            builder = ShapeBuilder(tool.Ifc.get())
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            new_points = [p / unit_scale for p in new_points]
            representation = builder.get_representation(context, [builder.polyline(new_points)])
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), annotation, representation)

            if obj := tool.Ifc.get_object(annotation):
                obj.matrix_world = mw
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=representation
                )
            else:
                ifcopenshell.api.geometry.edit_object_placement(tool.Ifc.get(), product=annotation, matrix=np.array(mw))

        annotation.Name = storey.Name or "Unnamed"
        return annotation

    @classmethod
    def generate_section_reference_points(
        cls, drawing: ifcopenshell.entity_instance, section: ifcopenshell.entity_instance
    ) -> list | None:
        import bonsai.bim.module.drawing.helper as helper

        camera = tool.Ifc.get_object(drawing)
        if camera.data.type != "ORTHO":
            return
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, section)
        m = ifcopenshell.util.shape.get_shape_matrix(shape)
        if not cls.is_matrix_perpendicular(camera.matrix_world, Matrix(m)):
            return
        if not cls.does_shape_intersect_camera(shape, camera):
            return

        # Get cutting plane as a line
        verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
        cutting_plane_verts = sorted(verts, key=lambda v: v[2])[-4:]
        v1, *_, v2 = sorted(cutting_plane_verts, key=lambda v: v[0])  # Cut is in +X direction
        im = camera.matrix_world.inverted()
        v1, v2 = [im @ Vector((m @ np.append(v, 1.0))[:3]) for v in [v1, v2]]

        target_view = cls.get_drawing_target_view(drawing)
        bounds = helper.ortho_view_frame(camera.data)

        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            # For plan views, clip to XY bounds and set Z=0
            if not (points := helper.clip_segment(bounds, [v1, v2])):
                return
            for v in points:
                v.z = 0
        elif target_view in ("ELEVATION_VIEW", "SECTION_VIEW"):
            # For section/elevation views, elevate the segment vertically
            if not (points := helper.elevate_segment(bounds, [v1, v2])):
                return
        elif target_view == "MODEL_VIEW":
            # For model views, clip to XY bounds and keep Z (3D line at true elevation)
            if not (points := helper.clip_segment(bounds, [v1, v2])):
                return
        else:
            return

        return points

    @classmethod
    def generate_section_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        section: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if not (points := cls.generate_section_reference_points(drawing, section)):
            return

        camera = tool.Ifc.get_object(drawing)
        mesh = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new(section.Name or "Unnamed", mesh)
        obj.matrix_world = cls.get_default_annotation_matrix(camera)
        element = cls.run_root_assign_class(
            obj=obj, ifc_class="IfcAnnotation", predefined_type="SECTION", should_add_representation=False
        )
        element.Name = section.Name or "Unnamed"
        builder = ShapeBuilder(tool.Ifc.get())
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        points = [p / unit_scale for p in points]
        representation = builder.get_representation(context, [builder.polyline(points)])
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)
        return element

    @classmethod
    def regenerate_section_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        annotation: ifcopenshell.entity_instance,
        section: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        if not (points := cls.generate_section_reference_points(drawing, section)):
            return

        camera = tool.Ifc.get_object(drawing)
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, annotation)
        m = ifcopenshell.util.shape.get_shape_matrix(shape)
        mw = cls.get_default_annotation_matrix(camera)
        existing_verts = [Vector(v) for v in ifcopenshell.util.shape.get_vertices(shape.geometry)]

        new_points = None
        if not np.allclose(m, np.array(mw), atol=1e-4):
            new_points = points
        elif len(existing_verts) != 2:
            new_points = points
        else:
            if not tool.Cad.are_edges_collinear(existing_verts, points):
                # Attempt to update the section line by projecting existing verts onto the new line
                v1 = tool.Cad.point_on_edge(existing_verts[0], points)
                v2 = tool.Cad.point_on_edge(existing_verts[1], points)
                existing_length = (existing_verts[0] - existing_verts[1]).length
                new_length = (v2 - v1).length
                if abs((existing_length - new_length) / existing_length) <= 0.10:
                    # If the projected line is within 10% of the previous length ...
                    new_points = (v1, v2)
                else:
                    new_points = points

        if new_points:
            if representation := ifcopenshell.util.representation.get_representation(annotation, context):
                ifcopenshell.api.geometry.unassign_representation(
                    tool.Ifc.get(), product=annotation, representation=representation
                )
            builder = ShapeBuilder(tool.Ifc.get())
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            new_points = [p / unit_scale for p in new_points]
            representation = builder.get_representation(context, [builder.polyline(new_points)])
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), annotation, representation)
            if obj := tool.Ifc.get_object(annotation):
                obj.matrix_world = mw
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=representation
                )
            else:
                ifcopenshell.api.geometry.edit_object_placement(tool.Ifc.get(), product=annotation, matrix=np.array(mw))
        annotation.Name = section.Name or "Unnamed"
        return annotation

    @classmethod
    def generate_elevation_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        elevation: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        camera = tool.Ifc.get_object(drawing)
        if camera.data.type != "ORTHO":
            return
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, elevation)
        m = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
        if cls.is_matrix_perpendicular(camera.matrix_world, m) and cls.does_shape_intersect_camera(shape, camera):
            obj = bpy.data.objects.new(elevation.Name or "Unnamed", None)
            obj.empty_display_size = 0.1
            obj.matrix_world = cls.get_default_annotation_matrix(camera, matrix_world=m)
            element = cls.run_root_assign_class(
                obj=obj, ifc_class="IfcAnnotation", predefined_type="ELEVATION", should_add_representation=False
            )
            element.Name = elevation.Name or "Unnamed"
            return element

    @classmethod
    def regenerate_elevation_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        annotation: ifcopenshell.entity_instance,
        elevation: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        camera = tool.Ifc.get_object(drawing)
        if camera.data.type != "ORTHO":
            return
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, elevation)
        m = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
        if cls.is_matrix_perpendicular(camera.matrix_world, m) and cls.does_shape_intersect_camera(shape, camera):
            existing_matrix = Matrix(ifcopenshell.util.placement.get_local_placement(annotation.ObjectPlacement))
            # The user is allowed to shift the elevation, but not rotate it
            if not np.allclose(np.array(m.to_3x3()), np.array(existing_matrix.to_3x3()), atol=1e-4):
                mw = cls.get_default_annotation_matrix(camera, matrix_world=m)
                if obj := tool.Ifc.get_object(annotation):
                    obj.matrix_world = mw
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                else:
                    ifcopenshell.api.geometry.edit_object_placement(
                        tool.Ifc.get(), product=annotation, matrix=np.array(mw)
                    )
            annotation.Name = elevation.Name or "Unnamed"
            return annotation

    @classmethod
    def generate_grid_axis_reference_points(
        cls, drawing: ifcopenshell.entity_instance, axis: ifcopenshell.entity_instance
    ) -> list | None:
        import bonsai.bim.module.drawing.helper as helper

        camera = tool.Ifc.get_object(drawing)
        if camera.data.type != "ORTHO":
            return

        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        geometry = ifcopenshell.geom.create_shape(settings, axis.AxisCurve)
        verts = ifcopenshell.util.shape.get_vertices(geometry)
        grid = (axis.PartOfU or axis.PartOfV or axis.PartOfW)[0]
        m = ifcopenshell.util.placement.get_local_placement(grid.ObjectPlacement)
        im = camera.matrix_world.inverted()
        v1, v2 = [im @ Vector((m @ np.append(v, 1.0))[:3]) for v in verts[:2]]

        target_view = tool.Drawing.get_drawing_target_view(drawing)
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            bounds = helper.ortho_view_frame(camera.data)
            if not (points := helper.clip_segment(bounds, [v1, v2])):
                return
        elif target_view in ("ELEVATION_VIEW", "SECTION_VIEW"):
            bounds = helper.ortho_view_frame(camera.data)
            if not (points := helper.elevate_segment(bounds, [v1, v2])):
                return
        else:
            return
        for v in points:
            v.z = 0
        return points

    @classmethod
    def generate_grid_axis_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        axis: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> Union[ifcopenshell.entity_instance, None]:
        if not (points := cls.generate_grid_axis_reference_points(drawing, axis)):
            return

        camera = tool.Ifc.get_object(drawing)
        mesh = bpy.data.meshes.new("Mesh")
        obj = bpy.data.objects.new(axis.AxisTag or "-", mesh)
        obj.matrix_world = cls.get_default_annotation_matrix(camera)
        element = cls.run_root_assign_class(
            obj=obj, ifc_class="IfcAnnotation", predefined_type="GRID", should_add_representation=False
        )
        element.Name = axis.AxisTag or "-"
        builder = ShapeBuilder(tool.Ifc.get())
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        points = [p / unit_scale for p in points]
        representation = builder.get_representation(context, [builder.polyline(points)])
        ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), element, representation)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)
        return element

    @classmethod
    def regenerate_grid_axis_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        annotation: ifcopenshell.entity_instance,
        axis: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> Union[ifcopenshell.entity_instance, None]:
        if not (points := cls.generate_grid_axis_reference_points(drawing, axis)):
            return

        camera = tool.Ifc.get_object(drawing)
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, annotation)
        m = ifcopenshell.util.shape.get_shape_matrix(shape)
        mw = cls.get_default_annotation_matrix(camera)
        existing_verts = [Vector(v) for v in ifcopenshell.util.shape.get_vertices(shape.geometry)]

        new_points = None
        if not np.allclose(m, np.array(mw), atol=1e-4):
            new_points = points
        elif len(existing_verts) != 2:
            new_points = points
        else:
            if not tool.Cad.are_edges_collinear(existing_verts, points):
                # Attempt to update the section line by projecting existing verts onto the new line
                v1 = tool.Cad.point_on_edge(existing_verts[0], points)
                v2 = tool.Cad.point_on_edge(existing_verts[1], points)
                existing_length = (existing_verts[0] - existing_verts[1]).length
                new_length = (v2 - v1).length
                if abs((existing_length - new_length) / existing_length) <= 0.10:
                    # If the projected line is within 10% of the previous length ...
                    new_points = (v1, v2)
                else:
                    new_points = points

        if new_points:
            if representation := ifcopenshell.util.representation.get_representation(annotation, context):
                ifcopenshell.api.geometry.unassign_representation(
                    tool.Ifc.get(), product=annotation, representation=representation
                )
            builder = ShapeBuilder(tool.Ifc.get())
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            new_points = [p / unit_scale for p in new_points]
            representation = builder.get_representation(context, [builder.polyline(new_points)])
            ifcopenshell.api.geometry.assign_representation(tool.Ifc.get(), annotation, representation)
            if obj := tool.Ifc.get_object(annotation):
                obj.matrix_world = mw
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
                bonsai.core.geometry.switch_representation(
                    tool.Ifc, tool.Geometry, obj=obj, representation=representation
                )
            else:
                ifcopenshell.api.geometry.edit_object_placement(tool.Ifc.get(), product=annotation, matrix=np.array(mw))
        annotation.Name = axis.AxisTag or "-"
        return annotation

    @classmethod
    def get_default_annotation_matrix(cls, camera, matrix_world=None):
        if matrix_world is None:
            # Use normalized camera matrix (without scale) for RCP compatibility
            matrix_world = cls.get_camera_matrix(camera)

        # Check if this is an RCP (reflected ceiling plan) by checking for negative scale
        camera_scale = camera.matrix_world.to_scale()
        is_rcp = camera_scale.x < 0 or camera_scale.y < 0 or camera_scale.z < 0

        # For RCP, the offset needs to be positive instead of negative
        # because the Z axis is flipped 180° in get_camera_matrix
        offset_direction = 1 if is_rcp else -1
        annotation_offset = Vector((0, 0, offset_direction * (camera.data.clip_start + 0.05)))
        annotation_offset = matrix_world.to_quaternion() @ annotation_offset
        matrix_world.translation += annotation_offset
        return matrix_world

    @classmethod
    def is_perpendicular(cls, a: bpy.types.Object, b: bpy.types.Object) -> bool:
        axes = [mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))]
        a_quaternion = a.matrix_world.to_quaternion()
        b_quaternion = b.matrix_world.to_quaternion()
        for axis in axes:
            if abs((a_quaternion @ axis).angle(b_quaternion @ axis) - (math.pi / 2)) < 1e-5:
                return True
        return False

    @classmethod
    def is_matrix_perpendicular(cls, a: Matrix, b: Matrix) -> bool:
        axes = [mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))]
        a_quaternion = a.to_quaternion()
        b_quaternion = b.to_quaternion()
        for axis in axes:
            if abs((a_quaternion @ axis).angle(b_quaternion @ axis) - (math.pi / 2)) < 1e-5:
                return True
        return False

    @classmethod
    def get_camera_block(cls, obj: bpy.types.Object) -> dict:
        assert isinstance(camera := obj.data, bpy.types.Camera)
        props = tool.Drawing.get_camera_props(camera)
        raster_x = props.raster_x
        raster_y = props.raster_y

        if raster_x > raster_y:
            width = camera.ortho_scale
            height = width / raster_x * raster_y
        else:
            height = camera.ortho_scale
            width = height / raster_y * raster_x
        depth = camera.clip_end

        verts = (
            obj.matrix_world @ mathutils.Vector((-width / 2, -height / 2, -depth)),
            obj.matrix_world @ mathutils.Vector((-width / 2, -height / 2, 0)),
            obj.matrix_world @ mathutils.Vector((-width / 2, height / 2, -depth)),
            obj.matrix_world @ mathutils.Vector((-width / 2, height / 2, 0)),
            obj.matrix_world @ mathutils.Vector((width / 2, -height / 2, -depth)),
            obj.matrix_world @ mathutils.Vector((width / 2, -height / 2, 0)),
            obj.matrix_world @ mathutils.Vector((width / 2, height / 2, -depth)),
            obj.matrix_world @ mathutils.Vector((width / 2, height / 2, 0)),
        )
        faces = [
            [0, 1, 3, 2],
            [2, 3, 7, 6],
            [6, 7, 5, 4],
            [4, 5, 1, 0],
            [2, 6, 4, 0],
            [7, 3, 1, 5],
        ]
        return {"verts": verts, "faces": faces}

    @classmethod
    def is_intersecting(cls, a: bpy.types.Object, b: bpy.types.Object) -> bool:
        a_block = cls.get_camera_block(a)
        a_tree = mathutils.bvhtree.BVHTree.FromPolygons(a_block["verts"], a_block["faces"])
        b_block = cls.get_camera_block(b)
        b_tree = mathutils.bvhtree.BVHTree.FromPolygons(b_block["verts"], b_block["faces"])
        return bool(a_tree.overlap(b_tree))

    @classmethod
    def does_shape_intersect_camera(cls, shape, camera) -> bool:
        a_block = cls.get_camera_block(camera)
        a_tree = mathutils.bvhtree.BVHTree.FromPolygons(a_block["verts"], a_block["faces"])
        m = ifcopenshell.util.shape.get_shape_matrix(shape)
        verts = [(m @ np.append(v, 1.0))[:3] for v in ifcopenshell.util.shape.get_vertices(shape.geometry)]
        faces = ifcopenshell.util.shape.get_faces(shape.geometry)
        b_tree = mathutils.bvhtree.BVHTree.FromPolygons(verts, faces)
        return bool(a_tree.overlap(b_tree))

    @classmethod
    def replace_text_literal_variables(
        cls,
        text: str,
        product: Optional[ifcopenshell.entity_instance] = None,
    ) -> str:
        if not product:
            return text

        for command in re.findall("``.+?``", text):
            original_command = command
            command_content = command[2:-2]
            try:
                text = text.replace(original_command, ifcopenshell.util.selector.format(command_content, product))
            except Exception:
                text = text.replace(original_command, "")
        for variable in re.findall("{{.*?}}", text):
            value = ifcopenshell.util.selector.get_element_value(product, variable[2:-2])
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(v) for v in value)
            text = text.replace(variable, str(value))
        return text

    @classmethod
    def sync_object_representation(cls, obj: bpy.types.Object) -> None:
        bpy.ops.bim.update_representation(obj=obj.name)

    @classmethod
    def sync_object_placement(cls, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
        blender_matrix = np.array(obj.matrix_world)
        element = tool.Ifc.get_entity(obj)
        if tool.Geometry.is_scaled(obj):
            bpy.ops.bim.update_representation(obj=obj.name)
            return element
        if element.is_a("IfcGridAxis"):
            return cls.sync_grid_axis_object_placement(obj, element)
        if not hasattr(element, "ObjectPlacement"):
            return
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        return element

    @classmethod
    def sync_grid_axis_object_placement(cls, obj: bpy.types.Object, element: ifcopenshell.entity_instance) -> None:
        grid = (element.PartOfU or element.PartOfV or element.PartOfW)[0]
        grid_obj = tool.Ifc.get_object(grid)
        if grid_obj:
            cls.sync_object_placement(grid_obj)
            if grid_obj.matrix_world != obj.matrix_world:
                bpy.ops.bim.update_representation(obj=obj.name)
        tool.Geometry.record_object_position(obj)

    @classmethod
    def get_document_references(cls, document: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        if tool.Ifc.get_schema() == "IFC2X3":
            return document.DocumentReferences or []
        return document.HasDocumentReferences or []

    @classmethod
    def get_references_with_location(cls, location: Union[str, None]) -> list[ifcopenshell.entity_instance]:
        return [r for r in tool.Ifc.get().by_type("IfcDocumentReference") if r.Location == location]

    @classmethod
    def update_embedded_svg_location(cls, uri: str, reference: ifcopenshell.entity_instance, new_location: str) -> None:
        tree = etree.parse(uri)
        root = tree.getroot()
        rel_location = os.path.relpath(new_location, os.path.dirname(uri))

        for g in root.findall(
            './/{http://www.w3.org/2000/svg}g[@data-type="drawing"][@data-id="' + str(reference.id()) + '"]'
        ):
            for foreground in g.findall('.//{http://www.w3.org/2000/svg}image[@data-type="foreground"]'):
                foreground.attrib["{http://www.w3.org/1999/xlink}href"] = rel_location
            for background in g.findall('.//{http://www.w3.org/2000/svg}image[@data-type="background"]'):
                background.attrib["{http://www.w3.org/1999/xlink}href"] = rel_location[0:-4] + "-underlay.png"
        tree.write(uri, pretty_print=True, xml_declaration=True, encoding="utf-8")

    @classmethod
    def get_reference_description(cls, reference: ifcopenshell.entity_instance) -> Union[str, None]:
        if reference.file.schema == "IFC2X3":
            return reference.Name
        return reference.Description

    @classmethod
    def generate_reference_attributes(
        cls, reference: ifcopenshell.entity_instance, **attributes: Any
    ) -> dict[str, Any]:
        """will automatically convert attributes below for IFC2X3 compatibility:

        - Identification -> ItemReference

        - Description -> Name
        """
        if reference.file.schema == "IFC2X3":
            if "Description" in attributes:
                attributes["Name"] = attributes["Description"]
                del attributes["Description"]
            if "Identification" in attributes:
                attributes["ItemReference"] = attributes["Identification"]
                del attributes["Identification"]
        return attributes

    @classmethod
    def get_reference_location(cls, reference: ifcopenshell.entity_instance) -> Union[str, None]:
        return reference.Location

    @classmethod
    def get_reference_element(
        cls, reference: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        if tool.Ifc.get_schema() == "IFC2X3":
            refs = [r for r in tool.Ifc.get().by_type("IfcRelAssociatesDocument") if r.RelatingDocument == reference]
        else:
            refs = reference.DocumentRefForObjects
        if refs:
            return refs[0].RelatedObjects[0]

    @classmethod
    def get_drawing_human_scale(cls, drawing: ifcopenshell.entity_instance) -> str:
        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing") or {}
        return "NTS" if pset.get("IsNTS", False) else pset.get("HumanScale", "NTS")

    @classmethod
    def get_drawing_metadata(cls, drawing: ifcopenshell.entity_instance) -> list[str]:
        pset_data = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        metadata_str = pset_data.get("Metadata", "") or ""
        return [v_ for v in metadata_str.split(",") if (v_ := v.strip())]

    @classmethod
    def get_annotation_z_index(cls, drawing: ifcopenshell.entity_instance) -> float:
        return ifcopenshell.util.element.get_pset(drawing, "EPset_Annotation", "ZIndex") or 0

    @classmethod
    def get_annotation_symbol(cls, element: ifcopenshell.entity_instance) -> Union[str, None]:
        symbol = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Symbol")
        if not symbol:
            # EPset_AnnotationSurveyArea is not standard! See bSI-4.3 proposal #660.
            symbol = ifcopenshell.util.element.get_pset(element, "EPset_AnnotationSurveyArea", "PointType")
        return symbol

    @classmethod
    def get_newline_at(cls, element: ifcopenshell.entity_instance) -> Union[int, 0]:
        newline_at = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Newline_At")
        return newline_at

    @classmethod
    def has_linework(cls, drawing: ifcopenshell.entity_instance) -> bool:
        return ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {}).get("HasLinework", False)

    @classmethod
    def has_annotation(cls, drawing: ifcopenshell.entity_instance) -> bool:
        return ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {}).get("HasAnnotation", False)

    @classmethod
    def get_drawing_elements(
        cls, drawing: ifcopenshell.entity_instance, ifc_file: Optional[ifcopenshell.file] = None
    ) -> set[ifcopenshell.entity_instance]:
        """returns a set of elements that are included in the drawing"""
        param_was_none = ifc_file is None
        if param_was_none:
            ifc_file = tool.Ifc.get()
        pset = ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {})
        include = pset.get("Include", None)

        # Only the active IFC file has Blender objects we can test against the
        # camera's view frustum, which lets us drop elements - including those
        # picked by an Include filter - that fall outside the drawing boundary.
        camera_view_elements = None
        if (param_was_none or include) and ifc_file is tool.Ifc.get():
            camera_view_elements = cls.get_elements_in_camera_view(tool.Ifc.get_object(drawing), bpy.data.objects)

        if include:
            try:
                data = json.loads(include)
                if isinstance(data, dict) and "filter_structure" in data:
                    elements = tool.Search.execute_filter_groups_from_json(data, ifc_file)
                elif isinstance(data, dict) and "query" in data:
                    elements = ifcopenshell.util.selector.filter_elements(ifc_file, data["query"])
                else:
                    elements = ifcopenshell.util.selector.filter_elements(ifc_file, include)
            except (json.JSONDecodeError, ValueError):
                elements = ifcopenshell.util.selector.filter_elements(ifc_file, include)
            # The Include filter chooses which elements may appear, but they must
            # still fall within the drawing's camera boundary.
            if camera_view_elements is not None:
                elements &= camera_view_elements
        else:
            if param_was_none:
                elements = camera_view_elements
            else:
                # This can probably be smarter
                elements = set(ifc_file.by_type("IfcElement"))
            if ifc_file.schema == "IFC2X3":
                base_elements = set(ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcSpatialStructureElement"))
            else:
                base_elements = set(ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcSpatialElement"))
            elements = {e for e in (elements & base_elements) if e.is_a() != "IfcSpace"}

        updated_set = set()
        for i in elements:
            # exclude annotations to avoid including annotations from other drawings
            if not i.is_a("IfcAnnotation"):
                updated_set.add(i)
                # add aggregate too, if element is host by one
                if hasattr(i, "Decomposes") and (decomposes := i.Decomposes):
                    aggregate = decomposes[0].RelatingObject
                    # remove IfcProject for class iterator. See https://github.com/IfcOpenShell/IfcOpenShell/issues/4361#issuecomment-2081223615
                    if aggregate.is_a("IfcProduct"):
                        updated_set.add(aggregate)
        elements = updated_set

        # add annotations from the current drawing
        annotations = tool.Drawing.get_group_elements(tool.Drawing.get_drawing_group(drawing))
        elements.update(annotations)

        exclude = pset.get("Exclude", None)
        if exclude:
            try:
                data = json.loads(exclude)
                if isinstance(data, dict) and "filter_structure" in data:
                    exclude_elements = tool.Search.execute_filter_groups_from_json(data, ifc_file)
                    elements -= exclude_elements
                elif isinstance(data, dict) and "query" in data:
                    elements -= ifcopenshell.util.selector.filter_elements(ifc_file, data["query"])
                else:
                    elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
            except (json.JSONDecodeError, ValueError):
                elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
                elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
        elements -= set(ifc_file.by_type("IfcOpeningElement"))
        return elements

    @classmethod
    def get_drawing_spaces(cls, drawing: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        pset = ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {})
        elements = cls.get_elements_in_camera_view(
            tool.Ifc.get_object(drawing), [tool.Ifc.get_object(e) for e in ifc_file.by_type("IfcSpace")]
        )
        # NOTE: EPset_Drawing.Include is not used to avoid adding other elements besides spaces
        exclude = pset.get("Exclude", None)
        if exclude:
            try:
                data = json.loads(exclude)
                if isinstance(data, dict) and "filter_structure" in data:
                    exclude_elements = tool.Search.execute_filter_groups_from_json(data, ifc_file)
                    elements -= exclude_elements
                elif isinstance(data, dict) and "query" in data:
                    elements -= ifcopenshell.util.selector.filter_elements(ifc_file, data["query"])
                else:
                    elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
            except (json.JSONDecodeError, ValueError):
                elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
                elements -= ifcopenshell.util.selector.filter_elements(ifc_file, exclude)
        return elements

    @classmethod
    def get_annotation_element(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def get_drawing_reference(cls, drawing: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for rel in drawing.HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument"):
                return rel.RelatingDocument

    @classmethod
    def get_reference_document(
        cls, reference: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        # TODO: migrate to document.get_reference_document.
        return tool.Document.get_reference_document(reference)

    @classmethod
    def select_assigned_product(cls, context: bpy.types.Context) -> None:
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        product = cls.get_assigned_product(element)
        if product:
            product_obj = tool.Ifc.get_object(product)
            product_obj.select_set(True)
            context.view_layer.objects.active = product_obj

    @classmethod
    def is_drawing_active(cls) -> bool:
        camera = bpy.context.scene.camera
        if not (camera is not None and camera.type == "CAMERA" and tool.Blender.get_ifc_definition_id(camera)):
            return False
        # A VIEW_3D area is meaningless (and unobtainable) in background
        # mode, but isn't otherwise required to generate a drawing.
        if bpy.app.background:
            return True
        return tool.Blender.get_view3d_area() is not None

    @classmethod
    def is_camera_orthographic(cls) -> bool:
        camera = bpy.context.scene.camera
        return True if (camera and camera.data.type == "ORTHO") else False

    @classmethod
    def is_active_drawing(cls, drawing: ifcopenshell.entity_instance) -> bool:
        props = tool.Drawing.get_document_props()
        return drawing.id() == props.active_drawing_id

    @classmethod
    def run_drawing_activate_model(cls) -> None:
        bpy.ops.bim.activate_model()

    @classmethod
    def isolate_camera_collection(cls, camera: bpy.types.Object) -> None:
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        drawing_collections = []
        camera_collection = tool.Blender.get_object_bim_props(camera).collection
        for drawing in drawings:
            if not (drawing_obj := tool.Ifc.get_object(drawing)):
                continue
            oprops = tool.Blender.get_object_bim_props(drawing_obj)
            if not (drawing_collection := oprops.collection):
                continue
            if drawing_obj == camera:
                drawing_collection.hide_render = False
            else:
                drawing_collection.hide_render = True

        project = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = tool.Blender.get_object_bim_props(project).collection
        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection == project_collection:
                for layer_collection2 in layer_collection.children:
                    if layer_collection2.collection in drawing_collections:
                        layer_collection2.hide_viewport = True
                    elif layer_collection2.collection == camera_collection:
                        layer_collection2.hide_viewport = False

    @classmethod
    def get_drawing_context_filters(cls, target_view: str) -> list[tuple[str, str, str]]:
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            return [
                ("Plan", "Body", target_view),
                ("Plan", "Body", "MODEL_VIEW"),
                ("Plan", "Facetation", target_view),
                ("Plan", "Facetation", "MODEL_VIEW"),
                ("Model", "Body", target_view),
                ("Model", "Body", "MODEL_VIEW"),
                ("Model", "Facetation", target_view),
                ("Model", "Facetation", "MODEL_VIEW"),
                ("Plan", "Annotation", target_view),
                ("Plan", "Annotation", "MODEL_VIEW"),
                ("Model", "Annotation", target_view),
                ("Model", "Annotation", "MODEL_VIEW"),
            ]
        else:
            return [
                ("Model", "Body", target_view),
                ("Model", "Body", "MODEL_VIEW"),
                ("Model", "Facetation", target_view),
                ("Model", "Facetation", "MODEL_VIEW"),
                ("Model", "Annotation", target_view),
                ("Model", "Annotation", "MODEL_VIEW"),
            ]

    @classmethod
    def get_drawing_subcontexts(cls, target_view: str) -> list[tuple[str, str, str]]:
        context_filters = cls.get_drawing_context_filters(target_view)
        subcontexts = []

        for context_filter in context_filters:
            subcontext = ifcopenshell.util.representation.get_context(tool.Ifc.get(), *context_filter)
            if subcontext:
                subcontexts.append(context_filter)

        return subcontexts

    @classmethod
    def get_active_drawing_subcontexts(cls) -> list[tuple[str, str, str]] | None:
        props = cls.get_document_props()
        target_view = props.get_active_target_view()
        if not target_view:
            return None

        return cls.get_drawing_subcontexts(target_view)

    @classmethod
    def activate_drawing(cls, camera: bpy.types.Object) -> None:
        # Sync viewport objects visibility with selectors from EPset_Drawing/Include and /Exclude
        drawing = tool.Ifc.get_entity(camera)
        assert drawing and isinstance(camera.data, bpy.types.Camera)
        cls.import_annotations_in_group(cls.get_drawing_group(drawing))

        filtered_elements = cls.get_drawing_elements(drawing) | cls.get_drawing_spaces(drawing)
        filtered_elements.add(drawing)

        target_view = cls.get_drawing_target_view(drawing)
        subcontexts = cls.get_drawing_subcontexts(target_view)

        # Switch representations
        for element in filtered_elements:
            obj = tool.Ifc.get_object(element)
            if not obj:
                continue
            current_representation = tool.Geometry.get_active_representation(obj)
            if current_representation:
                subcontext = current_representation.ContextOfItems
                current_representation_subcontext = tool.Geometry.get_subcontext_parameters(subcontext)

            has_context = False
            for subcontext in subcontexts:
                # prioritize already active representation if it matches the subcontext
                # (element could have multiple representations in the same subcontext)
                if current_representation and subcontext == current_representation_subcontext:
                    has_context = True
                    break
                priority_representation = ifcopenshell.util.representation.get_representation(element, *subcontext)
                if priority_representation:
                    bonsai.core.geometry.switch_representation(
                        tool.Ifc,
                        tool.Geometry,
                        obj=obj,
                        representation=priority_representation,
                    )
                    has_context = True
                    break

        linked_handles: set[bpy.types.Object] = set()
        for link in tool.Project.get_project_props().get_loaded_links_for_drawings():
            try:
                handle = tool.Project.get_link_empty_handle(link)
            except Exception:
                continue
            if handle:
                linked_handles.add(handle)

        visible_objects = []
        for obj in bpy.context.view_layer.objects:
            if element := tool.Ifc.get_entity(obj):
                if element in filtered_elements or obj in linked_handles:
                    visible_objects.append(obj)
            else:
                if obj.hide_get() is False:
                    visible_objects.append(obj)
        tool.Blender.isolate_objects(visible_objects)

        cls.import_camera_props(drawing, camera.data)

    @classmethod
    def get_elements_in_camera_view(
        cls, camera: bpy.types.Object, objs: list[bpy.types.Object]
    ) -> set[ifcopenshell.entity_instance]:
        props = tool.Drawing.get_camera_props(camera)
        x = props.width
        y = props.height

        camera_inverse_matrix = camera.matrix_world.inverted()
        return set(
            [
                tool.Ifc.get_entity(o)
                for o in objs
                if o
                and cls.is_in_camera_view(o, camera_inverse_matrix, x, y, camera.data.clip_start, camera.data.clip_end)
                and tool.Ifc.get_entity(o)
            ]
        )

    @classmethod
    def is_in_camera_view(
        cls,
        obj: bpy.types.Object,
        camera_inverse_matrix: Matrix,
        x: float,
        y: float,
        clip_start: float,
        clip_end: float,
    ) -> bool:
        local_bbox = [camera_inverse_matrix @ obj.matrix_world @ Vector(v) for v in obj.bound_box]
        local_x = [v.x for v in local_bbox]
        local_y = [v.y for v in local_bbox]
        local_z = [v.z for v in local_bbox]
        aabb1_min = (-x / 2, -y / 2, -clip_end)
        aabb1_max = (x / 2, y / 2, -clip_start)
        aabb2_min = (min(local_x), min(local_y), min(local_z))
        aabb2_max = (max(local_x), max(local_y), max(local_z))
        for i in range(3):
            if aabb1_max[i] < aabb2_min[i] or aabb1_min[i] > aabb2_max[i]:
                return False
        return True

    @classmethod
    def is_intersecting_camera(cls, obj: bpy.types.Object, camera: bpy.types.Object) -> bool:
        # Based on separating axis theorem
        plane_co = camera.matrix_world.translation
        plane_no = camera.matrix_world.col[2].xyz
        return cls.is_intersecting_plane(obj, plane_co, plane_no)

    @classmethod
    def is_intersecting_plane(cls, obj: bpy.types.Object, plane_co: Vector, plane_no: Vector) -> bool:
        # Broadphase check using the bounding box
        bounding_box_world_coords = [obj.matrix_world @ Vector(coord) for coord in obj.bound_box]
        bounding_box_signed_distances = [plane_no.dot(v - plane_co) for v in bounding_box_world_coords]

        pos_exists_bb = any(d > 0 for d in bounding_box_signed_distances)
        neg_exists_bb = any(d < 0 for d in bounding_box_signed_distances)

        if not (pos_exists_bb and neg_exists_bb):
            return False

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Transform the vertices to world space
        mesh_mat = obj.matrix_world
        bm.transform(mesh_mat)

        # Calculate the signed distances of all vertices from the plane
        signed_distances = [plane_no.dot(v.co - plane_co) for v in bm.verts]

        bm.free()

        # Check for intersection
        pos_exists = any(d > 0 for d in signed_distances)
        neg_exists = any(d < 0 for d in signed_distances)

        return pos_exists and neg_exists

    @classmethod
    def bisect_mesh(cls, obj: bpy.types.Object, camera: bpy.types.Object) -> tuple[list[Vector], list[list[int]]]:
        # TODO consolidate with other bisect functions
        camera_matrix = obj.matrix_world.inverted() @ camera.matrix_world
        plane_co = camera_matrix.translation
        plane_no = camera_matrix.col[2].xyz

        # Bisect verts are offset by the clip (with 5mm tolerance) to ensure it is visible in the viewport.
        global_offset = camera.matrix_world.col[2].xyz * (-camera.data.clip_start - 0.005)

        return cls.bisect_mesh_with_plane(obj, plane_co, plane_no, global_offset=global_offset)

    @classmethod
    def bisect_bmesh(cls, obj, bm, geom, camera):
        # TODO consolidate with other bisect functions
        camera_matrix = obj.matrix_world.inverted() @ camera.matrix_world
        plane_co = camera_matrix.translation
        plane_no = camera_matrix.col[2].xyz

        global_offset = camera.matrix_world.col[2].xyz * -camera.data.clip_start

        # Run the bisect operation
        results = bmesh.ops.bisect_plane(bm, geom=geom, dist=0.0001, plane_co=plane_co, plane_no=plane_no)

        vert_map = {}
        verts = []
        edges = []
        i = 0
        for geom in results["geom_cut"]:
            if isinstance(geom, bmesh.types.BMVert):
                verts.append(tuple((obj.matrix_world @ geom.co) + global_offset))
                vert_map[geom.index] = i
                i += 1
            else:
                # It seems as though edges always appear after verts
                edges.append([vert_map[v.index] for v in geom.verts])

        return verts, edges

    @classmethod
    def bisect_mesh_with_plane(
        cls, obj: bpy.types.Object, plane_co: Vector, plane_no: Vector, global_offset: Optional[Vector] = None
    ) -> tuple[list[Vector], list[list[int]]]:
        # TODO consolidate with other bisect functions
        if global_offset is None:
            global_offset = Vector()

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Run the bisect operation
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        results = bmesh.ops.bisect_plane(bm, geom=geom, dist=0.0001, plane_co=plane_co, plane_no=plane_no)

        vert_map: dict[int, int] = {}
        verts: list[Vector] = []
        edges: list[list[int]] = []
        i = 0
        for geom in results["geom_cut"]:
            if isinstance(geom, bmesh.types.BMVert):
                verts.append(tuple((obj.matrix_world @ geom.co) + global_offset))
                vert_map[geom.index] = i
                i += 1
            else:
                # It seems as though edges always appear after verts
                edges.append([vert_map[v.index] for v in geom.verts])

        bm.free()

        return verts, edges

    @classmethod
    def get_extrusion_vector(cls, wall):
        if body := ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW"):
            for item in ifcopenshell.util.representation.resolve_representation(body).Items:
                while item.is_a("IfcBooleanResult"):
                    item = item.FirstOperand
                if item.is_a("IfcExtrudedAreaSolid"):
                    return Vector(item.ExtrudedDirection.DirectionRatios)
        return Vector([0.0, 0.0, 1.0])

    @classmethod
    def get_scale_ratio(cls, scale: str) -> float:
        numerator, denominator = scale.split("/")
        return float(numerator) / float(denominator)

    @classmethod
    def get_diagram_scale(cls, camera: Union[bpy.types.Object, bpy.types.Camera]) -> dict[str, str]:
        props = cls.get_camera_props(camera)
        scale = props.diagram_scale
        if scale != "CUSTOM":
            human_scale, scale = scale.split("|")
            return {"HumanScale": human_scale, "Scale": scale}
        numerator_string = props.custom_scale_numerator
        denominator_string = props.custom_scale_denominator
        numerator = tool.Drawing.convert_scale_string(numerator_string)
        denominator = tool.Drawing.convert_scale_string(denominator_string)
        if not numerator or not denominator:
            return
        scale = str(Fraction(numerator / denominator).limit_denominator(1000))  # Any ratio >1000 is stupid.
        if "'" in scale or '"' in scale:
            human_separator = "="  # Imperial scales use "=", like 1" = 1' - 0"
            # If for some crazy reason we mix metric and imperial, assume metric is SI units, like 1m = 1'
            if "'" not in numerator_string and '"' not in numerator_string:
                numerator_string += "m"
            if "'" not in denominator_string and '"' not in denominator_string:
                denominator_string += "m"
        else:
            human_separator = ":"  # Metric scales use ":", like 1:100
        human_scale = f"{numerator_string}{human_separator}{denominator_string}"
        return {"HumanScale": human_scale, "Scale": scale}

    @classmethod
    def convert_scale_string(cls, value: str) -> float:
        try:
            return float(value)
        except:
            pass  # Perhaps it's imperial?
        l = lark.Lark("""start: feet? "-"? inches?
                    feet: NUMBER? "-"? fraction? "'"
                    inches: NUMBER? "-"? fraction? "\\""
                    fraction: NUMBER "/" NUMBER
                    %import common.NUMBER
                    %import common.WS
                    %ignore WS // Disregard spaces in text
                 """)

        try:
            start = l.parse(value)
        except:
            return 0
        result = 0
        for dimension in start.children:
            factor = 12 if dimension.data == "feet" else 1
            for child in dimension.children:
                if getattr(child, "data", None) == "fraction":
                    result += (float(child.children[0]) / float(child.children[1])) * factor
                else:
                    result += float(child) * factor
        return result * 0.0254

    @classmethod
    def extend_line(cls, start: Vector, end: Vector, distance: float) -> tuple[list[float], list[float]]:
        start = np.array(start)
        end = np.array(end)
        direction = end - start
        offset = distance * (direction / np.linalg.norm(direction))
        return (start - offset).tolist(), (end + offset).tolist()

    @classmethod
    def get_sheet_references(cls, drawing: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        sheet_references: list[ifcopenshell.entity_instance] = []
        drawing_reference = cls.get_drawing_document(drawing)
        for sheet in tool.Ifc.get().by_type("IfcDocumentInformation"):
            if not sheet.Scope == "SHEET":
                continue
            references = cls.get_document_references(sheet)
            for reference in references:
                if reference.Location == drawing_reference.Location:
                    sheet_references.append(reference)
                    break
        return sheet_references

    @classmethod
    def get_camera_matrix(cls, camera: bpy.types.Object) -> Matrix:
        matrix_world = camera.matrix_world.copy().normalized()
        location, rotation, scale = matrix_world.decompose()
        if scale.x < 0 or scale.y < 0 or scale.z < 0:
            # RCPs may be inversely scaled. We discard the scale and rotate the Z to compensate.
            rotate180z = mathutils.Matrix.Rotation(math.radians(180.0), 4, "Z")
            return mathutils.Matrix.Translation(location) @ rotation.to_matrix().to_4x4() @ rotate180z
        return mathutils.Matrix.Translation(location) @ rotation.to_matrix().to_4x4()

    @classmethod
    def convert_svg_to_dxf(cls, svg_filepath: Path, dxf_filepath: Path) -> None:
        import xml.etree.ElementTree as ET

        import ezdxf

        SVG = "{http://www.w3.org/2000/svg}"
        IFC = "{http://www.ifcopenshell.org/ns}"

        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        svg = ET.parse(svg_filepath).getroot()

        def finalize_dxf():
            doc.saveas(dxf_filepath)

        drawing = svg.findall(f"{SVG}g[@{IFC}name]")
        if not drawing:
            finalize_dxf()
            return
        drawing = drawing[0]

        NUMBER = r"-?\d+\.?\d+"
        COORD = rf"{NUMBER},{NUMBER}"
        POLYLINE_PATTERN = rf"M{COORD} (?:L{COORD} ?)+Z? ?"
        MULTI_POLYLINE_PATTERN = rf"^({POLYLINE_PATTERN})+$"

        for element_g in drawing.findall(f"{SVG}g"):
            paths = element_g.findall(f"{SVG}path")

            for path in paths:
                # For some reason `<path/>` without "d" attribute can occur too. See #6871.
                # It's unclear whether this issue is still present with the updated ifcopenshell core,
                # but adding this fix for now. Could be reveted later.
                if "d" not in path.attrib:
                    continue
                path = path.attrib["d"]

                if not re.match(MULTI_POLYLINE_PATTERN, path):
                    # print(f'Path "{path}" doesn\'t match expected pattern {MULTI_POLYLINE_PATTERN}')
                    continue

                for polyline_path in re.findall(POLYLINE_PATTERN, path):
                    points = re.findall(rf"{NUMBER}", polyline_path)
                    points = [float(p) for p in points]
                    POINT_SIZE = 2

                    grouped_points = []
                    for i in range(0, len(points), POINT_SIZE):
                        point = points[i : i + POINT_SIZE]
                        point[1] *= -1
                        grouped_points.append(point)
                    points = grouped_points

                    # Z marks closed polylines
                    is_closed_polyline = polyline_path.rstrip().endswith("Z")
                    if is_closed_polyline or len(points) > 2:
                        msp.add_lwpolyline(points, close=is_closed_polyline)
                    else:  # LINE
                        msp.add_line(*points)

        finalize_dxf()

    @classmethod
    def remove_drawing_from_sheet(cls, reference: ifcopenshell.entity_instance) -> None:
        import bonsai.bim.module.drawing.sheeter as sheeter

        sheet = tool.Drawing.get_reference_document(reference)

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.remove_drawing(reference, sheet)

        ifcopenshell.api.document.remove_reference(tool.Ifc.get(), reference=reference)

        tool.Drawing.import_sheets()

    @classmethod
    def hide_all_drawing_collections(cls) -> None:
        for element in tool.Ifc.get().by_type("IfcAnnotation"):
            if element.ObjectType == "DRAWING" and (obj := tool.Ifc.get_object(element)):
                tool.Blender.get_layer_collection(obj.users_collection[0]).hide_viewport = True

    @classmethod
    def clear_annotation_relationships(cls, drawing: ifcopenshell.entity_instance) -> None:
        for rel in drawing.ReferencedBy:
            tool.Ifc.get().remove(rel)
