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

import os
import re
import bpy
import math
import bmesh
import shutil
import logging
import mathutils
import webbrowser
import subprocess
import numpy as np
import blenderbim.core.tool
import blenderbim.core.geometry
import blenderbim.tool as tool
import ifcopenshell.util.representation
import blenderbim.bim.module.drawing.sheeter as sheeter
import blenderbim.bim.module.drawing.scheduler as scheduler
import blenderbim.bim.module.drawing.annotation as annotation
import blenderbim.bim.module.drawing.helper as helper

from blenderbim.bim.module.drawing.data import FONT_SIZES, DecoratorData
from blenderbim.bim.module.drawing.prop import get_diagram_scales, BOX_ALIGNMENT_POSITIONS

from mathutils import Vector
import collections


class Drawing(blenderbim.core.tool.Drawing):
    @classmethod
    def canonicalise_class_name(self, name):
        return re.sub("[^0-9a-zA-Z]+", "", name)

    @classmethod
    def copy_representation(cls, source, dest):
        if source.Representation:
            dest.Representation = ifcopenshell.util.element.copy_deep(
                tool.Ifc.get(), source.Representation, exclude=["IfcGeometricRepresentationContext"]
            )

    @classmethod
    def create_annotation_object(cls, drawing, object_type):
        data_type = {
            "ANGLE": "curve",
            "BATTING": "mesh",
            "BREAKLINE": "mesh",
            "DIAMETER": "curve",
            "DIMENSION": "curve",
            "FALL": "curve",
            "FILL_AREA": "mesh",
            "HIDDEN_LINE": "mesh",
            "LINEWORK": "mesh",
            "PLAN_LEVEL": "curve",
            "RADIUS": "curve",
            "SECTION_LEVEL": "curve",
            "STAIR_ARROW": "curve",
            "TEXT": "empty",
            "TEXT_LEADER": "curve",
        }[object_type]
        obj = annotation.Annotator.get_annotation_obj(drawing, object_type, data_type)
        if object_type == "FILL_AREA":
            obj = annotation.Annotator.add_plane_to_annotation(obj)
        elif object_type == "TEXT_LEADER":
            co1, _, co2, _ = annotation.Annotator.get_placeholder_coords()
            obj = annotation.Annotator.add_line_to_annotation(obj, co2, co1)
        elif object_type != "TEXT":
            obj = annotation.Annotator.add_line_to_annotation(obj)

        return obj

    @classmethod
    def ensure_annotation_in_drawing_plane(cls, obj, camera=None):
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
        current_pos.z = -camera.data.clip_start
        current_pos = camera.matrix_world @ current_pos
        obj.location = current_pos

    @classmethod
    def setup_annotation_object(cls, obj, object_type, related_object=None):
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
                float_is_zero = lambda f: 0.0001 >= f >= -0.0001
                arrow.location = stair.matrix_world @ Vector(
                    (bbox["min_x"], (bbox["max_y"] - bbox["min_y"]) / 2, bbox["max_z"])
                )
                last_step_x = max(v.co.x for v in stair.data.vertices if float_is_zero(v.co.z - bbox["max_z"]))
                arrow.data.splines[0].points[0].co = Vector((0, 0, 0, 1))
                arrow.data.splines[0].points[1].co = Vector((last_step_x, 0, 0, 1))

                cls.ensure_annotation_in_drawing_plane(obj)
                assign_product = True

        elif object_type == "TEXT":
            bbox = tool.Blender.get_object_bounding_box(related_object)

            obj.location = related_object.matrix_world @ bbox["center"]
            cls.ensure_annotation_in_drawing_plane(obj)
            assign_product = True

        if assign_product and not cls.get_assigned_product(obj_entity):
            tool.Ifc.run("drawing.assign_product", relating_product=related_entity, related_object=obj_entity)

        if object_type == "TEXT":
            tool.Drawing.update_text_value(obj)

    @classmethod
    def is_annotation_object_type(cls, element, object_types):
        if not isinstance(object_types, collections.abc.Iterable):
            object_types = [object_types]

        element_type = element.is_a()

        if element_type == "IfcAnnotation" and element.ObjectType in object_types:
            return True

        if element_type == "IfcTypeProduct" and element.ApplicableOccurrence.startswith("IfcAnnotation/"):
            applicable_object_type = element.ApplicableOccurrence.split("/")[1]
            if applicable_object_type in object_types:
                return True

        return False

    @classmethod
    def get_annotation_representation(cls, element):
        rep = ifcopenshell.util.representation.get_representation(
            element, "Plan", "Annotation"
        ) or ifcopenshell.util.representation.get_representation(element, "Model", "Annotation")
        if not rep:
            return None

        rep = tool.Geometry.resolve_mapped_representation(rep)
        return rep

    @classmethod
    def create_camera(cls, name, matrix):
        camera = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        camera.location = (0, 0, 1.5)  # The view shall be 1.5m above the origin
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 50  # The default of 6m is too small
        camera.data.clip_start = 0.002  # 2mm is close to zero but allows any GPU-drawn lines to be visible.
        camera.data.clip_end = 10  # A slightly more reasonable default
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            camera.data.BIMCameraProperties.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            camera.data.BIMCameraProperties.diagram_scale = "1:100|1/100"
        camera.matrix_world = matrix
        bpy.context.scene.collection.objects.link(camera)
        return camera

    @classmethod
    def create_svg_schedule(cls, schedule):
        schedule_creator = scheduler.Scheduler()
        schedule_creator.schedule(
            cls.get_document_uri(schedule), cls.get_path_with_ext(cls.get_document_uri(schedule), "svg")
        )

    @classmethod
    def create_svg_sheet(cls, document, titleblock):
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        uri = cls.get_document_uri(document, "LAYOUT")
        sheet_builder.create(uri, titleblock)
        return uri

    @classmethod
    def delete_collection(cls, collection):
        bpy.data.collections.remove(collection, do_unlink=True)

    @classmethod
    def delete_drawing_elements(cls, elements):
        for element in elements:
            ifcopenshell.api.run("root.remove_product", tool.Ifc.get(), product=element)
            obj = tool.Ifc.get_object(element)
            if obj:
                obj_data = obj.data
                bpy.data.objects.remove(obj)
                if obj_data and obj_data.users == 0:  # in case we have drawing element types
                    cls.remove_object_data(obj_data)

    @classmethod
    def remove_object_data(cls, data):
        """also removes all related objects"""
        if isinstance(data, bpy.types.Camera):
            bpy.data.cameras.remove(data)
        elif isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)

    @classmethod
    def delete_object(cls, obj):
        bpy.data.objects.remove(obj)

    @classmethod
    def disable_editing_drawings(cls):
        bpy.context.scene.DocProperties.is_editing_drawings = False

    @classmethod
    def disable_editing_schedules(cls):
        bpy.context.scene.DocProperties.is_editing_schedules = False

    @classmethod
    def disable_editing_sheets(cls):
        bpy.context.scene.DocProperties.is_editing_sheets = False

    @classmethod
    def disable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = False

    @classmethod
    def disable_editing_assigned_product(cls, obj):
        obj.BIMAssignedProductProperties.is_editing_product = False

    @classmethod
    def enable_editing(cls, obj):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.data:
            bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def enable_editing_drawings(cls):
        bpy.context.scene.DocProperties.is_editing_drawings = True

    @classmethod
    def enable_editing_schedules(cls):
        bpy.context.scene.DocProperties.is_editing_schedules = True

    @classmethod
    def enable_editing_sheets(cls):
        bpy.context.scene.DocProperties.is_editing_sheets = True

    @classmethod
    def enable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = True

    @classmethod
    def enable_editing_assigned_product(cls, obj):
        obj.BIMAssignedProductProperties.is_editing_product = True

    @classmethod
    def ensure_unique_drawing_name(cls, name):
        names = [e.Name for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        while name in names:
            name += "-X"
        return name

    @classmethod
    def ensure_unique_identification(cls, identification):
        if tool.Ifc.get_schema() == "IFC2X3":
            ids = [d.DocumentId for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"]
        else:
            ids = [
                d.Identification for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"
            ]
        while identification in ids:
            identification += "-X"
        return identification

    @classmethod
    def export_text_literal_attributes(cls, obj):
        literals = []
        for literal_props in obj.BIMTextProperties.literals:
            literal_data = blenderbim.bim.helper.export_attributes(literal_props.attributes)
            literals.append(literal_data)
        return literals

    @classmethod
    def get_annotation_context(cls, target_view):
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Annotation", target_view)
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Annotation", target_view)

    @classmethod
    def get_body_context(cls):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_document_uri(cls, document, description=None):
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
                if description and reference.Description != description:
                    continue
                location = cls.get_document_uri(reference)
                if location:
                    return location

    @classmethod
    def get_path_filename(cls, path):
        return os.path.splitext(os.path.basename(path))[0]

    @classmethod
    def get_path_with_ext(cls, path, ext):
        return os.path.splitext(path)[0] + f".{ext}"

    @classmethod
    def get_unit_system(cls):
        return bpy.context.scene.unit_settings.system

    @classmethod
    def get_drawing_collection(cls, drawing):
        obj = tool.Ifc.get_object(drawing)
        if obj:
            return obj.users_collection[0]

    @classmethod
    def get_drawing_group(cls, drawing):
        for rel in drawing.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToGroup"):
                return rel.RelatingGroup

    @classmethod
    def get_drawing_document(cls, drawing):
        for rel in drawing.HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument"):
                return rel.RelatingDocument

    @classmethod
    def get_drawing_references(cls, drawing):
        results = set()
        for inverse in tool.Ifc.get().get_inverse(drawing):
            if inverse.is_a("IfcRelAssignsToProduct") and inverse.RelatingProduct == drawing:
                results.update(inverse.RelatedObjects)
        return results

    @classmethod
    def get_drawing_target_view(cls, drawing):
        return ifcopenshell.util.element.get_psets(drawing)["EPset_Drawing"].get("TargetView", "MODEL_VIEW")

    @classmethod
    def get_group_elements(cls, group):
        for rel in group.IsGroupedBy or []:
            return rel.RelatedObjects

    @classmethod
    def get_ifc_representation_class(cls, object_type):
        if object_type == "TEXT":
            return "IfcTextLiteral"
        elif object_type == "TEXT_LEADER":
            return "IfcGeometricCurveSet/IfcTextLiteral"
        return ""

    @classmethod
    def get_name(cls, element):
        return element.Name

    @classmethod
    def generate_drawing_matrix(cls, target_view, location_hint):
        x = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[0][3]
        y = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[1][3]
        z = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[2][3]
        if target_view == "PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world[2][3]
                return mathutils.Matrix(((1, 0, 0, x), (0, 1, 0, y), (0, 0, 1, z + 1.6), (0, 0, 0, 1)))
        elif target_view == "REFLECTED_PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world[2][3]
                return mathutils.Matrix(((-1, 0, 0, x), (0, 1, 0, y), (0, 0, -1, z + 1.6), (0, 0, 0, 1)))
            return mathutils.Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
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
        return mathutils.Matrix()

    @classmethod
    def generate_sheet_identification(cls):
        number = len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"])
        return "A" + str(number).zfill(2)

    @classmethod
    def get_text_literal(cls, obj, return_list=False):
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
    def remove_literal_from_annotation(cls, obj, literal):
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
    def synchronise_ifc_and_text_attributes(cls, obj):
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
    def add_literal_to_annotation(cls, obj, Literal="Literal", Path="RIGHT", BoxAlignment="bottom-left"):
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
    def get_assigned_product(cls, element):
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def import_annotations_in_group(cls, group):
        elements = set(
            [e for e in cls.get_group_elements(group) if e.is_a("IfcAnnotation") and e.ObjectType != "DRAWING"]
        )
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = blenderbim.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = tool.Ifc.get()
        ifc_importer.calculate_unit_scale()
        ifc_importer.process_context_filter()
        ifc_importer.create_generic_elements(elements)
        for obj in ifc_importer.added_data.values():
            tool.Collector.assign(obj)

    @classmethod
    def import_drawing(cls, drawing):
        settings = ifcopenshell.geom.settings()
        settings.set(settings.STRICT_TOLERANCE, True)
        shape = ifcopenshell.geom.create_shape(settings, drawing)
        geometry = shape.geometry

        v = geometry.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        z = [v[i + 2] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        depth = max(z) - min(z)

        camera = bpy.data.cameras.new(tool.Loader.get_mesh_name(geometry))
        camera.type = "ORTHO"
        camera.ortho_scale = width if width > height else height
        camera.clip_start = 0.002
        camera.clip_end = depth

        if width > height:
            camera.BIMCameraProperties.raster_x = 1000
            camera.BIMCameraProperties.raster_y = round(1000 * (height / width))
        else:
            camera.BIMCameraProperties.raster_x = round(1000 * (width / height))
            camera.BIMCameraProperties.raster_y = 1000

        psets = ifcopenshell.util.element.get_psets(drawing)
        pset = psets.get("EPset_Drawing")
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
                    camera.BIMCameraProperties.custom_diagram_scale = pset["HumanScale"] + "|" + pset["Scale"]
            if "HasUnderlay" in pset:
                camera.BIMCameraProperties.has_underlay = pset["HasUnderlay"]
            if "HasLinework" in pset:
                camera.BIMCameraProperties.has_linework = pset["HasLinework"]
            if "HasAnnotation" in pset:
                camera.BIMCameraProperties.has_annotation = pset["HasAnnotation"]

        tool.Loader.link_mesh(shape, camera)

        obj = bpy.data.objects.new(tool.Loader.get_name(drawing), camera)
        tool.Ifc.link(drawing, obj)

        m = shape.transformation.matrix.data
        mat = mathutils.Matrix(
            ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
        )
        obj.matrix_world = mat
        tool.Geometry.record_object_position(obj)
        tool.Collector.assign(obj)

        return obj

    @classmethod
    def import_drawings(cls):
        current_drawings_selection = {
            d.ifc_definition_id: d.is_selected for d in bpy.context.scene.DocProperties.drawings
        }
        bpy.context.scene.DocProperties.drawings.clear()
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        for drawing in drawings:
            new = bpy.context.scene.DocProperties.drawings.add()
            new.ifc_definition_id = drawing.id()
            new.name = drawing.Name or "Unnamed"
            new.target_view = cls.get_drawing_target_view(drawing)
            new.is_selected = current_drawings_selection.get(drawing.id(), True)

    @classmethod
    def import_schedules(cls):
        bpy.context.scene.DocProperties.schedules.clear()
        schedules = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SCHEDULE"]
        for schedule in schedules:
            new = bpy.context.scene.DocProperties.schedules.add()
            new.ifc_definition_id = schedule.id()
            new.name = schedule.Name or "Unnamed"
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = schedule.DocumentId
            else:
                new.identification = schedule.Identification

    @classmethod
    def import_sheets(cls):
        props = bpy.context.scene.DocProperties
        expanded_sheets = {s.ifc_definition_id for s in props.sheets if s.is_expanded}
        props.sheets.clear()
        sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "SHEET"]
        for sheet in sheets:
            new = props.sheets.add()
            new.ifc_definition_id = sheet.id()
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = sheet.DocumentId
            else:
                new.identification = sheet.Identification
            new.name = sheet.Name
            new.is_sheet = True
            new.is_expanded = sheet.id() in expanded_sheets

            if not new.is_expanded:
                continue

            for reference in cls.get_document_references(sheet):
                if reference.Description in ("SHEET", "LAYOUT", "RASTER"):
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
                new.reference_type = reference.Description

    @classmethod
    def import_text_attributes(cls, obj):
        props = obj.BIMTextProperties
        props.literals.clear()

        for ifc_literal in cls.get_text_literal(obj, return_list=True):
            literal_props = props.literals.add()
            blenderbim.bim.helper.import_attributes2(ifc_literal, literal_props.attributes)

            box_alignment_mask = [False] * 9
            position_string = literal_props.attributes["BoxAlignment"].string_value
            box_alignment_mask[BOX_ALIGNMENT_POSITIONS.index(position_string)] = True
            literal_props.box_alignment = box_alignment_mask
            literal_props.ifc_definition_id = ifc_literal.id()

        text_data = DecoratorData.get_ifc_text_data(obj)
        props.font_size = str(text_data["FontSize"])

    @classmethod
    def import_assigned_product(cls, obj):
        element = tool.Ifc.get_entity(obj)
        product = cls.get_assigned_product(element)
        if product:
            obj.BIMAssignedProductProperties.relating_product = tool.Ifc.get_object(product)
        else:
            obj.BIMAssignedProductProperties.relating_product = None

    @classmethod
    def open_with_user_command(cls, user_command, path):
        if user_command:
            commands = eval(user_command)
            for command in commands:
                subprocess.Popen(command)
        else:
            webbrowser.open("file://" + path)

    @classmethod
    def open_spreadsheet(cls, uri):
        cls.open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.spreadsheet_command, uri)

    @classmethod
    def open_svg(cls, uri):
        cls.open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.svg_command, uri)

    @classmethod
    def run_root_assign_class(
        cls,
        obj=None,
        ifc_class=None,
        predefined_type=None,
        should_add_representation=True,
        context=None,
        ifc_representation_class=None,
    ):
        return blenderbim.core.root.assign_class(
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
    def set_drawing_collection_name(cls, group, collection):
        collection.name = f"IfcGroup/{group.Name}"

    @classmethod
    def set_name(cls, element, name):
        element.Name = name

    @classmethod
    def show_decorations(cls):
        bpy.context.scene.DocProperties.should_draw_decorations = True

    @classmethod
    def update_text_value(cls, obj):
        props = obj.BIMTextProperties

        literals = cls.get_text_literal(obj, return_list=True)
        if not literals:
            props.literals.clear()
            return

        cls.import_text_attributes(obj)

        for i, literal in enumerate(literals):
            product = cls.get_assigned_product(tool.Ifc.get_entity(obj))
            props.literals[i].value = cls.replace_text_literal_variables(literal.Literal, product)

    @classmethod
    def update_text_size_pset(cls, obj):
        """updates pset `EPset_Annotation.Classes` value
        based on current font size from `obj.BIMTextProperties.font_size`
        """
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

    # TODO below this point is highly experimental prototype code with no tests

    @classmethod
    def does_file_exist(cls, uri):
        return os.path.exists(uri)

    @classmethod
    def delete_file(cls, uri):
        os.remove(uri)

    @classmethod
    def move_file(cls, src, dest):
        shutil.move(src, dest)

    @classmethod
    def generate_drawing_name(cls, target_view, location_hint):
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW") and location_hint:
            location = tool.Ifc.get().by_id(location_hint)
            if target_view == "REFLECTED_PLAN_VIEW":
                target_view = "RCP_VIEW"
            return (location.Name or "UNNAMED").upper() + " " + target_view.split("_")[0]
        elif target_view in ("SECTION_VIEW", "ELEVATION_VIEW") and location_hint:
            return location_hint + " " + target_view.split("_")[0]
        return target_view

    @classmethod
    def get_default_layout_path(cls, identification, name):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        layouts_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "LayoutsDir")
            or bpy.context.scene.DocProperties.layouts_dir
        )
        return os.path.join(layouts_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_sheet_path(cls, identification, name):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        sheets_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "SheetsDir")
            or bpy.context.scene.DocProperties.sheets_dir
        )
        return os.path.join(sheets_dir, cls.sanitise_filename(f"{identification} - {name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_titleblock_path(cls, name):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        titleblocks_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "TitleblocksDir")
            or bpy.context.scene.DocProperties.titleblocks_dir
        )
        return os.path.join(titleblocks_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def get_default_drawing_path(cls, name):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        drawings_dir = (
            ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", "DrawingsDir")
            or bpy.context.scene.DocProperties.drawings_dir
        )
        return os.path.join(drawings_dir, cls.sanitise_filename(f"{name}.svg")).replace("\\", "/")

    @classmethod
    def sanitise_filename(cls, name):
        return "".join(x for x in name if (x.isalnum() or x in "._- "))

    @classmethod
    def get_default_drawing_resource_path(cls, resource):
        project = tool.Ifc.get().by_type("IfcProject")[0]
        resource_path = ifcopenshell.util.element.get_pset(project, "BBIM_Documentation", f"{resource}Path") or getattr(
            bpy.context.scene.DocProperties, f"{resource.lower()}_path"
        )
        if resource_path:
            return resource_path.replace("\\", "/")

    @classmethod
    def get_potential_reference_elements(cls, drawing):
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
    def get_drawing_reference_annotation(cls, drawing, reference_element):
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
    def generate_reference_annotation(cls, drawing, reference_element, context):
        if reference_element.is_a("IfcGridAxis"):
            return cls.generate_grid_axis_reference_annotation(drawing, reference_element, context)
        elif reference_element.is_a("IfcAnnotation") and reference_element.ObjectType == "DRAWING":
            psets = ifcopenshell.util.element.get_psets(reference_element)
            target_view = psets.get("EPset_Drawing", {}).get("TargetView", None)
            if target_view == "ELEVATION_VIEW":
                return cls.generate_elevation_reference_annotation(drawing, reference_element, context)
            elif target_view == "SECTION_VIEW":
                return cls.generate_section_reference_annotation(drawing, reference_element, context)
        elif reference_element.is_a("IfcBuildingStorey"):
            return cls.generate_storey_annotation(drawing, reference_element, context)

    @classmethod
    def generate_storey_annotation(cls, drawing, reference_element, context):
        camera = tool.Ifc.get_object(drawing)
        bounds = helper.ortho_view_frame(camera.data) if camera.data.type == "ORTHO" else None
        reference_obj = tool.Ifc.get_object(reference_element)

        def to_camera_coords(camera, reference_obj):
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat[0][3] = xyz[0]
            mat[1][3] = xyz[1]
            mat[2][3] = xyz[2]
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat[0][3] += annotation_offset[0]
            mat[1][3] += annotation_offset[1]
            mat[2][3] += annotation_offset[2]
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
    def generate_section_reference_annotation(cls, drawing, reference_element, context):
        reference_obj = tool.Ifc.get_object(reference_element)
        reference_obj.matrix_world
        camera = tool.Ifc.get_object(drawing)
        bounds = helper.ortho_view_frame(camera.data) if camera.data.type == "ORTHO" else None

        def to_camera_coords(camera, reference_obj):
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat[0][3] = xyz[0]
            mat[1][3] = xyz[1]
            mat[2][3] = xyz[2]
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat[0][3] += annotation_offset[0]
            mat[1][3] += annotation_offset[1]
            mat[2][3] += annotation_offset[2]
            return mat

        def clip_to_camera_boundary(mesh, bounds):
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

            # The reference mesh vertices represent a view cube. To convert this into a section line we:
            # 1. Select the 4 +Z vertices local to the reference element. This is the cutting plane.
            verts_local_to_reference = [reference_obj.matrix_world.inverted() @ v for v in reference_mesh["verts"]]
            cutting_plane_verts = sorted(verts_local_to_reference, key=lambda x: x.z)[-4:]
            global_cutting_plane_verts = [reference_obj.matrix_world @ v for v in cutting_plane_verts]
            # 2. Project the cutting plane onto our viewing camera.
            verts_local_to_camera = [camera.matrix_world.inverted() @ v for v in global_cutting_plane_verts]
            # 3. Collapse verts with the same XY coords, and set Z to be just below the clip_start so it's visible
            collapsed_verts = []
            for vert in verts_local_to_camera:
                if not [True for v in collapsed_verts if (vert.xy - v.xy).length < 1e-2]:
                    collapsed_verts.append(mathutils.Vector((vert.x, vert.y, -camera.data.clip_start - 0.05)))
            # 4. The first two vertices is the section line
            section_line = collapsed_verts[0:2]
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
    def generate_elevation_reference_annotation(cls, drawing, reference_element, context):
        reference_obj = tool.Ifc.get_object(reference_element)
        reference_obj.matrix_world
        camera = tool.Ifc.get_object(drawing)

        def to_camera_coords(camera, reference_obj):
            mat = reference_obj.matrix_world.copy()
            xyz = camera.matrix_world.inverted() @ reference_obj.matrix_world.translation
            xyz[2] = 0
            xyz = camera.matrix_world @ xyz
            mat[0][3] = xyz[0]
            mat[1][3] = xyz[1]
            mat[2][3] = xyz[2]
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            mat[0][3] += annotation_offset[0]
            mat[1][3] += annotation_offset[1]
            mat[2][3] += annotation_offset[2]
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
    def generate_grid_axis_reference_annotation(cls, drawing, reference_element, context):
        target_view = tool.Drawing.get_drawing_target_view(drawing)

        camera = tool.Ifc.get_object(drawing)

        is_ortho = camera.data.type == "ORTHO"
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None
        clipping = is_ortho and target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW")
        elevating = is_ortho and target_view in ("ELEVATION_VIEW", "SECTION_VIEW")

        def clone(src):
            dst = src.copy()
            dst.data = dst.data.copy()
            dst.name = dst.name.replace("IfcGridAxis/", "")
            dst.BIMObjectProperties.ifc_definition_id = 0
            dst.data.BIMMeshProperties.ifc_definition_id = 0
            return dst

        def disassemble(obj):
            mesh = bmesh.new()
            mesh.verts.ensure_lookup_table()
            mesh.from_mesh(obj.data)
            return obj, mesh

        def assemble(obj, mesh):
            mesh.to_mesh(obj.data)
            return obj

        def to_camera_coords(obj, mesh):
            mesh.transform(camera.matrix_world.inverted() @ obj.matrix_world)
            obj.matrix_world = camera.matrix_world
            annotation_offset = mathutils.Vector((0, 0, -camera.data.clip_start - 0.05))
            annotation_offset = camera.matrix_world.to_quaternion() @ annotation_offset
            obj.matrix_world[0][3] += annotation_offset[0]
            obj.matrix_world[1][3] += annotation_offset[1]
            obj.matrix_world[2][3] += annotation_offset[2]
            return obj, mesh

        def clip_to_camera_boundary(mesh):
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        def draw_grids_vertically(mesh):
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
    def is_perpendicular(cls, a, b):
        axes = [mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1))]
        a_quaternion = a.matrix_world.to_quaternion()
        b_quaternion = b.matrix_world.to_quaternion()
        for axis in axes:
            if abs((a_quaternion @ axis).angle((b_quaternion @ axis)) - (math.pi / 2)) < 1e-5:
                return True
        return False

    @classmethod
    def get_camera_block(cls, obj):
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
    def is_intersecting(cls, a, b):
        a_block = cls.get_camera_block(a)
        a_tree = mathutils.bvhtree.BVHTree.FromPolygons(a_block["verts"], a_block["faces"])
        b_block = cls.get_camera_block(b)
        b_tree = mathutils.bvhtree.BVHTree.FromPolygons(b_block["verts"], b_block["faces"])
        return bool(a_tree.overlap(b_tree))

    @classmethod
    def replace_text_literal_variables(cls, text, product):
        if not product:
            return text

        for command in re.findall("``.*?``", text):
            original_command = command
            for variable in re.findall("{{.*?}}", command):
                value = ifcopenshell.util.selector.get_element_value(product, variable[2:-2])
                command = command.replace(variable, repr(value))
            text = text.replace(original_command, str(eval(command[2:-2])))

        for variable in re.findall("{{.*?}}", text):
            value = ifcopenshell.util.selector.get_element_value(product, variable[2:-2])
            if isinstance(value, (list, tuple)):
                value = ", ".join(str(v) for v in value)
            text = text.replace(variable, str(value))

        return text

    @classmethod
    def sync_object_representation(cls, obj):
        bpy.ops.bim.update_representation(obj=obj.name)

    @classmethod
    def sync_object_placement(cls, obj):
        blender_matrix = np.array(obj.matrix_world)
        element = tool.Ifc.get_entity(obj)
        if (obj.scale - mathutils.Vector((1.0, 1.0, 1.0))).length > 1e-4:
            bpy.ops.bim.update_representation(obj=obj.name)
            return element
        if element.is_a("IfcGridAxis"):
            return cls.sync_grid_axis_object_placement(obj, element)
        if not hasattr(element, "ObjectPlacement"):
            return
        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        return element

    @classmethod
    def sync_grid_axis_object_placement(cls, obj, element):
        grid = (element.PartOfU or element.PartOfV or element.PartOfW)[0]
        grid_obj = tool.Ifc.get_object(grid)
        if grid_obj:
            cls.sync_object_placement(grid_obj)
            if grid_obj.matrix_world != obj.matrix_world:
                bpy.ops.bim.update_representation(obj=obj.name)
        tool.Geometry.record_object_position(obj)

    @classmethod
    def get_document_references(cls, document):
        if tool.Ifc.get_schema() == "IFC2X3":
            return document.DocumentReferences or []
        return document.HasDocumentReferences or []

    @classmethod
    def get_references_with_location(cls, location):
        return [r for r in tool.Ifc.get().by_type("IfcDocumentReference") if r.Location == location]

    @classmethod
    def update_embedded_svg_location(cls, uri, old_location, new_location):
        with open(uri, "r") as f:
            svg = f.read()
        svg = svg.replace(os.path.basename(old_location), os.path.basename(new_location))
        with open(uri, "w") as f:
            f.write(svg)

    @classmethod
    def get_reference_description(cls, reference):
        return reference.Description

    @classmethod
    def get_reference_location(cls, reference):
        return reference.Location

    @classmethod
    def get_reference_element(cls, reference):
        if tool.Ifc.get_schema() == "IFC2X3":
            refs = [r for r in tool.Ifc.get().by_type("IfcRelAssociatesDocument") if r.RelatingDocument == reference]
        else:
            refs = reference.DocumentRefForObjects
        if refs:
            return refs[0].RelatedObjects[0]

    @classmethod
    def get_drawing_human_scale(cls, drawing):
        return ifcopenshell.util.element.get_psets(drawing)["EPset_Drawing"].get("HumanScale", "NTS")

    @classmethod
    def get_drawing_metadata(cls, drawing):
        return [
            v.strip()
            for v in ifcopenshell.util.element.get_psets(drawing)["EPset_Drawing"].get("Metadata", "").split(",")
            if v
        ]

    @classmethod
    def get_annotation_z_index(cls, drawing):
        return ifcopenshell.util.element.get_pset(drawing, "EPset_Annotation", "ZIndex") or 0

    @classmethod
    def get_annotation_symbol(cls, drawing):
        return ifcopenshell.util.element.get_pset(drawing, "EPset_Annotation", "Symbol")

    @classmethod
    def has_linework(cls, drawing):
        return ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {}).get("HasLinework", False)

    @classmethod
    def get_drawing_elements(cls, drawing):
        """returns a set of elements that are included in the drawing"""
        ifc_file = tool.Ifc.get()
        pset = ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {})
        include = pset.get("Include", None)
        if include:
            elements = set(ifcopenshell.util.selector.Selector.parse(ifc_file, include))
        else:
            if tool.Ifc.get_schema() == "IFC2X3":
                elements = set(ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcSpatialStructureElement"))
            else:
                elements = set(ifc_file.by_type("IfcElement") + ifc_file.by_type("IfcSpatialElement"))
            elements = {e for e in elements if e.is_a() != "IfcSpace"}
            annotations = tool.Drawing.get_group_elements(tool.Drawing.get_drawing_group(drawing))
            elements.update(annotations)

        exclude = pset.get("Exclude", None)
        if exclude:
            elements -= set(ifcopenshell.util.selector.Selector.parse(ifc_file, exclude, elements=elements))
        elements -= set(ifc_file.by_type("IfcOpeningElement"))
        return elements

    @classmethod
    def get_drawing_spaces(cls, drawing):
        ifc_file = tool.Ifc.get()
        pset = ifcopenshell.util.element.get_psets(drawing).get("EPset_Drawing", {})
        include = pset.get("Include", None)
        elements = set(ifc_file.by_type("IfcSpace"))
        if include:
            elements = set(ifcopenshell.util.selector.Selector.parse(ifc_file, include, elements=elements))
        exclude = pset.get("Exclude", None)
        if exclude:
            elements -= set(ifcopenshell.util.selector.Selector.parse(ifc_file, exclude, elements=elements))
        return elements

    @classmethod
    def get_annotation_element(cls, element):
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def get_drawing_reference(cls, drawing):
        for rel in drawing.HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument"):
                return rel.RelatingDocument

    @classmethod
    def get_reference_document(cls, reference):
        if tool.Ifc.get_schema() == "IFC2X3":
            return reference.ReferenceToDocument[0]
        return reference.ReferencedDocument

    @classmethod
    def select_assigned_product(cls, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        product = cls.get_assigned_product(element)
        if product:
            tool.Ifc.get_object(product).select_set(True)

    @classmethod
    def is_drawing_active(cls):
        camera = bpy.context.scene.camera
        return (
            camera
            and camera.type == "CAMERA"
            and camera.BIMObjectProperties.ifc_definition_id
            and any(a.type == "VIEW_3D" for a in bpy.context.screen.areas)
        )

    @classmethod
    def is_camera_orthographic(cls):
        camera = bpy.context.scene.camera
        return True if (camera and camera.data.type == "ORTHO") else False

    @classmethod
    def activate_drawing(cls, camera):
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        is_local_view = area.spaces[0].local_view is not None
        if is_local_view:
            bpy.ops.view3d.localview()
            bpy.context.scene.camera = camera
            bpy.ops.view3d.localview()
        else:
            bpy.context.scene.camera = camera
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        views_collection = bpy.data.collections.get("Views")
        for collection in views_collection.children:
            # We assume the project collection is at the top level
            for project_collection in bpy.context.view_layer.layer_collection.children:
                # We assume a convention that the 'Views' collection is directly
                # in the project collection
                if (
                    "Views" in project_collection.children
                    and collection.name in project_collection.children["Views"].children
                ):
                    project_collection.children["Views"].children[collection.name].hide_viewport = True
                    bpy.data.collections.get(collection.name).hide_render = True

                    project_collection.children["Views"].children[camera.users_collection[0].name].hide_viewport = False
        bpy.data.collections.get(camera.users_collection[0].name).hide_render = False
        tool.Spatial.set_active_object(camera)

        # Sync viewport objects visibility with selectors from EPset_Drawing/Include and /Exclude
        drawing = tool.Ifc.get_entity(camera)
        all_elements = set(tool.Ifc.get().by_type("IfcElement")) - set(tool.Ifc.get().by_type("IfcOpeningElement"))
        filtered_elements = cls.get_drawing_elements(drawing)
        hidden_elements = list(all_elements - filtered_elements)
        hidden_objs = [tool.Ifc.get_object(e) for e in hidden_elements]

        # Running operators is much more efficient in this scenario than looping through each element
        bpy.ops.object.hide_view_clear()

        for hidden_obj in hidden_objs:
            if bpy.context.view_layer.objects.get(hidden_obj.name):
                hidden_obj.hide_set(True)
                hidden_obj.hide_render = True

        subcontexts = []
        target_view = cls.get_drawing_target_view(drawing)
        context_filters = [("Model", "Body", target_view), ("Model", "Body", "MODEL_VIEW")]
        if target_view in ("PLAN_VIEW", "REFLECTED_PLAN_VIEW"):
            plan_contexts = [("Plan", "Body", target_view), ("Plan", "Body", "MODEL_VIEW")]
            plan_contexts.extend(context_filters)
            context_filters = plan_contexts
        for context_filter in context_filters:
            subcontext = ifcopenshell.util.representation.get_context(tool.Ifc.get(), *context_filter)
            if subcontext:
                subcontexts.append(context_filter)

        for element in filtered_elements:
            obj = tool.Ifc.get_object(element)
            for subcontext in subcontexts:
                priority_representation = ifcopenshell.util.representation.get_representation(element, *subcontext)
                if priority_representation:
                    current_representation = tool.Geometry.get_active_representation(obj)
                    if current_representation != priority_representation:
                        blenderbim.core.geometry.switch_representation(
                            tool.Ifc,
                            tool.Geometry,
                            obj=obj,
                            representation=priority_representation,
                            should_reload=False,
                            is_global=True,
                            should_sync_changes_first=True,
                        )
                    break

    @classmethod
    def is_intersecting_camera(cls, obj, camera):
        # Based on separating axis theorem
        plane_co = camera.matrix_world.translation
        plane_no = camera.matrix_world.col[2].xyz

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
    def bisect_mesh(cls, obj, camera):
        camera_matrix = obj.matrix_world.inverted() @ camera.matrix_world
        plane_co = camera_matrix.translation
        plane_no = camera_matrix.col[2].xyz

        global_offset = camera.matrix_world.col[2].xyz * -camera.data.clip_start

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Run the bisect operation
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
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

        bm.free()

        return verts, edges
