import ifcopenshell
import ifcopenshell.geom
import bpy
import os
import json
import time
import mathutils
import multiprocessing
from .helper import SIUnitHelper
from . import schema

class MaterialCreator():
    def __init__(self, ifc_import_settings):
        self.mesh = None
        self.materials = {}
        self.parsed_meshes = []
        self.ifc_import_settings = ifc_import_settings

    def create(self, element, object, mesh):
        self.object = object
        self.mesh = mesh
        if not element.Representation:
            return
        if self.ifc_import_settings.should_treat_styled_item_as_material \
            and self.mesh.name in self.parsed_meshes:
            return
        for item in element.Representation.Representations[0].Items:
            if item.is_a('IfcMappedItem'):
                item = item.MappingSource.MappedRepresentation.Items[0]
            if item.StyledByItem:
                styled_item = item.StyledByItem[0]
                if styled_item.Name:
                    material_name = styled_item.Name
                # This is for a bug in Revit where Revit exports this in IFC4
                elif styled_item.Styles[0] \
                        and styled_item.Styles[0].is_a('IfcPresentationStyleAssignment') \
                        and styled_item.Styles[0].Styles[0].Name:
                    material_name = styled_item.Styles[0].Styles[0].Name
                elif styled_item.Styles[0] \
                        and styled_item.Styles[0].is_a('IfcPresentationStyle') \
                        and styled_item.Styles[0].Name:
                    material_name = styled_item.Styles[0].Name
                else:
                    material_name = str(styled_item.id())
                if material_name not in self.materials:
                    self.materials[material_name] = bpy.data.materials.new(material_name)
                    self.parse_styled_item(item.StyledByItem[0], self.materials[material_name])
                if self.ifc_import_settings.should_treat_styled_item_as_material:
                    # Revit workaround: since Revit exports all material
                    # assignments as individual object styled items. Treating
                    # them as reusable materials makes things much more
                    # efficient in Blender.
                    if self.mesh.name not in self.parsed_meshes:
                        self.assign_material_to_mesh(self.materials[material_name])
                else:
                    # Proper behaviour
                    self.assign_material_to_mesh(self.materials[material_name], is_styled_item=True)
                return # styled items override material styles
        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):
                material_select = association.RelatingMaterial
                if material_select.is_a('IfcMaterialDefinition'):
                    self.create_definition(material_select)

    def create_definition(self, material):
        if material.is_a('IfcMaterial'):
            self.create_single(material)

    def create_single(self, material):
        if material.Name not in self.materials:
            self.create_new_single(material)
        return self.assign_material_to_mesh(self.materials[material.Name])

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

    def parse_styled_item(self, styled_item, material):
        for style in styled_item.Styles:
            # Note IfcPresentationStyleAssignment is deprecated as of IFC4,
            # but we still support it as it is widely used, gee thanks Revit :(
            if style.is_a('IfcPresentationStyleAssignment'):
                style = style.Styles[0]
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

    def assign_material_to_mesh(self, material, is_styled_item=False):
        self.parsed_meshes.append(self.mesh.name)
        self.mesh.materials.append(material)
        if is_styled_item:
            self.object.material_slots[0].link = 'OBJECT'
            self.object.material_slots[0].material = material

