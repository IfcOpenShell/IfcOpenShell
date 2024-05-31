# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import os
import re
import bpy
import time
import json
import bmesh
import logging
import mathutils
import numpy as np
import numpy.typing as npt
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import blenderbim.tool as tool
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
from itertools import chain, accumulate
from blenderbim.bim.ifc import IfcStore, IFC_CONNECTED_TYPE
from blenderbim.tool.loader import OBJECT_DATA_TYPE
from blenderbim.bim.module.drawing.prop import ANNOTATION_TYPES_DATA
from typing import Dict, Union, Optional, Any


class MaterialCreator:
    def __init__(self, ifc_import_settings: IfcImportSettings, ifc_importer: IfcImporter):
        self.mesh: bpy.types.Mesh = None
        self.obj: bpy.types.Object = None
        self.materials: Dict[int, bpy.types.Material] = {}
        self.styles: Dict[int, bpy.types.Material] = {}
        self.parsed_meshes: set[str] = set()
        self.ifc_import_settings = ifc_import_settings
        self.ifc_importer = ifc_importer

    def create(self, element: ifcopenshell.entity_instance, obj: bpy.types.Object, mesh: bpy.types.Mesh) -> None:
        self.mesh = mesh
        # as ifcopenshell triangulates the mesh, we need to merge it to quads again
        self.obj = obj
        if (hasattr(element, "Representation") and not element.Representation) or (
            hasattr(element, "RepresentationMaps") and not element.RepresentationMaps
        ):
            return
        if not self.mesh or self.mesh.name in self.parsed_meshes:
            return
        self.parsed_meshes.add(self.mesh.name)
        self.add_default_material(element)
        if self.parse_representations(element):
            self.assign_material_slots_to_faces()
        tool.Geometry.record_object_materials(obj)

    def add_default_material(self, element: ifcopenshell.entity_instance) -> None:
        element_material = ifcopenshell.util.element.get_material(element)
        if not element_material:
            return
        for material in [m for m in self.ifc_importer.file.traverse(element_material) if m.is_a("IfcMaterial")]:
            if not material.HasRepresentation:
                continue
            surface_style = [
                s for s in self.ifc_importer.file.traverse(material.HasRepresentation[0]) if s.is_a("IfcSurfaceStyle")
            ]
            if surface_style:
                self.mesh.materials.append(self.styles[surface_style[0].id()])
                return
        # For authoring convenience, we choose to assign a material, even if it has no surface style. See #1585.
        for material in [m for m in self.ifc_importer.file.traverse(element_material) if m.is_a("IfcMaterial")]:
            self.mesh.materials.append(self.materials[material.id()])
            return

    def load_existing_materials(self) -> None:
        for material in bpy.data.materials:
            if material.BIMObjectProperties.ifc_definition_id:
                self.materials[material.BIMObjectProperties.ifc_definition_id] = material
            if material.BIMMaterialProperties.ifc_style_id:
                self.styles[material.BIMMaterialProperties.ifc_style_id] = material

    def parse_representations(self, element: ifcopenshell.entity_instance) -> bool:
        """Search for styles in in all `element`'s representation items
        and adds them to `self.mesh.materials`.\n
        Returns `True` if any styles were found and added, returns `False` otherwise."""
        has_parsed = False
        if hasattr(element, "Representation"):
            for representation in element.Representation.Representations:
                if self.parse_representation(representation):
                    has_parsed = True
        elif hasattr(element, "RepresentationMaps"):
            for representation_map in element.RepresentationMaps:
                if not representation_map.MappedRepresentation:
                    has_parsed = True  # Accommodate invalid IFC data from Revit
                elif self.parse_representation(representation_map.MappedRepresentation):
                    has_parsed = True
        return has_parsed

    def parse_representation(self, representation: ifcopenshell.entity_instance) -> bool:
        has_parsed = False
        representation_items = self.resolve_all_stylable_representation_items(representation)
        for item in representation_items:
            if self.parse_representation_item(item):
                has_parsed = True
        return has_parsed

    def parse_representation_item(self, item: ifcopenshell.entity_instance) -> bool:
        if not item.StyledByItem:
            return False
        style_ids = []
        styles = list(item.StyledByItem[0].Styles)
        while styles:
            style = styles.pop()
            if style.is_a("IfcSurfaceStyle"):
                style_ids.append(style.id())
            elif style.is_a("IfcPresentationStyleAssignment"):
                styles.extend(style.Styles)
        if not style_ids:
            return False
        for style_id in style_ids:
            material = self.styles[style_id]

            def get_ifc_coordinate(material: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
                """returns IfcTextureCoordinate"""
                texture_style = tool.Style.get_texture_style(material)
                if not texture_style:
                    return
                for texture in texture_style.Textures or []:
                    if coords := getattr(texture, "IsMappedBy", None):
                        coords = coords[0]
                        # IfcTextureCoordinateGenerator handled in the style shader graph
                        if coords.is_a("IfcIndexedTextureMap"):
                            return coords
                        # TODO: support IfcTextureMap
                        if coords.is_a("IfcTextureMap"):
                            print(f"WARNING. IfcTextureMap texture coordinates is not supported.")
                            return

            if coords := get_ifc_coordinate(material):
                tool.Loader.load_indexed_texture_map(coords, self.mesh)
            if self.mesh.materials.find(material.name) == -1:
                self.mesh.materials.append(material)
        return True

    def assign_material_slots_to_faces(self) -> None:
        if "ios_materials" not in self.mesh or not self.mesh["ios_materials"]:
            return
        if len(self.mesh.materials) == 1:
            return
        material_to_slot = {}

        if len(self.mesh.polygons) == len(self.mesh["ios_material_ids"]):
            for i, style_or_material_id in enumerate(self.mesh["ios_materials"]):
                if style_or_material_id in self.styles:
                    blender_material = self.styles[style_or_material_id]
                else:
                    blender_material = self.materials[style_or_material_id]
                slot_index = self.mesh.materials.find(blender_material.name)
                material_to_slot[i] = slot_index

            material_index = [
                (material_to_slot[mat_id] if mat_id != -1 else 0) for mat_id in self.mesh["ios_material_ids"]
            ]
            self.mesh.polygons.foreach_set("material_index", material_index)

    def resolve_all_stylable_representation_items(
        self, representation: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        """returns list of resolved IfcRepresentationItems"""
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
        return items


class IfcImporter:
    def __init__(self, ifc_import_settings: IfcImportSettings):
        self.ifc_import_settings = ifc_import_settings
        self.diff = None
        self.file: ifcopenshell.file = None
        self.context_settings: list[ifcopenshell.geom.main.settings] = []
        self.gross_context_settings: list[ifcopenshell.geom.main.settings] = []
        self.contexts = []
        self.project = None
        self.has_existing_project = False
        # element guids to blender collections mapping
        self.collections: dict[str, bpy.types.Collection] = {}
        self.elements: set[ifcopenshell.entity_instance] = set()
        self.annotations: set[ifcopenshell.entity_instance] = set()
        self.gross_elements: set[ifcopenshell.entity_instance] = set()
        self.element_types: set[ifcopenshell.entity_instance] = set()
        self.spatial_elements: set[ifcopenshell.entity_instance] = set()
        self.type_collection: bpy.types.Collection = None
        self.type_products = {}
        self.meshes = {}
        self.mesh_shapes = {}
        self.time = 0
        self.unit_scale = 1
        # ifc definition ids to blender elements mapping
        self.added_data: dict[int, IFC_CONNECTED_TYPE] = {}
        self.native_elements = set()
        self.native_data = {}
        self.progress = 0

        self.material_creator = MaterialCreator(ifc_import_settings, self)

    def profile_code(self, message):
        if not self.time:
            self.time = time.time()
        print("{} :: {:.2f}".format(message, time.time() - self.time))
        self.time = time.time()
        self.update_progress(self.progress + 1)

    def update_progress(self, progress):
        if progress <= 100:
            self.progress = progress
        bpy.context.window_manager.progress_update(self.progress)

    def execute(self):
        bpy.context.window_manager.progress_begin(0, 100)
        self.profile_code("Starting import process")
        self.load_file()
        self.profile_code("Loading file")
        self.calculate_unit_scale()
        self.profile_code("Calculate unit scale")
        self.process_context_filter()
        self.profile_code("Process context filter")
        self.calculate_model_offset()
        self.profile_code("Calculate model offset")
        self.predict_dense_mesh()
        self.profile_code("Predict dense mesh")
        self.set_units()
        self.profile_code("Set units")
        self.create_project()
        self.profile_code("Create project")
        self.process_element_filter()
        self.profile_code("Process element filter")
        self.create_collections()
        self.profile_code("Create collections")
        self.create_materials()
        self.profile_code("Create materials")
        self.create_styles()
        self.profile_code("Create styles")
        self.parse_native_elements()
        self.profile_code("Parsing native elements")
        self.create_native_elements()
        self.profile_code("Create native elements")
        self.create_elements()
        self.profile_code("Create elements")
        self.create_generic_elements(self.annotations)
        self.profile_code("Create annotations")
        self.create_grids()
        self.profile_code("Create grids")
        self.create_spatial_elements()
        self.profile_code("Create spatial elements")
        self.create_structural_items()
        self.profile_code("Create structural items")
        if not self.ifc_import_settings.is_coordinating:
            self.create_element_types()
            self.profile_code("Create element types")
        self.place_objects_in_collections()
        self.profile_code("Place objects in collections")
        self.add_project_to_scene()
        self.profile_code("Add project to scene")
        if self.ifc_import_settings.should_clean_mesh and len(self.file.by_type("IfcElement")) < 1000:
            self.clean_mesh()
            self.profile_code("Mesh cleaning")
        if self.ifc_import_settings.should_merge_materials_by_colour:
            self.merge_materials_by_colour()
            self.profile_code("Merging by colour")
        self.set_default_context()
        self.profile_code("Setting default context")
        if self.ifc_import_settings.should_setup_viewport_camera:
            self.setup_viewport_camera()
        self.setup_arrays()
        self.profile_code("Setup arrays")
        self.update_progress(100)
        bpy.context.window_manager.progress_end()

    def is_element_far_away(self, element: ifcopenshell.entity_instance) -> bool:
        try:
            placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            point = placement[:, 3][0:3]
            return self.is_point_far_away(point, is_meters=False)
        except:
            return False

    def is_point_far_away(
        self, point: Union[ifcopenshell.entity_instance, npt.NDArray[np.float64]], is_meters: bool = True
    ) -> bool:
        # Locations greater than 1km are not considered "small sites" according to the georeferencing guide
        # Users can configure this if they have to handle larger sites but beware of surveying precision
        limit = self.ifc_import_settings.distance_limit
        limit = limit if is_meters else (limit / self.unit_scale)
        coords = getattr(point, "Coordinates", point)
        return abs(coords[0]) > limit or abs(coords[1]) > limit or abs(coords[2]) > limit

    def process_context_filter(self):
        # Annotation ContextType is to accommodate broken Revit files
        # See https://github.com/Autodesk/revit-ifc/issues/187
        type_priority = ["Model", "Plan", "Annotation"]
        identifier_priority = [
            "Body",
            "Body-FallBack",
            "Facetation",
            "FootPrint",
            "Profile",
            "Surface",
            "Reference",
            "Axis",
            "Clearance",
            "Box",
            "Lighting",
            "Annotation",
            "CoG",
        ]
        target_view_priority = [
            "MODEL_VIEW",
            "PLAN_VIEW",
            "REFLECTED_PLAN_VIEW",
            "ELEVATION_VIEW",
            "SECTION_VIEW",
            "GRAPH_VIEW",
            "SKETCH_VIEW",
            "USERDEFINED",
            "NOTDEFINED",
        ]

        def sort_context(context):
            priority = []
            if context.ContextType in type_priority:
                priority.append(len(type_priority) - type_priority.index(context.ContextType))
            else:
                priority.append(0)
            return tuple(priority)

        def sort_subcontext(context):
            priority = []

            if context.ContextType in type_priority:
                priority.append(len(type_priority) - type_priority.index(context.ContextType))
            else:
                priority.append(0)

            if context.ContextIdentifier in identifier_priority:
                priority.append(len(identifier_priority) - identifier_priority.index(context.ContextIdentifier))
            else:
                priority.append(0)

            if context.TargetView in target_view_priority:
                priority.append(len(target_view_priority) - target_view_priority.index(context.TargetView))
            else:
                priority.append(0)

            priority.append(context.TargetScale or 0)  # Big then small

            return tuple(priority)

        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        self.contexts = sorted(
            self.file.by_type("IfcGeometricRepresentationSubContext"), key=sort_subcontext, reverse=True
        ) + sorted(
            self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False),
            key=sort_context,
            reverse=True,
        )

        for context in self.contexts:
            settings = ifcopenshell.geom.settings()
            settings.set_deflection_tolerance(self.ifc_import_settings.deflection_tolerance)
            settings.set_angular_tolerance(self.ifc_import_settings.angular_tolerance)
            settings.set(settings.STRICT_TOLERANCE, True)
            settings.set(settings.INCLUDE_CURVES, True)
            settings.set_context_ids([context.id()])
            self.context_settings.append(settings)

            settings = ifcopenshell.geom.settings()
            settings.set_deflection_tolerance(self.ifc_import_settings.deflection_tolerance)
            settings.set_angular_tolerance(self.ifc_import_settings.angular_tolerance)
            settings.set(settings.STRICT_TOLERANCE, True)
            settings.set(settings.INCLUDE_CURVES, True)
            settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
            settings.set_context_ids([context.id()])
            self.gross_context_settings.append(settings)

    def process_element_filter(self):
        offset = self.ifc_import_settings.element_offset
        offset_limit = offset + self.ifc_import_settings.element_limit

        if self.ifc_import_settings.has_filter:
            self.elements = self.ifc_import_settings.elements
            if isinstance(self.elements, set):
                self.elements = list(self.elements)
            # TODO: enable filtering for annotations
        else:
            if self.file.schema in ("IFC2X3", "IFC4"):
                self.elements = self.file.by_type("IfcElement") + self.file.by_type("IfcProxy")
            else:
                self.elements = self.file.by_type("IfcElement")

        drawing_groups = [g for g in self.file.by_type("IfcGroup") if g.ObjectType == "DRAWING"]
        drawing_annotations = set()
        for drawing_group in drawing_groups:
            for rel in drawing_group.IsGroupedBy:
                drawing_annotations.update(rel.RelatedObjects)
        self.annotations = set([a for a in self.file.by_type("IfcAnnotation")])
        self.annotations -= drawing_annotations

        self.elements = [e for e in self.elements if not e.is_a("IfcFeatureElement") or e.is_a("IfcSurfaceFeature")]
        if self.ifc_import_settings.is_coordinating:
            self.elements = [e for e in self.elements if e.Representation]

        self.elements = set(self.elements[offset:offset_limit])

        if self.ifc_import_settings.has_filter or offset or offset_limit < len(self.elements):
            self.element_types = set([ifcopenshell.util.element.get_type(e) for e in self.elements])
        else:
            self.element_types = set(self.file.by_type("IfcTypeProduct"))

        if self.ifc_import_settings.has_filter and self.ifc_import_settings.should_filter_spatial_elements:
            filtered_elements = self.elements | set(self.file.by_type("IfcGrid"))
            self.spatial_elements = self.get_spatial_elements_filtered_by_elements(filtered_elements)
        else:
            if self.file.schema == "IFC2X3":
                self.spatial_elements = set(self.file.by_type("IfcSpatialStructureElement"))
            else:
                self.spatial_elements = set(self.file.by_type("IfcSpatialElement"))

        # Detect excessive voids
        self.gross_elements = set(
            filter(lambda e: len(getattr(e, "HasOpenings", [])) > self.ifc_import_settings.void_limit, self.elements)
        )
        self.elements = self.elements.difference(self.gross_elements)

        if self.gross_elements:
            print("Warning! Excessive voids were found and skipped for the following elements:")
            for element in self.gross_elements:
                print(element)

    def get_spatial_elements_filtered_by_elements(
        self, elements: set[ifcopenshell.entity_instance]
    ) -> set[ifcopenshell.entity_instance]:
        leaf_spatial_elements = set([ifcopenshell.util.element.get_container(e) for e in elements])
        results = set()
        for spatial_element in leaf_spatial_elements:
            while True:
                results.add(spatial_element)
                spatial_element = ifcopenshell.util.element.get_aggregate(spatial_element)
                if not spatial_element or spatial_element.is_a() in ("IfcProject", "IfcProjectLibrary"):
                    break
        return results

    def parse_native_elements(self):
        if not self.ifc_import_settings.should_load_geometry:
            return
        for element in self.elements:
            if self.is_native(element):
                self.native_elements.add(element)
        self.elements -= self.native_elements

    def is_native(self, element):
        if (
            not element.Representation
            or not element.Representation.Representations
            or getattr(element, "HasOpenings", None)
        ):
            return

        representation = None
        representation_priority = None
        context = None

        for rep in element.Representation.Representations:
            if rep.ContextOfItems in self.contexts:
                rep_priority = self.contexts.index(rep.ContextOfItems)
                if representation is None or rep_priority < representation_priority:
                    representation = rep
                    representation_priority = rep_priority
                    context = rep.ContextOfItems

        if not representation:
            return

        matrix = np.eye(4)
        representation_id = None

        rep = representation
        while True:
            if len(rep.Items) == 1 and rep.Items[0].is_a("IfcMappedItem"):
                rep_matrix = ifcopenshell.util.placement.get_mappeditem_transformation(rep.Items[0])
                if not np.allclose(rep_matrix, np.eye(4)):
                    matrix = rep_matrix @ matrix
                    if representation_id is None:
                        representation_id = rep.id()
                rep = rep.Items[0].MappingSource.MappedRepresentation
            else:
                if representation_id is None:
                    representation_id = rep.id()
                break
        resolved_representation = ifcopenshell.util.representation.resolve_representation(representation)

        matrix[0][3] *= self.unit_scale
        matrix[1][3] *= self.unit_scale
        matrix[2][3] *= self.unit_scale

        # Single swept disk solids (e.g. rebar) are better natively represented as beveled curves
        if self.is_native_swept_disk_solid(element, resolved_representation):
            self.native_data[element.GlobalId] = {
                "matrix": matrix,
                "context": context,
                "geometry_id": representation_id,
                "representation": resolved_representation,
                "type": "IfcSweptDiskSolid",
            }
            return True

        if not self.ifc_import_settings.should_use_native_meshes:
            return False  # Performance improvements only occur on edge cases currently

        # FacetedBreps (without voids) are meshes. See #841.
        if self.is_native_faceted_brep(resolved_representation):
            self.native_data[element.GlobalId] = {
                "matrix": matrix,
                "context": context,
                "geometry_id": representation_id,
                "representation": resolved_representation,
                "type": "IfcFacetedBrep",
            }
            return True

        if self.is_native_face_based_surface_model(resolved_representation):
            self.native_data[element.GlobalId] = {
                "matrix": matrix,
                "context": context,
                "geometry_id": representation_id,
                "representation": resolved_representation,
                "type": "IfcFaceBasedSurfaceModel",
            }
            return True

    def is_native_swept_disk_solid(self, element, representation):
        items = [i["item"] for i in ifcopenshell.util.representation.resolve_items(representation)]
        if len(items) == 1 and items[0].is_a("IfcSweptDiskSolid"):
            if tool.Blender.Modifier.is_railing(element):
                return False
            return True
        elif len(items) and (  # See #2508 why we accommodate for invalid IFCs here
            items[0].is_a("IfcSweptDiskSolid")
            and len({i.is_a() for i in items}) == 1
            and len({i.Radius for i in items}) == 1
        ):
            if tool.Blender.Modifier.is_railing(element):
                return False
            return True
        return False

    def is_native_faceted_brep(self, representation):
        # TODO handle mapped items
        for i in representation.Items:
            if i.is_a() != "IfcFacetedBrep":
                return False
        return True

    def is_native_face_based_surface_model(self, representation):
        for i in representation.Items:
            if i.is_a() != "IfcFaceBasedSurfaceModel":
                return False
        return True

    def get_products_from_shape_representation(self, element):
        products = [pr.ShapeOfProduct[0] for pr in element.OfProductRepresentation]
        for rep_map in element.RepresentationMap:
            for usage in rep_map.MapUsage:
                for inverse_element in self.file.get_inverse(usage):
                    if inverse_element.is_a("IfcShapeRepresentation"):
                        products.extend(self.get_products_from_shape_representation(inverse_element))
        return products

    def predict_dense_mesh(self):
        if self.ifc_import_settings.should_use_native_meshes:
            return

        threshold = 10000  # Just from experience.

        # The check for CfsFaces/Faces/CoordIndex accommodates invalid data from Cadwork
        # 0 IfcClosedShell.CfsFaces
        faces = [len(faces) for e in self.file.by_type("IfcClosedShell") if (faces := e[0])]
        if faces and max(faces) > threshold:
            self.ifc_import_settings.should_use_native_meshes = True
            return

        if self.file.schema == "IFC2X3":
            return

        # 2 IfcPolygonalFaceSet.Faces
        faces = [len(faces) for e in self.file.by_type("IfcPolygonalFaceSet") if (faces := e[2])]
        if faces and max(faces) > threshold:
            self.ifc_import_settings.should_use_native_meshes = True
            return

        # 3 IfcTriangulatedFaceSet.CoordIndex
        faces = [len(index) for e in self.file.by_type("IfcTriangulatedFaceSet") if (index := e[3])]
        if faces and max(faces) > threshold:
            self.ifc_import_settings.should_use_native_meshes = True

    def calculate_model_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            return
        if self.ifc_import_settings.false_origin:
            return self.set_manual_blender_offset()
        if self.file.schema == "IFC2X3":
            project = self.file.by_type("IfcProject")[0]
        else:
            project = self.file.by_type("IfcContext")[0]
        site = self.find_decomposed_ifc_class(project, "IfcSite")
        if site and self.is_element_far_away(site):
            return self.guess_false_origin_and_project_north(site)
        building = self.find_decomposed_ifc_class(project, "IfcBuilding")
        if building and self.is_element_far_away(building):
            return self.guess_false_origin_and_project_north(building)
        return self.guess_false_origin()

    def set_manual_blender_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.blender_eastings = str(self.ifc_import_settings.false_origin[0])
        props.blender_northings = str(self.ifc_import_settings.false_origin[1])
        props.blender_orthogonal_height = str(self.ifc_import_settings.false_origin[2])
        props.has_blender_offset = True

    def guess_false_origin_and_project_north(self, element):
        if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
            return
        placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.blender_eastings = str(placement[0][3])
        props.blender_northings = str(placement[1][3])
        props.blender_orthogonal_height = str(placement[2][3])
        x_axis = mathutils.Vector(placement[:, 0][0:3])
        default_x_axis = mathutils.Vector((1, 0, 0))
        if (default_x_axis - x_axis).length > 0.01:
            props.blender_x_axis_abscissa = str(placement[0][0])
            props.blender_x_axis_ordinate = str(placement[1][0])
        props.has_blender_offset = True

    def guess_false_origin(self):
        # Civil BIM applications like to work in absolute coordinates, where the
        # ObjectPlacement is usually 0,0,0 (but not always, so we'll need to
        # check for the actual transformation) but each individual coordinate of
        # the shape representation is in absolute values.
        offset_point = self.get_offset_point()
        if offset_point is None:
            return
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.blender_eastings = str(offset_point[0])
        props.blender_northings = str(offset_point[1])
        props.blender_orthogonal_height = str(offset_point[2])
        props.has_blender_offset = True

    def get_offset_point(self) -> Union[npt.NDArray[np.float64], None]:
        elements_checked = 0
        # If more than these elements aren't far away, the file probably isn't absolutely positioned
        element_checking_threshold = 10
        for element in self.file.by_type("IfcElement"):
            if not element.Representation:
                continue
            elements_checked += 1
            if elements_checked > element_checking_threshold:
                return
            if element.ObjectPlacement and element.ObjectPlacement.is_a("IfcLocalPlacement"):
                placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)[:, 3][0:3]
                if self.is_point_far_away(placement, is_meters=False):
                    return placement
            if not self.does_element_likely_have_geometry_far_away(element):
                continue
            shape = self.create_generic_shape(element)
            if not shape:
                continue
            m = shape.transformation.matrix.data
            mat = np.array(
                ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
            )
            point = mat @ np.array(
                (
                    shape.geometry.verts[0],
                    shape.geometry.verts[1],
                    shape.geometry.verts[2],
                    0.0,
                )
            )
            point = point / self.unit_scale
            if self.is_point_far_away(point, is_meters=False):
                return point

    def does_element_likely_have_geometry_far_away(self, element: ifcopenshell.entity_instance) -> bool:
        for representation in element.Representation.Representations:
            items = []
            for item in representation.Items:
                if item.is_a("IfcMappedItem"):
                    items.extend(item.MappingSource.MappedRepresentation.Items)
                else:
                    items.append(item)
            for item in items:
                for subelement in self.file.traverse(item):
                    if subelement.is_a("IfcCartesianPointList3D"):
                        for point in subelement.CoordList:
                            if len(point) == 3 and self.is_point_far_away(point, is_meters=False):
                                return True
                    if subelement.is_a("IfcCartesianPoint"):
                        if len(subelement.Coordinates) == 3 and self.is_point_far_away(subelement, is_meters=False):
                            return True
        return False

    def apply_blender_offset_to_matrix_world(self, obj: bpy.types.Object, matrix: np.ndarray) -> mathutils.Matrix:
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            if obj.data and obj.data.get("has_cartesian_point_offset", None):
                obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
            elif self.is_point_far_away((matrix[:3, 3])):
                obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
                matrix = ifcopenshell.util.geolocation.global2local(
                    matrix,
                    float(props.blender_eastings) * self.unit_scale,
                    float(props.blender_northings) * self.unit_scale,
                    float(props.blender_orthogonal_height) * self.unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )

        return mathutils.Matrix(matrix.tolist())

    def find_decomposed_ifc_class(
        self, element: ifcopenshell.entity_instance, ifc_class: str
    ) -> Union[ifcopenshell.entity_instance, None]:
        if element.is_a(ifc_class):
            return element
        rel_aggregates = element.IsDecomposedBy
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                result = self.find_decomposed_ifc_class(part, ifc_class)
                if result:
                    return result

    def create_grids(self):
        if not self.ifc_import_settings.should_load_geometry:
            return
        grids = self.file.by_type("IfcGrid")
        for grid in grids:
            shape = None
            if not grid.UAxes or not grid.VAxes:
                # Revit can create invalid grids
                self.ifc_import_settings.logger.error("An invalid grid was found %s", grid)
                continue
            if grid.Representation:
                shape = self.create_generic_shape(grid)
            grid_obj = self.create_product(grid, shape)
            if bpy.context.preferences.addons["blenderbim"].preferences.lock_grids_on_import:
                grid_obj.lock_location = (True, True, True)
                grid_obj.lock_rotation = (True, True, True)
            collection = bpy.data.collections.new(tool.Loader.get_name(grid))
            u_axes = bpy.data.collections.new("UAxes")
            collection.children.link(u_axes)
            v_axes = bpy.data.collections.new("VAxes")
            collection.children.link(v_axes)
            self.create_grid_axes(grid.UAxes, u_axes, grid_obj)
            self.create_grid_axes(grid.VAxes, v_axes, grid_obj)
            if grid.WAxes:
                w_axes = bpy.data.collections.new("WAxes")
                collection.children.link(w_axes)
                self.create_grid_axes(grid.WAxes, w_axes, grid_obj)

    def create_grid_axes(self, axes, grid_collection, grid_obj):
        for axis in axes:
            shape = self.create_generic_shape(axis.AxisCurve)
            mesh = self.create_mesh(axis, shape)
            obj = bpy.data.objects.new(f"IfcGridAxis/{axis.AxisTag}", mesh)
            if bpy.context.preferences.addons["blenderbim"].preferences.lock_grids_on_import:
                obj.lock_location = (True, True, True)
                obj.lock_rotation = (True, True, True)
            self.link_element(axis, obj)
            self.set_matrix_world(obj, grid_obj.matrix_world)
            grid_collection.objects.link(obj)

    def create_element_types(self):
        for element_type in self.element_types:
            if not element_type:
                continue
            self.create_element_type(element_type)

    def create_element_type(self, element: ifcopenshell.entity_instance) -> None:
        self.ifc_import_settings.logger.info("Creating object %s", element)
        mesh = None
        if self.ifc_import_settings.should_load_geometry:
            for context in self.contexts:
                representation = ifcopenshell.util.representation.get_representation(element, context)
                if not representation:
                    continue
                mesh_name = "{}/{}".format(representation.ContextOfItems.id(), representation.id())
                mesh = self.meshes.get(mesh_name)
                if mesh is None:
                    shape = self.create_generic_shape(representation)
                    if shape:
                        mesh = self.create_mesh(element, shape)
                        tool.Loader.link_mesh(shape, mesh)
                        self.meshes[mesh_name] = mesh
                    else:
                        self.ifc_import_settings.logger.error("Failed to generate shape for %s", element)
                break
        obj = bpy.data.objects.new(tool.Loader.get_name(element), mesh)
        self.link_element(element, obj)
        self.material_creator.create(element, obj, mesh)
        self.type_products[element.GlobalId] = obj

    def create_native_elements(self):
        if not self.ifc_import_settings.should_load_geometry:
            return
        progress = 0
        checkpoint = time.time()
        total = len(self.native_elements)
        for element in self.native_elements:
            progress += 1
            if progress % 250 == 0:
                percent = round(progress / total * 100)
                print(
                    "{} / {} ({}%) elements processed in {:.2f}s ...".format(
                        progress, total, percent, time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
                self.incrementally_merge_objects()
            native_data = self.native_data[element.GlobalId]
            mesh_name = f"{native_data['context'].id()}/{native_data['geometry_id']}"
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                if native_data["type"] == "IfcSweptDiskSolid":
                    mesh = self.create_native_swept_disk_solid(element, mesh_name, native_data)
                elif native_data["type"] == "IfcFacetedBrep":
                    mesh = self.create_native_faceted_brep(element, mesh_name, native_data)
                elif native_data["type"] == "IfcFaceBasedSurfaceModel":
                    mesh = self.create_native_faceted_brep(element, mesh_name, native_data)
                tool.Ifc.link(tool.Ifc.get().by_id(native_data["geometry_id"]), mesh)
                mesh.name = mesh_name
                self.meshes[mesh_name] = mesh
            self.create_product(element, mesh=mesh)
        print("Done creating geometry")

    def create_spatial_elements(self) -> None:
        if bpy.context.preferences.addons["blenderbim"].preferences.spatial_elements_unselectable:
            self.create_generic_elements(self.spatial_elements, unselectable=True)
        else:
            self.create_generic_elements(self.spatial_elements, unselectable=False)

    def create_elements(self) -> None:
        self.create_generic_elements(self.elements)
        tmp = self.context_settings
        self.context_settings = self.gross_context_settings
        self.create_generic_elements(self.gross_elements)
        self.context_settings = tmp

    def create_generic_shape(
        self, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell_wrapper.TriangulationElement, None]:
        for settings in self.context_settings:
            try:
                result = ifcopenshell.geom.create_shape(settings, element)
                if result:
                    return result
            except:
                pass

    def create_generic_elements(self, elements: set[ifcopenshell.entity_instance], unselectable=False) -> None:
        if isinstance(self.file, ifcopenshell.sqlite):
            return self.create_generic_sqlite_elements(elements)

        if self.ifc_import_settings.should_load_geometry:
            for settings in self.context_settings:
                if not elements:
                    break
                products = self.create_products(elements, settings=settings)
                elements -= products
            products = self.create_pointclouds(elements)
            elements -= products

        total = len(elements)
        objects = set()
        for i, element in enumerate(elements):
            if i % 250 == 0:
                print("{} / {} elements processed ...".format(i, total))
            objects.add(self.create_product(element))

        if unselectable:
            for obj in objects:
                obj.hide_select = True

    def create_generic_sqlite_elements(self, elements: set[ifcopenshell.entity_instance]) -> None:
        self.geometry_cache = self.file.get_geometry([e.id() for e in elements])
        for geometry_id, geometry in self.geometry_cache["geometry"].items():
            mesh_name = tool.Loader.get_mesh_name(type("Geometry", (), {"id": geometry_id}))
            mesh = bpy.data.meshes.new(mesh_name)

            verts = geometry["verts"]
            mesh["has_cartesian_point_offset"] = False

            if geometry["faces"]:
                num_vertices = len(verts) // 3
                total_faces = len(geometry["faces"])
                loop_start = range(0, total_faces, 3)
                num_loops = total_faces // 3
                loop_total = [3] * num_loops
                num_vertex_indices = len(geometry["faces"])

                mesh.vertices.add(num_vertices)
                mesh.vertices.foreach_set("co", verts)
                mesh.loops.add(num_vertex_indices)
                mesh.loops.foreach_set("vertex_index", geometry["faces"])
                mesh.polygons.add(num_loops)
                mesh.polygons.foreach_set("loop_start", loop_start)
                mesh.polygons.foreach_set("loop_total", loop_total)
                mesh.update()
            else:
                e = geometry["edges"]
                v = verts
                vertices = [[v[i], v[i + 1], v[i + 2]] for i in range(0, len(v), 3)]
                edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
                mesh.from_pydata(vertices, edges, [])

            mesh["ios_materials"] = geometry["materials"]
            mesh["ios_material_ids"] = geometry["material_ids"]
            self.meshes[mesh_name] = mesh

        total = len(elements)
        for i, element in enumerate(elements):
            if i % 250 == 0:
                print("{} / {} elements processed ...".format(i, total))
            mesh = None
            geometry_id = self.geometry_cache["shapes"][element.id()]["geometry"]
            if geometry_id:
                mesh_name = tool.Loader.get_mesh_name(type("Geometry", (), {"id": geometry_id}))
                mesh = self.meshes.get(mesh_name)
            self.create_product(element, mesh=mesh)

    def create_products(
        self,
        products: set[ifcopenshell.entity_instance],
        settings: Optional[ifcopenshell.geom.main.settings] = None,
    ) -> set[ifcopenshell.entity_instance]:
        results = set()
        if not products:
            return results
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(settings, self.file, multiprocessing.cpu_count(), include=products)
        else:
            iterator = ifcopenshell.geom.iterator(settings, self.file, include=products)
        if self.ifc_import_settings.should_cache:
            cache = IfcStore.get_cache()
            if cache:
                iterator.set_cache(cache)
        valid_file = iterator.initialize()
        if not valid_file:
            return results
        checkpoint = time.time()
        progress = 0
        total = len(products)
        start_progress = self.progress
        progress_range = 85 - start_progress
        while True:
            progress += 1
            if progress % 250 == 0:
                percent_created = round(progress / total * 100)
                percent_preprocessed = iterator.progress()
                percent_average = (percent_created + percent_preprocessed) / 2
                print(
                    "{} / {} ({}% created, {}% preprocessed) elements processed in {:.2f}s ...".format(
                        progress, total, percent_created, percent_preprocessed, time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
                self.update_progress((percent_average / 100 * progress_range) + start_progress)
                self.incrementally_merge_objects()
            shape = iterator.get()
            if shape:
                product = self.file.by_id(shape.id)
                self.create_product(product, shape)
                results.add(product)
            if not iterator.next():
                break
        print("Done creating geometry")
        return results

    def incrementally_merge_objects(self):
        if not self.ifc_import_settings.is_coordinating:
            return
        if self.ifc_import_settings.merge_mode == "IFC_CLASS":
            self.merge_by_class()
            self.profile_code("Merging by class")
        elif self.ifc_import_settings.merge_mode == "IFC_TYPE":
            self.merge_by_type()
            self.profile_code("Merging by type")
        elif self.ifc_import_settings.merge_mode == "MATERIAL":
            self.merge_by_material()
            self.profile_code("Merging by material")

    def create_structural_items(self):
        # Create structural collections
        self.structural_member_collection = bpy.data.collections.new("Members")
        self.structural_connection_collection = bpy.data.collections.new("Connections")
        self.structural_collection = bpy.data.collections.new("StructuralItems")
        self.structural_collection.children.link(self.structural_member_collection)
        self.structural_collection.children.link(self.structural_connection_collection)
        self.project["blender"].children.link(self.structural_collection)

        self.create_generic_elements(set(self.file.by_type("IfcStructuralCurveMember")))
        self.create_generic_elements(set(self.file.by_type("IfcStructuralCurveConnection")))
        self.create_generic_elements(set(self.file.by_type("IfcStructuralSurfaceMember")))
        self.create_generic_elements(set(self.file.by_type("IfcStructuralSurfaceConnection")))
        self.create_structural_point_connections()

    def create_structural_point_connections(self):
        for product in self.file.by_type("IfcStructuralPointConnection"):
            # TODO: make this based off ifcopenshell. See #1409
            placement_matrix = ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement)
            vertex = None
            context = None
            representation = None
            for subelement in self.file.traverse(product.Representation):
                if subelement.is_a("IfcVertex") and subelement.VertexGeometry.is_a("IfcCartesianPoint"):
                    vertex = list(subelement.VertexGeometry.Coordinates)
                elif subelement.is_a("IfcGeometricRepresentationContext"):
                    context = subelement
                elif subelement.is_a("IfcTopologyRepresentation"):
                    representation = subelement
            if not vertex or not context or not representation:
                continue  # TODO implement non cartesian point vertexes

            mesh_name = f"{context.id()}/{representation.id()}"
            mesh = bpy.data.meshes.new(mesh_name)
            mesh.from_pydata([mathutils.Vector(vertex) * self.unit_scale], [], [])

            obj = bpy.data.objects.new("{}/{}".format(product.is_a(), product.Name), mesh)
            self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, placement_matrix))
            self.link_element(product, obj)

    def get_pointcloud_representation(self, product):
        if hasattr(product, "Representation") and hasattr(product.Representation, "Representations"):
            representations = product.Representation.Representations
        elif hasattr(product, "RepresentationMaps") and hasattr(product.RepresentationMaps, "RepresentationMaps"):
            representations = product.RepresentationMaps
        else:
            return None

        for representation in representations:
            if representation.RepresentationType in ("PointCloud", "Point"):
                return representation

            elif self.file.schema == "IFC2X3" and representation.RepresentationType == "GeometricSet":
                for item in representation.Items:
                    if not (item.is_a("IfcCartesianPointList") or item.is_a("IfcCartesianPoint")):
                        break
                else:
                    return representation

            elif representation.RepresentationType == "MappedRepresentation":
                for item in representation.Items:
                    mapped_representation = self.get_pointcloud_representation(item)
                    if mapped_representation is not None:
                        return mapped_representation
        return None

    def create_pointclouds(self, products: set[ifcopenshell.entity_instance]) -> set[ifcopenshell.entity_instance]:
        result = set()
        for product in products:
            representation = self.get_pointcloud_representation(product)
            if representation is not None:
                pointcloud = self.create_pointcloud(product, representation)
                if pointcloud is not None:
                    result.add(pointcloud)

        return result

    def create_pointcloud(
        self, product: ifcopenshell.entity_instance, representation: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        placement_matrix = self.get_element_matrix(product)
        vertex_list = []
        for item in representation.Items:
            if item.is_a("IfcCartesianPointList3D"):
                vertex_list.extend(
                    mathutils.Vector(list(coordinates)) * self.unit_scale for coordinates in item.CoordList
                )
            elif item.is_a("IfcCartesianPointList2D"):
                vertex_list.extend(
                    mathutils.Vector(list(coordinates)).to_3d() * self.unit_scale for coordinates in item.CoordList
                )
            elif item.is_a("IfcCartesianPoint"):
                vertex_list.append(mathutils.Vector(list(item.Coordinates)) * self.unit_scale)

        if len(vertex_list) == 0:
            return None

        mesh_name = f"{representation.ContextOfItems.id()}/{representation.id()}"
        mesh = bpy.data.meshes.new(mesh_name)
        mesh.from_pydata(vertex_list, [], [])
        tool.Ifc.link(representation, mesh)

        obj = bpy.data.objects.new("{}/{}".format(product.is_a(), product.Name), mesh)
        self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, placement_matrix))
        self.link_element(product, obj)
        return product

    def create_product(
        self,
        element: ifcopenshell.entity_instance,
        shape: Optional[Any] = None,
        mesh: Optional[OBJECT_DATA_TYPE] = None,
    ) -> Union[bpy.types.Object, None]:
        if element is None:
            return

        if self.has_existing_project:
            obj = tool.Ifc.get_object(element)
            if obj:
                return obj

        self.ifc_import_settings.logger.info("Creating object %s", element)

        if mesh:
            pass
        elif element.is_a("IfcAnnotation") and self.is_curve_annotation(element) and shape:
            mesh = self.create_curve(element, shape)
            tool.Loader.link_mesh(shape, mesh)
        elif shape:
            mesh_name = tool.Loader.get_mesh_name(shape.geometry)
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                mesh = self.create_mesh(element, shape)
                tool.Loader.link_mesh(shape, mesh)
                self.meshes[mesh_name] = mesh
        else:
            mesh = None

        obj = bpy.data.objects.new(tool.Loader.get_name(element), mesh)
        self.link_element(element, obj)

        if shape:
            m = shape.transformation.matrix.data
            # We use numpy here because Blender mathutils.Matrix is not accurate enough
            mat = np.array(
                ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
            )
            self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, mat))
            self.material_creator.create(element, obj, mesh)
        elif mesh:
            self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, self.get_element_matrix(element)))
            self.material_creator.create(element, obj, mesh)
        elif hasattr(element, "ObjectPlacement"):
            self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, self.get_element_matrix(element)))

        return obj

    def load_existing_meshes(self) -> None:
        self.meshes.update({m.name: m for m in bpy.data.meshes})

    def get_representation_item_material_name(self, item):
        if not item.StyledByItem:
            return
        styles = list(item.StyledByItem[0].Styles)
        while styles:
            style = styles.pop()
            if style.is_a("IfcSurfaceStyle"):
                return style.id()
            elif style.is_a("IfcPresentationStyleAssignment"):
                styles.extend(style.Styles)

    def create_native_faceted_brep(self, element, mesh_name, native_data):
        # TODO: georeferencing?
        # co [x y z x y z x y z ...]
        # vertex_index [i i i i i ...]
        # loop_start [0 3 6 9 ...] (for tris)
        # loop_total [3 3 3 3 ...] (for tris)
        self.mesh_data = {
            "co": [],
            "vertex_index": [],
            "loop_start": [],
            "loop_total": [],
            "total_verts": 0,
            "total_polygons": 0,
            "materials": [],
            "material_ids": [],
        }

        for item in native_data["representation"].Items:
            if item.is_a() == "IfcFacetedBrep":
                self.convert_representation_item_faceted_brep(item)
            elif item.is_a() == "IfcFaceBasedSurfaceModel":
                self.convert_representation_item_face_based_surface_model(item)

        mesh = bpy.data.meshes.new("Native")

        props = bpy.context.scene.BIMGeoreferenceProperties
        mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        if props.has_blender_offset and self.is_point_far_away(self.mesh_data["co"][0:3], is_meters=False):
            offset_point = np.linalg.inv(mat) @ np.array(
                (
                    float(props.blender_eastings),
                    float(props.blender_northings),
                    float(props.blender_orthogonal_height),
                    0.0,
                )
            )
            verts = [None] * len(self.mesh_data["co"])
            for i in range(0, len(self.mesh_data["co"]), 3):
                verts[i], verts[i + 1], verts[i + 2], _ = native_data["matrix"] @ mathutils.Vector(
                    (
                        *ifcopenshell.util.geolocation.enh2xyz(
                            self.mesh_data["co"][i] * self.unit_scale,
                            self.mesh_data["co"][i + 1] * self.unit_scale,
                            self.mesh_data["co"][i + 2] * self.unit_scale,
                            offset_point[0] * self.unit_scale,
                            offset_point[1] * self.unit_scale,
                            offset_point[2] * self.unit_scale,
                            float(props.blender_x_axis_abscissa),
                            float(props.blender_x_axis_ordinate),
                        ),
                        1,
                    )
                )
            mesh["has_cartesian_point_offset"] = True
        else:
            verts = [None] * len(self.mesh_data["co"])
            for i in range(0, len(self.mesh_data["co"]), 3):
                verts[i], verts[i + 1], verts[i + 2], _ = native_data["matrix"] @ mathutils.Vector(
                    (
                        self.mesh_data["co"][i] * self.unit_scale,
                        self.mesh_data["co"][i + 1] * self.unit_scale,
                        self.mesh_data["co"][i + 2] * self.unit_scale,
                        1,
                    )
                )
            mesh["has_cartesian_point_offset"] = False

        mesh.vertices.add(self.mesh_data["total_verts"])
        mesh.vertices.foreach_set("co", verts)
        mesh.loops.add(len(self.mesh_data["vertex_index"]))
        mesh.loops.foreach_set("vertex_index", self.mesh_data["vertex_index"])
        mesh.polygons.add(self.mesh_data["total_polygons"])
        mesh.polygons.foreach_set("loop_start", self.mesh_data["loop_start"])
        mesh.polygons.foreach_set("loop_total", self.mesh_data["loop_total"])
        mesh.polygons.foreach_set("use_smooth", [0] * self.mesh_data["total_polygons"])
        mesh.update()

        mesh["ios_materials"] = self.mesh_data["materials"]
        mesh["ios_material_ids"] = self.mesh_data["material_ids"]
        return mesh

    def convert_representation_item_face_based_surface_model(self, item):
        mesh = item.get_info_2(recursive=True)
        for face_set in mesh["FbsmFaces"]:
            self.convert_representation_item_face_set(item, face_set)

    def convert_representation_item_faceted_brep(self, item):
        mesh = item.get_info_2(recursive=True)
        return self.convert_representation_item_face_set(item, mesh["Outer"])

    def convert_representation_item_face_set(self, item, mesh):
        # On a few occasions, we flatten a list. This seems to be the most efficient way to do it.
        # https://stackoverflow.com/questions/20112776/how-do-i-flatten-a-list-of-lists-nested-lists

        # For huge face sets it might be better to do a "flatmap" instead of sum()
        # bounds = sum((f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1), ())
        bounds = tuple(chain.from_iterable(f["Bounds"] for f in mesh["CfsFaces"] if len(f["Bounds"]) == 1))
        # Here are some untested alternatives, are they faster?
        # bounds = tuple((f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1))[0]
        # bounds = chain.from_iterable(f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1)

        polygons = [[(p["id"], p["Coordinates"]) for p in b["Bound"]["Polygon"]] for b in bounds]

        for face in mesh["CfsFaces"]:
            # Blender cannot handle faces with holes.
            if len(face["Bounds"]) > 1:
                inner_bounds = []
                inner_bound_point_ids = []
                for bound in face["Bounds"]:
                    if bound["type"] == "IfcFaceOuterBound":
                        outer_bound = [[p["Coordinates"] for p in bound["Bound"]["Polygon"]]]
                        outer_bound_point_ids = [[p["id"] for p in bound["Bound"]["Polygon"]]]
                    else:
                        inner_bounds.append([p["Coordinates"] for p in bound["Bound"]["Polygon"]])
                        inner_bound_point_ids.append([p["id"] for p in bound["Bound"]["Polygon"]])
                points = outer_bound[0].copy()
                [points.extend(p) for p in inner_bounds]
                point_ids = outer_bound_point_ids[0].copy()
                [point_ids.extend(p) for p in inner_bound_point_ids]

                tessellated_polygons = mathutils.geometry.tessellate_polygon(outer_bound + inner_bounds)
                polygons.extend([[(point_ids[pi], points[pi]) for pi in t] for t in tessellated_polygons])

        # Clever vertex welding algorithm by Thomas Krijnen. See #841.

        # by id
        di0 = {}
        # by coords
        di1 = {}

        vertex_index_offset = self.mesh_data["total_verts"]

        def lookup(id_coords):
            idx = di0.get(id_coords[0])
            if idx is None:
                idx = di1.get(id_coords[1])
                if idx is None:
                    l = len(di0)
                    di0[id_coords[0]] = l
                    di1[id_coords[1]] = l
                    return l + vertex_index_offset
                else:
                    return idx + vertex_index_offset
            else:
                return idx + vertex_index_offset

        mapped_polygons = [list(map(lookup, p)) for p in polygons]

        self.mesh_data["vertex_index"].extend(chain.from_iterable(mapped_polygons))

        # Flattened vertex coords
        self.mesh_data["co"].extend(chain.from_iterable(di1.keys()))
        self.mesh_data["total_verts"] += len(di1.keys())
        loop_total = [len(p) for p in mapped_polygons]
        total_polygons = len(mapped_polygons)
        self.mesh_data["total_polygons"] += total_polygons

        self.mesh_data["materials"].append(self.get_representation_item_material_name(item) or "NULLMAT")
        material_index = len(self.mesh_data["materials"]) - 1
        if self.mesh_data["materials"][material_index] == "NULLMAT":
            # Magic number -1 represents no material, until this has a better approach
            self.mesh_data["material_ids"] += [-1] * total_polygons
        else:
            self.mesh_data["material_ids"] += [material_index] * total_polygons

        if self.mesh_data["loop_start"]:
            loop_start_offset = self.mesh_data["loop_start"][-1] + self.mesh_data["loop_total"][-1]
        else:
            loop_start_offset = 0

        loop_start = [loop_start_offset] + [loop_start_offset + i for i in list(accumulate(loop_total[0:-1]))]
        self.mesh_data["loop_total"].extend(loop_total)
        self.mesh_data["loop_start"].extend(loop_start)
        # list(di1.keys())

    def create_native_swept_disk_solid(self, element, mesh_name, native_data):
        # TODO: georeferencing?
        curve = bpy.data.curves.new(mesh_name, type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        polyline = curve.splines.new("POLY")

        for item_data in ifcopenshell.util.representation.resolve_items(native_data["representation"]):
            item = item_data["item"]
            matrix = item_data["matrix"]
            matrix[0][3] *= self.unit_scale
            matrix[1][3] *= self.unit_scale
            matrix[2][3] *= self.unit_scale
            # TODO: support inner radius, start param, and end param
            geometry = self.create_generic_shape(item.Directrix)
            e = geometry.edges
            v = geometry.verts
            vertices = [list(matrix @ [v[i], v[i + 1], v[i + 2], 1]) for i in range(0, len(v), 3)]
            edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
            v2 = None
            for edge in edges:
                v1 = vertices[edge[0]]
                if v1 != v2:
                    polyline = curve.splines.new("POLY")
                    polyline.points[-1].co = native_data["matrix"] @ mathutils.Vector(v1)
                v2 = vertices[edge[1]]
                polyline.points.add(1)
                polyline.points[-1].co = native_data["matrix"] @ mathutils.Vector(v2)

        curve.bevel_depth = self.unit_scale * item.Radius
        curve.use_fill_caps = True
        return curve

    def merge_by_class(self):
        merge_set = {}
        id_set = {}
        for ifc_definition_id, obj in self.added_data.items():
            if not isinstance(obj, bpy.types.Object) or not obj.data:
                continue
            element = self.file.by_id(ifc_definition_id)
            if not element.is_a("IfcElement"):
                continue
            merge_set.setdefault(element.is_a(), []).append(obj)
            id_set.setdefault(element.is_a(), []).append(ifc_definition_id)
        self.merge_objects(merge_set, id_set)

    def merge_by_type(self):
        merge_set = {}
        id_set = {}
        for ifc_definition_id, obj in self.added_data.items():
            if not isinstance(obj, bpy.types.Object) or not obj.data:
                continue
            element = self.file.by_id(ifc_definition_id)
            if not element.is_a("IfcElement"):
                continue
            element_type = ifcopenshell.util.element.get_type(element)
            if not element_type:
                continue
            merge_key = str(element_type.id()) + "-" + (element_type.Name or "Unnamed")
            merge_set.setdefault(merge_key, []).append(obj)
            id_set.setdefault(merge_key, []).append(ifc_definition_id)
        self.merge_objects(merge_set, id_set)

    def merge_by_material(self):
        merge_set = {}
        id_set = {}
        for ifc_definition_id, obj in self.added_data.items():
            if not isinstance(obj, bpy.types.Object) or not obj.data:
                continue
            element = self.file.by_id(ifc_definition_id)
            if not element.is_a("IfcElement"):
                continue
            merge_key = obj.material_slots[0].name if obj.material_slots else "no-material"
            merge_set.setdefault(merge_key, []).append(obj)
            id_set.setdefault(merge_key, []).append(ifc_definition_id)
        self.merge_objects(merge_set, id_set)

    def merge_objects(self, merge_set, id_set):
        total_objs = sum([len(o) for o in merge_set.values()])
        cumulative_total = 0
        merge_set = {k: v for k, v in sorted(merge_set.items(), key=lambda i: len(i[1]), reverse=True)}
        for group_name, objs in merge_set.items():
            total_group_objs = len(objs)
            if total_group_objs < 10:
                continue
            merge_potential = total_objs - cumulative_total
            if merge_potential < 250:
                print("Merge target achieved")
                return
            cumulative_total += total_group_objs
            print(f"Merging {total_group_objs} objects, {merge_potential} potentially remaining -", group_name)
            try:
                target = objs[0]
                target.data = target.data.copy()
                context_override = {}
                context_override["object"] = context_override["active_object"] = target
                context_override["selected_objects"] = context_override["selected_editable_objects"] = objs
                with bpy.context.temp_override(**context_override):
                    bpy.ops.object.join()
                target.data.name += "-merge"
                for ifc_definition_id in id_set[group_name][1:]:
                    del self.added_data[ifc_definition_id]
            except:
                print("Merge failed")

    def merge_materials_by_colour(self):
        cleaned_materials = {}
        for m in bpy.data.materials:
            key = "-".join([str(x) for x in m.diffuse_color])
            cleaned_materials[key] = {"diffuse_color": m.diffuse_color}

        for cleaned_material in cleaned_materials.values():
            cleaned_material["material"] = bpy.data.materials.new("Merged Material")
            cleaned_material["material"].diffuse_color = cleaned_material["diffuse_color"]

        for obj in self.added_data.values():
            if not isinstance(obj, bpy.types.Object):
                continue
            if not hasattr(obj, "material_slots") or not obj.material_slots:
                continue
            for slot in obj.material_slots:
                m = slot.material
                key = "-".join([str(x) for x in m.diffuse_color])
                slot.material = cleaned_materials[key]["material"]

        for material in self.material_creator.materials.values():
            bpy.data.materials.remove(material)

    def add_project_to_scene(self):
        try:
            bpy.context.scene.collection.children.link(self.project["blender"])
        except:
            # Occurs when reloading a project
            pass
        project_collection = bpy.context.view_layer.layer_collection.children[self.project["blender"].name]
        types_collection = project_collection.children[self.type_collection.name]
        types_collection.hide_viewport = False
        for obj in types_collection.collection.objects:  # turn off all objects inside Types collection.
            obj.hide_set(True)

    def clean_mesh(self):
        obj = None
        last_obj = None
        for obj in self.added_data.values():
            if not isinstance(obj, bpy.types.Object):
                continue
            if obj.type == "MESH":
                obj.select_set(True)
                last_obj = obj
        if not last_obj:
            return

        # temporarily unhide types collection to make sure all objects will be cleaned
        project_collection = bpy.context.view_layer.layer_collection.children[self.project["blender"].name]
        types_collection = project_collection.children[self.type_collection.name]
        types_collection.hide_viewport = False
        bpy.context.view_layer.objects.active = last_obj

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.editmode_toggle()

        types_collection.hide_viewport = True
        bpy.context.view_layer.objects.active = last_obj
        IfcStore.edited_objs.clear()

    def load_file(self):
        self.ifc_import_settings.logger.info("loading file %s", self.ifc_import_settings.input_file)
        if not bpy.context.scene.BIMProperties.ifc_file:
            bpy.context.scene.BIMProperties.ifc_file = self.ifc_import_settings.input_file
        self.file = IfcStore.get_file()

    def calculate_unit_scale(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

    def set_units(self):
        units = self.file.by_type("IfcUnitAssignment")[0]
        for unit in units.Units:
            if unit.is_a("IfcNamedUnit") and unit.UnitType == "LENGTHUNIT":
                if unit.is_a("IfcSIUnit"):
                    bpy.context.scene.unit_settings.system = "METRIC"
                    if unit.Name == "METRE":
                        if not unit.Prefix:
                            bpy.context.scene.unit_settings.length_unit = "METERS"
                        else:
                            bpy.context.scene.unit_settings.length_unit = f"{unit.Prefix}METERS"
                else:
                    bpy.context.scene.unit_settings.system = "IMPERIAL"
                    name = unit.Name.lower()
                    if name == "inch":
                        bpy.context.scene.unit_settings.length_unit = "INCHES"
                    elif name == "foot":
                        bpy.context.scene.unit_settings.length_unit = "FEET"
            elif unit.is_a("IfcNamedUnit") and unit.UnitType == "AREAUNIT":
                name = unit.Name if unit.is_a("IfcSIUnit") else unit.Name.lower()
                try:
                    bpy.context.scene.BIMProperties.area_unit = "{}{}".format(
                        unit.Prefix + "/" if hasattr(unit, "Prefix") and unit.Prefix else "", name
                    )
                except:  # Probably an invalid unit.
                    bpy.context.scene.BIMProperties.area_unit = "SQUARE_METRE"
            elif unit.is_a("IfcNamedUnit") and unit.UnitType == "VOLUMEUNIT":
                name = unit.Name if unit.is_a("IfcSIUnit") else unit.Name.lower()
                try:
                    bpy.context.scene.BIMProperties.volume_unit = "{}{}".format(
                        unit.Prefix + "/" if hasattr(unit, "Prefix") and unit.Prefix else "", name
                    )
                except:  # Probably an invalid unit.
                    bpy.context.scene.BIMProperties.volume_unit = "CUBIC_METRE"

    def create_project(self):
        project = self.file.by_type("IfcProject")[0]
        self.project = {"ifc": project}
        obj = tool.Ifc.get_object(project)
        if obj:
            self.project["blender"] = obj.BIMObjectProperties.collection
            self.has_existing_project = True
            return
        self.project["blender"] = bpy.data.collections.new(
            "{}/{}".format(self.project["ifc"].is_a(), self.project["ifc"].Name)
        )
        obj = self.create_product(self.project["ifc"])
        obj.hide_select = True
        self.project["blender"].objects.link(obj)
        self.project["blender"].BIMCollectionProperties.obj = obj
        obj.BIMObjectProperties.collection = self.collections[project.GlobalId] = self.project["blender"]

    def create_collections(self) -> None:
        self.create_spatial_decomposition_collections()
        if self.ifc_import_settings.collection_mode == "DECOMPOSITION":
            self.create_aggregate_and_nest_collections()
        elif self.ifc_import_settings.collection_mode == "SPATIAL_DECOMPOSITION":
            pass

    def create_spatial_decomposition_collections(self) -> None:
        for rel_aggregate in self.project["ifc"].IsDecomposedBy or []:
            self.create_spatial_decomposition_collection(self.project["blender"], rel_aggregate.RelatedObjects)

        # Invalid IFCs may have orphaned spatial structure elements.
        orphaned_spaces = [e for e in self.spatial_elements if e.GlobalId not in self.collections]
        while orphaned_spaces:
            self.create_spatial_decomposition_collection(self.project["blender"], orphaned_spaces)
            orphaned_spaces = [e for e in self.spatial_elements if e.GlobalId not in self.collections]

        tool.Loader.create_project_collection("Views")
        self.type_collection = tool.Loader.create_project_collection("Types")

    def create_spatial_decomposition_collection(
        self, parent: Union[bpy.types.Collection, bpy.types.Object], related_objects: list[ifcopenshell.entity_instance]
    ) -> None:
        for element in related_objects:
            if element not in self.spatial_elements:
                continue
            is_existing = False
            if self.has_existing_project:
                obj = tool.Ifc.get_object(element)
                if obj:
                    is_existing = True
                    collection = obj.BIMObjectProperties.collection
                    self.collections[element.GlobalId] = collection
            if not is_existing:
                collection = bpy.data.collections.new(tool.Loader.get_name(element))
                self.collections[element.GlobalId] = collection
                parent.children.link(collection)
            if element.IsDecomposedBy:
                for rel_aggregate in element.IsDecomposedBy:
                    self.create_spatial_decomposition_collection(collection, rel_aggregate.RelatedObjects)

    def create_aggregate_and_nest_collections(self):
        if self.ifc_import_settings.has_filter:
            rel_aggregates = set()
            for element in self.elements:
                if decomposed_by := element.IsDecomposedBy:
                    rel_aggregates.add(decomposed_by[0])
                elif decomposes := element.Decomposes:
                    rel_aggregates.add(decomposes[0])
                elif nested_by := getattr(element, "IsNestedBy", []):  # IFC2X3 does not have IsNestedBy
                    if next((e for e in nested_by[0].RelatedObjects if not e.is_a("IfcPort")), None):
                        rel_aggregates.add(nested_by[0])
                elif nests := getattr(element, "Nests", []):
                    rel_aggregates.add(nests[0])
                elif element.is_a("IfcSurfaceFeature") and self.file.schema == "IFC4X3":
                    rel_aggregates.add(element.AdheresToElement[0])
        else:
            rel_aggregates = [
                r
                for r in self.file.by_type("IfcRelAggregates")
                if (relating_obj := r.RelatingObject).is_a("IfcElement") or relating_obj.is_a("IfcElementType")
            ] + [
                r
                for r in self.file.by_type("IfcRelNests")
                if (
                    (relating_obj := r.RelatingObject).is_a("IfcElement")
                    or relating_obj.is_a("IfcElementType")
                    or (relating_obj.is_a("IfcPositioningElement") and not relating_obj.is_a("IfcGrid"))
                )
                and [e for e in r.RelatedObjects if not e.is_a("IfcPort")]
            ]
            if self.file.schema == "IFC4X3":
                rel_aggregates += [r for r in self.file.by_type("IfcRelAdheresToElement")]

        if len(rel_aggregates) > 10000:
            # More than 10,000 collections makes Blender unhappy
            print("Skipping aggregate collections for performance.")
            self.ifc_import_settings.collection_mode = "SPATIAL_DECOMPOSITION"
            return

        aggregates: dict[str, dict] = {}
        for rel_aggregate in rel_aggregates:
            element: ifcopenshell.entity_instance = getattr(rel_aggregate, "RelatingObject", None) or getattr(
                rel_aggregate, "RelatingElement"
            )
            collection = bpy.data.collections.new(tool.Loader.get_name(element))
            aggregates[element.GlobalId] = {"element": element, "collection": collection}
            self.collections[element.GlobalId] = collection

        for global_id, aggregate in aggregates.items():
            parent = ifcopenshell.util.element.get_aggregate(aggregate["element"])
            if parent:
                self.collections[parent.GlobalId].children.link(aggregate["collection"])
                continue
            parent = ifcopenshell.util.element.get_container(aggregate["element"])
            if parent:
                self.collections[parent.GlobalId].children.link(aggregate["collection"])
                continue
            if aggregate["element"].is_a("IfcElementType"):
                self.type_collection.children.link(aggregate["collection"])
                continue

    def create_materials(self) -> None:
        for material in self.file.by_type("IfcMaterial"):
            self.create_material(material)

    def create_material(self, material: ifcopenshell.entity_instance) -> bpy.types.Material:
        blender_material = bpy.data.materials.new(material.Name)
        self.link_element(material, blender_material)
        self.material_creator.materials[material.id()] = blender_material
        blender_material.use_fake_user = True
        return blender_material

    def create_styles(self) -> None:
        parsed_styles = set()

        for material_definition_representation in self.file.by_type("IfcMaterialDefinitionRepresentation"):
            material = material_definition_representation.RepresentedMaterial
            blender_material = self.material_creator.materials[material.id()]
            for representation in material_definition_representation.Representations:
                styles = []
                for styled_item in representation.Items:
                    styles.extend(styled_item.Styles)
                while styles:
                    style = styles.pop()
                    if style.is_a("IfcSurfaceStyle"):
                        self.create_style(style, blender_material)
                        parsed_styles.add(style.id())
                    elif style.is_a("IfcPresentationStyleAssignment"):
                        styles.extend(style.Styles)

        for style in self.file.by_type("IfcSurfaceStyle"):
            if style.id() in parsed_styles:
                continue
            self.create_style(style)

    def create_style(
        self, style: ifcopenshell.entity_instance, blender_material: Optional[bpy.types.Material] = None
    ) -> None:
        if not blender_material:
            name = style.Name or str(style.id())
            blender_material = bpy.data.materials.new(name)
            blender_material.use_fake_user = True

        self.link_element(style, blender_material)

        blender_material.BIMMaterialProperties.ifc_style_id = style.id()
        self.material_creator.styles[style.id()] = blender_material

        style_elements = tool.Style.get_style_elements(blender_material)
        if tool.Style.has_blender_external_style(style_elements):
            blender_material.BIMStyleProperties.active_style_type = "External"
        else:
            blender_material.BIMStyleProperties.active_style_type = "Shading"

    def place_objects_in_collections(self) -> None:
        for ifc_definition_id, obj in self.added_data.items():
            if isinstance(obj, bpy.types.Object):
                self.place_object_in_collection(self.file.by_id(ifc_definition_id), obj)

    def place_object_in_collection(self, element: ifcopenshell.entity_instance, obj: bpy.types.Object) -> None:
        if self.ifc_import_settings.collection_mode == "DECOMPOSITION":
            self.place_object_in_decomposition_collection(element, obj)
        elif self.ifc_import_settings.collection_mode == "SPATIAL_DECOMPOSITION":
            self.place_object_in_spatial_decomposition_collection(element, obj)

    def place_object_in_decomposition_collection(
        self, element: ifcopenshell.entity_instance, obj: bpy.types.Object
    ) -> None:
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcGridAxis"):
            return
        elif element.GlobalId in self.collections:
            collection = self.collections[element.GlobalId]
            collection.BIMCollectionProperties.obj = obj
            obj.BIMObjectProperties.collection = collection
            collection.name = obj.name
            return collection.objects.link(obj)
        elif getattr(element, "Decomposes", None):
            aggregate = ifcopenshell.util.element.get_aggregate(element)
            return self.collections[aggregate.GlobalId].objects.link(obj)
        elif getattr(element, "Nests", None) and not element.is_a("IfcPort"):
            nest = ifcopenshell.util.element.get_nest(element)
            return self.collections[nest.GlobalId].objects.link(obj)
        elif element.is_a("IfcSurfaceFeature") and self.file.schema == "IFC4X3":
            adherend = element.AdheresToElement[0].RelatingElement
            return self.collections[adherend.GlobalId].objects.link(obj)

        return self.place_object_in_spatial_decomposition_collection(element, obj)

    def place_object_in_spatial_decomposition_collection(
        self, element: ifcopenshell.entity_instance, obj: bpy.types.Object
    ) -> None:
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcGridAxis"):
            return
        elif element.GlobalId in self.collections:
            collection = self.collections[element.GlobalId]
            collection.BIMCollectionProperties.obj = obj
            obj.BIMObjectProperties.collection = collection
            return collection.objects.link(obj)
        elif element.is_a("IfcTypeObject"):
            return self.type_collection.objects.link(obj)
        elif element.is_a("IfcStructuralMember"):
            return self.structural_member_collection.objects.link(obj)
        elif element.is_a("IfcStructuralConnection"):
            return self.structural_connection_collection.objects.link(obj)
        elif element.is_a("IfcAnnotation"):
            group = self.get_drawing_group(element)
            if group:
                return self.collections[group.GlobalId].objects.link(obj)

        container = ifcopenshell.util.element.get_container(element)
        if container:
            if element.is_a("IfcGrid"):  # TODO: refactor into a more holistic collection mode feature
                grid_collection = bpy.data.collections.get(obj.name)
                if grid_collection:  # Just in case we run into invalid grids from Revit
                    self.collections[container.GlobalId].children.link(grid_collection)
                    grid_collection.objects.link(obj)
            else:
                self.collections[container.GlobalId].objects.link(obj)

        else:
            self.ifc_import_settings.logger.warning("Warning: this object is outside the spatial hierarchy %s", element)
            bpy.context.scene.collection.objects.link(obj)

    def is_curve_annotation(self, element):
        object_type = element.ObjectType
        return object_type in ANNOTATION_TYPES_DATA and ANNOTATION_TYPES_DATA[object_type][3] == "curve"

    def get_drawing_group(self, element):
        for rel in element.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.ObjectType == "DRAWING":
                return rel.RelatingGroup

    def get_element_matrix(self, element: ifcopenshell.entity_instance) -> np.ndarray:
        if isinstance(element, ifcopenshell.sqlite_entity):
            result = self.geometry_cache["shapes"][element.id()]["matrix"]
        else:
            result = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        result[0][3] *= self.unit_scale
        result[1][3] *= self.unit_scale
        result[2][3] *= self.unit_scale
        return result

    def scale_matrix(self, matrix: np.array) -> np.array:
        matrix[0][3] *= self.unit_scale
        matrix[1][3] *= self.unit_scale
        matrix[2][3] *= self.unit_scale
        return matrix

    def get_representation_id(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            if not representation.is_a("IfcShapeRepresentation"):
                continue
            if (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType != "MappedRepresentation"
            ):
                return representation.id()
            elif representation.RepresentationIdentifier == "Body":
                return representation.Items[0].MappingSource.MappedRepresentation.id()

    def get_representation_cartesian_transformation(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            if not representation.is_a("IfcShapeRepresentation"):
                continue
            if (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType == "MappedRepresentation"
            ):
                return representation.Items[0].MappingTarget

    def create_curve(self, element: ifcopenshell.entity_instance, shape) -> bpy.types.Curve:
        if hasattr(shape, "geometry"):
            geometry = shape.geometry
        else:
            geometry = shape

        curve = bpy.data.curves.new(tool.Loader.get_mesh_name(geometry), type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2

        e = geometry.edges
        v = geometry.verts
        vertices = [[v[i], v[i + 1], v[i + 2], 1] for i in range(0, len(v), 3)]
        edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
        v2 = None
        for edge in edges:
            v1 = vertices[edge[0]]
            if v1 != v2:
                polyline = curve.splines.new("POLY")
                polyline.points[-1].co = mathutils.Vector(v1)
            v2 = vertices[edge[1]]
            polyline.points.add(1)
            polyline.points[-1].co = mathutils.Vector(v2)
        return curve

    def create_mesh(self, element: ifcopenshell.entity_instance, shape) -> bpy.types.Mesh:
        try:
            if hasattr(shape, "geometry"):
                # shape is ifcopenshell_wrapper.TriangulationElement
                geometry: ifcopenshell_wrapper.Triangulation = shape.geometry
            else:
                geometry: ifcopenshell_wrapper.Triangulation = shape

            mesh = bpy.data.meshes.new(tool.Loader.get_mesh_name(geometry))

            props = bpy.context.scene.BIMGeoreferenceProperties
            if (
                props.has_blender_offset
                and geometry.verts
                and self.is_point_far_away((geometry.verts[0], geometry.verts[1], geometry.verts[2]))
            ):
                offset_point = np.array(
                    (
                        float(props.blender_eastings),
                        float(props.blender_northings),
                        float(props.blender_orthogonal_height),
                        0.0,
                    )
                )
                if geometry != shape:
                    m = shape.transformation.matrix.data
                    mat = np.array(
                        ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
                    )
                    offset_point = np.linalg.inv(mat) @ offset_point
                verts = [None] * len(geometry.verts)
                for i in range(0, len(geometry.verts), 3):
                    # Note: this enh2xyz call is crazy slow.
                    verts[i], verts[i + 1], verts[i + 2] = ifcopenshell.util.geolocation.enh2xyz(
                        geometry.verts[i],
                        geometry.verts[i + 1],
                        geometry.verts[i + 2],
                        offset_point[0] * self.unit_scale,
                        offset_point[1] * self.unit_scale,
                        offset_point[2] * self.unit_scale,
                        float(props.blender_x_axis_abscissa),
                        float(props.blender_x_axis_ordinate),
                    )
                mesh["has_cartesian_point_offset"] = True
            else:
                verts = geometry.verts
                mesh["has_cartesian_point_offset"] = False

            if geometry.faces:
                num_vertices = len(verts) // 3
                total_faces = len(geometry.faces)
                loop_start = range(0, total_faces, 3)
                num_loops = total_faces // 3
                loop_total = [3] * num_loops
                num_vertex_indices = len(geometry.faces)

                # See bug 3546
                # ios_edges holds true edges that aren't triangulated.
                #
                # we do `.tolist()` because Blender can't assign `np.int32` to it's custom attributes
                mesh["ios_edges"] = list(set(tuple(e) for e in ifcopenshell.util.shape.get_edges(geometry).tolist()))

                mesh.vertices.add(num_vertices)
                mesh.vertices.foreach_set("co", verts)
                mesh.loops.add(num_vertex_indices)
                mesh.loops.foreach_set("vertex_index", geometry.faces)
                mesh.polygons.add(num_loops)
                mesh.polygons.foreach_set("loop_start", loop_start)
                mesh.polygons.foreach_set("loop_total", loop_total)
                mesh.polygons.foreach_set("use_smooth", [0] * total_faces)
                mesh.update()
            else:
                e = geometry.edges
                v = verts
                vertices = [[v[i], v[i + 1], v[i + 2]] for i in range(0, len(v), 3)]
                edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
                mesh.from_pydata(vertices, edges, [])

            mesh["ios_materials"] = [int(m.name.split("-")[2]) for m in geometry.materials]
            mesh["ios_material_ids"] = geometry.material_ids
            return mesh
        except:
            self.ifc_import_settings.logger.error("Could not create mesh for %s", element)
            import traceback

            print(traceback.format_exc())

    def a2p(self, o: mathutils.Vector, z: mathutils.Vector, x: mathutils.Vector) -> mathutils.Matrix:
        y = z.cross(x)
        r = mathutils.Matrix((x, y, z, o))
        r.resize_4x4()
        r.transpose()
        return r

    def get_axis2placement(self, plc: ifcopenshell.entity_instance) -> mathutils.Matrix:
        if plc.is_a("IfcAxis2Placement3D"):
            z = mathutils.Vector(plc.Axis.DirectionRatios if plc.Axis else (0, 0, 1))
            x = mathutils.Vector(plc.RefDirection.DirectionRatios if plc.RefDirection else (1, 0, 0))
            o = plc.Location.Coordinates
        else:
            z = mathutils.Vector((0, 0, 1))
            if plc.RefDirection:
                x = mathutils.Vector(list(plc.RefDirection.DirectionRatios) + [0])
            else:
                x = mathutils.Vector((1, 0, 0))
            o = list(plc.Location.Coordinates) + [0]
        return self.a2p(o, z, x)

    def get_cartesiantransformationoperator(self, plc):
        x = mathutils.Vector(plc.Axis1.DirectionRatios if plc.Axis1 else (1, 0, 0))
        z = x.cross(mathutils.Vector(plc.Axis2.DirectionRatios if plc.Axis2 else (0, 1, 0)))
        o = plc.LocalOrigin.Coordinates
        return self.a2p(o, z, x)

    def get_local_placement(self, plc: Optional[ifcopenshell.entity_instance] = None) -> mathutils.Matrix:
        if plc is None:
            return mathutils.Matrix()
        if plc.PlacementRelTo is None:
            parent = mathutils.Matrix()
        else:
            parent = self.get_local_placement(plc.PlacementRelTo)
        return parent @ self.get_axis2placement(plc.RelativePlacement)

    def set_default_context(self):
        for subcontext in self.file.by_type("IfcGeometricRepresentationSubContext"):
            if subcontext.ContextIdentifier == "Body":
                bpy.context.scene.BIMRootProperties.contexts = str(subcontext.id())
                break

    def link_element(self, element: ifcopenshell.entity_instance, obj: IFC_CONNECTED_TYPE) -> None:
        self.added_data[element.id()] = obj
        tool.Ifc.link(element, obj)

    def set_matrix_world(self, obj: bpy.types.Object, matrix_world: mathutils.Matrix) -> None:
        obj.matrix_world = matrix_world
        tool.Geometry.record_object_position(obj)

    def setup_viewport_camera(self):
        context_override = tool.Blender.get_viewport_context()
        with bpy.context.temp_override(**context_override):
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.view3d.view_selected()
            bpy.ops.object.select_all(action="DESELECT")

    def setup_arrays(self):
        for element in self.file.by_type("IfcElement"):
            pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not pset_data or not pset_data.get("Data", None):  # skip array children
                continue
            for i in range(len(json.loads(pset_data["Data"]))):
                tool.Blender.Modifier.Array.set_children_lock_state(element, i, True)
                tool.Blender.Modifier.Array.constrain_children_to_parent(element)


class IfcImportSettings:
    def __init__(self):
        self.logger: logging.Logger = None
        self.input_file = None
        self.diff_file = None
        self.should_use_cpu_multiprocessing = True
        self.merge_mode = None
        self.should_merge_materials_by_colour = False
        self.should_load_geometry = True
        self.should_use_native_meshes = False
        self.should_clean_mesh = False
        self.should_cache = True
        self.is_coordinating = True
        self.deflection_tolerance = 0.001
        self.angular_tolerance = 0.5
        self.void_limit = 30
        self.distance_limit = 1000
        self.false_origin = None
        self.element_offset = 0
        self.element_limit = 30000
        self.has_filter = None
        self.should_filter_spatial_elements = True
        self.should_setup_viewport_camera = True
        self.elements: set[ifcopenshell.entity_instance] = set()
        self.collection_mode = "DECOMPOSITION"

    @staticmethod
    def factory(context=None, input_file=None, logger=None):
        scene_diff = bpy.context.scene.DiffProperties
        props = bpy.context.scene.BIMProjectProperties
        settings = IfcImportSettings()
        settings.input_file = input_file
        if logger is None:
            logger = logging.getLogger("ImportIFC")
        settings.logger = logger
        settings.diff_file = scene_diff.diff_json_file
        settings.collection_mode = props.collection_mode
        settings.should_use_cpu_multiprocessing = props.should_use_cpu_multiprocessing
        settings.merge_mode = props.merge_mode
        settings.should_merge_materials_by_colour = props.should_merge_materials_by_colour
        settings.should_load_geometry = props.should_load_geometry
        settings.should_use_native_meshes = props.should_use_native_meshes
        settings.should_clean_mesh = props.should_clean_mesh
        settings.should_cache = props.should_cache
        settings.is_coordinating = props.is_coordinating
        settings.deflection_tolerance = props.deflection_tolerance
        settings.angular_tolerance = props.angular_tolerance
        settings.void_limit = props.void_limit
        settings.distance_limit = props.distance_limit
        settings.false_origin = [float(o) for o in props.false_origin.split(",")] if props.false_origin else None
        if settings.false_origin == [0, 0, 0]:
            settings.false_origin = None
        settings.element_offset = props.element_offset
        settings.element_limit = props.element_limit
        return settings
