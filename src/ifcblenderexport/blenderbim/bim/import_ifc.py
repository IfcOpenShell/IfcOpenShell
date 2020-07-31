import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.geolocation
import ifcopenshell.util.selector
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
from pathlib import Path
from . import helper
from . import schema
from . import ifc

class FileCopy(threading.Thread):
    def __init__(self, file_path, destination):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.destination = destination

    def run(self):
        shutil.copy(self.file_path, self.destination)

class MaterialCreator():
    def __init__(self, ifc_import_settings):
        self.mesh = None
        self.materials = {}
        self.current_object_materials = []
        self.parsed_meshes = []
        self.ifc_import_settings = ifc_import_settings

    def create(self, element, obj, mesh):
        self.current_object_materials = []
        self.obj = obj
        self.mesh = mesh
        if (hasattr(element, 'Representation') and not element.Representation) \
                or (hasattr(element, 'RepresentationMaps') and not element.RepresentationMaps):
            return
        if self.ifc_import_settings.should_treat_styled_item_as_material \
                and self.mesh.name in self.parsed_meshes:
            return
        self.parse_material(element)
        self.parsed_meshes.append(self.mesh.name)
        if self.parse_representations(element):
            self.assign_material_slots_to_faces(obj, self.mesh)
            self.parsed_meshes.append(self.mesh.name)

    def parse_representations(self, element):
        has_parsed = False
        if hasattr(element, 'Representation'):
            for representation in element.Representation.Representations:
                if self.parse_representation(representation):
                    has_parsed = True
        elif hasattr(element, 'RepresentationMaps'):
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
        styled_item = item.StyledByItem[0]

        material_name = self.get_material_name(styled_item)

        if material_name in self.current_object_materials:
            return True

        if material_name not in self.materials.keys():
            material = bpy.data.materials.get(material_name)
            if material:
                self.materials[material_name] = material
            else:
                self.materials[material_name] = bpy.data.materials.new(material_name)
                self.parse_styled_item(styled_item, self.materials[material_name])

        if self.ifc_import_settings.should_treat_styled_item_as_material:
            # Revit workaround: since Revit/DDS-CAD exports all material
            # assignments as individual object styled items. Treating them as
            # reusable materials makes things much more efficient in Blender.
            self.assign_material_to_mesh(self.materials[material_name])
        else:
            # Proper behaviour
            self.assign_material_to_mesh(self.materials[material_name], is_styled_item=True)
        return True

    def assign_material_slots_to_faces(self, obj, mesh):
        if 'ios_materials' not in mesh or not mesh['ios_materials']:
            return
        if len(obj.material_slots) == 1:
            return
        slots = [self.canonicalise_material_name(s.name) for s in obj.material_slots]
        material_to_slot = {}
        for i, material in enumerate(mesh['ios_materials']):
            if material == 'NULLMAT':
                continue
            elif 'surface-style-' in material:
                material = material.split('-')[2]
            if len(material) > 63: # Blender material names are up to 63 characters
                material = material[0:63]
            try:
                material_to_slot[i] = slots.index(material)
            except:
                # If the material name duplicates, a `.001` is added, this
                # reduces the maxmium characters for the material name to 59.
                material = material[0:59]
                material_to_slot[i] = slots.index(material)

        if len(mesh.polygons) == len(mesh['ios_material_ids']):
            material_index = [(material_to_slot[mat_id] if mat_id != -1
                else 0) for mat_id in mesh['ios_material_ids']]
            mesh.polygons.foreach_set('material_index', material_index)

    def canonicalise_material_name(self, name):
        return re.sub(r'\.[0-9]{3}', '', name)

    def parse_material(self, element):
        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):
                material_select = association.RelatingMaterial
                if material_select.is_a('IfcMaterialDefinition'):
                    self.create_definition(material_select)
                elif material_select.is_a('IfcMaterialLayerSetUsage'):
                    self.create_layer_set_usage(material_select)

    def create_layer_set_usage(self, usage):
        # TODO import rest of the layer set usage data
        self.create_definition(usage.ForLayerSet)

    def create_definition(self, material):
        if material.is_a('IfcMaterial'):
            self.create_single(material)
        elif material.is_a('IfcMaterialLayerSet'):
            self.create_layer_set(material)

    def create_single(self, material):
        if material.Name not in self.materials:
            self.create_new_single(material)
        return self.assign_material_to_mesh(self.materials[material.Name])

    def create_layer_set(self, layer_set):
        for layer in layer_set.MaterialLayers:
            if layer.Material:
                if layer.Material.Name not in self.materials:
                    # TODO import rest of the layer set data
                    self.create_new_single(layer.Material)
                self.assign_material_to_mesh(self.materials[layer.Material.Name])

    def create_new_single(self, material):
        self.materials[material.Name] = bpy.data.materials.new(material.Name)
        if not material.HasRepresentation \
                or not material.HasRepresentation[0].Representations:
            return
        for representation in material.HasRepresentation[0].Representations:
            if not representation.Items:
                continue
            for item in representation.Items:
                if not item.is_a('IfcStyledItem'):
                    continue
                self.parse_styled_item(item, self.materials[material.Name])

    def get_material_name(self, styled_item):
        if styled_item.Name:
            return styled_item.Name
        styled_item = self.resolve_presentation_style_assignment(styled_item)
        for style in styled_item.Styles:
            if not style.is_a('IfcSurfaceStyle'):
                continue
            if style.Name:
                return style.Name
            return str(style.id())
        return str(styled_item.id())

    def parse_styled_item(self, styled_item, material):
        styled_item = self.resolve_presentation_style_assignment(styled_item)
        for style in styled_item.Styles:
            if not style.is_a('IfcSurfaceStyle'):
                continue
            external_style = None
            for surface_style in style.Styles:
                if surface_style.is_a('IfcSurfaceStyleShading'):
                    alpha = 1.
                    # Transparency was added in IFC4
                    if hasattr(surface_style, 'Transparency') \
                            and surface_style.Transparency:
                        alpha = 1 - surface_style.Transparency
                    material.diffuse_color = (
                        surface_style.SurfaceColour.Red,
                        surface_style.SurfaceColour.Green,
                        surface_style.SurfaceColour.Blue,
                        alpha)
                elif surface_style.is_a('IfcExternallyDefinedSurfaceStyle'):
                    external_style = surface_style
            if external_style:
                material.BIMMaterialProperties.is_external = True
                material.BIMMaterialProperties.location = external_style.Location
                material.BIMMaterialProperties.identification = external_style.Identification
                material.BIMMaterialProperties.name = external_style.Name

    # IfcPresentationStyleAssignment is deprecated as of IFC4
    # However it is still widely used thanks to Revit :(
    def resolve_presentation_style_assignment(self, styled_item):
        for style in styled_item.Styles:
            if style.is_a('IfcPresentationStyleAssignment'):
                return style
        return styled_item

    def resolve_mapped_representation_items(self, representation):
        items = []
        for item in representation.Items:
            if item.is_a('IfcMappedItem'):
                items.extend(item.MappingSource.MappedRepresentation.Items)
            else:
                items.append(item)
        return items

    def assign_material_to_mesh(self, material, is_styled_item=False):
        self.mesh.materials.append(material)
        self.current_object_materials.append(material.name)
        if is_styled_item:
            index = len(self.obj.material_slots) - 1
            self.obj.material_slots[index].link = 'OBJECT'
            self.obj.material_slots[index].material = material

