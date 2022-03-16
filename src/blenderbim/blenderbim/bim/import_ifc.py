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

import os
import re
import bpy
import time
import bmesh
import shutil
import logging
import threading
import mathutils
import numpy as np
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.selector
import ifcopenshell.util.geolocation
import blenderbim.tool as tool
from itertools import chain, accumulate
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.drawing.prop import get_diagram_scales


class FileCopy(threading.Thread):
    def __init__(self, file_path, destination):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.destination = destination

    def run(self):
        shutil.copy(self.file_path, self.destination)


class MaterialCreator:
    def __init__(self, ifc_import_settings, ifc_importer):
        self.mesh = None
        self.materials = {}
        self.styles = {}
        self.parsed_meshes = set()
        self.ifc_import_settings = ifc_import_settings
        self.ifc_importer = ifc_importer

    def create(self, element, obj, mesh):
        self.mesh = mesh
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

    def add_default_material(self, element):
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

    def load_existing_materials(self):
        for material in bpy.data.materials:
            if material.BIMObjectProperties.ifc_definition_id:
                self.materials[material.BIMObjectProperties.ifc_definition_id] = material
            if material.BIMMaterialProperties.ifc_style_id:
                self.styles[material.BIMMaterialProperties.ifc_style_id] = material

    def parse_representations(self, element):
        has_parsed = False
        if hasattr(element, "Representation"):
            for representation in element.Representation.Representations:
                if self.parse_representation(representation):
                    has_parsed = True
        elif hasattr(element, "RepresentationMaps"):
            for representation_map in element.RepresentationMaps:
                if self.parse_representation(representation_map.MappedRepresentation):
                    has_parsed = True
        return has_parsed

    def parse_representation(self, representation):
        has_parsed = False
        representation_items = self.resolve_all_representation_items(representation)
        for item in representation_items:
            if self.parse_representation_item(item):
                has_parsed = True
        return has_parsed

    def parse_representation_item(self, item):
        if not item.StyledByItem:
            return
        style_ids = [e.id() for e in self.ifc_importer.file.traverse(item.StyledByItem[0]) if e.is_a("IfcSurfaceStyle")]
        if not style_ids:
            return
        for style_id in style_ids:
            material = self.styles[style_id]
            if self.mesh.materials.find(material.name) == -1:
                self.mesh.materials.append(material)
        return True

    def assign_material_slots_to_faces(self):
        if "ios_materials" not in self.mesh or not self.mesh["ios_materials"]:
            return
        if len(self.obj.material_slots) == 1:
            return
        material_to_slot = {}
        for i, material in enumerate(self.mesh["ios_materials"]):
            slot_index = self.obj.material_slots.find(self.styles[material].name)
            material_to_slot[i] = slot_index

        if len(self.mesh.polygons) == len(self.mesh["ios_material_ids"]):
            material_index = [
                (material_to_slot[mat_id] if mat_id != -1 else 0) for mat_id in self.mesh["ios_material_ids"]
            ]
            self.mesh.polygons.foreach_set("material_index", material_index)

    def resolve_all_representation_items(self, representation):
        items = []
        for item in representation.Items:
            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            items.append(item)
        return items


