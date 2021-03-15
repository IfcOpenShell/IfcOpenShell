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
from pathlib import Path
from itertools import cycle
from datetime import datetime
from blenderbim.bim.module.context.data import Data as ContextData
from blenderbim.bim.ifc import IfcStore
from . import schema


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
        self.parsed_meshes = set()
        self.ifc_import_settings = ifc_import_settings
        self.ifc_importer = ifc_importer

    def create(self, element, obj, mesh):
        self.obj = obj
        self.mesh = mesh
        self.parse_material(element)
        if (hasattr(element, "Representation") and not element.Representation) or (
            hasattr(element, "RepresentationMaps") and not element.RepresentationMaps
        ):
            return
        if not self.mesh or self.mesh.name in self.parsed_meshes:
            return
        self.parsed_meshes.add(self.mesh.name)
        if self.parse_representations(element):
            self.assign_material_slots_to_faces(obj)

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

        item_id = self.mesh.BIMMeshProperties.ifc_item_ids.add()
        item_id.name = str(item.id())

        styled_item = item.StyledByItem[0]  # Cardinality is S[0:1]
        style_name = self.get_surface_style_name(styled_item)

        if not style_name:
            return

        if self.mesh.materials.get(style_name):
            item_id.slot_index = self.mesh.materials.find(style_name)
            return True

        style = bpy.data.materials.get(style_name)
        if not style:
            style = bpy.data.materials.new(style_name)
        self.parse_styled_item(styled_item, style)

        self.assign_style_to_mesh(style)
        item_id.slot_index = len(self.mesh.materials) - 1
        return True

    def assign_material_slots_to_faces(self, obj):
        if "ios_materials" not in self.mesh or not self.mesh["ios_materials"]:
            return
        if len(obj.material_slots) == 1:
            return
        material_to_slot = {}
        for i, material in enumerate(self.mesh["ios_materials"]):
            if material == "NULLMAT":
                continue
            elif "surface-style-" in material:
                material = material.split("-")[2]
            if len(bytes(material, "utf-8")) > 63:  # Blender material names are up to 63 UTF-8 bytes
                material = bytes(material, "utf-8")[0:63].decode("utf-8")

            slot_index = obj.material_slots.find(material)
            if slot_index == -1:
                # If we can't find the material, it is possible that the
                # material name is duplicated, and so a '.001' is added.
                # The maximum characters for the material name is 59 in this
                # scenario.
                material = bytes(material, "utf-8")[0:59].decode("utf-8")
                slot_index = [self.canonicalise_material_name(s.name) for s in obj.material_slots].index(material)
            material_to_slot[i] = slot_index

        if len(self.mesh.polygons) == len(self.mesh["ios_material_ids"]):
            material_index = [
                (material_to_slot[mat_id] if mat_id != -1 else 0) for mat_id in self.mesh["ios_material_ids"]
            ]
            self.mesh.polygons.foreach_set("material_index", material_index)

    def canonicalise_material_name(self, name):
        return re.sub(r"\.[0-9]{3}$", "", name)

    def parse_material(self, element):
        for association in element.HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                material_select = association.RelatingMaterial
                if material_select.is_a("IfcMaterialDefinition"):
                    self.create_definition(material_select)
                elif material_select.is_a("IfcMaterialUsageDefinition"):
                    self.create_usage_definition(material_select)
                elif material_select.is_a("IfcMaterialList"):
                    # Note that lists are deprecated
                    self.create_material_list(material_select)
                # To support IFC2X3 equivalent of IfcMaterialDefinition
                elif material_select.is_a("IfcMaterial") or material_select.is_a("IfcMaterialLayerSet"):
                    self.create_definition(material_select)
                # To support IFC2X3 equivalent of IfcMaterialUsageDefinition
                elif material_select.is_a("IfcMaterialLayerSetUsage"):
                    self.create_usage_definition(material_select)
                # IFC2X3 supports assigning a material layer directly. This is silly.
                elif material_select.is_a("IfcMaterialLayer"):
                    pass

    def create_layer_set_usage(self, usage):
        # TODO import rest of the layer set usage data
        self.create_definition(usage.ForLayerSet)

    def create_definition(self, material):
        if material.is_a("IfcMaterial"):
            self.create_single(material)
        elif material.is_a("IfcMaterialConstituentSet"):
            self.create_constituent_set(material)
        elif material.is_a("IfcMaterialLayerSet"):
            self.create_layer_set(material)
        elif material.is_a("IfcMaterialProfileSet"):
            self.create_profile_set(material)

    def create_usage_definition(self, material):
        if material.is_a("IfcMaterialLayerSetUsage"):
            self.create_layer_set_usage(material)
        elif material.is_a("IfcMaterialProfileSetUsage"):
            pass  # TODO

    def create_single(self, material):
        if material.Name not in self.materials:
            self.create_new_single(material)

    def create_layer_set(self, layer_set):
        for layer in layer_set.MaterialLayers:
            if layer.Material:
                if layer.Material.Name not in self.materials:
                    self.create_new_single(layer.Material)

    def create_constituent_set(self, constituent_set):
        for constituent in constituent_set.MaterialConstituents:
            if constituent.Material.Name not in self.materials:
                self.create_new_single(constituent.Material)

    def create_profile_set(self, profile_set):
        for profile in profile_set.MaterialProfiles:
            if profile.Material.Name not in self.materials:
                self.create_new_single(profile.Material)

    def create_material_list(self, material_list):
        for material in material_list.Materials:
            if material.Name not in self.materials:
                self.create_new_single(material)

    def create_new_single(self, material):
        self.materials[material.Name] = obj = bpy.data.materials.new(material.Name)
        obj.BIMObjectProperties.ifc_definition_id = int(material.id())
        if not material.HasRepresentation or not material.HasRepresentation[0].Representations:
            return
        for representation in material.HasRepresentation[0].Representations:
            if not representation.Items:
                continue
            for item in representation.Items:
                if not item.is_a("IfcStyledItem"):
                    continue
                self.parse_styled_item(item, obj)

    def get_surface_style_name(self, styled_item):
        if styled_item.Name:
            return styled_item.Name
        styles = self.get_styled_item_styles(styled_item)
        for style in styles:
            if not style.is_a("IfcSurfaceStyle"):
                continue
            if style.Name:
                return style.Name
            return str(style.id())
        return None  # We only support surface styles right now

    def parse_styled_item(self, styled_item, material):
        styles = self.get_styled_item_styles(styled_item)
        for style in styles:
            if not style.is_a("IfcSurfaceStyle"):
                continue
            material.BIMMaterialProperties.ifc_style_id = int(style.id())
            for surface_style in style.Styles:
                if surface_style.is_a("IfcSurfaceStyleShading"):
                    alpha = 1.0
                    # Transparency was added in IFC4
                    if hasattr(surface_style, "Transparency") and surface_style.Transparency:
                        alpha = 1 - surface_style.Transparency
                    material.diffuse_color = (
                        surface_style.SurfaceColour.Red,
                        surface_style.SurfaceColour.Green,
                        surface_style.SurfaceColour.Blue,
                        alpha,
                    )

    # IfcPresentationStyleAssignment is deprecated as of IFC4
    # However it is still widely used thanks to Revit :(
    def get_styled_item_styles(self, styled_item):
        styles = []
        for style in styled_item.Styles:
            if style.is_a("IfcPresentationStyleAssignment"):
                styles.extend(self.get_styled_item_styles(style))
            else:
                styles.append(style)
        return styles

    def resolve_mapped_representation_items(self, representation):
        items = []
        for item in representation.Items:
            if item.is_a("IfcMappedItem"):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            else:
                items.append(item)
        return items

    def assign_style_to_mesh(self, material):
        if not self.mesh:
            return
        self.mesh.materials.append(material)


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
        self.include_elements = []
        self.exclude_elements = []
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
        self.native_elements = {}
        self.native_data = {}
        self.aggregates = {}
        self.aggregate_collections = {}

        self.material_creator = MaterialCreator(ifc_import_settings, self)

    def profile_code(self, message):
        if not self.time:
            self.time = time.time()
        print("{} :: {:.2f}".format(message, time.time() - self.time))
        self.time = time.time()

    def execute(self):
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
        self.create_openings_collection()
        self.profile_code("Create opening collection")
        self.process_element_filter()
        self.profile_code("Process element filter")
        # TODO: Deprecate
        # self.parse_native_elements()
        # self.profile_code("Parsing native elements")
        self.create_grids()
        self.profile_code("Create grids")
        # TODO: Deprecate
        # self.create_native_products()
        # self.profile_code("Create native products")
        self.create_products()
        self.profile_code("Create products")
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

    def is_element_far_away(self, element):
        try:
            return self.is_point_far_away(element.ObjectPlacement.RelativePlacement.Location)
        except:
            pass

    def is_point_far_away(self, point):
        # Arbitrary threshold based on experience
        if hasattr(point, "Coordinates"):
            return (
                abs(point.Coordinates[0]) > 1000000
                or abs(point.Coordinates[1]) > 1000000
                or abs(point.Coordinates[2]) > 1000000
            )
        return abs(point[0]) > 1000000 or abs(point[1]) > 1000000 or abs(point[2]) > 1000000

    def process_element_filter(self):
        if not self.ifc_import_settings.ifc_selector:
            return
        self.include_elements = []
        selector = ifcopenshell.util.selector.Selector()
        elements = selector.parse(self.file, self.ifc_import_settings.ifc_selector)
        if self.ifc_import_settings.ifc_import_filter == "WHITELIST":
            self.include_elements = elements
        elif self.ifc_import_settings.ifc_import_filter == "BLACKLIST":
            self.exclude_elements = elements

    def parse_native_elements(self):
        self.parse_native_swept_disk_solid()
        self.parse_native_extruded_area_solid()
        self.parse_native_faceted_brep()
        if self.include_elements:
            include_global_ids = [e.GlobalId for e in self.include_elements]
            filtered_native_elements = {}
            for global_id in self.native_elements.keys():
                if global_id in include_global_ids:
                    filtered_native_elements[global_id] = self.native_elements[global_id]
            self.native_elements = filtered_native_elements
        elif self.exclude_elements:
            exclude_global_ids = [e.GlobalId for e in self.exclude_elements]
            filtered_native_elements = {}
            for global_id in self.native_elements.keys():
                if global_id not in exclude_global_ids:
                    filtered_native_elements[global_id] = self.native_elements[global_id]
            self.native_elements = filtered_native_elements

    def parse_native_swept_disk_solid(self):
        for element in self.file.by_type("IfcSweptDiskSolid"):
            if [e for e in self.file.get_inverse(element) if e.is_a("IfcBooleanResult")]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def parse_native_extruded_area_solid(self):
        for element in self.file.by_type("IfcExtrudedAreaSolid"):
            if element.SweptArea.is_a() not in [
                "IfcArbitraryClosedProfileDef",
                "IfcRectangleProfileDef",
                "IfcCircleProfileDef",
            ]:
                continue
            if [e for e in self.file.get_inverse(element) if e.is_a("IfcBooleanResult")]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def parse_native_faceted_brep(self):
        for element in self.file.by_type("IfcFacetedBrep"):
            if [e for e in self.file.get_inverse(element) if e.is_a("IfcBooleanResult")]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def swap_out_with_dummy_geometry(self, element):
        dummy_geometry = self.get_dummy_geometry()
        inverse_elements = self.file.get_inverse(element)
        for inverse_element in inverse_elements:
            if inverse_element.is_a("IfcShapeRepresentation"):
                inverse_element.RepresentationType = "Curve"
                for product in self.get_products_from_shape_representation(inverse_element):
                    self.native_elements.setdefault(product.GlobalId, {})[dummy_geometry.id()] = element
            ifcopenshell.util.element.replace_attribute(inverse_element, element, dummy_geometry)

    def get_dummy_geometry(self):
        point = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        direction = self.file.createIfcVector(self.file.createIfcDirection((0.0, 0.0, 1.0)), 1000.0)
        return self.file.createIfcLine(point, direction)

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
        if site and self.is_element_far_away(site[0]):
            return self.guess_georeferencing(site[0])
        building = self.find_decomposed_ifc_class(project, "IfcBuilding")
        if building and self.is_element_far_away(building[0]):
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
        props.blender_offset_type = "OBJECT_PLACEMENT"

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
        props.blender_offset_type = "CARTESIAN_POINT"

    def get_offset_point(self):
        offset_point = None
        elements_checked = 0
        # If more than these points aren't far away, the file probably isn't absolutely positioned
        element_checking_threshold = 100
        try:
            point_lists = self.file.by_type("IfcCartesianPointList3D")
        except:
            # IFC2X3 does not have IfcCartesianPointList3D
            point_lists = []
        for point_list in point_lists:
            elements_checked += 1
            if elements_checked > element_checking_threshold:
                return
            for i, point in enumerate(point_list.CoordList):
                if len(point) == 3 and self.is_point_far_away(point):
                    return point[0]

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
            if len(point.Coordinates) == 3 and self.is_point_far_away(point):
                return point[0]

    def apply_blender_offset_to_matrix(self, matrix):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and props.blender_offset_type == "OBJECT_PLACEMENT":
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
            element_matrix = self.get_local_placement(grid.ObjectPlacement)
            element_matrix[0][3] *= self.unit_scale
            element_matrix[1][3] *= self.unit_scale
            element_matrix[2][3] *= self.unit_scale
            u_axes = bpy.data.collections.new("UAxes")
            collection.children.link(u_axes)
            v_axes = bpy.data.collections.new("VAxes")
            collection.children.link(v_axes)
            self.create_grid_axes(grid.UAxes, u_axes, element_matrix)
            self.create_grid_axes(grid.VAxes, v_axes, element_matrix)
            if grid.WAxes:
                w_axes = bpy.data.collections.new("WAxes")
                collection.children.link(w_axes)
                self.create_grid_axes(grid.WAxes, w_axes, element_matrix)

    def create_grid_axes(self, axes, grid, matrix_world):
        for axis in axes:
            shape = ifcopenshell.geom.create_shape(self.settings_2d, axis.AxisCurve)
            mesh = self.create_mesh(axis, shape)
            obj = bpy.data.objects.new(f"IfcGridAxis/{axis.AxisTag}", mesh)
            obj.BIMObjectProperties.ifc_definition_id = axis.id()
            obj.matrix_world = matrix_world
            grid.objects.link(obj)

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
        if not self.native_elements:
            return
        # TODO: the iterator is kind of useless here, rewrite this
        iterator = ifcopenshell.geom.iterator(
            self.settings_native,
            self.file,
            multiprocessing.cpu_count(),
            include=[self.file.by_guid(guid) for guid in self.native_elements.keys()] or None,
        )
        valid_file = iterator.initialize()
        total = 0
        checkpoint = time.time()
        if not valid_file:
            return False
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
        total = 0
        while True:
            total += 1
            if total % 250 == 0:
                print("{} elements processed in {:.2f}s ...".format(total, time.time() - checkpoint))
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                if shape.context != "Body" and shape.guid in IfcStore.guid_map:
                    # We only load a single context, and we prioritise the Body context. See #1290.
                    pass
                else:
                    self.create_product(self.file.by_id(shape.guid), shape)
            if not iterator.next():
                break
        print("Done creating geometry")

    def create_annotation(self):
        self.create_curve_products(self.file.by_type("IfcAnnotation"))

    def create_structural_elements(self):
        self.create_curve_products(self.file.by_type("IfcStructuralCurveMember"))
        self.create_curve_products(self.file.by_type("IfcStructuralCurveConnection"))
        # self.create_curve_products(self.file.by_type("IfcStructuralPointConnection"))

    def create_curve_products(self, products):
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings_2d,
                self.file,
                multiprocessing.cpu_count(),
                include=products
            )
        else:
            iterator = ifcopenshell.geom.iterator(
                self.settings_2d, self.file, include=products
            )
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

    def create_product(self, element, shape=None):
        if element is None:
            return

        if not self.ifc_import_settings.should_import_spaces and element.is_a("IfcSpace"):
            return

        self.ifc_import_settings.logger.info("Creating object %s", element)

        if shape:
            mesh_name = self.get_mesh_name(shape.geometry)
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                if element.GlobalId in self.native_elements:
                    mesh = self.create_native_mesh(element, shape)
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
            obj.matrix_world = self.apply_blender_offset_to_matrix(mat)
            self.material_creator.create(element, obj, mesh)
        elif hasattr(element, "ObjectPlacement"):
            obj.matrix_world = self.apply_blender_offset_to_matrix(self.get_element_matrix(element))

        self.add_opening_relation(element, obj)

        if element.is_a("IfcOpeningElement"):
            obj.display_type = "WIRE"
        return obj

    def create_native_mesh(self, element, shape):
        # TODO This should be split off into its own module for run-time native mesh conversion
        data = self.native_elements[element.GlobalId]
        materials = []
        items = []
        for representation in self.get_body_representations(element.Representation.Representations):
            for item in representation["raw"].Items:
                material_name = self.get_representation_item_material_name(item)
                if not material_name:
                    # Magic string NULLMAT represents no material, unless this has a better approach
                    material_name = "NULLMAT"
                materials.append(material_name)
                if item.id() in data:
                    item = data[item.id()]
                if item.is_a() == "IfcExtrudedAreaSolid":
                    native = self.create_native_extruded_area_solid(item, element)
                    if native:
                        bmesh.ops.transform(
                            native["blender"], matrix=representation["matrix"], verts=native["blender"].verts
                        )
                        items.append(native)
                    else:
                        items.append(None)
                elif item.is_a("IfcSweptDiskSolid"):
                    items.append(
                        {
                            "blender": self.transform_curve(
                                self.create_native_swept_disk_solid(item, element), representation["matrix"]
                            ),
                            "raw": item,
                            "subitems": [],
                        }
                    )
                elif item.is_a("IfcFacetedBrep"):
                    bm = self.create_native_faceted_brep(item, element)
                    if bm:
                        bmesh.ops.transform(bm, matrix=representation["matrix"], verts=bm.verts)
                        items.append({"blender": bm, "raw": item, "subitems": []})
                    else:
                        items.append(None)
                else:
                    items.append(None)

        if not items:
            return None

        bevel_depth = None
        merged_curve = None
        merged_bm = bmesh.new()
        material_ids = []
        representation_items = []
        for i, item in enumerate(items):
            if not item:
                continue
            if isinstance(item["blender"], bpy.types.Curve):
                if bevel_depth is None:
                    bevel_depth = item["blender"].bevel_depth
                    merged_curve = item["blender"]
                elif item["blender"].bevel_depth == bevel_depth:
                    self.merge_curves(merged_curve, item["blender"])
                else:
                    # TODO: handle if there are multiple different radiuses
                    # We don't have a choice but to meshify it
                    pass
            elif isinstance(item["blender"], bmesh.types.BMesh):
                representation_items.append(
                    {
                        "name": item["raw"].is_a(),
                        "total_vertices": len(item["blender"].verts),
                        "subitems": item["subitems"],
                    }
                )
                total_polygons = len(item["blender"].faces)
                if merged_bm is None:
                    merged_bm = item["blender"]
                else:
                    self.merge_bmeshes(merged_bm, item["blender"])
                # Magic string NULLMAT represents no material, unless this has a better approach
                if materials[i] == "NULLMAT":
                    # Magic number -1 represents no material, until this has a better approach
                    material_ids += [-1] * total_polygons
                else:
                    material_ids += [i] * total_polygons
        if merged_curve:
            return merged_curve
        # TODO: handle both curve and bmeshes combined
        mesh = bpy.data.meshes.new("Native Mesh")
        merged_bm.to_mesh(mesh)
        merged_bm.free()
        mesh["ios_materials"] = materials
        mesh["ios_material_ids"] = material_ids
        mesh["ios_items"] = representation_items
        mesh.BIMMeshProperties.is_native = True
        return mesh

    def get_representation_item_material_name(self, item):
        if not item.StyledByItem:
            return
        styled_item = item.StyledByItem[0]
        return self.material_creator.get_surface_style_name(styled_item)

    def transform_curve(self, curve, matrix):
        for spline in curve.splines:
            for point in spline.points:
                point.co = matrix @ point.co
        return curve

    def merge_curves(self, a, b):
        for spline in b.splines:
            new_spline = a.splines.new("POLY")
            is_first = True
            for point in spline.points:
                if is_first:
                    is_first = False
                else:
                    new_spline.points.add(1)
                new_spline.points[-1].co = point.co
        return a

    def merge_bmeshes(self, a, b):
        mesh = bpy.data.meshes.new("x")
        b.to_mesh(mesh)
        b.free()
        a.from_mesh(mesh)
        return a

    def create_native_faceted_brep(self, item, element):
        vertex_map = {}
        vertices = []
        faces = []
        vertex_index = 0
        for face in item.Outer.CfsFaces:
            if len(face.Bounds) > 1:
                # TODO: implement tesselate_polygon
                return None
            for point in face.Bounds[0].Bound.Polygon:
                if point.id() not in vertex_map:
                    vertices.append([c * self.unit_scale for c in point.Coordinates])
                    vertex_map[point.id()] = vertex_index
                    vertex_index += 1
            faces.append([vertex_map[p.id()] for p in face.Bounds[0].Bound.Polygon])
        return self.bmesh_from_pydata(vertices, [], faces)

    def create_native_swept_disk_solid(self, item, element):
        # TODO: support inner radius, start param, and end param
        shape = ifcopenshell.geom.create_shape(self.settings_native, item.Directrix)
        mesh = self.create_mesh(element, shape, is_curve=True)
        mesh.bevel_depth = self.unit_scale * item.Radius
        return mesh

    def create_native_extruded_area_solid(self, item, element):
        # print(shape.materials)
        subitems = []
        if item.SweptArea.is_a() == "IfcArbitraryClosedProfileDef":
            shape = ifcopenshell.geom.create_shape(self.settings_native, item.SweptArea.OuterCurve)
            bm = self.bmesh_from_pydata(*self.shape_to_mesh(shape))
            bm.faces.new([v for v in bm.verts])
            bm.faces.ensure_lookup_table()
            subitems.append({"name": item.SweptArea.is_a(), "vertices": range(0, len(bm.verts))})
        elif item.SweptArea.is_a() == "IfcRectangleProfileDef":
            bm = self.bmesh_from_rectangle(item.SweptArea.XDim, item.SweptArea.YDim)
            if item.SweptArea.Position:
                bmesh.ops.transform(bm, matrix=self.get_axis2placement(item.SweptArea.Position), verts=bm.verts)
            bmesh.ops.transform(bm, matrix=mathutils.Matrix() * self.unit_scale, verts=bm.verts)
            subitems.append({"name": item.SweptArea.is_a(), "vertices": [0, 1, 2, 3]})
        elif item.SweptArea.is_a() == "IfcCircleProfileDef":
            bm = self.bmesh_from_circle(item.SweptArea.Radius)
            if item.SweptArea.Position:
                bmesh.ops.transform(bm, matrix=self.get_axis2placement(item.SweptArea.Position), verts=bm.verts)
            bmesh.ops.transform(bm, matrix=mathutils.Matrix() * self.unit_scale, verts=bm.verts)
            subitems.append(
                {
                    "name": item.SweptArea.is_a(),
                    # This strange vertice offset is due to a Blender quirk
                    "vertices": range(1, len(bm.verts) + 1),
                }
            )
        else:
            # TODO: what if we can't handle it?
            return
        results = bmesh.ops.extrude_face_region(bm, geom=[bm.faces[0]])
        bm.faces.ensure_lookup_table()
        offset = self.unit_scale * item.Depth * mathutils.Vector(item.ExtrudedDirection.DirectionRatios)
        if item.SweptArea.is_a() == "IfcCircleProfileDef":
            # Circle profiles have a quirk apparently in Blender
            subitems.append({"name": "ExtrudedDirection", "vertices": [0, 1]})
        else:
            subitems.append({"name": "ExtrudedDirection", "vertices": [0, len(subitems[-1]["vertices"])]})
        for geom in results["geom"]:
            if isinstance(geom, bmesh.types.BMVert):
                geom.co += offset
        if item.Position:
            bmesh.ops.transform(bm, matrix=self.scale_matrix(self.get_axis2placement(item.Position)), verts=bm.verts)
        return {"blender": bm, "raw": item, "subitems": subitems}
        # mesh['ios_material_ids'] = [0] * len(bm.faces)

    def bmesh_from_rectangle(self, x, y):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=x / 2)
        bm.verts.ensure_lookup_table()
        diff_vector = mathutils.Vector((0.0, (x - y) / 2.0, 0.0))
        bm.verts[0].co += diff_vector
        bm.verts[1].co += diff_vector
        bm.verts[2].co -= diff_vector
        bm.verts[3].co -= diff_vector
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        return bm

    def bmesh_from_circle(self, r):
        bm = bmesh.new()
        # Segments should be a multiple of 4 to easily measure the diameter
        si_radius = r * self.unit_scale
        # I'm arbitrarily deciding that 28 verts is enough for a 1m radius
        closest_power_of_2 = int(math.log(si_radius, 2) + 0.5)
        segments = (closest_power_of_2 * 4) + 28
        bmesh.ops.create_circle(bm, cap_ends=True, segments=segments, radius=r)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        return bm

    def merge_by_class(self):
        merge_set = {}
        for obj in self.added_data.values():
            if "/" not in obj.name or "IfcRelAggregates" in obj.users_collection[0].name:
                continue
            merge_set.setdefault(obj.name.split("/")[0], []).append(obj)
        self.merge_objects(merge_set)

    def merge_by_material(self):
        merge_set = {}
        for obj in self.added_data.values():
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
            if element.is_a("IfcSpace"):
                continue
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

    def create_aggregate(self, rel_aggregate):
        element = rel_aggregate.RelatingObject

        obj = bpy.data.objects.new("{}/{}".format(element.is_a(), element.Name), None)
        self.link_element(element, obj)

        container = self.get_aggregate_spatial_container(element)
        container_collection = self.spatial_structure_elements[container.GlobalId]["blender"]

        collection = bpy.data.collections.new(obj.name)
        container_collection.children.link(collection)
        collection.objects.link(obj)

        self.aggregates[element.GlobalId] = obj
        self.aggregate_collections[rel_aggregate.id()] = collection

    def get_aggregate_spatial_container(self, element):
        if hasattr(element, "ContainedInStructure") and element.ContainedInStructure:
            container = element.ContainedInStructure[0].RelatingStructure
        elif hasattr(element, "Decomposes") and element.Decomposes:
            return self.get_aggregate_spatial_container(element.Decomposes[0].RelatingObject)
        if container.is_a("IfcSpace"):
            return self.get_aggregate_spatial_container(container)
        return container

    def create_openings_collection(self):
        self.opening_collection = bpy.data.collections.new("IfcOpeningElements")
        self.project["blender"].children.link(self.opening_collection)

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
        for global_id, obj in self.added_data.items():
            self.place_object_in_spatial_tree(self.file.by_guid(global_id), obj)

    def place_object_in_spatial_tree(self, element, obj):
        if element.is_a("IfcProject"):
            return
        elif element.is_a("IfcTypeObject"):
            self.type_collection.objects.link(obj)
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
            if container.is_a("IfcSpace"):
                return self.place_object_in_spatial_tree(container, obj)
            elif element.is_a("IfcGrid"):
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
                if element.is_a("IfcSpatialStructureElement") and not element.is_a("IfcSpace"):
                    global_id = element.GlobalId
                else:
                    global_id = element.Decomposes[0].RelatingObject.GlobalId
                if global_id in self.spatial_structure_elements:
                    if (
                        element.is_a("IfcSpatialStructureElement")
                        and not element.is_a("IfcSpace")
                        and "blender_obj" in self.spatial_structure_elements[global_id]
                    ):
                        bpy.data.objects.remove(self.spatial_structure_elements[global_id]["blender_obj"])
                    collection = self.spatial_structure_elements[global_id]["blender"]
                # This may occur if we are nesting an IfcSpace (which is special
                # since it does not have a collection within an IfcSpace
                if not collection:
                    return self.place_object_in_spatial_tree(element.Decomposes[0].RelatingObject, obj)
            else:
                collection = self.aggregate_collections[element.Decomposes[0].id()]
            if collection:
                collection.objects.link(obj)
            else:
                self.ifc_import_settings.logger.error("An element could not be placed in the spatial tree %s", element)
        elif element.is_a("IfcOpeningElement"):
            self.opening_collection.objects.link(obj)
        else:
            self.ifc_import_settings.logger.warning("Warning: this object is outside the spatial hierarchy %s", element)
            bpy.context.scene.collection.objects.link(obj)

    def cast_edge_case_attribute(self, ifc_class, key, value):
        if key == "RefLatitude" or key == "RefLongitude":
            return ifcopenshell.util.geolocation.dms2dd(*value)
        return value

    def get_element_matrix(self, element, mesh_name=None):
        result = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        result[0][3] *= self.unit_scale
        result[1][3] *= self.unit_scale
        result[2][3] *= self.unit_scale
        return result

    def get_body_representations(self, representations, matrix=None):
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
                        self.get_body_representations([item.MappingSource.MappedRepresentation], transform @ matrix)
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

    def create_mesh(self, element, shape, is_curve=False):
        try:
            if hasattr(shape, "geometry"):
                geometry = shape.geometry
            else:
                geometry = shape

            if is_curve:
                return self.create_curve(geometry)

            mesh = bpy.data.meshes.new(self.get_mesh_name(geometry))

            props = bpy.context.scene.BIMGeoreferenceProperties
            if props.has_blender_offset and props.blender_offset_type == "CARTESIAN_POINT":
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

            ios_materials = []
            for mat in geometry.materials:
                if mat.original_name():
                    ios_materials.append(mat.original_name())
                else:
                    ios_materials.append(mat.name)
            mesh["ios_materials"] = ios_materials
            mesh["ios_material_ids"] = geometry.material_ids
            return mesh
        except:
            self.ifc_import_settings.logger.error("Could not create mesh for %s", element)
            import traceback

            print(traceback.format_exc())

    def create_curve(self, geometry):
        curve = bpy.data.curves.new(geometry.id, type="CURVE")
        curve.dimensions = "3D"
        curve.resolution_u = 2
        polyline = curve.splines.new("POLY")
        e = geometry.edges
        v = geometry.verts
        vertices = [[v[i], v[i + 1], v[i + 2], 1] for i in range(0, len(v), 3)]
        edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
        v2 = None
        for edge in edges:
            v1 = vertices[edge[0]]
            if v1 != v2:
                polyline = curve.splines.new("POLY")
                polyline.points[-1].co = v1
            v2 = vertices[edge[1]]
            polyline.points.add(1)
            polyline.points[-1].co = v2
        return curve

    def shape_to_mesh(self, shape):
        if hasattr(shape, "geometry"):
            geometry = shape.geometry
        else:
            geometry = shape
        f = geometry.faces
        e = geometry.edges
        v = geometry.verts
        vertices = [[v[i], v[i + 1], v[i + 2]] for i in range(0, len(v), 3)]
        faces = [[f[i], f[i + 1], f[i + 2]] for i in range(0, len(f), 3)]
        if faces:
            edges = []
        else:
            edges = [[e[i], e[i + 1]] for i in range(0, len(e), 2)]
        return (vertices, edges, faces)

    def bmesh_from_pydata(self, verts=[], edges=[], faces=[]):
        bm = bmesh.new()
        [bm.verts.new(co) for co in verts]
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
        if faces:
            for face in faces:
                bm.faces.new(tuple(bm.verts[i] for i in face))
            bm.faces.index_update()
        bm.faces.ensure_lookup_table()
        if edges:
            for edge in edges:
                edge_seq = tuple(bm.verts[i] for i in edge)
                try:
                    bm.edges.new(edge_seq)
                except ValueError:
                    # edge exists!
                    pass
            bm.edges.index_update()
        bm.edges.ensure_lookup_table()
        return bm

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
        self.added_data[element.GlobalId] = obj
        IfcStore.link_element(element, obj)


class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
        self.diff_file = None
        self.should_import_spaces = False
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