class IfcImporter():
    def __init__(self, ifc_import_settings):
        self.ifc_import_settings = ifc_import_settings
        self.diff = None
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        if self.ifc_import_settings.should_import_curves:
            self.settings.set(self.settings.INCLUDE_CURVES, True)
        self.settings_native = ifcopenshell.geom.settings()
        self.settings_native.set(self.settings_native.INCLUDE_CURVES, True)
        if self.ifc_import_settings.should_import_native:
            self.settings.set(self.settings.DISABLE_OPENING_SUBTRACTIONS, True)
            self.ifc_import_settings.should_import_opening_elements = True
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set(self.settings_2d.INCLUDE_CURVES, True)
        self.existing_elements = {}
        self.include_elements = []
        self.exclude_elements = []
        self.project = None
        self.classifications = {}
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
        self.groups = {}
        self.aggregates = {}
        self.aggregate_collection = None
        self.aggregate_collections = {}

        self.material_creator = MaterialCreator(ifc_import_settings)

    def profile_code(self, message):
        if not self.ifc_import_settings.should_import_with_profiling:
            return
        if not self.time:
            self.time = time.time()
        print('{} :: {:.2f}'.format(message, time.time() - self.time))
        self.time = time.time()

    def execute(self):
        self.profile_code('Starting import process')
        self.load_existing_rooted_elements()
        self.profile_code('Load existing rooted elements')
        self.load_diff()
        self.profile_code('Load diff')
        self.cache_file()
        self.profile_code('Caching file')
        self.load_file()
        self.profile_code('Loading file')
        self.set_ifc_file()
        self.profile_code('Setting file')
        if self.ifc_import_settings.should_auto_set_workarounds:
            self.auto_set_workarounds()
            self.profile_code('Set vendor worksarounds')
        self.calculate_unit_scale()
        self.profile_code('Calculate unit scale')
        self.filter_ifc()
        self.profile_code('Filtering ifc')
        self.patch_ifc()
        self.profile_code('Patching ifc')
        self.set_units()
        self.profile_code('Set units')
        self.create_geometric_representation_contexts()
        self.profile_code('Create contexts')
        self.create_project()
        self.profile_code('Create project')
        self.create_classifications()
        self.profile_code('Create classifications')
        self.create_constraints()
        self.profile_code('Create constraints')
        self.create_document_information()
        self.profile_code('Create doc info')
        self.create_document_references()
        self.profile_code('Create doc refs')
        self.create_spatial_hierarchy()
        self.profile_code('Create spatial hierarchy')
        self.purge_diff()
        self.profile_code('Purge diffs')
        self.create_type_products()
        self.profile_code('Create type products')
        if self.ifc_import_settings.should_import_aggregates:
            self.create_aggregates()
            self.profile_code('Create aggregates')
        self.create_openings_collection()
        self.profile_code('Create opening collection')
        self.process_element_filter()
        self.profile_code('Process element filter')
        if self.ifc_import_settings.should_import_native:
            self.parse_native_elements()
            self.profile_code('Parsing native elements')
        self.create_georeferencing()
        self.profile_code('Georeferencing ifc')
        self.create_groups()
        self.profile_code('Creating groups')
        self.create_grids()
        self.profile_code('Creating grids')
        if self.ifc_import_settings.should_import_native:
            self.create_native_products()
        self.profile_code('Creating native products')
        # TODO: Deprecate after bug #682 is fixed and the new importer is stable
        if self.ifc_import_settings.should_use_legacy:
            self.create_products_legacy()
        else:
            self.create_products()
            self.profile_code('Creating meshified products')
        self.relate_openings()
        self.profile_code('Relating openings')
        self.place_objects_in_spatial_tree()
        self.profile_code('Placing objects in spatial tree')
        if self.ifc_import_settings.should_merge_aggregates:
            self.merge_aggregates()
            self.profile_code('Merging aggregates')
        if self.ifc_import_settings.should_merge_by_class:
            self.merge_by_class()
            self.profile_code('Merging by class')
        elif self.ifc_import_settings.should_merge_by_material:
            self.merge_by_material()
            self.profile_code('Merging by material')
        if self.ifc_import_settings.should_merge_materials_by_colour \
                or (self.ifc_import_settings.should_auto_set_workarounds \
                    and len(self.material_creator.materials) > 300):
            self.merge_materials_by_colour()
            self.profile_code('Merging by colour')
        self.add_project_to_scene()
        self.profile_code('Add project to scene')
        if self.ifc_import_settings.should_clean_mesh and len(self.file.by_type('IfcElement')) < 10000:
            self.clean_mesh()
            self.profile_code('Mesh cleaning')

    def auto_set_workarounds(self):
        if 'DDS-CAD' in self.file.wrapped_data.header.file_name.originating_system \
                or 'DDS' in self.file.wrapped_data.header.file_name.preprocessor_version:
            self.ifc_import_settings.should_treat_styled_item_as_material = True
            self.ifc_import_settings.should_reset_absolute_coordinates = True
        applications = self.file.by_type('IfcApplication')
        if not applications:
            return
        if applications[0].ApplicationIdentifier == 'Revit':
            self.ifc_import_settings.should_treat_styled_item_as_material = True
            if self.is_ifc_class_far_away('IfcSite'):
                self.ifc_import_settings.should_ignore_site_coordinates = True
            if self.is_ifc_class_far_away('IfcBuilding'):
                self.ifc_import_settings.should_ignore_building_coordinates = True
        elif applications[0].ApplicationFullName.lower() == '12d model':
            self.ifc_import_settings.should_reset_absolute_coordinates = True
        elif 'Civil 3D' in applications[0].ApplicationFullName:
            self.ifc_import_settings.should_reset_absolute_coordinates = True
        elif applications[0].ApplicationFullName == 'Tekla Structures':
            if self.is_ifc_class_far_away('IfcSite'):
                self.ifc_import_settings.should_ignore_site_coordinates = True

    def is_ifc_class_far_away(self, ifc_class):
        for site in self.file.by_type(ifc_class):
            if not site.ObjectPlacement \
                    or not site.ObjectPlacement.RelativePlacement \
                    or not site.ObjectPlacement.RelativePlacement.Location:
                continue
            if self.is_point_far_away(site.ObjectPlacement.RelativePlacement.Location):
                return True

    def is_point_far_away(self, point):
        # Arbitrary threshold based on experience
        if hasattr(point, 'Coordinates'):
            return abs(point.Coordinates[0]) > 1000000 \
                or abs(point.Coordinates[1]) > 1000000 \
                or abs(point.Coordinates[2]) > 1000000
        return abs(point[0]) > 1000000 \
            or abs(point[1]) > 1000000 \
            or abs(point[2]) > 1000000

    def process_element_filter(self):
        if not self.ifc_import_settings.ifc_selector:
            return
        self.include_elements = []
        selector = ifcopenshell.util.selector.Selector()
        elements = selector.parse(self.file, self.ifc_import_settings.ifc_selector)
        if self.ifc_import_settings.ifc_import_filter == 'WHITELIST':
            self.include_elements = elements
        elif self.ifc_import_settings.ifc_import_filter == 'BLACKLIST':
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
        for element in self.file.by_type('IfcSweptDiskSolid'):
            if [e for e in self.file.get_inverse(element) if e.is_a('IfcBooleanResult')]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def parse_native_extruded_area_solid(self):
        for element in self.file.by_type('IfcExtrudedAreaSolid'):
            if element.SweptArea.is_a() not in [
                    'IfcArbitraryClosedProfileDef',
                    'IfcRectangleProfileDef'
                    ]:
                continue
            if [e for e in self.file.get_inverse(element) if e.is_a('IfcBooleanResult')]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def parse_native_faceted_brep(self):
        for element in self.file.by_type('IfcFacetedBrep'):
            if [e for e in self.file.get_inverse(element) if e.is_a('IfcBooleanResult')]:
                continue
            self.swap_out_with_dummy_geometry(element)

    def swap_out_with_dummy_geometry(self, element):
        dummy_geometry = self.get_dummy_geometry()
        inverse_elements = self.file.get_inverse(element)
        for inverse_element in inverse_elements:
            if inverse_element.is_a('IfcShapeRepresentation'):
                inverse_element.RepresentationType = 'Curve'
                for product in self.get_products_from_shape_representation(inverse_element):
                    self.native_elements.setdefault(product.GlobalId, {})[dummy_geometry.id()] = element
            self.replace_attribute(inverse_element, element, dummy_geometry)

    def get_dummy_geometry(self):
        point = self.file.createIfcCartesianPoint((0., 0., 0.))
        direction = self.file.createIfcVector(self.file.createIfcDirection((0., 0., 1.)), 1000.)
        return self.file.createIfcLine(point, direction)

    def get_products_from_shape_representation(self, element):
        products = [pr.ShapeOfProduct[0] for pr in element.OfProductRepresentation]
        for rep_map in element.RepresentationMap:
            for usage in rep_map.MapUsage:
                for inverse_element in self.file.get_inverse(usage):
                    if inverse_element.is_a('IfcShapeRepresentation'):
                        products.extend(self.get_products_from_shape_representation(inverse_element))
        return products

    def replace_attribute(self, element, old, new):
        for i, attribute in enumerate(element):
            if attribute == old:
                element[i] = new
            elif isinstance(attribute, tuple):
                new_attribute = list(attribute)
                for j, item in enumerate(attribute):
                    if item == old:
                        new_attribute[j] = new
                        element[i] = new_attribute

    def filter_ifc(self):
        for element in self.file.by_type('IfcElement'):
            if self.diff \
                    and element.GlobalId not in self.diff['added'] \
                    and element.GlobalId not in self.diff['changed'].keys():
                self.file.remove(element)

    def patch_ifc(self):
        project = self.file.by_type('IfcProject')[0]
        if self.ifc_import_settings.should_ignore_site_coordinates:
            sites = self.find_decomposed_ifc_class(project, 'IfcSite')
            for site in sites:
                self.patch_placement_to_origin(site)
        if self.ifc_import_settings.should_ignore_building_coordinates:
            buildings = self.find_decomposed_ifc_class(project, 'IfcBuilding')
            for building in buildings:
                self.patch_placement_to_origin(building)
        if self.ifc_import_settings.should_reset_absolute_coordinates:
            self.reset_absolute_coordinates()

    def reset_absolute_coordinates(self):
        # 12D can have some funky coordinates out of any sensible range. This
        # method will not work all the time, but will catch most issues.
        offset_point = None
        try:
            point_lists = self.file.by_type('IfcCartesianPointList3D')
        except:
            # IFC2X3 does not have IfcCartesianPointList3D
            point_lists = []
        for point_list in point_lists:
            coord_list = [None] * len(point_list.CoordList)
            for i, point in enumerate(point_list.CoordList):
                if len(point) == 2 or not self.is_point_far_away(point):
                    coord_list[i] = point
                    continue
                if not offset_point:
                    offset_point = (point[0], point[1], point[2])
                    self.ifc_import_settings.logger.info(f'Resetting absolute coordinates by {point}')
                point = (
                    point[0] - offset_point[0],
                    point[1] - offset_point[1],
                    point[2] - offset_point[2]
                )
                coord_list[i] = point
            point_list.CoordList = coord_list
        for point in self.file.by_type('IfcCartesianPoint'):
            if len(point.Coordinates) == 2 or not self.is_point_far_away(point):
                continue
            if not offset_point:
                offset_point = (point.Coordinates[0], point.Coordinates[1], point.Coordinates[2])
                self.ifc_import_settings.logger.info(f'Resetting absolute coordinates by {point}')
            point.Coordinates = (
                point.Coordinates[0] - offset_point[0],
                point.Coordinates[1] - offset_point[1],
                point.Coordinates[2] - offset_point[2]
            )
        if not offset_point:
            return
        if self.file.wrapped_data.schema == 'IFC2X3':
            properties = [
                self.file.createIfcPropertySingleValue('Eastings', None,
                    self.file.createIfcLengthMeasure(offset_point[0])),
                self.file.createIfcPropertySingleValue('Northings', None,
                    self.file.createIfcLengthMeasure(offset_point[1])),
                self.file.createIfcPropertySingleValue('OrthogonalHeight', None,
                    self.file.createIfcLengthMeasure(offset_point[2]))
            ]
            history = self.file.createIfcOwnerHistory()
            pset = self.file.createIfcPropertySet(
                ifcopenshell.guid.new(), history, 'EPset_MapConversion', None, properties)
            self.file.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(), history, None, None, self.file.by_type('IfcSite'), pset)
        else:
            # We don't have the full geolocation information, so we'll add what we can
            scene = bpy.context.scene
            scene.MapConversion.eastings = str(offset_point[0])
            scene.MapConversion.northings = str(offset_point[1])
            scene.MapConversion.orthogonal_height = str(offset_point[2])

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

    def patch_placement_to_origin(self, element):
        element.ObjectPlacement.RelativePlacement.Location.Coordinates = (0., 0., 0.)
        if element.ObjectPlacement.RelativePlacement.Axis:
            element.ObjectPlacement.RelativePlacement.Axis.DirectionRatios = (0., 0., 1.)
        if element.ObjectPlacement.RelativePlacement.RefDirection:
            element.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios = (1., 0., 0.)

    def create_georeferencing(self):
        try:
            map_conversion = self.file.by_type('IfcMapConversion')
            projected_crs = self.file.by_type('IfcProjectedCRS')
            if not map_conversion or not projected_crs:
                return
        except:
            return # For example, in IFC2X3
        map_conversion = map_conversion[0]
        projected_crs = projected_crs[0]
        scene = bpy.context.scene
        scene.BIMProperties.has_georeferencing = True
        map_conversion_map = {
            'Eastings': 'eastings',
            'Northings': 'northings',
            'OrthogonalHeight': 'orthogonal_height',
            'XAxisAbscissa': 'x_axis_abscissa',
            'XAxisOrdinate': 'x_axis_ordinate',
            'Scale': 'scale'
        }
        target_crs_map = {
            'Name': 'name',
            'Description': 'description',
            'GeodeticDatum': 'geodetic_datum',
            'VerticalDatum': 'vertical_datum',
            'MapProjection': 'map_projection',
            'MapZone': 'map_zone',
            'MapUnit': 'map_unit'
        }
        for keyA, keyB in map_conversion_map.items():
            value = getattr(map_conversion, keyA)
            if value is not None:
                setattr(scene.MapConversion, keyB, str(value))
        for keyA, keyB in target_crs_map.items():
            value = getattr(projected_crs, keyA)
            if value is not None:
                if keyA == 'MapUnit':
                    value = self.get_unit_name(value)
                setattr(scene.TargetCRS, keyB, str(value))

    def get_unit_name(self, named_unit):
        name = ''
        if hasattr(named_unit, 'Prefix') and named_unit.Prefix:
            name += named_unit.Prefix
        name += named_unit.Name
        return name

    def create_groups(self):
        group_collection = None
        for collection in self.project['blender'].children:
            if collection.name == 'Groups':
                group_collection = collection
                break
        if group_collection is None:
            group_collection = bpy.data.collections.new('Groups')
            self.project['blender'].children.link(group_collection)
        for element in self.file.by_type('IfcGroup'):
            self.create_group(element, group_collection)

    def create_group(self, element, group_collection):
        if element.GlobalId in self.existing_elements:
            obj = self.existing_elements[element.GlobalId]
        else:
            obj = bpy.data.objects.new(f'{element.is_a()}/{element.Name}', None)
            self.add_element_attributes(element, obj)
            group_collection.objects.link(obj)
        self.groups[element.GlobalId] = {
            'ifc': element,
            'blender': obj
        }

    def create_grids(self):
        grids = self.file.by_type('IfcGrid')
        for grid in grids:
            collection = bpy.data.collections.new(self.get_name(grid))
            self.project['blender'].children.link(collection)
            element_matrix = self.get_local_placement(grid.ObjectPlacement)
            element_matrix[0][3] *= self.unit_scale
            element_matrix[1][3] *= self.unit_scale
            element_matrix[2][3] *= self.unit_scale
            self.create_grid_axes(grid.UAxes, collection, element_matrix)
            self.create_grid_axes(grid.VAxes, collection, element_matrix)
            self.create_grid_axes(grid.WAxes, collection, element_matrix)

    def create_grid_axes(self, axes, grid, matrix_world):
        if not axes:
            return
        for axis in axes:
            shape = ifcopenshell.geom.create_shape(self.settings_2d, axis.AxisCurve)
            mesh = self.create_mesh(axis, shape)
            obj = bpy.data.objects.new(f'IfcGridAxis/{axis.AxisTag}', mesh)
            obj.matrix_world = matrix_world
            grid.objects.link(obj)

    def create_type_products(self):
        type_products = self.file.by_type('IfcTypeProduct')
        for collection in self.project['blender'].children:
            if collection.name == 'Types':
                self.type_collection = collection
                break
        if not self.type_collection:
            self.type_collection = bpy.data.collections.new('Types')
            self.project['blender'].children.link(self.type_collection)
        for type_product in type_products:
            self.create_type_product(type_product)

    def create_type_product(self, element):
        self.ifc_import_settings.logger.info('Creating object {}'.format(element))
        if element.GlobalId in self.existing_elements:
            return
        representation_map = self.get_type_product_body_representation_map(element)
        mesh = None
        if self.ifc_import_settings.should_import_type_representations and representation_map:
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, representation_map.MappedRepresentation)
                mesh_name = f'mesh-{shape.id}'
                mesh = self.meshes.get(mesh_name)
                if mesh is None:
                    mesh = self.create_mesh(element, shape)
                    self.meshes[mesh_name] = mesh
            except:
                self.ifc_import_settings.logger.error('Failed to generate shape for {}'.format(element))
        obj = bpy.data.objects.new(self.get_name(element), mesh)
        if mesh:
            self.material_creator.create(element, obj, mesh)
        self.add_element_attributes(element, obj)
        self.add_element_classifications(element, obj)
        self.add_element_document_relations(element, obj)
        self.add_type_product_psets(element, obj)
        self.add_product_representation_contexts(element, obj)
        self.type_collection.objects.link(obj)
        self.type_products[element.GlobalId] = obj

    def get_type_product_body_representation_map(self, element):
        if not element.RepresentationMaps:
            return
        for representation_map in element.RepresentationMaps:
            context = representation_map.MappedRepresentation.ContextOfItems
            if context.ContextType == 'Model' \
                    and context.ContextIdentifier == 'Body' \
                    and context.TargetView == 'MODEL_VIEW':
                return representation_map

    def create_products_legacy(self):
        elements = self.file.by_type('IfcElement') + self.file.by_type('IfcSpace')
        for element in elements:
            self.create_product_legacy(element)

    def create_native_products(self):
        if not self.native_elements:
            return
        # TODO: the iterator is kind of useless here, rewrite this
        iterator = ifcopenshell.geom.iterator(
            self.settings_native, self.file, multiprocessing.cpu_count(),
            include=[self.file.by_guid(guid) for guid in self.native_elements.keys()] or None)
        valid_file = iterator.initialize()
        total = 0
        checkpoint = time.time()
        if not valid_file:
            return False
        while True:
            total += 1
            if total % 250 == 0:
                print('{} elements processed in {:.2f}s ...'.format(total, time.time() - checkpoint))
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                self.create_product(self.file.by_id(shape.guid), shape)
            if not iterator.next():
                break
        print('Done creating geometry')

    def create_products(self):
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(
                self.settings, self.file, multiprocessing.cpu_count(),
                include=self.include_elements or None,
                exclude=self.exclude_elements or None
                )
        else:
            iterator = ifcopenshell.geom.iterator(
                self.settings, self.file,
                include=self.include_elements or None,
                exclude=self.exclude_elements or None)
        valid_file = iterator.initialize()
        if not valid_file:
            return False
        checkpoint = time.time()
        total = 0
        while True:
            total += 1
            if total % 250 == 0:
                print('{} elements processed in {:.2f}s ...'.format(total, time.time() - checkpoint))
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                self.create_product(self.file.by_id(shape.guid), shape)
            if not iterator.next():
                break
        print('Done creating geometry')

    def create_product(self, element, shape=None):
        if element is None:
            return

        if not self.ifc_import_settings.should_import_opening_elements \
                and element.is_a('IfcOpeningElement'):
            return

        if not self.ifc_import_settings.should_import_spaces \
                and element.is_a('IfcSpace'):
            return

        if element.GlobalId in self.existing_elements:
            return self.existing_elements[element.GlobalId]

        self.ifc_import_settings.logger.info('Creating object {}'.format(element))

        is_fresh_mesh = False
        if shape:
            # TODO: make names more meaningful
            mesh_name = f'mesh-{shape.geometry.id}'
            mesh = self.meshes.get(mesh_name)
            if mesh is None:
                if element.GlobalId in self.native_elements:
                    mesh = self.create_native_mesh(element, shape)
                if mesh is None:
                    mesh = self.create_mesh(element, shape)
                self.meshes[mesh_name] = mesh
                is_fresh_mesh = True
        else:
            mesh = None

        obj = bpy.data.objects.new(self.get_name(element), mesh)

        if shape:
            m = shape.transformation.matrix.data
            mat = mathutils.Matrix(([m[0], m[1], m[2], 0],
                                    [m[3], m[4], m[5], 0],
                                    [m[6], m[7], m[8], 0],
                                    [m[9], m[10], m[11], 1]))
            mat.transpose()
            obj.matrix_world = mat
            if is_fresh_mesh:
                self.material_creator.create(element, obj, mesh)
        elif hasattr(element, 'ObjectPlacement'):
            obj.matrix_world = self.get_element_matrix(element)

        self.add_element_representation_items(element, obj)
        self.add_element_attributes(element, obj)
        self.add_element_classifications(element, obj)
        self.add_element_document_relations(element, obj)
        self.add_defines_by_type_relation(element, obj)
        self.add_opening_relation(element, obj)
        self.add_product_definitions(element, obj)
        self.add_product_representation_contexts(element, obj)
        self.added_data[element.GlobalId] = obj
        return obj

    def add_element_representation_items(self, element, obj):
        if not obj.data or 'ios_items' not in obj.data:
            return
        cumulative_vertex_index = 0
        for i, item in enumerate(obj.data['ios_items']):
            vg = obj.vertex_groups.new(name=f'Item/{i}/' + item['name'])
            vg.add([v.index for v in obj.data.vertices[cumulative_vertex_index:cumulative_vertex_index+item['total_vertices']]], 1, 'ADD')
            for subitem in item['subitems']:
                vg = obj.vertex_groups.new(name=f'Subitem/{i}/' + subitem['name'])
                vg.add([v + cumulative_vertex_index for v in subitem['vertices']],
                    1, 'ADD')
            cumulative_vertex_index += item['total_vertices']

    def create_native_mesh(self, element, shape):
        data = self.native_elements[element.GlobalId]
        materials = []
        items = []
        for representation in self.get_body_representations(element.Representation.Representations):
            for item in representation['raw'].Items:
                material_name = self.get_representation_item_material_name(item)
                if not material_name:
                    # Magic string NULLMAT represents no material, unless this has a better approach
                    material_name = 'NULLMAT'
                materials.append(material_name)
                if item.id() in data:
                    item = data[item.id()]
                if item.is_a() == 'IfcExtrudedAreaSolid':
                    native = self.create_native_extruded_area_solid(item, element)
                    if native:
                        bmesh.ops.transform(
                            native['blender'], matrix=representation['matrix'], verts=native['blender'].verts)
                        items.append(native)
                    else:
                        items.append(None)
                elif item.is_a('IfcSweptDiskSolid'):
                    items.append({
                        'blender': self.transform_curve(
                            self.create_native_swept_disk_solid(item, element), representation['matrix']),
                        'raw': item,
                        'subitems': []
                    })
                elif item.is_a('IfcFacetedBrep'):
                    bm = self.create_native_faceted_brep(item, element)
                    if bm:
                        bmesh.ops.transform(bm, matrix=representation['matrix'], verts=bm.verts)
                        items.append({'blender': bm, 'raw': item, 'subitems': []})
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
            if isinstance(item['blender'], bpy.types.Curve):
                if bevel_depth is None:
                    bevel_depth = item['blender'].bevel_depth
                    merged_curve = item['blender']
                elif item['blender'].bevel_depth == bevel_depth:
                    self.merge_curves(merged_curve, item['blender'])
                else:
                    # TODO: handle if there are multiple different radiuses
                    # We don't have a choice but to meshify it
                    pass
            elif isinstance(item['blender'], bmesh.types.BMesh):
                representation_items.append({
                    'name': item['raw'].is_a(),
                    'total_vertices': len(item['blender'].verts),
                    'subitems': item['subitems']
                })
                total_polygons = len(item['blender'].faces)
                if merged_bm is None:
                    merged_bm = item['blender']
                else:
                    self.merge_bmeshes(merged_bm, item['blender'])
                # Magic string NULLMAT represents no material, unless this has a better approach
                if materials[i] == 'NULLMAT':
                    # Magic number -1 represents no material, until this has a better approach
                    material_ids += [-1] * total_polygons
                else:
                    material_ids += [i] * total_polygons
        if merged_curve:
            return merged_curve
        # TODO: handle both curve and bmeshes combined
        mesh = bpy.data.meshes.new('Native Mesh')
        merged_bm.to_mesh(mesh)
        merged_bm.free()
        mesh['ios_materials'] = materials
        mesh['ios_material_ids'] = material_ids
        mesh['ios_items'] = representation_items
        mesh.BIMMeshProperties.is_native = True
        for representation_item in representation_items:
            new = mesh.BIMMeshProperties.representation_items.add()
            new.name = representation_item['name']
        return mesh

    def get_representation_item_material_name(self, item):
        if not item.StyledByItem:
            return
        styled_item = item.StyledByItem[0]
        return self.material_creator.get_material_name(styled_item)

    def transform_curve(self, curve, matrix):
        for spline in curve.splines:
            for point in spline.points:
                point.co = matrix @ point.co
        return curve

    def merge_curves(self, a, b):
        for spline in b.splines:
            new_spline = a.splines.new('POLY')
            is_first = True
            for point in spline.points:
                if is_first:
                    is_first = False
                else:
                    new_spline.points.add(1)
                new_spline.points[-1].co = point.co
        return a

    def merge_bmeshes(self, a, b):
        mesh = bpy.data.meshes.new('x')
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
        #print(shape.materials)
        subitems = []
        if item.SweptArea.is_a() == 'IfcArbitraryClosedProfileDef':
            shape = ifcopenshell.geom.create_shape(self.settings_native, item.SweptArea.OuterCurve)
            bm = self.bmesh_from_pydata(*self.shape_to_mesh(shape))
            bm.faces.new([v for v in bm.verts])
            bm.faces.ensure_lookup_table()
            subitems.append({
                'name': item.SweptArea.is_a(),
                'vertices': range(0, len(bm.verts))
            })
        elif item.SweptArea.is_a() == 'IfcRectangleProfileDef':
            bm = self.bmesh_from_rectangle(item.SweptArea.XDim, item.SweptArea.YDim)
            if item.SweptArea.Position:
                bmesh.ops.transform(bm, matrix=self.get_axis2placement(item.SweptArea.Position), verts=bm.verts)
            bmesh.ops.transform(bm, matrix=mathutils.Matrix() * self.unit_scale, verts=bm.verts)
            subitems.append({
                'name': item.SweptArea.is_a(),
                'vertices': [0, 1, 2, 3]
            })
        else:
            # TODO: what if we can't handle it?
            return
        results = bmesh.ops.extrude_face_region(bm, geom=[bm.faces[0]])
        bm.faces.ensure_lookup_table()
        offset = self.unit_scale * item.Depth * mathutils.Vector(item.ExtrudedDirection.DirectionRatios)
        subitems.append({
            'name': 'ExtrudedDirection',
            'vertices': [0, len(subitems[-1]['vertices'])]
        })
        for geom in results['geom']:
            if isinstance(geom, bmesh.types.BMVert):
                geom.co += offset
        if item.Position:
            bmesh.ops.transform(
                bm, matrix=self.scale_matrix(self.get_axis2placement(item.Position)), verts=bm.verts)
        return {
            'blender': bm,
            'raw': item,
            'subitems': subitems
        }
        #mesh['ios_material_ids'] = [0] * len(bm.faces)

    def bmesh_from_rectangle(self, x, y):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=x/2)
        bm.verts.ensure_lookup_table()
        diff_vector = mathutils.Vector((0., (x - y) / 2., 0.))
        bm.verts[0].co += diff_vector
        bm.verts[1].co += diff_vector
        bm.verts[2].co -= diff_vector
        bm.verts[3].co -= diff_vector
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        return bm

    def merge_aggregates(self):
        self.merge_objects_inside_aggregates()
        self.convert_aggregate_instances_to_object()

    def merge_objects_inside_aggregates(self):
        global_ids_to_delete = []
        for collection in self.aggregate_collections.values():
            obs = []
            for i, ob in enumerate(collection.objects):
                if ob.type == 'MESH':
                    if i > 0:
                        global_ids_to_delete.append(ob.BIMObjectProperties.attributes.get('GlobalId').string_value)
                    obs.append(ob)
            ctx = {}
            ctx['active_object'] = obs[0]
            ctx['selected_editable_objects'] = obs
            if obs[0].data.users > 1:
                obs[0].data = obs[0].data.copy()
            bpy.ops.object.join(ctx)

        for global_id in global_ids_to_delete:
            del self.added_data[global_id]

    def convert_aggregate_instances_to_object(self):
        for obj in self.aggregates.values():
            aggregate = obj.instance_collection.objects[0]
            obj.users_collection[0].objects.link(aggregate)
            aggregate.name = obj.name
            bpy.data.collections.remove(obj.instance_collection)
            bpy.data.objects.remove(obj)

    def merge_by_class(self):
        merge_set = {}
        for obj in self.added_data.values():
            if '/' not in obj.name \
                    or 'IfcRelAggregates' in obj.users_collection[0].name:
                continue
            merge_set.setdefault(obj.name.split('/')[0], []).append(obj)
        self.merge_objects(merge_set)

    def merge_by_material(self):
        merge_set = {}
        for obj in self.added_data.values():
            if '/' not in obj.name \
                    or 'IfcRelAggregates' in obj.users_collection[0].name:
                continue
            if not obj.material_slots:
                merge_set.setdefault('no-material', []).append(obj)
            else:
                merge_set.setdefault(obj.material_slots[0].name, []).append(obj)
        self.merge_objects(merge_set)

    def merge_objects(self, merge_set):
        for ifc_class, objs in merge_set.items():
            context_override = {}
            context_override['object'] = context_override['active_object'] = objs[0]
            context_override['selected_objects'] = context_override['selected_editable_objects'] = objs
            bpy.ops.object.join(context_override)

    def merge_materials_by_colour(self):
        cleaned_materials = {}
        for m in bpy.data.materials:
            key = '-'.join([str(x) for x in m.diffuse_color])
            cleaned_materials[key] = { 'diffuse_color': m.diffuse_color }

        for cleaned_material in cleaned_materials.values():
            cleaned_material['material'] = bpy.data.materials.new('Merged Material')
            cleaned_material['material'].diffuse_color = cleaned_material['diffuse_color']

        for obj in self.added_data.values():
            if not hasattr(obj, 'material_slots') \
                    or not obj.material_slots:
                continue
            for slot in obj.material_slots:
                m = slot.material
                key = '-'.join([str(x) for x in m.diffuse_color])
                slot.material = cleaned_materials[key]['material']

        for material in self.material_creator.materials.values():
            bpy.data.materials.remove(material)

    def add_project_to_scene(self):
        bpy.context.scene.collection.children.link(self.project['blender'])
        for collection in bpy.context.view_layer.layer_collection.children[self.project['blender'].name].children[self.aggregate_collection.name].children:
            collection.hide_viewport = True
        bpy.context.view_layer.layer_collection.children[self.project['blender'].name].children[self.opening_collection.name].hide_viewport = True
        bpy.context.view_layer.layer_collection.children[self.project['blender'].name].children[self.type_collection.name].hide_viewport = True

    def clean_mesh(self):
        obj = None
        last_obj = None
        for obj in self.added_data.values():
            if obj.type == 'MESH':
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

    def add_product_representation_contexts(self, element, obj):
        subcontexts = []
        if element.is_a('IfcProduct'):
            if not element.Representation:
                return
            for r in element.Representation.Representations:
                if r.ContextOfItems.is_a('IfcGeometricRepresentationSubContext'):
                    subcontexts.append('{}/{}/{}'.format(
                        r.ContextOfItems.ContextType or '',
                        r.ContextOfItems.ContextIdentifier or '',
                        r.ContextOfItems.TargetView or ''))
                else:
                    subcontexts.append('{}/{}/{}'.format(
                        r.ContextOfItems.ContextType or '',
                        r.ContextOfItems.ContextIdentifier or '',
                        ''))
        elif element.is_a('IfcTypeProduct'):
            if not element.RepresentationMaps:
                return
            for r in element.RepresentationMaps:
                subcontexts.append('{}/{}/{}'.format(
                    r.MappedRepresentation.ContextOfItems.ContextType or '',
                    r.MappedRepresentation.ContextOfItems.ContextIdentifier or '',
                    r.MappedRepresentation.ContextOfItems.TargetView or ''))
        subcontexts = set(subcontexts)
        for subcontext in subcontexts:
            representation_context = obj.BIMObjectProperties.representation_contexts.add()
            representation_context.context, representation_context.name, representation_context.target_view = subcontext.split('/')

    def add_product_definitions(self, element, obj):
        if not hasattr(element, 'IsDefinedBy') or not element.IsDefinedBy:
            return
        for definition in element.IsDefinedBy:
            if not definition.is_a('IfcRelDefinesByProperties'):
                continue
            if definition.RelatingPropertyDefinition.is_a('IfcPropertySet'):
                self.add_pset(definition.RelatingPropertyDefinition, obj)
            elif definition.RelatingPropertyDefinition.is_a('IfcElementQuantity'):
                self.add_qto(definition.RelatingPropertyDefinition, obj)

    def add_type_product_psets(self, element, obj):
        if not hasattr(element, 'HasPropertySets') or not element.HasPropertySets:
            return
        for definition in element.HasPropertySets:
            if definition.is_a('IfcPropertySet'):
                self.add_pset(definition, obj)

    def add_pset(self, pset, obj):
        new_pset = obj.BIMObjectProperties.psets.add()
        new_pset.name = pset.Name
        if new_pset.name in schema.ifc.psets:
            for prop_name in schema.ifc.psets[new_pset.name]['HasPropertyTemplates'].keys():
                prop = new_pset.properties.add()
                prop.name = prop_name
        # Invalid IFC, but some vendors like Solidworks do this so we accomodate it
        if not pset.HasProperties:
            return
        for prop in pset.HasProperties:
            if prop.is_a('IfcPropertySingleValue') and prop.NominalValue:
                index = new_pset.properties.find(prop.Name)
                if index >= 0:
                    new_pset.properties[index].string_value = str(prop.NominalValue.wrappedValue)
                else:
                    new_prop = new_pset.properties.add()
                    new_prop.name = prop.Name
                    new_prop.string_value = str(prop.NominalValue.wrappedValue)

    def add_qto(self, qto, obj):
        new_qto = obj.BIMObjectProperties.qtos.add()
        new_qto.name = str(qto.Name)
        if new_qto.name in schema.ifc.qtos:
            for prop_name in schema.ifc.qtos[new_qto.name]['HasPropertyTemplates'].keys():
                prop = new_qto.properties.add()
                prop.name = prop_name
        for prop in qto.Quantities:
            if prop.is_a('IfcPhysicalSimpleQuantity'):
                value = getattr(prop, '{}Value'.format(prop.is_a()[len('IfcQuantity'):]))
                if not value:
                    continue
                index = new_qto.properties.find(prop.Name)
                if index >= 0:
                    new_qto.properties[index].string_value = str(value)
                else:
                    new_prop = new_qto.properties.add()
                    new_prop.name = prop.Name
                    new_prop.string_value = str(value)

    def add_defines_by_type_relation(self, element, obj):
        related_type = self.get_type(element)
        if related_type:
            obj.BIMObjectProperties.relating_type = self.type_products[related_type.GlobalId]

    # TODO: migrate into util function
    def get_type(self, element):
        if hasattr(element, 'IsTypedBy') and element.IsTypedBy:
            return element.IsTypedBy[0].RelatingType
        elif hasattr(element, 'IsDefinedBy') and element.IsDefinedBy: # IFC2X3
            for relationship in element.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByType'):
                    return relationship.RelatingType

    def add_opening_relation(self, element, obj):
        if not element.is_a('IfcOpeningElement'):
            return
        self.openings[element.GlobalId] = obj

    def load_existing_rooted_elements(self):
        for obj in bpy.data.objects:
            if hasattr(obj, 'BIMObjectProperties') and obj.BIMObjectProperties.attributes.get('GlobalId'):
                self.existing_elements[obj.BIMObjectProperties.attributes.get('GlobalId').string_value] = obj

    def load_diff(self):
        if not self.ifc_import_settings.diff_file:
            return
        with open(self.ifc_import_settings.diff_file, 'r') as file:
            self.diff = json.load(file)

    def cache_file(self):
        destination = os.path.join(bpy.context.scene.BIMProperties.data_dir, 'cache', 'ifc')
        copythread = FileCopy(self.ifc_import_settings.input_file, destination)
        bpy.context.scene.BIMProperties.ifc_cache = os.path.join(destination,
            os.path.basename(self.ifc_import_settings.input_file))
        copythread.start()
        copythread.join()

    def load_file(self):
        self.ifc_import_settings.logger.info('loading file {}'.format(self.ifc_import_settings.input_file))
        extension = self.ifc_import_settings.input_file.split('.')[-1]
        if extension.lower() == 'ifczip':
            with tempfile.TemporaryDirectory() as unzipped_path:
                with zipfile.ZipFile(self.ifc_import_settings.input_file, 'r') as zip_ref:
                    zip_ref.extractall(unzipped_path)
                for filename in Path(unzipped_path).glob('**/*.ifc'):
                    self.file = ifcopenshell.open(filename)
                    break
        elif extension.lower() == 'ifcxml':
            self.file = ifcopenshell.file(
                ifcopenshell.ifcopenshell_wrapper.parse_ifcxml(self.ifc_import_settings.input_file))
        elif extension.lower() == 'ifc':
            self.file = ifcopenshell.open(self.ifc_import_settings.input_file)
        ifc.IfcStore.file = self.file

    def set_ifc_file(self):
        bpy.context.scene.BIMProperties.ifc_file = self.ifc_import_settings.input_file
        ifc.IfcStore.path = 'self.ifc_import_settings.input_file'

    def calculate_unit_scale(self):
        units = self.file.by_type('IfcUnitAssignment')[0]
        for unit in units.Units:
            if not hasattr(unit, 'UnitType') \
                    or unit.UnitType != 'LENGTHUNIT':
                continue
            while unit.is_a('IfcConversionBasedUnit'):
                self.unit_scale *= unit.ConversionFactor.ValueComponent.wrappedValue
                unit = unit.ConversionFactor.UnitComponent
            if unit.is_a('IfcSIUnit'):
                self.unit_scale *= helper.SIUnitHelper.get_prefix_multiplier(unit.Prefix)

    def set_units(self):
        units = self.file.by_type('IfcUnitAssignment')[0]
        for unit in units.Units:
            if unit.is_a('IfcNamedUnit') and unit.UnitType == 'LENGTHUNIT':
                if unit.is_a('IfcSIUnit'):
                    bpy.context.scene.unit_settings.system = 'METRIC'
                    if unit.Name == 'METRE':
                        if not unit.Prefix:
                            bpy.context.scene.unit_settings.length_unit = 'METERS'
                        else:
                            bpy.context.scene.unit_settings.length_unit = f'{unit.Prefix}METERS'
                else:
                    bpy.context.scene.unit_settings.system = 'IMPERIAL'
                    if unit.Name == 'inch':
                        bpy.context.scene.unit_settings.length_unit = 'INCHES'
                    elif unit.Name == 'foot':
                        bpy.context.scene.unit_settings.length_unit = 'FEET'

    def create_geometric_representation_contexts(self):
        bpy.context.scene.BIMProperties.has_model_context = False
        for context in self.file.by_type('IfcGeometricRepresentationContext'):
            if context.is_a('IfcGeometricRepresentationSubContext'):
                if not context.ContextIdentifier:
                    # Revit creates invalid contexts, so we just ignore them
                    continue
                if context.ContextType == 'Model':
                    subcontexts = bpy.context.scene.BIMProperties.model_subcontexts
                elif context.ContextType == 'Plan':
                    subcontexts = bpy.context.scene.BIMProperties.plan_subcontexts
                if subcontexts.get(context.ContextIdentifier):
                    continue
                subcontext = subcontexts.add()
                subcontext.name = context.ContextIdentifier
                subcontext.target_view = context.TargetView
            elif context.ContextType == 'Model':
                bpy.context.scene.BIMProperties.has_model_context = True
            elif context.ContextType == 'Plan':
                bpy.context.scene.BIMProperties.has_plan_context = True

    def create_project(self):
        self.project = { 'ifc': self.file.by_type('IfcProject')[0] }
        if self.project['ifc'].GlobalId in self.existing_elements:
            self.project['blender'] = self.existing_elements[self.project['ifc'].GlobalId].users_collection[0]
            return
        self.project['blender'] = bpy.data.collections.new('IfcProject/{}'.format(self.project['ifc'].Name))
        obj = self.create_product(self.project['ifc'])
        if obj:
                self.project['blender'].objects.link(obj)
                del self.added_data[self.project['ifc'].GlobalId]

    def create_classifications(self):
        for element in self.file.by_type('IfcClassification'):
            classification = bpy.context.scene.BIMProperties.classifications.add()
            data_map = {
                'name': 'Name', 'source': 'Source',
                'edition': 'Edition', 'edition_date': 'EditionDate',
                'description': 'Description', 'location': 'Location',
                'reference_tokens': 'ReferenceTokens'
            }
            for key, value in data_map.items():
                if hasattr(element, value) and getattr(element, value):
                    setattr(classification, key, str(getattr(element, value)))
            classification_file = ifcopenshell.file()

            # IFC2X3 has no references, so let's manually add them
            if self.file.wrapped_data.schema == 'IFC2X3':
                classification_element = classification_file.createIfcClassification(
                    element.Source, element.Edition, element.EditionDate, element.Name)
                for reference in self.file.by_type('IfcClassificationReference'):
                    classification_file.createIfcClassificationReference(
                        reference.Location, reference.ItemReference, reference.Name, classification_element)
            else:
                references = [element]
                while references:
                    entities_to_add = references
                    references = self.get_classification_references(references)
                for entity in entities_to_add:
                    classification_file.add(entity)

            classification_filename = '{}-{}'.format(
                Path(os.path.basename(self.ifc_import_settings.input_file)).stem, element.Name)
            classification_file.write(os.path.join(
                bpy.context.scene.BIMProperties.schema_dir, 'classifications',
                '{}.ifc'.format(classification_filename)))
            classification.filename = classification_filename
            self.classifications[classification.filename] = classification

    def get_classification_references(self, references):
        results = []
        for reference in references:
            results.extend(self.file.get_inverse(reference))
        return results

    def create_constraints(self):
        for element in self.file.by_type('IfcObjective'):
            constraint = bpy.context.scene.BIMProperties.constraints.add()
            data_map = {
                'name': 'Name',
                'description': 'Description',
                'constraint_grade': 'ConstraintGrade',
                'constraint_source': 'ConstraintSource',
                'user_defined_grade': 'UserDefinedGrade',
                'objective_qualifier': 'ObjectiveQualifier',
                'user_defined_qualifier': 'UserDefinedQualifier',
            }
            for key, value in data_map.items():
                if hasattr(element, value) and getattr(element, value):
                    setattr(constraint, key, getattr(element, value))

    def create_document_information(self):
        for element in self.file.by_type('IfcDocumentInformation'):
            info = bpy.context.scene.BIMProperties.document_information.add()
            data_map = {
                'name': 'Identification',
                'human_name': 'Name',
                'description': 'Description',
                'location': 'Location',
                'purpose': 'Purpose',
                'intended_use': 'IntendedUse',
                'scope': 'Scope',
                'revision': 'Revision',
                'creation_time': 'CreationTime',
                'last_revision_time': 'LastRevisionTime',
                'electronic_format': 'ElectronicFormat',
                'valid_from': 'ValidFrom',
                'valid_until': 'ValidUntil',
                'confidentiality': 'Confidentiality',
                'status': 'Status'
            }
            for key, value in data_map.items():
                if hasattr(element, value) and getattr(element, value):
                    setattr(info, key, getattr(element, value))


    def create_document_references(self):
        for element in self.file.by_type('IfcDocumentReference'):
            reference = bpy.context.scene.BIMProperties.document_references.add()
            data_map = {
                'name': 'Identification',
                'human_name': 'Name',
                'location': 'Location',
                'description': 'Description'
            }
            for key, value in data_map.items():
                if hasattr(element, value) and getattr(element, value):
                    setattr(reference, key, getattr(element, value))
            if element.ReferencedDocument:
                reference.referenced_document = element.ReferencedDocument.Identification

    def create_spatial_hierarchy(self):
        if self.project['ifc'].IsDecomposedBy:
            for rel_aggregate in self.project['ifc'].IsDecomposedBy:
                self.add_related_objects(self.project['blender'], rel_aggregate.RelatedObjects)

    def add_related_objects(self, parent, related_objects):
        for element in related_objects:
            if element.is_a('IfcSpace'):
                continue
            global_id = element.GlobalId
            if global_id in self.existing_elements:
                collection = self.existing_elements[global_id].users_collection[0]
                self.spatial_structure_elements[global_id] = { 'blender': collection }
            else:
                collection = bpy.data.collections.new(self.get_name(element))
                self.spatial_structure_elements[global_id] = { 'blender': collection }
                parent.children.link(collection)
                obj = self.create_product(element)
                if obj:
                    collection.objects.link(obj)
                    del self.added_data[element.GlobalId]
            if element.IsDecomposedBy:
                for rel_aggregate in element.IsDecomposedBy:
                    self.add_related_objects(collection, rel_aggregate.RelatedObjects)

    def create_aggregates(self):
        rel_aggregates = [a for a in self.file.by_type('IfcRelAggregates')
                if a.RelatingObject.is_a('IfcElement')]
        for collection in self.project['blender'].children:
            if collection.name == 'Aggregates':
                self.aggregate_collection = collection
                break
        if not self.aggregate_collection:
            self.aggregate_collection = bpy.data.collections.new('Aggregates')
            self.project['blender'].children.link(self.aggregate_collection)

        for rel_aggregate in rel_aggregates:
            self.create_aggregate(rel_aggregate)

    def create_aggregate(self, rel_aggregate):
        collection = bpy.data.collections.new(f'IfcRelAggregates/{rel_aggregate.id()}')
        self.aggregate_collection.children.link(collection)
        element = rel_aggregate.RelatingObject

        obj = bpy.data.objects.new('{}/{}'.format(element.is_a(), element.Name), None)
        obj.instance_type = 'COLLECTION'
        obj.instance_collection = collection
        self.place_object_in_spatial_tree(element, obj)
        self.add_element_attributes(element, obj)
        self.add_element_classifications(element, obj)
        self.add_element_document_relations(element, obj)
        self.add_defines_by_type_relation(element, obj)
        self.add_product_definitions(element, obj)
        self.aggregates[element.GlobalId] = obj
        self.aggregate_collections[rel_aggregate.id()] = collection

    def create_openings_collection(self):
        self.opening_collection = bpy.data.collections.new('IfcOpeningElements')
        self.project['blender'].children.link(self.opening_collection)

    def get_name(self, element):
        return '{}/{}'.format(element.is_a(), element.Name)

    def purge_diff(self):
        if not self.diff:
            return
        objects_to_purge = []
        for obj in bpy.data.objects:
            if 'GlobalId' not in obj.BIMObjectProperties.attributes:
                continue
            global_id = obj.BIMObjectProperties.attributes['GlobalId'].string_value
            if global_id in self.diff['deleted'] \
                or global_id in self.diff['changed'].keys():
                objects_to_purge.append(obj)
        bpy.ops.object.delete({'selected_objects': objects_to_purge})

    def create_product_legacy(self, element):
        if self.diff \
                and element.GlobalId not in self.diff['added'] \
                and element.GlobalId not in self.diff['changed'].keys():
            return

        self.ifc_import_settings.logger.info('Creating object {}'.format(element))
        self.time = time.time()
        if element.is_a('IfcOpeningElement'):
            return

        try:
            representation_id = self.get_representation_id(element)

            mesh_name = 'mesh-{}'.format(representation_id)
            mesh = self.meshes.get(mesh_name)
            if mesh is None \
                or representation_id is None:
                shape = ifcopenshell.geom.create_shape(self.settings, element)
                self.ifc_import_settings.logger.info('Shape was generated in {:.2f}'.format(time.time() - self.time))
                self.time = time.time()

                mesh = self.create_mesh(element, shape)
                self.meshes[mesh_name] = mesh
                self.mesh_shapes[mesh_name] = shape
            else:
                self.ifc_import_settings.logger.info('Mesh reused.')
        except:
            self.ifc_import_settings.logger.error('Failed to generate shape for {}'.format(element))
            return

        obj = bpy.data.objects.new(self.get_name(element), mesh)
        self.material_creator.create(element, obj, mesh)
        obj.matrix_world = self.get_element_matrix(element, mesh_name)
        self.add_element_attributes(element, obj)
        self.add_element_classifications(element, obj)
        self.add_element_document_relations(element, obj)
        self.add_defines_by_type_relation(element, obj)
        self.add_product_definitions(element, obj)
        self.added_data[element.GlobalId] = obj

    def add_element_document_relations(self, element, obj):
        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesDocument'):
                reference = obj.BIMObjectProperties.document_references.add()
                data_map = {
                    'name': 'Identification',
                    'human_name': 'Name',
                    'description': 'Description',
                    'location': 'Location'
                }
                attributes = {}
                for key, value in data_map.items():
                    if hasattr(association.RelatingDocument, value) \
                            and getattr(association.RelatingDocument, value):
                        setattr(reference, key, getattr(association.RelatingDocument, value))

    def relate_openings(self):
        for global_id, opening in self.openings.items():
            building_element_global_id = self.file.by_guid(global_id).VoidsElements[0].RelatingBuildingElement.GlobalId
            if building_element_global_id not in self.added_data:
                continue
            building_element = self.added_data[building_element_global_id]
            modifier = building_element.modifiers.new('IfcOpeningElement', 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.object = opening

    def place_objects_in_spatial_tree(self):
        for global_id, obj in self.added_data.items():
            self.place_object_in_spatial_tree(self.file.by_guid(global_id), obj)

    def place_object_in_spatial_tree(self, element, obj):
        if hasattr(element, 'ContainedInStructure') \
                and element.ContainedInStructure \
                and element.ContainedInStructure[0].RelatingStructure:
            container = element.ContainedInStructure[0].RelatingStructure
            if container.is_a('IfcSpace'):
                if self.ifc_import_settings.should_import_spaces and container.GlobalId in self.added_data:
                    obj.BIMObjectProperties.relating_structure = self.added_data[container.GlobalId]
                return self.place_object_in_spatial_tree(container, obj)
            self.spatial_structure_elements[container.GlobalId]['blender'].objects.link(obj)
        elif hasattr(element, 'Decomposes') \
                and element.Decomposes:
            collection = None
            if element.Decomposes[0].RelatingObject.is_a('IfcProject'):
                collection = self.project['blender']
            elif element.Decomposes[0].RelatingObject.is_a('IfcSpatialStructureElement'):
                global_id = element.Decomposes[0].RelatingObject.GlobalId
                if global_id in self.spatial_structure_elements:
                    collection = self.spatial_structure_elements[global_id]['blender']
            elif self.ifc_import_settings.should_import_aggregates:
                collection = self.aggregate_collections[element.Decomposes[0].id()]
            else:
                return self.place_object_in_spatial_tree(element.Decomposes[0].RelatingObject, obj)
            if collection:
                collection.objects.link(obj)
            else:
                self.ifc_import_settings.logger.error('An element could not be placed in the spatial tree {}'.format(element))
        elif hasattr(element, 'HasFillings') \
                and element.HasFillings:
            self.opening_collection.objects.link(obj)
        else:
            self.ifc_import_settings.logger.warning('Warning: this object is outside the spatial hierarchy')
            bpy.context.scene.collection.objects.link(obj)

    def add_element_attributes(self, element, obj):
        attributes = element.get_info()
        if element.is_a() in schema.ifc.elements:
            applicable_attributes = [a['name'] for a in schema.ifc.elements[element.is_a()]['attributes']]
            for key, value in attributes.items():
                if key not in applicable_attributes \
                        or value is None:
                    continue
                attribute = obj.BIMObjectProperties.attributes.add()
                attribute.name = key
                attribute.data_type = 'string'
                attribute.string_value = str(self.cast_edge_case_attribute(element.is_a(), key, value))

    def cast_edge_case_attribute(self, ifc_class, key, value):
        if key == 'RefLatitude' or key == 'RefLongitude':
            return ifcopenshell.util.geolocation.dms2dd(*value)
        return value

    def add_element_classifications(self, element, obj):
        if not element.HasAssociations:
            return
        for association in element.HasAssociations:
            if not association.is_a('IfcRelAssociatesClassification'):
                continue
            data = association.RelatingClassification
            reference = obj.BIMObjectProperties.classifications.add()
            data_map = {
                'name': 'Identification', 'location': 'Location', 'human_name': 'Name',
                'description': 'Description', 'sort': 'Sort'
            }
            if self.file.schema == 'IFC2X3':
                data_map['name'] = 'ItemReference'
            for key, value in data_map.items():
                if hasattr(data, value) and getattr(data, value):
                    setattr(reference, key, getattr(data, value))
            if hasattr(data, 'ReferencedSource') and data.ReferencedSource:
                reference.referenced_source = self.get_referenced_source_name(data.ReferencedSource)

    def get_referenced_source_name(self, element):
        if not hasattr(element, 'ReferencedSource') or not element.ReferencedSource:
            if element.is_a('IfcClassification'):
                for filename, classification in self.classifications.items():
                    if classification.name == element.Name:
                        return filename
                return element.Name
            else:
                return element.Identification
        return self.get_referenced_source_name(element.ReferencedSource)

    def get_element_matrix(self, element, mesh_name=None):
        element_matrix = self.get_local_placement(element.ObjectPlacement)

        if mesh_name:
            # Blender supports reusing a mesh with a different transformation
            # applied at the object level. In contrast, IFC supports reusing a mesh
            # with a different transformation applied at the mesh level _as well as_
            # the object level. For this reason, if the end-goal is to re-use mesh
            # data, we must combine IFC's mesh-level transformation into Blender's
            # object level transformation.

            # The first step to do this is to _undo_ the mesh-level transformation
            # from whatever shared mesh we are using, as it is not necessarily the
            # same as the current mesh.
            shared_shape_transformation = self.get_representation_cartesian_transformation(
                self.file.by_id(self.mesh_shapes[mesh_name].product.id()))
            if shared_shape_transformation:
                shared_transform = self.get_cartesiantransformationoperator(shared_shape_transformation)
                shared_transform.invert()
                element_matrix = element_matrix @ shared_transform

            # The next step is to apply the current element's mesh level
            # transformation to our current element's object transformation
            transformation = self.get_representation_cartesian_transformation(element)
            if transformation:
                element_matrix = self.get_cartesiantransformationoperator(transformation) @ element_matrix

        element_matrix[0][3] *= self.unit_scale
        element_matrix[1][3] *= self.unit_scale
        element_matrix[2][3] *= self.unit_scale

        return element_matrix

    def get_body_representations(self, representations, matrix=None):
        if matrix is None:
            matrix = mathutils.Matrix()
        results = []
        for representation in representations:
            if representation.RepresentationIdentifier == 'Body' \
                    and representation.RepresentationType == 'MappedRepresentation':
                for item in representation.Items:
                    # TODO: Confirm if this transformation is right
                    transform = self.get_axis2placement(item.MappingSource.MappingOrigin)
                    if item.MappingTarget:
                        transform = transform @ self.get_cartesiantransformationoperator(item.MappingTarget)
                    results.extend(self.get_body_representations([item.MappingSource.MappedRepresentation],
                        transform @ matrix))
            elif representation.RepresentationIdentifier == 'Body':
                results.append({ 'raw': representation, 'matrix': self.scale_matrix(matrix) })
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
            if not representation.is_a('IfcShapeRepresentation'):
                continue
            if representation.RepresentationIdentifier == 'Body' \
                    and representation.RepresentationType != 'MappedRepresentation':
                return representation.id()
            elif representation.RepresentationIdentifier == 'Body':
                return representation.Items[0].MappingSource.MappedRepresentation.id()

    def get_representation_cartesian_transformation(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            if not representation.is_a('IfcShapeRepresentation'):
                continue
            if representation.RepresentationIdentifier == 'Body' \
                and representation.RepresentationType == 'MappedRepresentation':
                return representation.Items[0].MappingTarget

    def get_geometry_type(self, element):
        tree = []
        if hasattr(element, 'Representation'):
            tree = self.file.traverse(element.Representation)
        elif hasattr(element, 'RepresentationMaps'):
            for representation_map in element.RepresentationMaps:
                tree.extend(self.file.traverse(representation_map))
        representations = [e for e in tree if e.is_a('IfcRepresentation') \
            and e.RepresentationIdentifier == 'Body' \
            and e.RepresentationType != 'MappedRepresentation']
        for representation in representations:
            return representation.Items[0].is_a()

    def create_mesh(self, element, shape, is_curve=False):
        try:
            if hasattr(shape, 'geometry'):
                geometry = shape.geometry
            else:
                geometry = shape

            if is_curve:
                return self.create_curve(geometry)

            mesh = bpy.data.meshes.new(geometry.id)

            if geometry.faces:
                num_vertices = len(geometry.verts) // 3
                total_faces = len(geometry.faces)
                loop_start = range(0, total_faces, 3)
                num_loops = total_faces // 3
                loop_total = [3] * num_loops
                num_vertex_indices = len(geometry.faces)

                mesh.vertices.add(num_vertices)
                mesh.vertices.foreach_set('co', geometry.verts)
                mesh.loops.add(num_vertex_indices)
                mesh.loops.foreach_set('vertex_index', geometry.faces)
                mesh.polygons.add(num_loops)
                mesh.polygons.foreach_set('loop_start', loop_start)
                mesh.polygons.foreach_set('loop_total', loop_total)
                mesh.update()
            else:
                e = geometry.edges
                v = geometry.verts
                vertices = [[v[i], v[i + 1], v[i + 2]]
                         for i in range(0, len(v), 3)]
                edges = [[e[i], e[i + 1]]
                         for i in range(0, len(e), 2)]
                mesh.from_pydata(vertices, edges, [])

            ios_materials = []
            for mat in geometry.materials:
                if mat.original_name():
                    ios_materials.append(mat.original_name())
                else:
                    ios_materials.append(mat.name)
            mesh['ios_materials'] = ios_materials
            mesh['ios_material_ids'] = geometry.material_ids
            mesh.BIMMeshProperties.geometry_type = str(self.get_geometry_type(element))
            return mesh
        except:
            self.ifc_import_settings.logger.error('Could not create mesh for {}'.format(element))

    def create_curve(self, geometry):
        curve = bpy.data.curves.new(geometry.id, type='CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 2
        polyline = curve.splines.new('POLY')
        e = geometry.edges
        v = geometry.verts
        vertices = [[v[i], v[i + 1], v[i + 2], 1]
                 for i in range(0, len(v), 3)]
        edges = [[e[i], e[i + 1]]
                 for i in range(0, len(e), 2)]
        v2 = None
        for edge in edges:
            v1 = vertices[edge[0]]
            if v1 != v2:
                polyline = curve.splines.new('POLY')
                polyline.points[-1].co = v1
            v2 = vertices[edge[1]]
            polyline.points.add(1)
            polyline.points[-1].co = v2
        return curve

    def shape_to_mesh(self, shape):
        if hasattr(shape, 'geometry'):
            geometry = shape.geometry
        else:
            geometry = shape
        f = geometry.faces
        e = geometry.edges
        v = geometry.verts
        vertices = [[v[i], v[i + 1], v[i + 2]]
                 for i in range(0, len(v), 3)]
        faces = [[f[i], f[i + 1], f[i + 2]]
                 for i in range(0, len(f), 3)]
        if faces:
            edges = []
        else:
            edges = [[e[i], e[i + 1]]
                     for i in range(0, len(e), 2)]
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
        if plc.is_a('IfcAxis2Placement3D'):
            z = mathutils.Vector(plc.Axis.DirectionRatios if plc.Axis else (0,0,1))
            x = mathutils.Vector(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0))
            o = plc.Location.Coordinates
        else:
            z = mathutils.Vector((0,0,1))
            if plc.RefDirection:
                x = mathutils.Vector(list(plc.RefDirection.DirectionRatios) + [0])
            else:
                x = mathutils.Vector((1,0,0))
            o = list(plc.Location.Coordinates) + [0]
        return self.a2p(o,z,x)

    def get_cartesiantransformationoperator(self, plc):
        x = mathutils.Vector(plc.Axis1.DirectionRatios if plc.Axis1 else (1,0,0))
        z = x.cross(mathutils.Vector(plc.Axis2.DirectionRatios if plc.Axis2 else (0,1,0)))
        o = plc.LocalOrigin.Coordinates
        return self.a2p(o,z,x)

    def get_local_placement(self, plc):
        if plc is None:
            return mathutils.Matrix()
        if plc.PlacementRelTo is None:
            parent = mathutils.Matrix()
        else:
            parent = self.get_local_placement(plc.PlacementRelTo)
        return parent @ self.get_axis2placement(plc.RelativePlacement)

class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
        self.should_auto_set_workarounds = True
        self.should_ignore_site_coordinates = False
        self.should_ignore_building_coordinates = False
        self.should_reset_absolute_coordinates = False
        self.should_merge_materials_by_colour = False
        self.should_import_type_representations = False
        self.should_import_curves = False
        self.should_import_opening_elements = False
        self.should_import_spaces = False
        self.should_treat_styled_item_as_material = False
        self.should_use_cpu_multiprocessing = False
        self.should_import_with_profiling = False
        self.should_import_native = False
        self.should_use_legacy = False
        self.should_merge_aggregates = False
        self.should_merge_by_class = False
        self.should_merge_by_material = False
        self.should_import_aggregates = True
        self.should_clean_mesh = True
        self.diff_file = None

    @staticmethod
    def factory(context, input_file, logger):
        scene_bim = context.scene.BIMProperties
        settings = IfcImportSettings()
        settings.input_file = input_file
        settings.logger = logger
        settings.diff_file = scene_bim.diff_json_file
        settings.ifc_import_filter = scene_bim.ifc_import_filter
        settings.ifc_selector = scene_bim.ifc_selector
        settings.should_ignore_site_coordinates = scene_bim.import_should_ignore_site_coordinates
        settings.should_ignore_building_coordinates = scene_bim.import_should_ignore_building_coordinates
        settings.should_reset_absolute_coordinates = scene_bim.import_should_reset_absolute_coordinates
        settings.should_import_type_representations = scene_bim.import_should_import_type_representations
        settings.should_import_curves = scene_bim.import_should_import_curves
        settings.should_import_opening_elements = scene_bim.import_should_import_opening_elements
        settings.should_import_spaces = scene_bim.import_should_import_spaces
        settings.should_auto_set_workarounds = scene_bim.import_should_auto_set_workarounds
        settings.should_treat_styled_item_as_material = scene_bim.import_should_treat_styled_item_as_material
        settings.should_use_cpu_multiprocessing = scene_bim.import_should_use_cpu_multiprocessing
        settings.should_import_with_profiling = scene_bim.import_should_import_with_profiling
        settings.should_import_native = scene_bim.import_should_import_native
        settings.should_use_legacy = scene_bim.import_should_use_legacy
        settings.should_import_aggregates = scene_bim.import_should_import_aggregates
        settings.should_merge_aggregates = scene_bim.import_should_merge_aggregates
        settings.should_merge_by_class = scene_bim.import_should_merge_by_class
        settings.should_merge_by_material = scene_bim.import_should_merge_by_material
        settings.should_merge_materials_by_colour = scene_bim.import_should_merge_materials_by_colour
        settings.should_clean_mesh = scene_bim.import_should_clean_mesh
        return settings