class IfcImporter():
    def __init__(self, ifc_import_settings):
        self.ifc_import_settings = ifc_import_settings
        self.diff = None
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        if self.ifc_import_settings.should_import_curves:
            self.settings.set(self.settings.INCLUDE_CURVES, True)
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set(self.settings_2d.INCLUDE_CURVES, True)
        self.project = None
        self.spatial_structure_elements = {}
        self.elements = {}
        self.type_products = {}
        self.meshes = {}
        self.mesh_shapes = {}
        self.time = 0
        self.unit_scale = 1
        self.added_objects = []

        self.material_creator = MaterialCreator(ifc_import_settings)

    def execute(self):
        self.load_diff()
        self.load_file()
        self.set_ifc_file()
        if self.ifc_import_settings.should_auto_set_workarounds:
            self.auto_set_workarounds()
        self.calculate_unit_scale()
        self.create_project()
        self.create_spatial_hierarchy()
        self.create_aggregates()
        if self.ifc_import_settings.should_import_opening_elements:
            self.create_openings_collection()
        self.purge_diff()
        self.patch_ifc()
        self.create_type_products()
        self.create_grids()
        # TODO: Deprecate after bug #682 is fixed and the new importer is stable
        if self.ifc_import_settings.should_use_legacy or self.diff:
            self.create_products_legacy()
        else:
            self.create_products()
        if self.ifc_import_settings.should_merge_by_class:
            self.merge_by_class()
        elif self.ifc_import_settings.should_merge_by_material:
            self.merge_by_material()

    def auto_set_workarounds(self):
        applications = self.file.by_type('IfcApplication')
        if not applications:
            return
        if applications[0].ApplicationIdentifier == 'Revit':
            self.ifc_import_settings.should_treat_styled_item_as_material = True
            if self.is_ifc_class_far_away('IfcSite'):
                self.ifc_import_settings.should_ignore_site_coordinates = True
            if self.is_ifc_class_far_away('IfcBuilding'):
                self.ifc_import_settings.should_ignore_building_coordinates = True
        elif applications[0].ApplicationFullName == '12D Model':
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
        return abs(point.Coordinates[0]) > 1000000 \
            or abs(point.Coordinates[1]) > 1000000 \
            or abs(point.Coordinates[2]) > 1000000

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

    def create_grids(self):
        grids = self.file.by_type('IfcGrid')
        for grid in grids:
            collection = bpy.data.collections.new(self.get_name(grid))
            self.project['blender'].children.link(collection)
            self.create_grid_axes(grid.UAxes, collection)
            self.create_grid_axes(grid.VAxes, collection)

    def create_grid_axes(self, axes, grid):
        for axis in axes:
            shape = ifcopenshell.geom.create_shape(self.settings_2d, axis.AxisCurve)
            mesh = self.create_mesh(axis, shape)
            obj = bpy.data.objects.new(f'IfcGrisAxis/{axis.AxisTag}', mesh)
            grid.objects.link(obj)

    def create_type_products(self):
        type_products = self.file.by_type('IfcTypeProduct')
        for type_product in type_products:
            self.create_type_product(type_product)

    def create_type_product(self, type_product):
        obj = bpy.data.objects.new(self.get_name(type_product), None)
        self.add_element_attributes(type_product, obj)
        self.add_element_document_relations(type_product, obj)
        self.add_type_product_psets(type_product, obj)
        self.project['blender'].objects.link(obj)
        self.type_products[type_product.GlobalId] = obj

    def create_products_legacy(self):
        elements = self.file.by_type('IfcElement') + self.file.by_type('IfcSpace')
        for element in elements:
            self.create_object(element)

    def create_products(self):
        if self.ifc_import_settings.should_use_cpu_multiprocessing:
            iterator = ifcopenshell.geom.iterator(self.settings, self.file, multiprocessing.cpu_count())
        else:
            iterator = ifcopenshell.geom.iterator(self.settings, self.file)
        valid_file = iterator.initialize()
        if not valid_file:
            self.create_products_legacy() # Sometimes, this can still work, not 100% sure why yet
            return False
        old_progress = -1
        while True:
            progress = iterator.progress() // 2
            if progress > old_progress:
                print("\r[" + "#" * progress + " " * (50 - progress) + "]", end="")
                old_progress = progress
            self.create_product(iterator.get())
            if not iterator.next():
                break
        print("\rDone creating geometry" + " " * 30)

    def create_product(self, shape):
        if shape is None:
            return

        element = self.file.by_id(shape.guid)

        if not self.ifc_import_settings.should_import_opening_elements \
                and element.is_a('IfcOpeningElement'):
            return

        if not self.ifc_import_settings.should_import_spaces \
                and element.is_a('IfcSpace'):
            return

        self.ifc_import_settings.logger.info('Creating object {}'.format(element))

        # TODO: make names more meaningful
        mesh_name = f'mesh-{shape.geometry.id}'
        mesh = self.meshes.get(mesh_name)
        if mesh is None:
            mesh = self.create_mesh(element, shape)
            self.meshes[mesh_name] = mesh
            self.mesh_shapes[mesh_name] = shape

        obj = bpy.data.objects.new(self.get_name(element), mesh)

        m = shape.transformation.matrix.data
        mat = mathutils.Matrix(([m[0], m[1], m[2], 0],
                                [m[3], m[4], m[5], 0],
                                [m[6], m[7], m[8], 0],
                                [m[9], m[10], m[11], 1]))
        mat.transpose()
        obj.matrix_world = mat

        self.material_creator.create(element, obj, mesh)
        self.add_element_attributes(element, obj)
        self.add_element_document_relations(element, obj)
        self.add_defines_by_type_relation(element, obj)
        self.place_object_in_spatial_tree(element, obj)
        self.add_product_psets(element, obj)
        self.added_objects.append(obj)

    def merge_by_class(self):
        merge_set = {}
        for obj in self.added_objects:
            if '/' in obj.name:
                merge_set.setdefault(obj.name.split('/')[0], []).append(obj)
        self.merge_objects(merge_set)

    def merge_by_material(self):
        merge_set = {}
        for obj in self.added_objects:
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

    def add_product_psets(self, element, obj):
        if not hasattr(element, 'IsDefinedBy') or not element.IsDefinedBy:
            return
        for definition in element.IsDefinedBy:
            if not definition.is_a('IfcRelDefinesByProperties') \
                    or not definition.RelatingPropertyDefinition.is_a('IfcPropertySet'):
                continue
            self.add_pset(definition.RelatingPropertyDefinition, obj)

    def add_type_product_psets(self, element, obj):
        if not hasattr(element, 'HasPropertySets') or not element.HasPropertySets:
            return
        for definition in element.HasPropertySets:
            if definition.is_a('IfcPropertySet'):
                self.add_pset(definition, obj)

    def add_pset(self, pset, obj):
            new_pset = obj.BIMObjectProperties.override_psets.add()
            new_pset.name = pset.Name
            if new_pset.name in schema.ifc.psets:
                for prop_name in schema.ifc.psets[new_pset.name]['HasPropertyTemplates'].keys():
                    prop = new_pset.properties.add()
                    prop.name = prop_name
            for prop in pset.HasProperties:
                if prop.is_a('IfcPropertySingleValue') and prop.NominalValue:
                    index = new_pset.properties.find(prop.Name)
                    if index >= 0:
                        new_pset.properties[index].string_value = str(prop.NominalValue.wrappedValue)
                    else:
                        new_prop = new_pset.properties.add()
                        new_prop.name = prop.Name
                        new_prop.string_value = str(prop.NominalValue.wrappedValue)

    def add_defines_by_type_relation(self, element, obj):
        related_type = None
        if self.file.schema == 'IFC2X3':
            if not hasattr(element, 'IsDefinedBy') or not element.IsDefinedBy:
                return
            for relationship in element.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByType'):
                    related_type = relationship.RelatingType
                    break
        else:
            if not hasattr(element, 'IsTypedBy') or not element.IsTypedBy:
                return
            related_type = element.IsTypedBy[0].RelatingType
        if related_type:
            obj.BIMObjectProperties.type_product = self.type_products[related_type.GlobalId]

    def load_diff(self):
        if not self.ifc_import_settings.diff_file:
            return
        with open(self.ifc_import_settings.diff_file, 'r') as file:
            self.diff = json.load(file)

    def load_file(self):
        self.ifc_import_settings.logger.info('loading file {}'.format(self.ifc_import_settings.input_file))
        self.file = ifcopenshell.open(self.ifc_import_settings.input_file)

    def set_ifc_file(self):
        bpy.context.scene.BIMProperties.ifc_file = self.ifc_import_settings.input_file

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
                self.unit_scale *= SIUnitHelper.get_prefix_multiplier(unit.Prefix)

    def create_project(self):
        self.project = { 'ifc': self.file.by_type('IfcProject')[0] }
        self.project['blender'] = bpy.data.collections.new('IfcProject/{}'.format(self.project['ifc'].Name))
        bpy.context.scene.collection.children.link(self.project['blender'])

    def create_spatial_hierarchy(self):
        elements = self.file.by_type('IfcSite') + self.file.by_type('IfcBuilding') + self.file.by_type('IfcBuildingStorey')
        attempts = 0
        while len(self.spatial_structure_elements) < len(elements) \
            and attempts <= len(elements):
            for element in elements:
                name = self.get_name(element)
                global_id = element.GlobalId
                if global_id in self.spatial_structure_elements:
                    continue
                # Occurs when some naughty programs export IFC site objects
                if not element.Decomposes:
                    continue
                parent = element.Decomposes[0].RelatingObject
                parent_name = self.get_name(parent)
                parent_global_id = parent.GlobalId
                if parent.is_a('IfcProject'):
                    self.spatial_structure_elements[global_id] = {
                        'blender': bpy.data.collections.new(name)}
                    self.project['blender'].children.link(self.spatial_structure_elements[global_id]['blender'])
                elif parent_global_id in self.spatial_structure_elements:
                    self.spatial_structure_elements[global_id] = {
                        'blender': bpy.data.collections.new(name)}
                    self.spatial_structure_elements[parent_global_id]['blender'].children.link(
                        self.spatial_structure_elements[global_id]['blender'])
            attempts += 1

    def create_aggregates(self):
        rel_aggregates = [a for a in self.file.by_type('IfcRelAggregates')
                if a.RelatingObject.is_a('IfcElement')]
        for rel_aggregate in rel_aggregates:
            self.create_aggregate(rel_aggregate)

    def create_aggregate(self, rel_aggregate):
        collection = bpy.data.collections.new(f'IfcRelAggregates/{rel_aggregate.id()}')
        bpy.context.scene.collection.children.link(collection)
        bpy.context.view_layer.layer_collection.children[collection.name].hide_viewport = True

        instance = bpy.data.objects.new('{}/{}'.format(
            rel_aggregate.RelatingObject.is_a(),
            rel_aggregate.RelatingObject.Name),
            None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = collection
        self.place_object_in_spatial_tree(rel_aggregate.RelatingObject, instance)

    def create_openings_collection(self):
        collection = bpy.data.collections.new('IfcOpeningElements')
        bpy.context.scene.collection.children.link(collection)

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

    def create_object(self, element):
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
        self.add_element_document_relations(element, obj)
        self.place_object_in_spatial_tree(element, obj)

    def add_element_document_relations(self, element, obj):
        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesDocument'):
                document_reference = association.RelatingDocument
                document = obj.BIMObjectProperties.documents.add()
                document.file = document_reference.Location

    def place_object_in_spatial_tree(self, element, obj):
        if hasattr(element, 'ContainedInStructure') \
                and element.ContainedInStructure \
                and element.ContainedInStructure[0].RelatingStructure:
            relating_structure_global_id = element.ContainedInStructure[0].RelatingStructure.GlobalId
            if relating_structure_global_id in self.spatial_structure_elements:
                self.spatial_structure_elements[relating_structure_global_id]['blender'].objects.link(obj)
        elif hasattr(element, 'Decomposes') \
                and element.Decomposes:
            if element.Decomposes[0].RelatingObject.is_a('IfcProject'):
                collection = bpy.data.collections.get(f'IfcProject/{element.Decomposes[0].RelatingObject.Name}')
            elif element.Decomposes[0].RelatingObject.is_a('IfcSpatialStructureElement'):
                global_id = element.Decomposes[0].RelatingObject.GlobalId
                if global_id in self.spatial_structure_elements:
                    collection = self.spatial_structure_elements[global_id]['blender']
            else:
                collection = bpy.data.collections.get(f'IfcRelAggregates/{element.Decomposes[0].id()}')
            if collection:
                collection.objects.link(obj)
        elif hasattr(element, 'HasFillings') \
                and element.HasFillings:
            bpy.data.collections.get('IfcOpeningElements').objects.link(obj)
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
                attribute.string_value = str(value)

    def get_element_matrix(self, element, mesh_name):
        element_matrix = self.get_local_placement(element.ObjectPlacement)

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

    def create_mesh(self, element, shape):
        try:
            if hasattr(shape, 'geometry'):
                geometry = shape.geometry
            else:
                geometry = shape
            mesh = bpy.data.meshes.new(geometry.id)
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
            mesh.from_pydata(vertices, edges, faces)
            return mesh
        except:
            self.ifc_import_settings.logger.error('Could not create mesh for {}: {}/{}'.format(element.GlobalId, self.get_name(element)))

    def a2p(self, o, z, x):
        y = z.cross(x)
        r = mathutils.Matrix((x, y, z, o))
        r.resize_4x4()
        r.transpose()
        return r

    def get_axis2placement(self, plc):
        z = mathutils.Vector(plc.Axis.DirectionRatios if plc.Axis else (0,0,1))
        x = mathutils.Vector(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0))
        o = plc.Location.Coordinates
        return self.a2p(o,z,x)

    def get_cartesiantransformationoperator(self, plc):
        x = mathutils.Vector(plc.Axis1.DirectionRatios if plc.Axis1 else (1,0,0))
        z = x.cross(mathutils.Vector(plc.Axis2.DirectionRatios if plc.Axis2 else (0,1,0)))
        o = plc.LocalOrigin.Coordinates
        return self.a2p(o,z,x)

    def get_local_placement(self, plc):
        if plc.PlacementRelTo is None:
            parent = mathutils.Matrix()
        else:
            parent = self.get_local_placement(plc.PlacementRelTo)
        if self.ifc_import_settings.should_ignore_site_coordinates \
            and 'IfcSite' in [o.is_a() for o in plc.PlacesObject]:
            return parent
        return parent @ self.get_axis2placement(plc.RelativePlacement)

class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
        self.should_auto_set_workarounds = True
        self.should_ignore_site_coordinates = False
        self.should_ignore_building_coordinates = False
        self.should_reset_absolute_coordinates = False
        self.should_import_curves = False
        self.should_import_opening_elements = False
        self.should_import_spaces = False
        self.should_treat_styled_item_as_material = False
        self.should_use_cpu_multiprocessing = False
        self.should_use_legacy = False
        self.should_merge_by_class = False
        self.should_merge_by_material = False
        self.diff_file = None