class IfcImporter:
    def __init__(self, ifc_import_settings):
        self.ifc_import_settings = ifc_import_settings
        self.diff = None
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        self.settings.set_deflection_tolerance(self.ifc_import_settings.deflection_tolerance)
        self.settings.set_angular_tolerance(self.ifc_import_settings.angular_tolerance)
        # See https://github.com/IfcOpenShell/IfcOpenShell/issues/2053
        # self.settings.set(self.settings.STRICT_TOLERANCE, True)
        self.settings_native = ifcopenshell.geom.settings()
        self.settings_native.set(self.settings_native.INCLUDE_CURVES, True)
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set(self.settings_2d.INCLUDE_CURVES, True)
        self.project = None
        self.collections = {}
        self.elements = set()
        self.type_collection = None
        self.type_products = {}
        self.openings = {}
        self.meshes = {}
        self.mesh_shapes = {}
        self.time = 0
        self.unit_scale = 1
        self.added_data = {}
        self.native_elements = set()
        self.native_data = {}

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
        self.progress = 0
        self.profile_code("Starting import process")
        self.load_file()
        self.profile_code("Loading file")
        self.calculate_unit_scale()
        self.profile_code("Calculate unit scale")
        self.calculate_model_offset()
        self.profile_code("Calculate model offset")
        self.set_units()
        self.profile_code("Set units")
        self.create_project()
        self.profile_code("Create project")
        self.process_element_filter()
        self.profile_code("Process element filter")
        self.process_context_filter()
        self.profile_code("Process context filter")
        self.create_collections()
        self.profile_code("Create collections")
        self.create_openings_collection()
        self.profile_code("Create opening collection")
        self.create_materials()
        self.profile_code("Create materials")
        self.create_styles()
        self.profile_code("Create styles")
        self.create_annotations()
        self.profile_code("Create annotation")
        self.parse_native_elements()
        self.profile_code("Parsing native elements")
        self.create_native_elements()
        self.profile_code("Create native elements")
        self.create_elements()
        self.profile_code("Create elements")
        self.create_grids()
        self.profile_code("Create grids")
        self.create_spatial_elements()
        self.profile_code("Create spatial elements")
        self.create_structural_items()
        self.profile_code("Create structural items")
        self.create_type_products()
        self.profile_code("Create type products")
        self.place_objects_in_collections()
        self.profile_code("Place objects in collections")
        if self.ifc_import_settings.should_merge_by_class:
            self.merge_by_class()
            self.profile_code("Merging by class")
        elif self.ifc_import_settings.should_merge_by_material:
            self.merge_by_material()
            self.profile_code("Merging by material")
        if self.ifc_import_settings.should_merge_materials_by_colour or len(self.material_creator.materials) > 300:
            self.merge_materials_by_colour()
            self.profile_code("Merging by colour")
        self.add_project_to_scene()
        self.profile_code("Add project to scene")
        if self.ifc_import_settings.should_clean_mesh and len(self.file.by_type("IfcElement")) < 1000:
            self.clean_mesh()
            self.profile_code("Mesh cleaning")
        self.set_default_context()
        self.profile_code("Setting default context")
        self.update_progress(100)
        bpy.context.window_manager.progress_end()

    def is_element_far_away(self, element):
        try:
            placement = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            point = placement[:, 3][0:3]
            return self.is_point_far_away(point, is_meters=False)
        except:
            pass

    def is_point_far_away(self, point, is_meters=True):
        # Locations greater than 1km are not considered "small sites" according to the georeferencing guide
        limit = 1000 if is_meters else (1000 / self.unit_scale)
        coords = point
        if hasattr(point, "Coordinates"):
            coords = point.Coordinates
        return abs(coords[0]) > limit or abs(coords[1]) > limit or abs(coords[2]) > limit

    def process_context_filter(self):
        # Facetation is to accommodate broken Revit files
        # See https://forums.buildingsmart.org/t/suggestions-on-how-to-improve-clarity-of-representation-context-usage-in-documentation/3663/6?u=moult
        self.body_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier in ["Body", "Facetation"]
        ]
        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        self.body_contexts.extend(
            [
                c.id()
                for c in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
                if c.ContextType == "Model"
            ]
        )
        if self.body_contexts:
            self.settings.set_context_ids(self.body_contexts)
        # Annotation is to accommodate broken Revit files
        # See https://github.com/Autodesk/revit-ifc/issues/187
        self.plan_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationContext")
            if c.ContextType in ["Plan", "Annotation"]
        ]
        if self.plan_contexts:
            self.settings_2d.set_context_ids(self.plan_contexts)

    def process_element_filter(self):
        if self.ifc_import_settings.has_filter:
            self.elements = set(self.ifc_import_settings.elements)
            # TODO: enable filtering for annotations
            self.annotations = set(self.file.by_type("IfcAnnotation"))
        else:
            self.elements = set(self.file.by_type("IfcElement"))
            self.annotations = set(self.file.by_type("IfcAnnotation"))

        if self.ifc_import_settings.has_filter and self.ifc_import_settings.should_filter_spatial_elements:
            self.spatial_elements = self.get_spatial_elements_filtered_by_elements(self.elements)
        else:
            if self.file.schema == "IFC2X3":
                self.spatial_elements = set(self.file.by_type("IfcSpatialStructureElement"))
            else:
                self.spatial_elements = set(self.file.by_type("IfcSpatialElement"))

    def get_spatial_elements_filtered_by_elements(self, elements):
        leaf_spatial_elements = set([ifcopenshell.util.element.get_container(e) for e in elements])
        results = set()
        for spatial_element in leaf_spatial_elements:
            while True:
                results.add(spatial_element)
                spatial_element = ifcopenshell.util.element.get_aggregate(spatial_element)
                if not spatial_element or spatial_element.is_a("IfcContext"):
                    break
        return results

    def parse_native_elements(self):
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
        representations = self.get_transformed_body_representations(element.Representation.Representations)

        # Single swept disk solids (e.g. rebar) are better natively represented as beveled curves
        if self.is_native_swept_disk_solid(representations):
            self.native_data[element.GlobalId] = {
                "representations": representations,
                "representation": self.get_body_representation(element.Representation.Representations),
                "type": "IfcSweptDiskSolid",
            }
            return True
        # FacetedBreps (without voids) are meshes. See #841.
        # Commented out as seems currently too slow.
        # if self.is_native_faceted_brep(representations):
        #    self.native_data[element.GlobalId] = {
        #        "representations": representations,
        #        "representation": self.get_body_representation(element.Representation.Representations),
        #        "type": "IfcFacetedBrep",
        #    }
        #    return True

    def is_native_swept_disk_solid(self, representations):
        for representation in representations:
            items = representation["raw"].Items or []  # Be forgiving of invalid IFCs because Revit :(
            if len(items) == 1 and items[0].is_a("IfcSweptDiskSolid"):
                return True
        return False

    def is_native_faceted_brep(self, representations):
        for representation in representations:
            for i in representation["raw"].Items:
                if i.is_a() != "IfcFacetedBrep":
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

    def calculate_model_offset(self):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            return
        if self.file.schema == "IFC2X3":
            project = self.file.by_type("IfcProject")[0]
        else:
            project = self.file.by_type("IfcContext")[0]
        site = self.find_decomposed_ifc_class(project, "IfcSite")
        if site and self.is_element_far_away(site):
            return self.guess_georeferencing(site)
        building = self.find_decomposed_ifc_class(project, "IfcBuilding")
        if building and self.is_element_far_away(building):
            return self.guess_georeferencing(building)
        return self.guess_absolute_coordinate()

    def guess_georeferencing(self, element):
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

    def guess_absolute_coordinate(self):
        # Civil BIM applications like to work in absolute coordinates, where the ObjectPlacement is 0,0,0 but each
        # individual coordinate of the shape representation is in absolute values.
        offset_point = self.get_offset_point()
        if not offset_point:
            return
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.blender_eastings = str(offset_point[0])
        props.blender_northings = str(offset_point[1])
        props.blender_orthogonal_height = str(offset_point[2])
        props.has_blender_offset = True

    def get_offset_point(self):
        elements_checked = 0
        # If more than these points aren't far away, the file probably isn't absolutely positioned
        element_checking_threshold = 100
        if self.file.schema == "IFC2X3":
            # IFC2X3 does not have IfcCartesianPointList3D
            point_lists = []
        else:
            point_lists = self.file.by_type("IfcCartesianPointList3D")
        for point_list in point_lists:
            elements_checked += 1
            if elements_checked > element_checking_threshold:
                return
            for i, point in enumerate(point_list.CoordList):
                if len(point) == 3 and self.is_point_far_away(point, is_meters=False):
                    return point

        for point in self.file.by_type("IfcCartesianPoint"):
            is_used_in_placement = False
            for inverse in self.file.get_inverse(point):
                if inverse.is_a("IfcAxis2Placement3D"):
                    is_used_in_placement = True
                    break
            if is_used_in_placement:
                continue
            elements_checked += 1
            if elements_checked > element_checking_threshold:
                return
            if len(point.Coordinates) == 3 and self.is_point_far_away(point, is_meters=False):
                return point.Coordinates

    def apply_blender_offset_to_matrix_world(self, obj, matrix):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            if obj.data and obj.data.get("has_cartesian_point_offset", None):
                obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
            elif self.is_point_far_away((matrix[0, 3], matrix[1, 3], matrix[2, 3])):
                obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
                matrix = ifcopenshell.util.geolocation.global2local(
                    matrix,
                    float(props.blender_eastings) * self.unit_scale,
                    float(props.blender_northings) * self.unit_scale,
                    float(props.blender_orthogonal_height) * self.unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )

        if self.ifc_import_settings.should_offset_model:
            matrix[0, 3] += self.ifc_import_settings.model_offset_coordinates[0]
            matrix[1, 3] += self.ifc_import_settings.model_offset_coordinates[1]
            matrix[2, 3] += self.ifc_import_settings.model_offset_coordinates[2]

        return mathutils.Matrix(matrix.tolist())

    def find_decomposed_ifc_class(self, element, ifc_class):
        if element.is_a(ifc_class):
            return element
        rel_aggregates = element.IsDecomposedBy
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                result = self.find_decomposed_ifc_class(part, ifc_class)
                if result:
                    return result

    def create_grids(self):
        grids = self.file.by_type("IfcGrid")
        for grid in grids:
            shape = None
            if not grid.UAxes or not grid.VAxes:
                # Revit can create invalid grids
                self.ifc_import_settings.logger.error("An invalid grid was found %s", grid)
                continue
            if grid.Representation:
                shape = ifcopenshell.geom.create_shape(self.settings_2d, grid)
            grid_obj = self.create_product(grid, shape)
            collection = bpy.data.collections.new(self.get_name(grid))
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
            shape = ifcopenshell.geom.create_shape(self.settings_2d, axis.AxisCurve)
            mesh = self.create_mesh(axis, shape)
            obj = bpy.data.objects.new(f"IfcGridAxis/{axis.AxisTag}", mesh)
            self.link_element(axis, obj)
            self.set_matrix_world(obj, grid_obj.matrix_world)
            grid_collection.objects.link(obj)

    def create_type_products(self):
        # TODO allow filtering of spatial elements too
        if self.ifc_import_settings.has_filter:
            type_products = set([ifcopenshell.util.element.get_type(e) for e in self.elements])
        else:
            type_products = self.file.by_type("IfcTypeProduct")

        for type_product in type_products:
            if not type_product:
                continue
            self.create_type_product(type_product)

    def create_type_product(self, element):
        self.ifc_import_settings.logger.info("Creating object %s", element)
        representation_map = self.get_type_product_body_representation_map(element)
        mesh = None
        if representation_map:
            representation = representation_map.MappedRepresentation
            mesh_name = "{}/{}".format(representation.ContextOfItems.id(), representation.id())
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                try:
                    shape = ifcopenshell.geom.create_shape(self.settings, representation_map.MappedRepresentation)
                    mesh = self.create_mesh(element, shape)
                    self.link_mesh(shape, mesh)
                    self.meshes[mesh_name] = mesh
                except:
                    self.ifc_import_settings.logger.error("Failed to generate shape for %s", element)
        obj = bpy.data.objects.new(self.get_name(element), mesh)
        self.link_element(element, obj)
        self.material_creator.create(element, obj, mesh)
        self.type_products[element.GlobalId] = obj

    def get_type_product_body_representation_map(self, element):
        if not element.RepresentationMaps:
            return
        for representation_map in element.RepresentationMaps:
            context = representation_map.MappedRepresentation.ContextOfItems
            if (
                context.ContextType == "Model"
                and context.ContextIdentifier == "Body"
                and context.TargetView == "MODEL_VIEW"
            ):
                return representation_map

    def create_native_elements(self):
        total = 0
        checkpoint = time.time()
        for element in self.native_elements:
            total += 1
            if total % 250 == 0:
                print("{} elements processed in {:.2f}s ...".format(total, time.time() - checkpoint))
                checkpoint = time.time()
            native_data = self.native_data[element.GlobalId]
            representation = native_data["representation"]
            if not representation:
                continue
            context_id = representation.ContextOfItems.id() if hasattr(representation, "ContextOfItems") else 0
            mesh_name = f"{context_id}/{representation.id()}"
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                if native_data["type"] == "IfcSweptDiskSolid":
                    mesh = self.create_native_swept_disk_solid(element, mesh_name)
                elif native_data["type"] == "IfcFacetedBrep":
                    mesh = self.create_native_faceted_brep(element, mesh_name)
                mesh.BIMMeshProperties.ifc_definition_id = representation.id()
                mesh.name = mesh_name
                self.meshes[mesh_name] = mesh
            self.create_product(element, mesh=mesh)
        print("Done creating geometry")

    def create_spatial_elements(self):
        self.create_generic_elements(self.spatial_elements)

    def create_annotations(self):
        self.create_generic_elements(self.annotations)

    def create_elements(self):
        self.create_generic_elements(self.elements)

    def create_generic_elements(self, elements):
        # Based on my experience in viewing BIM models, representations are prioritised as follows:
        # 1. 3D Body, 2. 2D Plans, 3. Point clouds, 4. No representation
        # If an element has a representation that doesn't follow 1, 2, or 3, it will not show by default.
        # The user can load them later if they want to view them.
        products = self.create_products(elements)
        elements -= products
        products = self.create_curve_products(elements)
        elements -= products
        products = self.create_pointclouds(elements)
        elements -= products
        for element in elements:
            self.create_product(element)

    def create_products(self, products):
        results = set()
        if not products:
            return results
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings, self.file, multiprocessing.cpu_count(), include=products
            )
        else:
            iterator = ifcopenshell.geom.iterator(self.settings, self.file, include=products)
        cache = IfcStore.get_cache()
        if cache:
            iterator.set_cache(cache)
        valid_file = iterator.initialize()
        if not valid_file:
            return results
        checkpoint = time.time()
        total = 0
        start_progress = self.progress
        progress_range = 85 - start_progress
        while True:
            total += 1
            if total % 250 == 0:
                print(
                    "{} ({}%) elements processed in {:.2f}s ...".format(
                        total, iterator.progress(), time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
                self.update_progress((iterator.progress() / 100 * progress_range) + start_progress)
            shape = iterator.get()
            if shape:
                product = self.file.by_id(shape.guid)
                if self.body_contexts:
                    self.create_product(product, shape)
                    results.add(product)
                else:
                    if shape.context not in ["Body", "Facetation"] and IfcStore.get_element(shape.guid):
                        # We only load a single context, and we prioritise the Body context. See #1290.
                        pass
                    else:
                        self.create_product(product, shape)
                        results.add(product)
            if not iterator.next():
                break
        print("Done creating geometry")
        return results

    def create_structural_items(self):
        # Create structural collections
        self.structural_member_collection = bpy.data.collections.new("Members")
        self.structural_connection_collection = bpy.data.collections.new("Connections")
        self.structural_collection = bpy.data.collections.new("StructuralItems")
        self.structural_collection.children.link(self.structural_member_collection)
        self.structural_collection.children.link(self.structural_connection_collection)
        self.project["blender"].children.link(self.structural_collection)

        self.create_curve_products(self.file.by_type("IfcStructuralCurveMember"))
        self.create_curve_products(self.file.by_type("IfcStructuralCurveConnection"))
        self.create_curve_products(self.file.by_type("IfcStructuralSurfaceMember"))
        self.create_curve_products(self.file.by_type("IfcStructuralSurfaceConnection"))
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
            if representation.RepresentationType == "PointCloud":
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

    def create_pointclouds(self, products):
        result = set()
        for product in products:
            representation = self.get_pointcloud_representation(product)
            if representation is not None:
                pointcloud = self.create_pointcloud(product, representation)
                if pointcloud is not None:
                    result.add(pointcloud)

        return result

    def create_pointcloud(self, product, representation):
        placement_matrix = ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement)
        vertex_list = []
        for item in representation.Items:
            if item.is_a("IfcCartesianPointList"):
                vertex_list.extend(
                    mathutils.Vector(list(coordinates)) * self.unit_scale for coordinates in item.CoordList
                )
            elif item.is_a("IfcCartesianPoint"):
                vertex_list.append(mathutils.Vector(list(item.Coordinates)) * self.unit_scale)

        if len(vertex_list) == 0:
            return None

        mesh_name = f"{representation.ContextOfItems.id()}/{representation.id()}"
        mesh = bpy.data.meshes.new(mesh_name)
        mesh.from_pydata(vertex_list, [], [])

        obj = bpy.data.objects.new("{}/{}".format(product.is_a(), product.Name), mesh)
        self.set_matrix_world(obj, self.apply_blender_offset_to_matrix_world(obj, placement_matrix))
        self.link_element(product, obj)
        return product

    def create_curve_products(self, products):
        results = set()
        if not products:
            return results
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings_2d, self.file, multiprocessing.cpu_count(), include=products
            )
        else:
            iterator = ifcopenshell.geom.iterator(self.settings_2d, self.file, include=products)
        cache = IfcStore.get_cache()
        if cache:
            iterator.set_cache(cache)
        valid_file = iterator.initialize()
        if not valid_file:
            return results
        checkpoint = time.time()
        total = 0
        while True:
            total += 1
            if total % 250 == 0:
                print("{} elements processed in {:.2f}s ...".format(total, time.time() - checkpoint))
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                product = self.file.by_id(shape.guid)
                self.create_product(self.file.by_id(shape.guid), shape)
                results.add(product)
            if not iterator.next():
                break
        print("Done creating geometry")
        return results

    def create_product(self, element, shape=None, mesh=None):
        if element is None:
            return

        self.ifc_import_settings.logger.info("Creating object %s", element)

        if mesh:
            pass
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            mesh = self.create_camera(element, shape)
            self.link_mesh(shape, mesh)
        elif element.is_a("IfcAnnotation") and self.is_curve_annotation(element):
            mesh = self.create_curve(element, shape)
            self.link_mesh(shape, mesh)
        elif shape:
            mesh_name = self.get_mesh_name(shape.geometry)
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                mesh = self.create_mesh(element, shape)
                self.link_mesh(shape, mesh)
                self.meshes[mesh_name] = mesh
        else:
            mesh = None

        obj = bpy.data.objects.new(self.get_name(element), mesh)
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

        self.add_opening_relation(element, obj)

        if element.is_a("IfcOpeningElement"):
            obj.display_type = "WIRE"
        return obj

    def get_representation_item_material_name(self, item):
        if not item.StyledByItem:
            return
        style_ids = [e.id() for e in self.file.traverse(item.StyledByItem[0]) if e.is_a("IfcSurfaceStyle")]
        return style_ids[0] if style_ids else None

    def create_native_faceted_brep(self, element, mesh_name):
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

        for representation in element.Representation.Representations:
            if representation.ContextOfItems.id() not in self.body_contexts:
                continue
            self.convert_representation(representation)

        mesh = bpy.data.meshes.new("Native")
        mesh.vertices.add(self.mesh_data["total_verts"])
        mesh.vertices.foreach_set("co", [c * self.unit_scale for c in self.mesh_data["co"]])
        # mesh.vertices.foreach_set("co", self.mesh_data["co"])
        mesh.loops.add(len(self.mesh_data["vertex_index"]))
        mesh.loops.foreach_set("vertex_index", self.mesh_data["vertex_index"])
        mesh.polygons.add(self.mesh_data["total_polygons"])
        mesh.polygons.foreach_set("loop_start", self.mesh_data["loop_start"])
        mesh.polygons.foreach_set("loop_total", self.mesh_data["loop_total"])
        mesh.update()

        mesh["ios_materials"] = self.mesh_data["materials"]
        mesh["ios_material_ids"] = self.mesh_data["material_ids"]
        return mesh

    def convert_representation(self, representation):
        for item in representation.Items:
            self.convert_representation_item(item)

    def convert_representation_item(self, item):
        if item.is_a("IfcMappedItem"):
            # mapping_target = matrix
            self.convert_representation(item.MappingSource.MappedRepresentation)
        elif item.is_a() == "IfcFacetedBrep":
            self.convert_representation_item_faceted_brep(item)

    def convert_representation_item_faceted_brep(self, item):
        # On a few occasions, we flatten a list. This seems to be the most efficient way to do it.
        # https://stackoverflow.com/questions/20112776/how-do-i-flatten-a-list-of-lists-nested-lists
        mesh = item.get_info_2(recursive=True)

        # For huge face sets it might be better to do a "flatmap" instead of sum()
        # bounds = sum((f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1), ())
        bounds = tuple(chain.from_iterable(f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1))
        # Here are some untested alternatives, are they faster?
        # bounds = tuple((f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1))[0]
        # bounds = chain.from_iterable(f["Bounds"] for f in mesh["Outer"]["CfsFaces"] if len(f["Bounds"]) == 1)

        polygons = [[(p["id"], p["Coordinates"]) for p in b["Bound"]["Polygon"]] for b in bounds]

        for face in mesh["Outer"]["CfsFaces"]:
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

    def create_native_swept_disk_solid(self, element, mesh_name):
        # TODO: georeferencing?
        curve = bpy.data.curves.new(mesh_name, type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        polyline = curve.splines.new("POLY")

        for representation in self.native_data[element.GlobalId]["representations"]:
            for item in representation["raw"].Items:
                # TODO: support inner radius, start param, and end param
                geometry = ifcopenshell.geom.create_shape(self.settings_native, item.Directrix)
                e = geometry.edges
                v = geometry.verts
                vertices = [[v[i], v[i + 1], v[i + 2], 1] for i in range(0, len(v), 3)]
                edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
                v2 = None
                for edge in edges:
                    v1 = vertices[edge[0]]
                    if v1 != v2:
                        polyline = curve.splines.new("POLY")
                        polyline.points[-1].co = representation["matrix"] @ mathutils.Vector(v1)
                    v2 = vertices[edge[1]]
                    polyline.points.add(1)
                    polyline.points[-1].co = representation["matrix"] @ mathutils.Vector(v2)

        curve.bevel_depth = self.unit_scale * item.Radius
        return curve

    def create_native_annotation(self, element, mesh_name):
        # TODO: georeferencing?
        curve = bpy.data.curves.new(mesh_name, type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        polyline = curve.splines.new("POLY")

        for representation in self.native_data[element.GlobalId]["representations"]:
            for item in representation["raw"].Items:
                # TODO: support inner radius, start param, and end param
                geometry = ifcopenshell.geom.create_shape(self.settings_native, item.Directrix)
                e = geometry.edges
                v = geometry.verts
                vertices = [[v[i], v[i + 1], v[i + 2], 1] for i in range(0, len(v), 3)]
                edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
                v2 = None
                for edge in edges:
                    v1 = vertices[edge[0]]
                    if v1 != v2:
                        polyline = curve.splines.new("POLY")
                        polyline.points[-1].co = representation["matrix"] @ mathutils.Vector(v1)
                    v2 = vertices[edge[1]]
                    polyline.points.add(1)
                    polyline.points[-1].co = representation["matrix"] @ mathutils.Vector(v2)

        curve.bevel_depth = self.unit_scale * item.Radius
        return curve

    def merge_by_class(self):
        merge_set = {}
        for obj in self.added_data.values():
            if not isinstance(obj, bpy.types.Object):
                continue
            if "/" not in obj.name or "IfcRelAggregates" in obj.users_collection[0].name:
                continue
            merge_set.setdefault(obj.name.split("/")[0], []).append(obj)
        self.merge_objects(merge_set)

    def merge_by_material(self):
        merge_set = {}
        for obj in self.added_data.values():
            if not isinstance(obj, bpy.types.Object):
                continue
            if "/" not in obj.name or "IfcRelAggregates" in obj.users_collection[0].name:
                continue
            if not obj.material_slots:
                merge_set.setdefault("no-material", []).append(obj)
            else:
                merge_set.setdefault(obj.material_slots[0].name, []).append(obj)
        self.merge_objects(merge_set)

    def merge_objects(self, merge_set):
        for ifc_class, objs in merge_set.items():
            context_override = {}
            context_override["object"] = context_override["active_object"] = objs[0]
            context_override["selected_objects"] = context_override["selected_editable_objects"] = objs
            bpy.ops.object.join(context_override)

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
        project_collection.children[self.opening_collection.name].hide_viewport = True
        project_collection.children[self.type_collection.name].hide_viewport = True

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
        bpy.context.view_layer.objects.active = last_obj
        context_override = {}
        bpy.ops.object.editmode_toggle(context_override)
        bpy.ops.mesh.remove_doubles(context_override)
        bpy.ops.mesh.tris_convert_to_quads(context_override)
        bpy.ops.mesh.normals_make_consistent(context_override)
        bpy.ops.object.editmode_toggle(context_override)
        IfcStore.edited_objs.clear()

    def add_opening_relation(self, element, obj):
        if not element.is_a("IfcOpeningElement"):
            return
        self.openings[element.GlobalId] = obj

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
                bpy.context.scene.BIMProperties.area_unit = "{}{}".format(
                    unit.Prefix + "/" if hasattr(unit, "Prefix") and unit.Prefix else "", name
                )
            elif unit.is_a("IfcNamedUnit") and unit.UnitType == "VOLUMEUNIT":
                name = unit.Name if unit.is_a("IfcSIUnit") else unit.Name.lower()
                bpy.context.scene.BIMProperties.volume_unit = "{}{}".format(
                    unit.Prefix + "/" if hasattr(unit, "Prefix") and unit.Prefix else "", name
                )

    def create_project(self):
        self.project = {"ifc": self.file.by_type("IfcProject")[0]}
        self.project["blender"] = bpy.data.collections.new(
            "{}/{}".format(self.project["ifc"].is_a(), self.project["ifc"].Name)
        )
        obj = self.create_product(self.project["ifc"])
        if obj:
            self.project["blender"].objects.link(obj)

    def create_collections(self):
        if self.ifc_import_settings.collection_mode == "DECOMPOSITION":
            self.create_decomposition_collections()
        elif self.ifc_import_settings.collection_mode == "SPATIAL_DECOMPOSITION":
            self.create_spatial_decomposition_collections()

    def create_decomposition_collections(self):
        self.create_spatial_decomposition_collections()
        self.create_aggregate_collections()

    def create_spatial_decomposition_collections(self):
        for rel_aggregate in self.project["ifc"].IsDecomposedBy or []:
            self.create_spatial_decomposition_collection(self.project["blender"], rel_aggregate.RelatedObjects)
        self.create_views_collection()
        self.create_type_collection()

    def create_type_collection(self):
        for collection in self.project["blender"].children:
            if collection.name == "Types":
                self.type_collection = collection
                break
        if not self.type_collection:
            self.type_collection = bpy.data.collections.new("Types")
            self.project["blender"].children.link(self.type_collection)

    def create_views_collection(self):
        view_collection = None
        for collection in self.project["blender"].children:
            if collection.name == "Views":
                view_collection = collection
                break
        if not view_collection:
            view_collection = bpy.data.collections.new("Views")
            self.project["blender"].children.link(view_collection)
        for element in self.file.by_type("IfcAnnotation"):
            if element.ObjectType == "DRAWING":
                group = [r for r in element.HasAssignments if r.is_a("IfcRelAssignsToGroup")][0].RelatingGroup
                collection = bpy.data.collections.new("IfcGroup/" + group.Name)
                self.collections[group.GlobalId] = collection
                view_collection.children.link(collection)

    def create_spatial_decomposition_collection(self, parent, related_objects):
        for element in related_objects:
            if element not in self.spatial_elements:
                continue
            global_id = element.GlobalId
            collection = bpy.data.collections.new(self.get_name(element))
            self.collections[global_id] = collection
            parent.children.link(collection)
            if element.IsDecomposedBy:
                for rel_aggregate in element.IsDecomposedBy:
                    self.create_spatial_decomposition_collection(collection, rel_aggregate.RelatedObjects)

    def create_aggregate_collections(self):
        if self.ifc_import_settings.has_filter:
            rel_aggregates = [e.IsDecomposedBy[0] for e in self.elements if e.IsDecomposedBy]
            rel_aggregates += [e.Decomposes[0] for e in self.elements if e.Decomposes]
            rel_aggregates = set(rel_aggregates)
        else:
            rel_aggregates = [a for a in self.file.by_type("IfcRelAggregates") if a.RelatingObject.is_a("IfcElement")]

        if len(rel_aggregates) > 10000:
            # More than 10,000 collections makes Blender unhappy
            print("Skipping aggregate collections for performance.")
            self.ifc_import_settings.collection_mode = "SPATIAL_DECOMPOSITION"
            return

        aggregates = {}
        for rel_aggregate in rel_aggregates:
            element = rel_aggregate.RelatingObject
            collection = bpy.data.collections.new(self.get_name(element))
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

    def create_openings_collection(self):
        self.opening_collection = bpy.data.collections.new("IfcOpeningElements")
        self.project["blender"].children.link(self.opening_collection)

    def create_materials(self):
        for material in self.file.by_type("IfcMaterial"):
            self.create_material(material)

    def create_material(self, material):
        blender_material = bpy.data.materials.new(material.Name)
        self.link_element(material, blender_material)
        self.material_creator.materials[material.id()] = blender_material
        blender_material.use_fake_user = True
        return blender_material

    def create_styles(self):
        parsed_styles = set()

        for material_definition_representation in self.file.by_type("IfcMaterialDefinitionRepresentation"):
            material = material_definition_representation.RepresentedMaterial
            for representation in material_definition_representation.Representations:
                for style in [e for e in self.file.traverse(representation) if e.is_a("IfcSurfaceStyle")]:
                    blender_material = self.material_creator.materials[material.id()]
                    self.create_style(style, blender_material)
                    parsed_styles.add(style.id())

        for style in self.file.by_type("IfcSurfaceStyle"):
            if style.id() in parsed_styles:
                continue
            self.create_style(style)

    def create_style(self, style, blender_material=None):
        if not blender_material:
            name = style.Name or str(style.id())
            blender_material = bpy.data.materials.new(name)

        old_definition_id = blender_material.BIMObjectProperties.ifc_definition_id
        if not old_definition_id:
            self.link_element(style, blender_material)
        blender_material.BIMObjectProperties.ifc_definition_id = old_definition_id

        blender_material.BIMMaterialProperties.ifc_style_id = style.id()
        self.material_creator.styles[style.id()] = blender_material

        rendering_style = None
        texture_style = None

        for surface_style in style.Styles:
            if surface_style.is_a() == "IfcSurfaceStyleShading":
                self.create_surface_style_shading(blender_material, surface_style)
            elif surface_style.is_a("IfcSurfaceStyleRendering"):
                rendering_style = surface_style
                self.create_surface_style_rendering(blender_material, surface_style)
            elif surface_style.is_a("IfcSurfaceStyleWithTextures"):
                texture_style = surface_style

        if rendering_style and texture_style:
            self.create_surface_style_with_textures(blender_material, rendering_style, texture_style)

    def create_surface_style_shading(self, blender_material, surface_style):
        alpha = 1.0
        # Transparency was added in IFC4
        if hasattr(surface_style, "Transparency") and surface_style.Transparency:
            alpha = 1 - surface_style.Transparency
        blender_material.diffuse_color = (
            surface_style.SurfaceColour.Red,
            surface_style.SurfaceColour.Green,
            surface_style.SurfaceColour.Blue,
            alpha,
        )

    def create_surface_style_rendering(self, blender_material, surface_style):
        self.create_surface_style_shading(blender_material, surface_style)
        if surface_style.ReflectanceMethod in ["PHYSICAL", "NOTDEFINED"]:
            blender_material.use_nodes = True
            bsdf = blender_material.node_tree.nodes["Principled BSDF"]
            if surface_style.DiffuseColour and surface_style.DiffuseColour.is_a("IfcColourRgb"):
                bsdf.inputs["Base Color"].default_value = (
                    surface_style.DiffuseColour.Red,
                    surface_style.DiffuseColour.Green,
                    surface_style.DiffuseColour.Blue,
                    1,
                )
            if surface_style.SpecularColour and surface_style.SpecularColour.is_a("IfcNormalisedRatioMeasure"):
                bsdf.inputs["Metallic"].default_value = surface_style.SpecularColour.wrappedValue
            if surface_style.SpecularHighlight and surface_style.SpecularHighlight.is_a("IfcSpecularRoughness"):
                bsdf.inputs["Roughness"].default_value = surface_style.SpecularHighlight.wrappedValue
            if hasattr(surface_style, "Transparency") and surface_style.Transparency:
                bsdf.inputs["Alpha"].default_value = 1 - surface_style.Transparency
                blender_material.blend_method = "BLEND"
        elif surface_style.ReflectanceMethod == "FLAT":
            blender_material.use_nodes = True

            output = {n.type: n for n in self.settings["material"].node_tree.nodes}.get("OUTPUT_MATERIAL", None)
            bsdf = blender_material.node_tree.nodes["Principled BSDF"]

            mix = blender_material.node_tree.nodes.new(type="ShaderNodeMixShader")
            mix.location = bsdf.location
            blender_material.node_tree.links.new(lightpath.outputs[0], output.inputs["Surface"])

            blender_material.node_tree.nodes.remove(bsdf)

            lightpath = blender_material.node_tree.nodes.new(type="ShaderNodeLightPath")
            lightpath.location = mix.location - mathutils.Vector((200, -200))
            blender_material.node_tree.links.new(lightpath.outputs[0], mix.inputs[0])

            bsdf = blender_material.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
            bsdf.location = mix.location - mathutils.Vector((200, 0))
            blender_material.node_tree.links.new(bsdf.outputs[0], mix.inputs[1])

            rgb = blender_material.node_tree.nodes.new(type="ShaderNodeRGB")
            rgb.location = mix.location - mathutils.Vector((200, 200))
            blender_material.node_tree.links.new(rgb.outputs[0], mix.inputs[2])

            if surface_style.DiffuseColour and surface_style.DiffuseColour.is_a("IfcColourRgb"):
                rgb.outputs[0].default_value = (
                    surface_style.DiffuseColour.Red,
                    surface_style.DiffuseColour.Green,
                    surface_style.DiffuseColour.Blue,
                    1,
                )

    def create_surface_style_with_textures(self, blender_material, rendering_style, texture_style):
        for texture in texture_style.Textures:
            mode = getattr(texture, "Mode", None)
            node = None

            if texture.is_a("IfcImageTexture"):
                image_url = texture.URLReference
                if not os.path.abspath(texture.URLReference) and tool.Ifc.get_path():
                    image_url = os.path.join(os.path.dirname(tool.Ifc.get_path()), texture.URLReference)

            if rendering_style.ReflectanceMethod in ["PHYSICAL", "NOTDEFINED"]:
                bsdf = blender_material.node_tree.nodes["Principled BSDF"]
                if mode == "NORMAL":
                    normalmap = blender_material.node_tree.nodes.new(type="ShaderNodeNormalMap")
                    normalmap.location = bsdf.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(normalmap.outputs[0], bsdf.inputs["Normal"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = normalmap.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], normalmap.inputs["Color"])
                elif mode == "EMISSIVE":
                    output = {n.type: n for n in blender_material.node_tree.nodes}.get("OUTPUT_MATERIAL", None)

                    add = blender_material.node_tree.nodes.new(type="ShaderNodeAddShader")
                    add.location = bsdf.location + mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(bsdf.outputs[0], add.inputs[1])
                    blender_material.node_tree.links.new(add.outputs[0], output.inputs[0])

                    emission = blender_material.node_tree.nodes.new(type="ShaderNodeEmission")
                    emission.location = add.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(emission.outputs[0], add.inputs[0])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = emission.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], emission.inputs[0])
                elif mode == "METALLICROUGHNESS":
                    separate = blender_material.node_tree.nodes.new(type="ShaderNodeSeparateRGB")
                    separate.location = bsdf.location - mathutils.Vector((200, 0))
                    blender_material.node_tree.links.new(separate.outputs[1], bsdf.inputs["Roughness"])
                    blender_material.node_tree.links.new(separate.outputs[2], bsdf.inputs["Metallic"])

                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = separate.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    image.colorspace_settings.name = "Non-Color"
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], separate.inputs[0])
                elif mode == "OCCLUSION":
                    # TODO work out how to implement glTF settings here
                    # https://docs.blender.org/manual/en/dev/addons/import_export/scene_gltf2.html
                    pass
                elif mode == "DIFFUSE":
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = bsdf.location - mathutils.Vector((400, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs["Base Color"])
                    blender_material.node_tree.links.new(node.outputs[1], bsdf.inputs["Alpha"])
                    blender_material.blend_method = "BLEND"
            elif rendering_style.ReflectanceMethod == "FLAT":
                bsdf = blender_material.node_tree.nodes["Mix Shader"]
                if mode == "EMISSIVE":
                    node = blender_material.node_tree.nodes.new(type="ShaderNodeTexImage")
                    node.location = bsdf.location - mathutils.Vector((200, 0))
                    image = bpy.data.images.load(image_url)
                    node.image = image
                    blender_material.node_tree.links.new(node.outputs[0], bsdf.inputs[2])

            if node and getattr(texture, "IsMappedBy", None):
                coordinates = texture.IsMappedBy[0]
                coord = blender_material.node_tree.nodes.new(type="ShaderNodeTexCoord")
                coord.location = node.location - mathutils.Vector((200, 0))
                if coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD":
                    blender_material.node_tree.links.new(coord.outputs["Generated"], node.inputs["Vector"])
                elif coordinates.is_a("IfcTextureCoordinateGenerator") and coordinates.Mode == "COORD-EYE":
                    blender_material.node_tree.links.new(coord.outputs["Camera"], node.inputs["Vector"])
                else:
                    blender_material.node_tree.links.new(coord.outputs["UV"], node.inputs["Vector"])

    def get_name(self, element):
        return "{}/{}".format(element.is_a(), element.Name)

    def place_objects_in_collections(self):
        for ifc_definition_id, obj in self.added_data.items():
            if isinstance(obj, bpy.types.Object):
                self.place_object_in_collection(self.file.by_id(ifc_definition_id), obj)

    def place_object_in_collection(self, element, obj):
        if self.ifc_import_settings.collection_mode == "DECOMPOSITION":
            self.place_object_in_decomposition_collection(element, obj)
        elif self.ifc_import_settings.collection_mode == "SPATIAL_DECOMPOSITION":
            self.place_object_in_spatial_decomposition_collection(element, obj)

    def place_object_in_decomposition_collection(self, element, obj):
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcGridAxis"):
            return
        elif element.GlobalId in self.collections:
            collection = self.collections[element.GlobalId]
            collection.name = obj.name
            return collection.objects.link(obj)
        elif getattr(element, "Decomposes", None):
            aggregate = ifcopenshell.util.element.get_aggregate(element)
            return self.collections[aggregate.GlobalId].objects.link(obj)
        else:
            return self.place_object_in_spatial_decomposition_collection(element, obj)

    def place_object_in_spatial_decomposition_collection(self, element, obj):
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcGridAxis"):
            return
        elif element.GlobalId in self.collections:
            return self.collections[element.GlobalId].objects.link(obj)
        elif element.is_a("IfcTypeObject"):
            return self.type_collection.objects.link(obj)
        elif element.is_a("IfcOpeningElement"):
            return self.opening_collection.objects.link(obj)
        elif element.is_a("IfcStructuralMember"):
            return self.structural_member_collection.objects.link(obj)
        elif element.is_a("IfcStructuralConnection"):
            return self.structural_connection_collection.objects.link(obj)
        elif element.is_a("IfcAnnotation") and self.is_drawing_annotation(element):
            group = [r for r in element.HasAssignments if r.is_a("IfcRelAssignsToGroup")][0].RelatingGroup
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
        return element.ObjectType in [
            "DIMENSION",
            "EQUAL_DIMENSION",
            "MISC",
            "PLAN_LEVEL",
            "SECTION_LEVEL",
            "STAIR_ARROW",
            "TEXT_LEADER",
        ]

    def is_drawing_annotation(self, element):
        return element.ObjectType in [
            "BREAKLINE",
            "DIMENSION",
            "DRAWING",
            "EQUAL_DIMENSION",
            "GRID",
            "HIDDEN_LINE",
            "MISC",
            "PLAN_LEVEL",
            "SECTION_LEVEL",
            "STAIR_ARROW",
            "TEXT",
            "TEXT_LEADER",
        ]

    def get_element_matrix(self, element):
        result = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        result[0][3] *= self.unit_scale
        result[1][3] *= self.unit_scale
        result[2][3] *= self.unit_scale
        return result

    def get_body_representation(self, representations):
        for representation in representations:
            if (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType == "MappedRepresentation"
            ):
                if len(representation.Items) > 1:
                    return representation
                return self.get_body_representation([representation.Items[0].MappingSource.MappedRepresentation])
            elif representation.RepresentationIdentifier == "Body":
                return representation

    def get_transformed_body_representations(self, representations, matrix=None):
        if matrix is None:
            matrix = mathutils.Matrix()
        results = []
        for representation in representations:
            if (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType == "MappedRepresentation"
            ):
                for item in representation.Items:
                    # TODO: Confirm if this transformation is right
                    transform = self.get_axis2placement(item.MappingSource.MappingOrigin)
                    if item.MappingTarget:
                        transform = transform @ self.get_cartesiantransformationoperator(item.MappingTarget)
                    results.extend(
                        self.get_transformed_body_representations(
                            [item.MappingSource.MappedRepresentation], transform @ matrix
                        )
                    )
            elif representation.RepresentationIdentifier == "Body":
                results.append({"raw": representation, "matrix": self.scale_matrix(matrix)})
        return results

    def scale_matrix(self, matrix):
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

    def get_mesh_name(self, geometry):
        representation_id = geometry.id
        if "-" in representation_id:
            representation_id = int(re.sub(r"\D", "", representation_id.split("-")[0]))
        else:
            representation_id = int(re.sub(r"\D", "", representation_id))
        representation = self.file.by_id(representation_id)
        context_id = representation.ContextOfItems.id() if hasattr(representation, "ContextOfItems") else 0
        return "{}/{}".format(context_id, representation_id)

    def create_camera(self, element, shape):
        if hasattr(shape, "geometry"):
            geometry = shape.geometry
        else:
            geometry = shape

        v = geometry.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        z = [v[i + 2] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        depth = max(z) - min(z)

        camera = bpy.data.cameras.new(self.get_mesh_name(geometry))
        camera.type = "ORTHO"
        camera.ortho_scale = width if width > height else height
        camera.clip_end = depth

        if width > height:
            camera.BIMCameraProperties.raster_x = 1000
            camera.BIMCameraProperties.raster_y = round(1000 * (height / width))
        else:
            camera.BIMCameraProperties.raster_x = round(1000 * (width / height))
            camera.BIMCameraProperties.raster_y = 1000

        psets = ifcopenshell.util.element.get_psets(element)
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
                    camera.BIMCameraProperties.custom_diagram_scale = pset["Scale"]
        return camera

    def create_curve(self, element, shape):
        if hasattr(shape, "geometry"):
            geometry = shape.geometry
        else:
            geometry = shape

        curve = bpy.data.curves.new(self.get_mesh_name(geometry), type="CURVE")
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

    def create_mesh(self, element, shape):
        try:
            if hasattr(shape, "geometry"):
                geometry = shape.geometry
            else:
                geometry = shape

            mesh = bpy.data.meshes.new(self.get_mesh_name(geometry))

            props = bpy.context.scene.BIMGeoreferenceProperties
            if (
                props.has_blender_offset
                and geometry.verts
                and self.is_point_far_away((geometry.verts[0], geometry.verts[1], geometry.verts[2]))
            ):
                verts = [None] * len(geometry.verts)
                for i in range(0, len(geometry.verts), 3):
                    verts[i], verts[i + 1], verts[i + 2] = ifcopenshell.util.geolocation.enh2xyz(
                        geometry.verts[i],
                        geometry.verts[i + 1],
                        geometry.verts[i + 2],
                        float(props.blender_eastings) * self.unit_scale,
                        float(props.blender_northings) * self.unit_scale,
                        float(props.blender_orthogonal_height) * self.unit_scale,
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

                mesh.vertices.add(num_vertices)
                mesh.vertices.foreach_set("co", verts)
                mesh.loops.add(num_vertex_indices)
                mesh.loops.foreach_set("vertex_index", geometry.faces)
                mesh.polygons.add(num_loops)
                mesh.polygons.foreach_set("loop_start", loop_start)
                mesh.polygons.foreach_set("loop_total", loop_total)
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

    def a2p(self, o, z, x):
        y = z.cross(x)
        r = mathutils.Matrix((x, y, z, o))
        r.resize_4x4()
        r.transpose()
        return r

    def get_axis2placement(self, plc):
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

    def get_local_placement(self, plc):
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
                bpy.context.scene.BIMProperties.contexts = str(subcontext.id())
                break

    def link_element(self, element, obj):
        self.added_data[element.id()] = obj
        IfcStore.link_element(element, obj)

    def link_mesh(self, shape, mesh):
        if hasattr(shape, "geometry"):
            geometry = shape.geometry
        else:
            geometry = shape
        if "-" in geometry.id:
            mesh.BIMMeshProperties.ifc_definition_id = int(geometry.id.split("-")[0])
        else:
            # TODO: See #2002
            mesh.BIMMeshProperties.ifc_definition_id = int(geometry.id.replace(",", ""))

    def set_matrix_world(self, obj, matrix_world):
        obj.matrix_world = matrix_world
        tool.Geometry.record_object_position(obj)


class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
        self.diff_file = None
        self.should_use_cpu_multiprocessing = True
        self.should_merge_by_class = False
        self.should_merge_by_material = False
        self.should_merge_materials_by_colour = False
        self.should_clean_mesh = True
        self.deflection_tolerance = 0.001
        self.angular_tolerance = 0.5
        self.should_offset_model = False
        self.model_offset_coordinates = (0, 0, 0)
        self.has_filter = None
        self.should_filter_spatial_elements = True
        self.elements = set()
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
        settings.should_merge_by_class = props.should_merge_by_class
        settings.should_merge_by_material = props.should_merge_by_material
        settings.should_merge_materials_by_colour = props.should_merge_materials_by_colour
        settings.should_clean_mesh = props.should_clean_mesh
        settings.deflection_tolerance = props.deflection_tolerance
        settings.angular_tolerance = props.angular_tolerance
        settings.should_offset_model = props.should_offset_model
        settings.model_offset_coordinates = (
            [float(o) for o in props.model_offset_coordinates.split(",")]
            if props.model_offset_coordinates
            else (0, 0, 0)
        )
        return settings
