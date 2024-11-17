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

import os
import re
import collections
import collections.abc
import bpy
import math
import json
import lark
import bmesh
import shutil
import logging
import shapely
import platform
import mathutils
import subprocess
import numpy as np
import bonsai.core.tool
import bonsai.core.geometry
import bonsai.tool as tool
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.util.representation
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.util.shape
import bonsai.bim.helper
import bonsai.bim.import_ifc
import bonsai.core.root
from shapely.ops import unary_union
from lxml import etree
from mathutils import Vector, Matrix
from fractions import Fraction
from typing import Optional, Union, Iterable, Any, Literal
from pathlib import Path


class Drawing(bonsai.core.tool.Drawing):
    ANNOTATION_DATA_TYPE = Literal["empty", "curve", "mesh"]
    DOCUMENT_TYPE = Literal["SCHEDULE", "REFERENCE"]

    # ObjectType: annotation_name, description, icon, data_type
    # fmt: off
    ANNOTATION_TYPES_DATA = {
        "DIMENSION":     ("Dimension",        "Add dimensions annotation.\nMeasurement values can be hidden through ShowDescriptionOnly property\nof BBIM_Dimension property set", "FIXED_SIZE", "curve"),
        "ANGLE":         ("Angle",            "", "DRIVER_ROTATIONAL_DIFFERENCE", "curve"),
        "RADIUS":        ("Radius",           "", "FORWARD", "curve"),
        "DIAMETER":      ("Diameter",         "Add diameter annotation.\nMeasurement values can be hidden through ShowDescriptionOnly property\nof BBIM_Dimension property set", "ARROW_LEFTRIGHT", "curve"),
        "TEXT":          ("Text",             "", "SMALL_CAPS", "empty"),
        "TEXT_LEADER":   ("Leader",           "", "TRACKING_BACKWARDS", "curve"),
        "STAIR_ARROW":   ("Stair Arrow",      "Add stair arrow annotation.\nIf you have IfcStairFlight object selected, it will be used as a reference for the annotation", "SCREEN_BACK", "curve"),
        "PLAN_LEVEL":    ("Level (Plan)",     "", "SORTBYEXT", "curve"),
        "SECTION_LEVEL": ("Level (Section)",  "", "TRIA_DOWN", "curve"),
        "BREAKLINE":     ("Breakline",        "", "FCURVE", "mesh"),
        "SYMBOL":        ("Symbol",           "", "KEYFRAME", "empty"),
        "MULTI_SYMBOL":  ("Multi-Symbol",     "", "OUTLINER_DATA_POINTCLOUD", "mesh"),
        "LINEWORK":      ("Line",             "", "SNAP_MIDPOINT", "mesh"),
        "BATTING":       ("Batting",          "Add batting annotation.\nThickness could be changed through Thickness property of BBIM_Batting property set", "FORCE_FORCE", "mesh"),
        "REVISION_CLOUD":("Revision Cloud",   "Add revision cloud", "VOLUME_DATA", "mesh"),
        "FILL_AREA":     ("Fill Area",        "", "NODE_TEXTURE", "mesh"),
        "FALL":          ("Fall",             "", "SORT_ASC", "curve"),
        "IMAGE":         ("Image",            "Add reference image attached to the drawing", "TEXTURE", "mesh"),
    }
    # fmt: on

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
        return cls.ANNOTATION_TYPES_DATA[object_type][3]

    @classmethod
    def create_annotation_object(cls, drawing: ifcopenshell.entity_instance, object_type: str) -> bpy.types.Object:
        import bonsai.bim.module.drawing.annotation as annotation

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
        elif object_type != "TEXT":
            obj = annotation.Annotator.add_line_to_annotation(obj)

        return obj

    @classmethod
    def ensure_annotation_in_drawing_plane(
        cls, obj: bpy.types.Object, camera: Optional[bpy.types.Object] = None
    ) -> None:
        """Make sure annotation object is going to be visible in the camera view"""

        def get_camera_from_annotation_object(obj):
            entity = tool.Ifc.get_entity(obj)
            if not entity:
                return
            for rel in entity.HasAssignments:
                if rel.is_a("IfcRelAssignsToGroup"):
                    for e in rel.RelatedObjects:
                        if e.ObjectType == "DRAWING":
                            return tool.Ifc.get_object(e)

        if not camera:
            camera = get_camera_from_annotation_object(obj) or bpy.context.scene.camera

        current_pos = camera.matrix_world.inverted() @ obj.location
        current_pos.z = -camera.data.clip_start - 0.05
        current_pos = camera.matrix_world @ current_pos
        obj.location = current_pos

    ANNOTATION_TYPES_SUPPORT_SETUP = ("STAIR_ARROW", "TEXT", "REVISION_CLOUD", "FILL_AREA")

    @classmethod
    def setup_annotation_object(
        cls, obj: bpy.types.Object, object_type: str, related_object: Optional[bpy.types.Object] = None
    ) -> None:
        """Finish object's adjustments after both object and entity are created"""

        if not related_object:
            related_object = bpy.context.active_object
        related_entity = tool.Ifc.get_entity(related_object)
        if not related_entity:
            return

        obj_entity = tool.Ifc.get_entity(obj)
        assign_product = False

        if object_type == "STAIR_ARROW":
            if related_entity.is_a("IfcStairFlight"):
                stair, arrow = related_object, obj

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
            tool.Ifc.run("drawing.assign_product", relating_product=related_entity, related_object=obj_entity)

        if object_type == "TEXT":
            tool.Drawing.update_text_value(obj)

    @classmethod
    def is_annotation_object_type(
        cls, element: ifcopenshell.entity_instance, object_types: Union[str, list[str]]
    ) -> bool:
        if not isinstance(object_types, collections.abc.Iterable):
            object_types = [object_types]

        element_type = element.is_a()

        if element_type == "IfcAnnotation" and element.ObjectType in object_types:
            return True

        if (
            element_type == "IfcTypeProduct"
            and element.ApplicableOccurrence
            and element.ApplicableOccurrence.startswith("IfcAnnotation/")
        ):
            applicable_object_type = element.ApplicableOccurrence.split("/")[1]
            if applicable_object_type in object_types:
                return True

        return False

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
        cls, name: str, matrix: Matrix, location_hint: Literal["PERSPECTIVE", "ORTHOGRAPHIC"]
    ) -> bpy.types.Object:
        camera = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        camera.location = (0, 0, 1.5)  # The view shall be 1.5m above the origin
        camera.data.show_limits = True
        if location_hint == "PERSPECTIVE":
            camera.data.type = "PERSP"
        else:
            camera.data.type = "ORTHO"
        camera.data.ortho_scale = 50  # The default of 6m is too small
        camera.data.clip_start = 0.002  # 2mm is close to zero but allows any GPU-drawn lines to be visible.
        camera.data.clip_end = 10  # A slightly more reasonable default
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            camera.data.BIMCameraProperties.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            camera.data.BIMCameraProperties.diagram_scale = "1:100|1/100"
        camera.matrix_world = matrix
        return camera

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
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        uri = cls.get_document_uri(document, "LAYOUT")
        sheet_builder.create(uri, titleblock)
        return uri

    @classmethod
    def add_drawings(cls, sheet: ifcopenshell.entity_instance) -> None:
        import bonsai.bim.module.drawing.sheeter as sheeter

        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
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
            ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
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
        bpy.context.scene.DocProperties.is_editing_drawings = False

    @classmethod
    def disable_editing_schedules(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_schedules = False

    @classmethod
    def disable_editing_references(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_references = False

    @classmethod
    def disable_editing_sheets(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_sheets = False

    @classmethod
    def disable_editing_text(cls, obj: bpy.types.Object) -> None:
        obj.BIMTextProperties.is_editing = False

    @classmethod
    def disable_editing_assigned_product(cls, obj: bpy.types.Object) -> None:
        obj.BIMAssignedProductProperties.is_editing_product = False

    @classmethod
    def enable_editing(cls, obj: bpy.types.Object) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.data:
            bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def enable_editing_drawings(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_drawings = True

    @classmethod
    def enable_editing_schedules(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_schedules = True

    @classmethod
    def enable_editing_references(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_references = True

    @classmethod
    def enable_editing_sheets(cls) -> None:
        bpy.context.scene.DocProperties.is_editing_sheets = True

    @classmethod
    def enable_editing_text(cls, obj: bpy.types.Object) -> None:
        obj.BIMTextProperties.is_editing = True

    @classmethod
    def enable_editing_assigned_product(cls, obj: bpy.types.Object) -> None:
        obj.BIMAssignedProductProperties.is_editing_product = True

    @classmethod
    def ensure_unique_drawing_name(cls, name: str) -> str:
        names = [e.Name for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        while name in names:
            name += "-X"
        return name

    @classmethod
    def ensure_unique_identification(cls, identification: str) -> str:
        attr = "DocumentId" if tool.Ifc.get_schema() == "IFC2X3" else "Identification"
        ids = [getattr(d, attr) for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
        while identification in ids:
            identification += "-X"
        return identification

    @classmethod
    def export_text_literal_attributes(cls, obj: bpy.types.Object) -> list[dict[str, Any]]:
        literals = []
        for literal_props in obj.BIMTextProperties.literals:
            literal_data = bonsai.bim.helper.export_attributes(literal_props.attributes)
            literals.append(literal_data)
        return literals

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
        else:
            parent = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model")

        return ifcopenshell.api.run(
            "context.add_context",
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
            return obj.BIMObjectProperties.collection

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
    def generate_drawing_matrix(
        cls, target_view: ifcopenshell.util.representation.TARGET_VIEW, location_hint: str
    ) -> Matrix:
        x, y, z = (0, 0, 0) if location_hint == 0 else bpy.context.scene.cursor.matrix.translation
        if target_view == "PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world.translation.z
                return mathutils.Matrix(((1, 0, 0, x), (0, 1, 0, y), (0, 0, 1, z + 1.6), (0, 0, 0, 1)))
        elif target_view == "REFLECTED_PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world.translation.z
                m = mathutils.Matrix()
                m[2][2] = -1
                m.translation = (x, y, z + 1.6)
                return m
            return mathutils.Matrix(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
        elif target_view == "ELEVATION_VIEW":
            if location_hint == "NORTH":
                return mathutils.Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "SOUTH":
                return mathutils.Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "EAST":
                return mathutils.Matrix(((0, 0, 1, x), (1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "WEST":
                return mathutils.Matrix(((0, 0, -1, x), (-1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
        elif target_view == "SECTION_VIEW":
            if location_hint == "NORTH":
                return mathutils.Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "SOUTH":
                return mathutils.Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "EAST":
                return mathutils.Matrix(((0, 0, -1, x), (-1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "WEST":
                return mathutils.Matrix(((0, 0, 1, x), (1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
        elif target_view == "MODEL_VIEW":
            return mathutils.Matrix(((1, 0, 0, x), (0, 1, 0, y), (0, 0, 1, z), (0, 0, 0, 1)))
        return mathutils.Matrix()

    @classmethod
    def generate_sheet_identification(cls) -> str:
        number = len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"])
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
        return bpy.context.scene.DocProperties.is_editing_sheets

    @classmethod
    def remove_literal_from_annotation(cls, obj: bpy.types.Object, literal: ifcopenshell.entity_instance) -> None:
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        rep = cls.get_annotation_representation(element)
        if not rep:
            return

        ifc_file = tool.Ifc.get()
        rep.Items = [l for l in rep.Items if l != literal]
        ifcopenshell.util.element.remove_deep2(ifc_file, literal)

    @classmethod
    def synchronise_ifc_and_text_attributes(cls, obj: bpy.types.Object) -> None:
        literals = cls.get_text_literal(obj, return_list=True)
        literals_attributes = cls.export_text_literal_attributes(obj)
        defined_ifc_ids = [l.ifc_definition_id for l in obj.BIMTextProperties.literals]
        ifc_file = tool.Ifc.get()

        for ifc_definition_id, attributes in zip(defined_ifc_ids, literals_attributes):
            # making sure all literals from text edit exist in ifc
            if ifc_definition_id == 0:
                literal = cls.add_literal_to_annotation(obj, **attributes)
            else:
                literal = ifc_file.by_id(ifc_definition_id)
                tool.Ifc.run(
                    "drawing.edit_text_literal",
                    text_literal=literal,
                    attributes=attributes,
                )

        # remove from ifc the literals that were removed during the edit
        for literal in literals:
            if literal.id() not in defined_ifc_ids:
                cls.remove_literal_from_annotation(obj, literal)

    @classmethod
    def add_literal_to_annotation(
        cls, obj: bpy.types.Object, Literal: str = "Literal", Path: str = "RIGHT", BoxAlignment: str = "bottom-left"
    ) -> Union[ifcopenshell.entity_instance, None]:
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        rep = cls.get_annotation_representation(element)

        if not rep:
            return

        ifc_file = tool.Ifc.get()

        origin = ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            ifc_file.createIfcDirection((0.0, 0.0, 1.0)),
            ifc_file.createIfcDirection((1.0, 0.0, 0.0)),
        )

        ifc_literal = ifc_file.createIfcTextLiteralWithExtent(
            Literal, origin, Path, ifc_file.createIfcPlanarExtent(1000, 1000), BoxAlignment
        )

        rep.Items = rep.Items + (ifc_literal,)
        return ifc_literal

    @classmethod
    def get_assigned_product(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def import_annotations_in_group(cls, group: ifcopenshell.entity_instance) -> None:
        elements = set(
            [e for e in cls.get_group_elements(group) if e.is_a("IfcAnnotation") and e.ObjectType != "DRAWING"]
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
        for obj in ifc_importer.added_data.values():
            tool.Collector.assign(obj)

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

        mat = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
        obj.matrix_world = mat

        if cls.get_drawing_target_view(drawing) == "REFLECTED_PLAN_VIEW":
            obj.matrix_world[1][1] *= -1

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
        mat = Matrix(ifcopenshell.util.shape.get_shape_matrix(shape))
        obj.matrix_world = mat
        if cls.get_drawing_target_view(drawing) == "REFLECTED_PLAN_VIEW":
            obj.matrix_world[1][1] *= -1
        return obj

    @classmethod
    def import_camera_props(cls, drawing: ifcopenshell.entity_instance, camera: bpy.types.Camera) -> None:
        from bonsai.bim.module.drawing.prop import get_diagram_scales

        # Temporarily clear the definition id to prevent prop update callbacks to IFC.
        camera_props = camera.BIMCameraProperties
        update_props = camera_props.update_props
        camera_props.update_props = False

        camera.BIMCameraProperties.has_underlay = False
        camera.BIMCameraProperties.has_linework = True
        camera.BIMCameraProperties.has_annotation = True
        camera.BIMCameraProperties.target_view = "PLAN_VIEW"
        camera.BIMCameraProperties.is_nts = False

        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        if pset:
            if "TargetView" in pset:
                camera.BIMCameraProperties.target_view = pset["TargetView"]
            if "Scale" in pset:
                valid_scales = [
                    i[0] for i in get_diagram_scales(None, bpy.context) if pset["Scale"] == i[0].split("|")[-1]
                ]
                if valid_scales:
                    camera.BIMCameraProperties.diagram_scale = valid_scales[0]
                else:
                    camera.BIMCameraProperties.diagram_scale = "CUSTOM"
                    if ":" in pset["HumanScale"]:
                        numerator, denominator = pset["HumanScale"].split(":")
                    else:
                        numerator, denominator = pset["HumanScale"].split("=")
                    camera.BIMCameraProperties.custom_scale_numerator = numerator
                    camera.BIMCameraProperties.custom_scale_denominator = denominator
            if "HasUnderlay" in pset:
                camera.BIMCameraProperties.has_underlay = bool(pset["HasUnderlay"])
            if "HasLinework" in pset:
                camera.BIMCameraProperties.has_linework = bool(pset["HasLinework"])
            if "HasAnnotation" in pset:
                camera.BIMCameraProperties.has_annotation = bool(pset["HasAnnotation"])
            if "IsNTS" in pset:
                camera.BIMCameraProperties.is_nts = bool(pset["IsNTS"])

        camera_props.update_props = update_props

    @classmethod
    def import_drawings(cls) -> None:
        props = bpy.context.scene.DocProperties
        expanded_target_views = {d.target_view for d in props.drawings if d.is_expanded}
        if not hasattr(cls, "drawing_selected_states"):
            cls.drawing_selected_states = {}
        cls.drawing_selected_states.update({d.ifc_definition_id: d.is_selected for d in props.drawings if d.is_drawing})
        props.drawings.clear()
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        grouped_drawings = {
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
        dprops = bpy.context.scene.DocProperties
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
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = schedule.DocumentId
            else:
                new.identification = schedule.Identification

    @classmethod
    def import_sheets(cls) -> None:
        props = bpy.context.scene.DocProperties
        expanded_sheets = {s.ifc_definition_id for s in props.sheets if s.is_expanded}
        if not hasattr(cls, "sheet_selected_states"):
            cls.sheet_selected_states = {}
        cls.sheet_selected_states.update({s.ifc_definition_id: s.is_selected for s in props.sheets if s.is_sheet})
        props.sheets.clear()
        sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
        for sheet in sorted(sheets, key=lambda s: getattr(s, "Identification", getattr(s, "DocumentId", None))):
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

                if tool.Ifc.get_schema() == "IFC2X3":
                    new.identification = reference.ItemReference or ""
                else:
                    new.identification = reference.Identification or ""

                new.name = os.path.basename(reference.Location)
                new.reference_type = reference_description

    @classmethod
    def get_active_sheet(cls, context: bpy.types.Context) -> bpy.types.PropertyGroup:
        props = context.scene.DocProperties
        return next(s for s in props.sheets[: props.active_sheet_index + 1][::-1] if s.is_sheet)

    @classmethod
    def get_active_drawing_item(cls) -> Union[bpy.types.PropertyGroup, None]:
        props = bpy.context.scene.DocProperties
        drawing_index = props.active_drawing_index
        if len(props.drawings) > drawing_index >= 0:
            item = props.drawings[drawing_index]
            if item.is_drawing:
                return item

    @classmethod
    def import_text_attributes(cls, obj: bpy.types.Object) -> None:
        from bonsai.bim.module.drawing.prop import BOX_ALIGNMENT_POSITIONS

        props = obj.BIMTextProperties
        props.literals.clear()

        for ifc_literal in cls.get_text_literal(obj, return_list=True):
            literal_props = props.literals.add()
            bonsai.bim.helper.import_attributes2(ifc_literal, literal_props.attributes)

            box_alignment_mask = [False] * 9
            position_string = literal_props.attributes["BoxAlignment"].string_value
            box_alignment_mask[BOX_ALIGNMENT_POSITIONS.index(position_string)] = True
            literal_props.box_alignment = box_alignment_mask
            literal_props.ifc_definition_id = ifc_literal.id()

        from bonsai.bim.module.drawing.data import DecoratorData

        text_data = DecoratorData.get_ifc_text_data(obj)
        props.font_size = str(text_data["FontSize"])

    @classmethod
    def import_assigned_product(cls, obj: bpy.types.Object) -> None:
        element = tool.Ifc.get_entity(obj)
        product = cls.get_assigned_product(element)
        if product:
            obj.BIMAssignedProductProperties.relating_product = tool.Ifc.get_object(product)
        else:
            obj.BIMAssignedProductProperties.relating_product = None

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
    def set_drawing_collection_name(
        cls, drawing: ifcopenshell.entity_instance, collection: bpy.types.Collection
    ) -> None:
        collection.name = tool.Loader.get_name(drawing)

    @classmethod
    def set_name(cls, element: ifcopenshell.entity_instance, name: str) -> None:
        element.Name = name

    @classmethod
    def show_decorations(cls) -> None:
        bpy.context.scene.DocProperties.should_draw_decorations = True

    @classmethod
    def update_text_value(cls, obj: bpy.types.Object) -> None:
        props = obj.BIMTextProperties
        literals = cls.get_text_literal(obj, return_list=True)
        cls.import_text_attributes(obj)
        for i, literal in enumerate(literals):
            product = cls.get_assigned_product(tool.Ifc.get_entity(obj)) or tool.Ifc.get_entity(obj)
            props.literals[i].value = cls.replace_text_literal_variables(literal.Literal, product)

    @classmethod
    def update_text_size_pset(cls, obj: bpy.types.Object) -> None:
        """updates pset `EPset_Annotation.Classes` value
        based on current font size from `obj.BIMTextProperties.font_size`
        """
        from bonsai.bim.module.drawing.data import FONT_SIZES

        props = obj.BIMTextProperties
        element = tool.Ifc.get_entity(obj)
        # updating text font size in EPset_Annotation.Classes
        font_size = float(props.font_size)
        font_size_str = next((key for key in FONT_SIZES if FONT_SIZES[key] == font_size), None)
        classes = ifcopenshell.util.element.get_pset(element, "EPset_Annotation", "Classes")
        classes_split = classes.split() if classes else []

        different_font_sizes = [c for c in classes_split if c in FONT_SIZES and c != font_size_str]

        # we do need to change pset value in ifc
        # only if there are different font sizes in classes already
        # or if the current font size is not present in classes
        # (except regular font size because it's default)
        if different_font_sizes or (font_size_str not in classes_split and font_size_str != "regular"):
            classes_split = [c for c in classes_split if c not in FONT_SIZES] + [font_size_str]
            classes = " ".join(classes_split)

            ifc_file = tool.Ifc.get()
            pset = tool.Pset.get_element_pset(element, "EPset_Annotation")
            if not pset:
                pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="EPset_Annotation")
            ifcopenshell.api.run(
                "pset.edit_pset",
                ifc_file,
                pset=pset,
                properties={"Classes": classes},
            )

    @classmethod
    def update_newline_at(cls, obj: bpy.types.Object) -> None:
        props = obj.BIMTextProperties
        element = tool.Ifc.get_entity(obj)
        newline_at = int(props.newline_at)
        ifc_file = tool.Ifc.get()
        pset = tool.Pset.get_element_pset(element, "EPset_Annotation")
        if not pset:
            pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=element, name="EPset_Annotation")
        ifcopenshell.api.run(
            "pset.edit_pset",
            ifc_file,
            pset=pset,
            properties={"Newline_At": newline_at},
        )
    # TODO below this point is highly experimental prototype code with no tests

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
        cls, target_view: ifcopenshell.util.representation.TARGET_VIEW, location_hint: str
    ) -> str:
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW") and location_hint:
            location = tool.Ifc.get().by_id(location_hint)
            if target_view == "REFLECTED_PLAN_VIEW":
                target_view = "RCP_VIEW"
            return (location.Name or "UNNAMED").upper() + " " + target_view.split("_")[0]
        elif target_view in ("SECTION_VIEW", "ELEVATION_VIEW") and location_hint:
            return location_hint + " " + target_view.split("_")[0]
        elif target_view == "MODEL_VIEW" and location_hint:
            return location_hint
        return target_view

    @classmethod
    def get_default_layout_path(cls, identification: str, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        layouts_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "LayoutsDir")
            or bpy.context.scene.DocProperties.layouts_dir
        )
        return os.path.join(layouts_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_sheet_path(cls, identification: str, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        sheets_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "SheetsDir")
            or bpy.context.scene.DocProperties.sheets_dir
        )
        return os.path.join(sheets_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_titleblock_path(cls, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        titleblocks_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "TitleblocksDir")
            or bpy.context.scene.DocProperties.titleblocks_dir
        )
        return os.path.join(titleblocks_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_drawing_path(cls, name: str) -> str:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        drawings_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "DrawingsDir")
            or bpy.context.scene.DocProperties.drawings_dir
        )
        return os.path.join(drawings_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def sanitise_filename(cls, name: str) -> str:
        return "".join(x for x in name if (x.isalnum() or x in "._- "))

    @classmethod
    def get_default_drawing_resource_path(cls, resource: str) -> Union[str, None]:
        project = tool.Ifc.get().by_type("IfcProject")[0]
        resource_path = ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", f"{resource}Path") or getattr(
            bpy.context.scene.DocProperties, f"{resource.lower()}_path"
        )
        if resource_path:
            return resource_path.replace("\\", "/")

    @classmethod
    def get_default_shading_style(cls) -> str:
        dprops = bpy.context.scene.DocProperties
        return dprops.shadingstyle_default

    @classmethod
    def setup_shading_styles_path(cls, resource_path: str) -> None:
        resource_path = tool.Ifc.resolve_uri(resource_path)
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)
        if not os.path.exists(resource_path):
            resource_basename = os.path.basename(resource_path)
            ootb_resource = os.path.join(bpy.context.scene.BIMProperties.data_dir, "assets", resource_basename)
            if os.path.exists(ootb_resource):
                shutil.copy(ootb_resource, resource_path)

    @classmethod
    def get_potential_reference_elements(
        cls, drawing: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        elements = []
        existing_references = cls.get_group_elements(cls.get_drawing_group(drawing))
        for element in tool.Ifc.get().by_type("IfcAnnotation"):
            if element in existing_references or element == drawing:
                continue
            if element.ObjectType == "DRAWING":
                pset = ifcopenshell.util.element.get_psets(element).get("EPset_Drawing", {})
                if pset.get("TargetView", None) in ("SECTION_VIEW", "ELEVATION_VIEW") and pset.get(
                    "GlobalReferencing", False
                ):
                    elements.append(element)
        for element in tool.Ifc.get().by_type("IfcGridAxis"):
            elements.append(element)
        target_view = tool.Drawing.get_drawing_target_view(drawing)
        if target_view in ("SECTION_VIEW", "ELEVATION_VIEW"):
            for element in tool.Ifc.get().by_type("IfcBuildingStorey"):
                elements.append(element)
        return elements

    @classmethod
    def get_drawing_reference_annotation(
        cls, drawing: ifcopenshell.entity_instance, reference_element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, bool, None]:
        if drawing == reference_element:
            return True
        for element in cls.get_group_elements(cls.get_drawing_group(drawing)):
            if element.is_a("IfcAnnotation"):
                for rel in element.HasAssignments:
                    if rel.is_a("IfcRelAssignsToProduct"):
                        if rel.RelatingProduct == reference_element:
                            return element
                        # We cannot associate IfcGridAxis directly, so we establish a convention:
                        # IfcRelAssignsToProduct.RelatingProduct = IfcGrid
                        # IfcRelAssignsToProduct.Name = IfcGridAxis.AxisTag
                        elif reference_element.is_a("IfcGridAxis") and rel.Name == reference_element.AxisTag:
                            return element

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

            def ensure_referenced_drawing_obj_exists(drawing: ifcopenshell.entity_instance):
                obj = tool.Ifc.get_object(drawing)
                if obj is None:
                    obj = cls.import_drawing(drawing)
                    # there is no need for other drawing annotations in that case
                    # but we import them anyway so we won't break that drawing activation
                    cls.import_annotations_in_group(cls.get_drawing_group(drawing))
                    tool.Blender.get_layer_collection(obj.users_collection[0]).hide_viewport = True

            target_view = ifcopenshell.util.element.get_pset(reference_element, "EPset_Drawing", "TargetView")
            if target_view == "ELEVATION_VIEW":
                ensure_referenced_drawing_obj_exists(reference_element)
                return cls.generate_elevation_reference_annotation(drawing, reference_element, context)
            elif target_view == "SECTION_VIEW":
                ensure_referenced_drawing_obj_exists(reference_element)
                return cls.generate_section_reference_annotation(drawing, reference_element, context)

        elif reference_element.is_a("IfcBuildingStorey"):
            return cls.generate_storey_annotation(drawing, reference_element, context)

    @classmethod
    def generate_storey_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        import bonsai.bim.module.drawing.helper as helper

        camera = tool.Ifc.get_object(drawing)
        bounds = helper.ortho_view_frame(camera.data) if camera.data.type == "ORTHO" else None
        reference_obj = tool.Ifc.get_object(reference_element)

        def to_camera_coords(camera: bpy.types.Object, reference_obj: bpy.types.Object) -> Matrix:
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat.translation = xyz
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat.translation += annotation_offset
            return mat

        def project_point_onto_camera(point, camera):
            projection = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
            return camera.matrix_world.inverted() @ mathutils.geometry.intersect_line_plane(
                point.xyz, point.xyz - projection, camera.location, projection
            )

        obj_matrix = to_camera_coords(camera, reference_obj)

        if camera.data.BIMCameraProperties.raster_x > camera.data.BIMCameraProperties.raster_y:
            width = camera.data.ortho_scale
            height = width / camera.data.BIMCameraProperties.raster_x * camera.data.BIMCameraProperties.raster_y
        else:
            height = camera.data.ortho_scale
            width = height / camera.data.BIMCameraProperties.raster_y * camera.data.BIMCameraProperties.raster_x

        projection = project_point_onto_camera(reference_obj.location, camera)
        co1 = camera.matrix_world @ mathutils.Vector((width / 2, projection[1], -1))
        co2 = camera.matrix_world @ mathutils.Vector((-(width / 2), projection[1], -1))
        co1 = obj_matrix.inverted() @ co1
        co2 = obj_matrix.inverted() @ co2

        data = bpy.data.curves.new("Annotation", type="CURVE")
        data.dimensions = "3D"
        data.resolution_u = 2

        polyline = data.splines.new("POLY")
        polyline.points.add(1)
        polyline.points[-2].co = list(co1) + [1]
        polyline.points[-1].co = list(co2) + [1]

        obj = bpy.data.objects.new(reference_obj.name, data)
        obj.matrix_world = obj_matrix

        element = cls.run_root_assign_class(
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type="SECTION_LEVEL",
            should_add_representation=True,
            context=context,
            ifc_representation_class=None,
        )
        return element

    @classmethod
    def generate_section_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        import bonsai.bim.module.drawing.helper as helper

        reference_obj = tool.Ifc.get_object(reference_element)
        reference_obj.matrix_world
        camera = tool.Ifc.get_object(drawing)
        bounds = helper.ortho_view_frame(camera.data) if camera.data.type == "ORTHO" else None

        def to_camera_coords(camera: bpy.types.Object, reference_obj: bpy.types.Object) -> Matrix:
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat.translation = xyz
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat.translation += annotation_offset
            return mat

        def clip_to_camera_boundary(
            mesh: bpy.types.Mesh, bounds: tuple[float, float, float, float, float, float]
        ) -> Union[bpy.types.Mesh, None]:
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        if cls.is_perpendicular(camera, reference_obj) and cls.is_intersecting(camera, reference_obj):
            reference_mesh = cls.get_camera_block(reference_obj)
            obj_matrix = to_camera_coords(camera, reference_obj)

            # The reference mesh vertices represent a view cube. To convert
            # this into a section line we:
            # 1. Select the 4 +Z vertices local to the reference element. This
            # is the cutting plane.
            verts_local_to_reference = [reference_obj.matrix_world.inverted() @ v for v in reference_mesh["verts"]]
            cutting_plane_verts = sorted(verts_local_to_reference, key=lambda x: x.z)[-4:]
            global_cutting_plane_verts = [reference_obj.matrix_world @ v for v in cutting_plane_verts]
            # 2. Project the cutting plane onto our viewing camera.
            verts_local_to_camera = [camera.matrix_world.inverted() @ v for v in global_cutting_plane_verts]
            # 3. Collapse verts with the same XY coords, and set Z to be just
            # below the clip_start so it's visible
            collapsed_verts = []
            for vert in verts_local_to_camera:
                if not [True for v in collapsed_verts if (vert.xy - v.xy).length < 1e-2]:
                    collapsed_verts.append(mathutils.Vector((vert.x, vert.y, -camera.data.clip_start - 0.05)))
            # 4. The first two vertices is the section line
            section_line = collapsed_verts[0:2]
            # 5. Sort the vertices in the +X direction so that the vertices are
            # ordered to "point" in the direction of the section cut.
            section_line = sorted(
                section_line, key=lambda co: (reference_obj.matrix_world.inverted() @ camera.matrix_world @ co).x
            )
            global_section_line = [camera.matrix_world @ v for v in section_line]
            local_section_line = [obj_matrix.inverted() @ v for v in global_section_line]

            mesh = bpy.data.meshes.new(name="Annotation")
            mesh.from_pydata(local_section_line, [(0, 1)], [])
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm = clip_to_camera_boundary(bm, bounds)
            bm.to_mesh(mesh)
            bm.free()

            obj = bpy.data.objects.new(reference_obj.name, mesh)
            obj.matrix_world = obj_matrix

            element = cls.run_root_assign_class(
                obj=obj,
                ifc_class="IfcAnnotation",
                predefined_type="SECTION",
                should_add_representation=True,
                context=context,
                ifc_representation_class=None,
            )
            return element

    @classmethod
    def generate_elevation_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        reference_obj = tool.Ifc.get_object(reference_element)
        reference_obj.matrix_world
        camera = tool.Ifc.get_object(drawing)

        def to_camera_coords(camera: bpy.types.Object, reference_obj: bpy.types.Object) -> Matrix:
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat.translation = xyz
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat.translation += annotation_offset
            return mat

        if cls.is_perpendicular(camera, reference_obj) and cls.is_intersecting(camera, reference_obj):
            obj = bpy.data.objects.new(reference_obj.name, None)
            obj.empty_display_size = 0.1
            obj.matrix_world = to_camera_coords(camera, reference_obj)

            element = cls.run_root_assign_class(
                obj=obj,
                ifc_class="IfcAnnotation",
                predefined_type="ELEVATION",
                should_add_representation=False,
                context=context,
                ifc_representation_class=None,
            )
            return element

    @classmethod
    def generate_grid_axis_reference_annotation(
        cls,
        drawing: ifcopenshell.entity_instance,
        reference_element: ifcopenshell.entity_instance,
        context: ifcopenshell.entity_instance,
    ) -> ifcopenshell.entity_instance:
        import bonsai.bim.module.drawing.helper as helper

        target_view = tool.Drawing.get_drawing_target_view(drawing)

        camera = tool.Ifc.get_object(drawing)

        is_ortho = camera.data.type == "ORTHO"
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None
        clipping = is_ortho and target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW")
        elevating = is_ortho and target_view in ("ELEVATION_VIEW", "SECTION_VIEW")

        def clone(src: bpy.types.Object) -> bpy.types.Object:
            dst = src.copy()
            dst.data = dst.data.copy()
            dst.name = dst.name.replace("IfcGridAxis/", "")
            dst.BIMObjectProperties.ifc_definition_id = 0
            dst.data.BIMMeshProperties.ifc_definition_id = 0
            return dst

        def disassemble(obj: bpy.types.Object) -> tuple[bpy.types.Object, bmesh.types.BMesh]:
            mesh = bmesh.new()
            mesh.verts.ensure_lookup_table()
            mesh.from_mesh(obj.data)
            return obj, mesh

        def assemble(obj: bpy.types.Object, mesh: bmesh.types.BMesh) -> bpy.types.Object:
            mesh.to_mesh(obj.data)
            return obj

        def to_camera_coords(obj: bpy.types.Object, mesh: bpy.types.Mesh) -> tuple[bpy.types.Object, bpy.types.Mesh]:
            mesh.transform(camera.matrix_world.inverted() @ obj.matrix_world)
            obj.matrix_world = camera.matrix_world
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            obj.matrix_world.translation += annotation_offset
            return obj, mesh

        def clip_to_camera_boundary(mesh: bmesh.types.BMesh) -> bmesh.types.BMesh:
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        def draw_grids_vertically(mesh: bmesh.types.BMesh) -> bmesh.types.BMesh:
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.elevate_segment(bounds, points)
            if points is None:
                return None
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        obj = tool.Ifc.get_object(reference_element)
        if not obj:
            return
        obj, mesh = to_camera_coords(*disassemble(clone(obj)))

        if clipping:
            mesh = clip_to_camera_boundary(mesh)
        elif elevating:
            mesh = draw_grids_vertically(mesh)

        if mesh is None:
            return

        assemble(obj, mesh)

        element = cls.run_root_assign_class(
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type="GRID",
            should_add_representation=True,
            context=context,
            ifc_representation_class=None,
        )
        return element

    @classmethod
    def is_perpendicular(cls, a: bpy.types.Object, b: bpy.types.Object) -> bool:
        axes = [mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))]
        a_quaternion = a.matrix_world.to_quaternion()
        b_quaternion = b.matrix_world.to_quaternion()
        for axis in axes:
            if abs((a_quaternion @ axis).angle((b_quaternion @ axis)) - (math.pi / 2)) < 1e-5:
                return True
        return False

    @classmethod
    def get_camera_block(cls, obj: bpy.types.Object) -> dict:
        raster_x = obj.data.BIMCameraProperties.raster_x
        raster_y = obj.data.BIMCameraProperties.raster_y

        if raster_x > raster_y:
            width = obj.data.ortho_scale
            height = width / raster_x * raster_y
        else:
            height = obj.data.ortho_scale
            width = height / raster_y * raster_x
        depth = obj.data.clip_end

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
    def replace_text_literal_variables(cls, text: str, product: Optional[ifcopenshell.entity_instance] = None) -> str:
        if not product:
            return text

        for command in re.findall("``.*?``", text):
            original_command = command
            for variable in re.findall("{{.*?}}", command):
                value = ifcopenshell.util.selector.get_element_value(product, variable[2:-2])
                value = '"' + str(value).replace('"', '\\"') + '"'
                command = command.replace(variable, value)
            text = text.replace(original_command, ifcopenshell.util.selector.format(command[2:-2]))

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
        # fmt: off
        return [
            v.strip()
            for v in (
                ifcopenshell.util.element.get_psets(drawing)["EPset_Drawing"].get("Metadata", "") or ""
            ).split(",")
            if v
        ]
        # fmt: on

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
        if ifc_file is None:
            ifc_file = tool.Ifc.get()
            elements = cls.get_elements_in_camera_view(tool.Ifc.get_object(drawing), bpy.data.objects)
        else:
            # This can probably be smarter
            elements = set(ifc_file.by_type("IfcElement"))
        pset = ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {})
        include = pset.get("Include", None)
        if include:
            elements = ifcopenshell.util.selector.filter_elements(ifc_file, include)
        else:
            if tool.Ifc.get_schema() == "IFC2X3":
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
                if decomposes := i.Decomposes:
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
        if tool.Ifc.get_schema() == "IFC2X3":
            return reference.ReferenceToDocument[0]
        return reference.ReferencedDocument

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
        area = tool.Blender.get_view3d_area()
        return bool(
            camera is not None
            and camera.type == "CAMERA"
            and camera.BIMObjectProperties.ifc_definition_id
            and area is not None
        )

    @classmethod
    def is_camera_orthographic(cls) -> bool:
        camera = bpy.context.scene.camera
        return True if (camera and camera.data.type == "ORTHO") else False

    @classmethod
    def is_active_drawing(cls, drawing: ifcopenshell.entity_instance) -> bool:
        return drawing.id() == bpy.context.scene.DocProperties.active_drawing_id

    @classmethod
    def run_drawing_activate_model(cls) -> None:
        bpy.ops.bim.activate_model()

    @classmethod
    def isolate_camera_collection(cls, camera: bpy.types.Object) -> None:
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        drawing_collections = []
        camera_collection = camera.BIMObjectProperties.collection
        for drawing in drawings:
            if not (drawing_obj := tool.Ifc.get_object(drawing)):
                continue
            if not (drawing_collection := drawing_obj.BIMObjectProperties.collection):
                continue
            if drawing_obj == camera:
                drawing_collection.hide_render = False
            else:
                drawing_collection.hide_render = True

        project = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = project.BIMObjectProperties.collection
        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection == project_collection:
                for layer_collection2 in layer_collection.children:
                    if layer_collection2.collection in drawing_collections:
                        layer_collection2.hide_viewport = True
                    elif layer_collection2.collection == camera_collection:
                        layer_collection2.hide_viewport = False

    @classmethod
    def activate_drawing(cls, camera: bpy.types.Object) -> None:
        selected_objects_before = bpy.context.selected_objects
        non_ifc_objects_hide = {o: o.hide_get() for o in bpy.context.view_layer.objects if not tool.Ifc.get_entity(o)}

        # Sync viewport objects visibility with selectors from EPset_Drawing/Include and /Exclude
        drawing = tool.Ifc.get_entity(camera)

        filtered_elements = cls.get_drawing_elements(drawing) | cls.get_drawing_spaces(drawing)
        filtered_elements.add(drawing)

        subcontexts: list[ifcopenshell.entity_instance] = []
        target_view = cls.get_drawing_target_view(drawing)

        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            context_filters = [
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
            context_filters = [
                ("Model", "Body", target_view),
                ("Model", "Body", "MODEL_VIEW"),
                ("Model", "Facetation", target_view),
                ("Model", "Facetation", "MODEL_VIEW"),
                ("Model", "Annotation", target_view),
                ("Model", "Annotation", "MODEL_VIEW"),
            ]

        for context_filter in context_filters:
            subcontext = ifcopenshell.util.representation.get_context(tool.Ifc.get(), *context_filter)
            if subcontext:
                subcontexts.append(context_filter)

        # Hide everything first, then selectively show. This is significantly faster.
        with bpy.context.temp_override(area=next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")):
            bpy.ops.object.hide_view_set(unselected=False)
            bpy.ops.object.hide_view_set(unselected=True)

        # switch representations and hide elements without representations
        element_obj_names = set()
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
                        should_reload=False,
                        is_global=True,
                        should_sync_changes_first=True,
                    )
                    has_context = True
                    break

            # Don't hide IfcAnnotations or Aggregates as some of them might exist without representations
            if has_context or element.is_a("IfcAnnotation") or element.IsDecomposedBy:
                element_obj_names.add(obj.name)

        # Note that render visibility is only set on drawing generation time for speed.
        for obj in bpy.context.view_layer.objects:
            if obj.name in element_obj_names:
                obj.hide_set(False)  # Show the object
                continue
            if (hide := non_ifc_objects_hide.get(obj)) is not None:
                obj.hide_set(hide)

        cls.import_camera_props(drawing, camera.data)

        for obj in selected_objects_before:
            obj.hide_set(False)
            obj.select_set(True)

    @classmethod
    def get_elements_in_camera_view(
        cls, camera: bpy.types.Object, objs: list[bpy.types.Object]
    ) -> set[ifcopenshell.entity_instance]:
        props = camera.data.BIMCameraProperties
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
        camera_matrix = obj.matrix_world.inverted() @ camera.matrix_world
        plane_co = camera_matrix.translation
        plane_no = camera_matrix.col[2].xyz

        # Bisect verts are offset by the clip (with 5mm tolerance) to ensure it is visible in the viewport.
        global_offset = camera.matrix_world.col[2].xyz * (-camera.data.clip_start - 0.005)

        return cls.bisect_mesh_with_plane(obj, plane_co, plane_no, global_offset=global_offset)

    @classmethod
    def bisect_mesh_with_plane(
        cls, obj: bpy.types.Object, plane_co: Vector, plane_no: Vector, global_offset: Optional[Vector] = None
    ) -> tuple[list[Vector], list[list[int]]]:
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
    def get_scale_ratio(cls, scale: str) -> float:
        numerator, denominator = scale.split("/")
        return float(numerator) / float(denominator)

    @classmethod
    def get_diagram_scale(cls, obj: bpy.types.Object) -> dict[str, float]:
        props = obj.data.BIMCameraProperties
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
        l = lark.Lark(
            """start: feet? "-"? inches?
                    feet: NUMBER? "-"? fraction? "'"
                    inches: NUMBER? "-"? fraction? "\\""
                    fraction: NUMBER "/" NUMBER
                    %import common.NUMBER
                    %import common.WS
                    %ignore WS // Disregard spaces in text
                 """
        )

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
        import ezdxf
        import xml.etree.ElementTree as ET

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
