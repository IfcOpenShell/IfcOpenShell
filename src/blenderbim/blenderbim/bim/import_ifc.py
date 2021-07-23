import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.geolocation
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.unit
import bpy
import bmesh
import os
import re
import shutil
import threading
import json
import time
import mathutils
import math
import multiprocessing
import zipfile
import tempfile
import numpy as np
from blenderbim.bim.module.drawing.prop import getDiagramScales
from pathlib import Path
from itertools import cycle
from datetime import datetime
from blenderbim.bim.ifc import IfcStore


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
        if self.parse_representations(element):
            self.assign_material_slots_to_faces()

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
        representation_items = self.resolve_mapped_representation_items(representation)
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

    def resolve_mapped_representation_items(self, representation):
        items = []
        for item in representation.Items:
            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            else:
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
        self.settings_native = ifcopenshell.geom.settings()
        self.settings_native.set(self.settings_native.INCLUDE_CURVES, True)
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set(self.settings_2d.INCLUDE_CURVES, True)
        self.filter_mode = "BLACKLIST"
        self.include_elements = set()
        self.exclude_elements = set()
        self.project = None
        self.spatial_structure_elements = {}
        self.elements = {}
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
        self.aggregates = {}

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
        self.load_diff()
        self.profile_code("Load diff")
        self.purge_diff()
        self.profile_code("Purge diffs")
        self.load_file()
        self.profile_code("Loading file")
        self.set_ifc_file()
        self.profile_code("Setting file")
        self.calculate_unit_scale()
        self.profile_code("Calculate unit scale")
        self.calculate_model_offset()
        self.profile_code("Calculate model offset")
        self.set_units()
        self.profile_code("Set units")
        self.create_project()
        self.profile_code("Create project")
        self.create_spatial_hierarchy()
        self.profile_code("Create spatial hierarchy")
        self.create_aggregates()
        self.profile_code("Create aggregates")
        self.create_aggregate_tree()
        self.profile_code("Create aggregate tree")
        self.create_openings_collection()
        self.profile_code("Create opening collection")
        self.create_materials()
        self.profile_code("Create materials")
        self.create_styles()
        self.profile_code("Create styles")
        self.process_element_filter()
        self.profile_code("Process element filter")
        self.parse_native_elements()
        self.profile_code("Parsing native elements")
        self.create_grids()
        self.profile_code("Create grids")
        self.create_native_products()
        self.profile_code("Create native products")
        self.create_products()
        self.profile_code("Create products")
        self.create_empty_and_2d_elements()
        self.profile_code("Create empty products")
        self.create_type_products()
        self.profile_code("Create type products")
        self.create_annotation()
        self.profile_code("Create annotation")
        self.create_structural_elements()
        self.profile_code("Create structural elements")
        self.place_objects_in_spatial_tree()
        self.profile_code("Placing objects in spatial tree")
        if self.ifc_import_settings.should_merge_by_class:
            self.merge_by_class()
            self.profile_code("Merging by class")
        elif self.ifc_import_settings.should_merge_by_material:
            self.merge_by_material()
            self.profile_code("Merging by material")
        if self.ifc_import_settings.should_merge_materials_by_colour or (
            self.ifc_import_settings.should_auto_set_workarounds and len(self.material_creator.materials) > 300
        ):
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

    def is_element_far_away(self, element, is_meters=True):
        try:
            return self.is_point_far_away(element.ObjectPlacement.RelativePlacement.Location, is_meters=is_meters)
        except:
            pass

    def is_point_far_away(self, point, is_meters=True):
        # Locations greater than 1km are not considered "small sites" according to the georeferencing guide
        limit = 1000 if is_meters else (1000 / self.unit_scale)
        coords = point
        if hasattr(point, "Coordinates"):
            coords = point.Coordinates
        return abs(coords[0]) > limit or abs(coords[1]) > limit or abs(coords[2]) > limit

    def process_element_filter(self):
        if not self.ifc_import_settings.ifc_selector:
            return
        selector = ifcopenshell.util.selector.Selector()
        elements = selector.parse(self.file, self.ifc_import_settings.ifc_selector)
        if self.ifc_import_settings.ifc_import_filter == "WHITELIST":
            self.filter_mode = "WHITELIST"
            self.include_elements = set(elements)
        elif self.ifc_import_settings.ifc_import_filter == "BLACKLIST":
            self.exclude_elements = set(elements)
            self.filter_mode = "BLACKLIST"

    def parse_native_elements(self):
        if self.filter_mode == "WHITELIST":
            for element in self.include_elements:
                if self.is_native(element):
                    self.native_elements[element.GlobalId] = element
            self.include_elements -= self.native_elements
        elif self.filter_mode == "BLACKLIST":
            for element in set(self.file.by_type("IfcElement")) - self.exclude_elements:
                if self.is_native(element):
                    self.native_elements.add(element)
            self.exclude_elements |= self.native_elements

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
        #     self.native_data[element.GlobalId] = {
        #         "representations": representations,
        #         "representation": self.get_body_representation(element.Representation.Representations),
        #         "type": "IfcFacetedBrep",
        #     }
        #     return True

    def is_native_swept_disk_solid(self, representations):
        for representation in representations:
            if len(representation["raw"].Items) == 1 and representation["raw"].Items[0].is_a("IfcSweptDiskSolid"):
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
        project = self.file.by_type("IfcProject")[0]
        site = self.find_decomposed_ifc_class(project, "IfcSite")
        if site and self.is_element_far_away(site[0], is_meters=False):
            return self.guess_georeferencing(site[0])
        building = self.find_decomposed_ifc_class(project, "IfcBuilding")
        if building and self.is_element_far_away(building[0], is_meters=False):
            return self.guess_georeferencing(building[0])
        return self.guess_absolute_coordinate()

    def guess_georeferencing(self, element):
        if not element.ObjectPlacement.is_a("IfcLocalPlacement"):
            return
        placement = element.ObjectPlacement.RelativePlacement
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.blender_eastings = str(placement.Location.Coordinates[0])
        props.blender_northings = str(placement.Location.Coordinates[1])
        props.blender_orthogonal_height = str(placement.Location.Coordinates[2])
        if placement.RefDirection:
            props.blender_x_axis_abscissa = str(placement.RefDirection.DirectionRatios[0])
            props.blender_x_axis_ordinate = str(placement.RefDirection.DirectionRatios[1])
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
        offset_point = None
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
            if self.is_point_far_away((matrix[0, 3], matrix[1, 3], matrix[2, 3])):
                obj.BIMObjectProperties.blender_offset_type = "OBJECT_PLACEMENT"
                return mathutils.Matrix(
                    ifcopenshell.util.geolocation.global2local(
                        matrix,
                        float(props.blender_eastings) * self.unit_scale,
                        float(props.blender_northings) * self.unit_scale,
                        float(props.blender_orthogonal_height) * self.unit_scale,
                        float(props.blender_x_axis_abscissa),
                        float(props.blender_x_axis_ordinate),
                    ).tolist()
                )
            else:
                obj.BIMObjectProperties.blender_offset_type = "CARTESIAN_POINT"
        return mathutils.Matrix(matrix.tolist())

    def find_decomposed_ifc_class(self, element, ifc_class):
        results = []
        rel_aggregates = element.IsDecomposedBy
        if not rel_aggregates:
            return results
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                if part.is_a(ifc_class):
                    results.append(part)
                results.extend(self.find_decomposed_ifc_class(part, ifc_class))
        return results

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
            obj.BIMObjectProperties.ifc_definition_id = axis.id()
            obj.matrix_world = grid_obj.matrix_world
            grid_collection.objects.link(obj)

    def create_type_products(self):
        type_products = self.file.by_type("IfcTypeProduct")
        for collection in self.project["blender"].children:
            if collection.name == "Types":
                self.type_collection = collection
                break
        if not self.type_collection:
            self.type_collection = bpy.data.collections.new("Types")
            self.project["blender"].children.link(self.type_collection)
        for type_product in type_products:
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

    def create_native_products(self):
        total = 0
        checkpoint = time.time()
        bm = bmesh.new()
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
            if native_data["type"] == "IfcFacetedBrep":
                # The current implementation doesn't reuse vertices, so we weld it after assigning materials.
                # This welding isn't true to the representation, but is easy and seems inexpensive.
                bm.from_mesh(mesh)
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
                bm.to_mesh(mesh)
                bm.clear()
        bm.free()

        print("Done creating geometry")

    def create_products(self):
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings,
                self.file,
                multiprocessing.cpu_count(),
                include=self.include_elements or None,
                exclude=self.exclude_elements or None,
            )
        else:
            iterator = ifcopenshell.geom.iterator(
                self.settings, self.file, include=self.include_elements or None, exclude=self.exclude_elements or None
            )
        valid_file = iterator.initialize()
        if not valid_file:
            return False
        checkpoint = time.time()
        total_created = 0
        approx_total_products = len(self.include_elements) or len(self.file.by_type("IfcElement"))
        start_progress = self.progress
        progress_range = 85 - start_progress
        while True:
            if total_created % 250 == 0:
                print(
                    "{} / ~{} elements processed in {:.2f}s ...".format(
                        total_created, approx_total_products, time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
                self.update_progress(
                    ((total_created / approx_total_products) * progress_range) + start_progress
                )
            shape = iterator.get()
            if shape:
                product = self.file.by_id(shape.guid)
                # Facetation is to accommodate broken Revit files
                # See https://forums.buildingsmart.org/t/suggestions-on-how-to-improve-clarity-of-representation-context-usage-in-documentation/3663/6?u=moult
                if shape.context not in ["Body", "Facetation"] and IfcStore.get_element(shape.guid):
                    # We only load a single context, and we prioritise the Body context. See #1290.
                    pass
                elif product.is_a("IfcAnnotation") and product.ObjectType == "DRAWING":
                    # We have already processed this during the create_annotation step
                    pass
                else:
                    self.create_product(product, shape)
                    total_created += 1
            if not iterator.next():
                break
        print("Done creating geometry")

    def create_empty_and_2d_elements(self):
        curve_products = []
        for element in self.file.by_type("IfcElement"):
            if element.id() in self.added_data:
                continue
            if element.is_a("IfcPort"):
                continue
            if not element.Representation:
                self.create_product(element)
            else:
                curve_products.append(element)
        if curve_products:
            self.create_curve_products(curve_products)

    def create_annotation(self):
        self.create_curve_products(self.file.by_type("IfcAnnotation"))

    def create_structural_elements(self):
        # Create structural collections
        self.structural_member_collection = bpy.data.collections.new("Members")
        self.structural_connection_collection = bpy.data.collections.new("Connections")
        self.structural_collection = bpy.data.collections.new("StructuralItems")
        self.structural_collection.children.link(self.structural_member_collection)
        self.structural_collection.children.link(self.structural_connection_collection)
        self.project["blender"].children.link(self.structural_collection)

        self.create_curve_products(self.file.by_type("IfcStructuralCurveMember"))
        self.create_curve_products(self.file.by_type("IfcStructuralCurveConnection"))
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
            obj.matrix_world = self.apply_blender_offset_to_matrix_world(obj, placement_matrix)
            self.link_element(product, obj)

    def create_curve_products(self, products):
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings_2d, self.file, multiprocessing.cpu_count(), include=products
            )
        else:
            iterator = ifcopenshell.geom.iterator(self.settings_2d, self.file, include=products)
        valid_file = iterator.initialize()
        if not valid_file:
            return False
        checkpoint = time.time()
        total = 0
        while True:
            total += 1
            if total % 250 == 0:
                print("{} elements processed in {:.2f}s ...".format(total, time.time() - checkpoint))
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                self.create_product(self.file.by_id(shape.guid), shape)
            if not iterator.next():
                break
        print("Done creating geometry")

    def create_product(self, element, shape=None, mesh=None):
        if element is None:
            return

        self.ifc_import_settings.logger.info("Creating object %s", element)

        if mesh:
            pass
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            mesh = self.create_camera(element, shape)
        elif shape:
            mesh_name = self.get_mesh_name(shape.geometry)
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                mesh = self.create_mesh(element, shape)
                if "-" in shape.geometry.id:
                    mesh.BIMMeshProperties.ifc_definition_id = int(shape.geometry.id.split("-")[0])
                else:
                    mesh.BIMMeshProperties.ifc_definition_id = int(shape.geometry.id)
                self.meshes[mesh_name] = mesh
        else:
            mesh = None

        obj = bpy.data.objects.new(self.get_name(element), mesh)
        self.link_element(element, obj)

        if shape:
            m = shape.transformation.matrix.data
            # We use numpy here because Blender mathutils.Matrix is not accurate enough
            mat = np.matrix(
                ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
            )
            obj.matrix_world = self.apply_blender_offset_to_matrix_world(obj, mat)
            self.material_creator.create(element, obj, mesh)
        elif mesh:
            obj.matrix_world = self.apply_blender_offset_to_matrix_world(obj, self.get_element_matrix(element))
            self.material_creator.create(element, obj, mesh)
        elif hasattr(element, "ObjectPlacement"):
            obj.matrix_world = self.apply_blender_offset_to_matrix_world(obj, self.get_element_matrix(element))

        self.add_opening_relation(element, obj)

        if element.is_a("IfcOpeningElement"):
            obj.display_type = "WIRE"
        return obj

    def get_representation_item_material_name(self, item):
        if not item.StyledByItem:
            return
        style_ids = [e.id() for e in self.ifc_importer.file.traverse(item.StyledByItem[0]) if e.is_a("IfcSurfaceStyle")]
        return style_ids[0] if style_ids else None

    def create_native_faceted_brep(self, element, mesh_name):
        # TODO: georeferencing?
        # Note: to make this algorithm simpler (it's already confusing) we don't reuse / weld verts
        # co [x y z x y z x y z ...]
        # vertex_index [i i i i i ...]
        # loop_start [0 3 6 9 ...] (for tris)
        # loop_total [3 3 3 3 ...] (for tris)
        co = []
        vertex_index = []
        loop_start = []
        loop_total = []
        total_verts = 0
        total_polygons = 0
        materials = []
        material_ids = []
        item_index = 0

        for representation in self.native_data[element.GlobalId]["representations"]:
            for item in representation["raw"].Items:
                # TODO: if I reimplement native faceted breps, recheck this material implementation
                materials.append(self.get_representation_item_material_name(item) or "NULLMAT")
                mesh = item.get_info_2(recursive=True)  # See bug #841
                total_item_polygons = 0
                for face in mesh["Outer"]["CfsFaces"]:
                    # Blender cannot handle faces with holes.
                    if len(face["Bounds"]) > 1:
                        inner_bounds = []
                        for bound in face["Bounds"]:
                            if bound["type"] == "IfcFaceOuterBound":
                                outer_bound = [[p["Coordinates"] for p in bound["Bound"]["Polygon"]]]
                            else:
                                inner_bounds.append([p["Coordinates"] for p in bound["Bound"]["Polygon"]])
                        points = outer_bound[0].copy()
                        [points.extend(p) for p in inner_bounds]
                        tessellated_polygons = mathutils.geometry.tessellate_polygon(outer_bound + inner_bounds)
                        tessellated_faces = [({"Coordinates": points[pi]} for pi in t) for t in tessellated_polygons]
                    else:
                        tessellated_faces = [face["Bounds"][0]["Bound"]["Polygon"]]

                    for tessellated_face in tessellated_faces:
                        loop_start.append(total_verts)
                        loop_count = 0
                        total_polygons += 1
                        total_item_polygons += 1
                        for point in tessellated_face:
                            co.extend(
                                representation["matrix"]
                                @ mathutils.Vector((c * self.unit_scale for c in point["Coordinates"]))
                            )
                            total_verts += 1
                            loop_count += 1
                        loop_total.append(loop_count)
                vertex_index = range(0, total_verts)
                if materials[item_index] == "NULLMAT":
                    # Magic number -1 represents no material, until this has a better approach
                    material_ids += [-1] * total_item_polygons
                else:
                    material_ids += [item_index] * total_item_polygons
                item_index += 1
        mesh = bpy.data.meshes.new("Tester")

        mesh.vertices.add(total_verts)
        mesh.vertices.foreach_set("co", co)
        mesh.loops.add(total_verts)
        mesh.loops.foreach_set("vertex_index", vertex_index)
        mesh.polygons.add(total_polygons)
        mesh.polygons.foreach_set("loop_start", loop_start)
        mesh.polygons.foreach_set("loop_total", loop_total)
        mesh.update()

        mesh["ios_materials"] = materials
        mesh["ios_material_ids"] = material_ids
        return mesh

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

    def load_diff(self):
        if not self.ifc_import_settings.diff_file:
            return
        with open(self.ifc_import_settings.diff_file, "r") as file:
            self.diff = json.load(file)

    def load_file(self):
        self.ifc_import_settings.logger.info("loading file %s", self.ifc_import_settings.input_file)
        extension = self.ifc_import_settings.input_file.split(".")[-1]
        if extension.lower() == "ifczip":
            with tempfile.TemporaryDirectory() as unzipped_path:
                with zipfile.ZipFile(self.ifc_import_settings.input_file, "r") as zip_ref:
                    zip_ref.extractall(unzipped_path)
                for filename in Path(unzipped_path).glob("**/*.ifc"):
                    self.file = ifcopenshell.open(filename)
                    break
        elif extension.lower() == "ifcxml":
            self.file = ifcopenshell.file(
                ifcopenshell.ifcopenshell_wrapper.parse_ifcxml(self.ifc_import_settings.input_file)
            )
        elif extension.lower() == "ifc":
            self.file = ifcopenshell.open(self.ifc_import_settings.input_file)
        IfcStore.file = self.file

    def set_ifc_file(self):
        bpy.context.scene.BIMProperties.ifc_file = self.ifc_import_settings.input_file
        IfcStore.file = self.file
        IfcStore.path = self.ifc_import_settings.input_file

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
        self.project["blender"] = bpy.data.collections.new("IfcProject/{}".format(self.project["ifc"].Name))
        obj = self.create_product(self.project["ifc"])
        if obj:
            self.project["blender"].objects.link(obj)

    def create_spatial_hierarchy(self):
        if self.project["ifc"].IsDecomposedBy:
            for rel_aggregate in self.project["ifc"].IsDecomposedBy:
                self.add_related_objects(self.project["blender"], rel_aggregate.RelatedObjects)

    def add_related_objects(self, parent, related_objects):
        for element in related_objects:
            global_id = element.GlobalId
            collection = bpy.data.collections.new(self.get_name(element))
            self.spatial_structure_elements[global_id] = {"blender": collection}
            parent.children.link(collection)
            obj = self.create_product(element)
            if obj:
                self.spatial_structure_elements[global_id]["blender_obj"] = obj
                collection.objects.link(obj)
            if element.IsDecomposedBy:
                for rel_aggregate in element.IsDecomposedBy:
                    self.add_related_objects(collection, rel_aggregate.RelatedObjects)

    def create_aggregates(self):
        rel_aggregates = [a for a in self.file.by_type("IfcRelAggregates") if a.RelatingObject.is_a("IfcElement")]
        for rel_aggregate in rel_aggregates:
            self.create_aggregate(rel_aggregate)

    def create_aggregate_tree(self):
        for aggregate in self.aggregates.values():
            if aggregate["container"].is_a("IfcSpatialStructureElement"):
                self.spatial_structure_elements[aggregate["container"].GlobalId]["blender"].children.link(
                    aggregate["blender"]
                )
            else:
                self.aggregates[aggregate["container"].GlobalId]["blender"].children.link(aggregate["blender"])

    def create_aggregate(self, rel_aggregate):
        element = rel_aggregate.RelatingObject
        obj = bpy.data.objects.new("{}/{}".format(element.is_a(), element.Name), None)
        obj.matrix_world = self.apply_blender_offset_to_matrix_world(obj, self.get_element_matrix(element))
        self.link_element(element, obj)
        collection = bpy.data.collections.new(obj.name)
        collection.objects.link(obj)
        self.aggregates[element.GlobalId] = {
            "blender": collection,
            "blender_obj": obj,
            "container": self.get_aggregate_container(element),
        }

    def get_aggregate_container(self, element):
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            container = element.ContainedInStructure[0].RelatingStructure
        elif hasattr(element, "Decomposes") and element.Decomposes:
            container = element.Decomposes[0].RelatingObject
        return container

    def create_openings_collection(self):
        self.opening_collection = bpy.data.collections.new("IfcOpeningElements")
        self.project["blender"].children.link(self.opening_collection)

    def create_materials(self):
        for material in self.file.by_type("IfcMaterial"):
            blender_material = bpy.data.materials.new(material.Name)
            self.link_element(material, blender_material)
            self.material_creator.materials[material.id()] = blender_material
            blender_material.use_fake_user = True

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
            name = style.Name or str(style.id())
            blender_material = bpy.data.materials.new(name)
            self.create_style(style, blender_material)

    def create_style(self, style, blender_material):
        old_definition_id = blender_material.BIMObjectProperties.ifc_definition_id
        if not old_definition_id:
            self.link_element(style, blender_material)
        blender_material.BIMObjectProperties.ifc_definition_id = old_definition_id

        blender_material.BIMMaterialProperties.ifc_style_id = style.id()
        self.material_creator.styles[style.id()] = blender_material
        for surface_style in style.Styles:
            if surface_style.is_a("IfcSurfaceStyleShading"):
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

    def get_name(self, element):
        return "{}/{}".format(element.is_a(), element.Name)

    def purge_diff(self):
        if not self.diff:
            return
        objects_to_purge = []
        for obj in bpy.data.objects:
            if "GlobalId" not in obj.BIMObjectProperties.attributes:
                continue
            global_id = obj.BIMObjectProperties.attributes["GlobalId"].string_value
            if global_id in self.diff["deleted"] or global_id in self.diff["changed"].keys():
                objects_to_purge.append(obj)
        bpy.ops.object.delete({"selected_objects": objects_to_purge})

    def place_objects_in_spatial_tree(self):
        for ifc_definition_id, obj in self.added_data.items():
            if isinstance(obj, bpy.types.Object):
                self.place_object_in_spatial_tree(self.file.by_id(ifc_definition_id), obj)

    def place_object_in_spatial_tree(self, element, obj):
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcTypeObject"):
            self.type_collection.objects.link(obj)
        elif element.GlobalId in self.aggregates:
            return
        elif element.GlobalId in self.spatial_structure_elements:
            if not obj.data:
                return
            # Since spatial structure elements are generated as empties, we'll replace it with the representation
            spatial_obj = self.spatial_structure_elements[element.GlobalId]["blender_obj"]
            spatial_collection = self.spatial_structure_elements[element.GlobalId]["blender"]
            spatial_name = spatial_obj.name
            spatial_collection.objects.link(obj)
            bpy.data.objects.remove(spatial_obj)
            obj.name = spatial_name
        elif (
            hasattr(element, "ContainedInStructure")
            and element.ContainedInStructure
            and element.ContainedInStructure[0].RelatingStructure
        ):
            container = element.ContainedInStructure[0].RelatingStructure
            if element.is_a("IfcGrid"):
                grid_collection = bpy.data.collections.get(obj.name)
                if grid_collection:  # Just in case we ran into invalid grids from Revit
                    self.spatial_structure_elements[container.GlobalId]["blender"].children.link(grid_collection)
                    grid_collection.objects.link(obj)
            else:
                self.spatial_structure_elements[container.GlobalId]["blender"].objects.link(obj)
        elif hasattr(element, "Decomposes") and element.Decomposes:
            collection = None
            if element.Decomposes[0].RelatingObject.is_a("IfcProject"):
                collection = self.project["blender"]
            elif element.Decomposes[0].RelatingObject.is_a("IfcSpatialStructureElement"):
                if element.is_a("IfcSpatialStructureElement"):
                    global_id = element.GlobalId
                if global_id in self.spatial_structure_elements:
                    if (
                        element.is_a("IfcSpatialStructureElement")
                        and "blender_obj" in self.spatial_structure_elements[global_id]
                    ):
                        bpy.data.objects.remove(self.spatial_structure_elements[global_id]["blender_obj"])
                    collection = self.spatial_structure_elements[global_id]["blender"]
            else:
                collection = self.aggregates[element.Decomposes[0].RelatingObject.GlobalId]["blender"]
            if collection:
                collection.objects.link(obj)
            else:
                self.ifc_import_settings.logger.error("An element could not be placed in the spatial tree %s", element)
        elif element.is_a("IfcOpeningElement"):
            self.opening_collection.objects.link(obj)
        elif element.is_a("IfcStructuralMember"):
            self.structural_member_collection.objects.link(obj)
        elif element.is_a("IfcStructuralConnection"):
            self.structural_connection_collection.objects.link(obj)
        elif element.is_a("IfcAnnotation") and element.ObjectType == "DRAWING":
            view_collection = bpy.data.collections.get("Views")
            if not view_collection:
                view_collection = bpy.data.collections.new("Views")
                bpy.context.scene.collection.children.link(view_collection)
            group = [r for r in element.HasAssignments if r.is_a("IfcRelAssignsToGroup")][0].RelatingGroup
            drawing_collection = bpy.data.collections.new("IfcGroup/" + group.Name)
            view_collection.children.link(drawing_collection)
            drawing_collection.objects.link(obj)
        else:
            self.ifc_import_settings.logger.warning("Warning: this object is outside the spatial hierarchy %s", element)
            bpy.context.scene.collection.objects.link(obj)

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
                valid_scales = [i[0] for i in getDiagramScales(None, None) if pset["Scale"] == i[0].split("|")[-1]]
                if valid_scales:
                    camera.BIMCameraProperties.diagram_scale = valid_scales[0]
                else:
                    camera.BIMCameraProperties.diagram_scale = "CUSTOM"
                    camera.BIMCameraProperties.custom_diagram_scale = pset["Scale"]
        return camera

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
                ordinate_index = 0
                verts = [None] * len(geometry.verts)
                offset_point = (
                    float(props.blender_eastings) * self.unit_scale,
                    float(props.blender_northings) * self.unit_scale,
                    float(props.blender_orthogonal_height) * self.unit_scale,
                )
                for i, vert in enumerate(geometry.verts):
                    if ordinate_index > 2:
                        ordinate_index = 0
                    verts[i] = vert - offset_point[ordinate_index]
                    ordinate_index += 1
            else:
                verts = geometry.verts

            if geometry.faces:
                num_vertices = len(verts) // 3
                total_faces = len(geometry.faces)
                loop_start = range(0, total_faces, 3)
                num_loops = total_faces // 3
                loop_total = [3] * num_loops
                num_vertex_indices = len(geometry.faces)

                mesh.vertices.add(num_vertices)
                if self.ifc_import_settings.should_offset_model:
                    # Potentially, there is a smarter way to do this. See #1047
                    v_index = cycle((0, 1, 2))
                    verts = [v + self.ifc_import_settings.model_offset_coordinates[next(v_index)] for v in verts]
                    mesh.vertices.foreach_set("co", verts)
                else:
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


class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
        self.diff_file = None
        self.should_auto_set_workarounds = True
        self.should_use_cpu_multiprocessing = True
        self.should_merge_by_class = False
        self.should_merge_by_material = False
        self.should_merge_materials_by_colour = False
        self.should_clean_mesh = True
        self.deflection_tolerance = 0.001
        self.angular_tolerance = 0.5
        self.should_offset_model = False
        self.model_offset_coordinates = (0, 0, 0)
        self.ifc_import_filter = "NONE"
        self.ifc_selector = ""

    @staticmethod
    def factory(context, input_file, logger):
        scene_bim = context.scene.BIMProperties
        scene_diff = context.scene.DiffProperties
        settings = IfcImportSettings()
        settings.input_file = input_file
        settings.logger = logger
        settings.diff_file = scene_diff.diff_json_file
        return settings
