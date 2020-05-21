import bpy
import csv
import json
import time
import datetime
import os
import zipfile
import tempfile
from pathlib import Path
from mathutils import Vector, Matrix
from .helper import SIUnitHelper
from . import schema
import ifcopenshell
import addon_utils
from .ifc2json import IFC2JSON

class ArrayModifier:
    count: int
    offset: Vector


class QtoCalculator():
    def get_units(self, o, vg_index):
        return len([v for v in o.data.vertices if vg_index in [g.group for g in v.groups]])

    def get_length(self, o, vg_index):
        length = 0
        edges = [e for e in o.data.edges if (
                vg_index in [g.group for g in o.data.vertices[e.vertices[0]].groups] and
                vg_index in [g.group for g in o.data.vertices[e.vertices[1]].groups]
        )]
        for e in edges:
            length += self.get_edge_distance(o, e)
        return length

    def get_edge_distance(self, obj, edge):
        return (obj.data.vertices[edge.vertices[1]].co - obj.data.vertices[edge.vertices[0]].co).length

    def get_area(self, o, vg_index):
        area = 0
        vertices_in_vg = [v.index for v in o.data.vertices if vg_index in [g.group for g in v.groups]]
        for polygon in o.data.polygons:
            if self.is_polygon_in_vg(polygon, vertices_in_vg):
                area += polygon.area
        return area

    def is_polygon_in_vg(self, polygon, vertices_in_vg):
        for v in polygon.vertices:
            if v not in vertices_in_vg:
                return False
        return True

    def get_volume(self, o, vg_index):
        volume = 0
        ob_mat = o.matrix_world
        me = o.data
        me.calc_loop_triangles()
        for tf in me.loop_triangles:
            tfv = tf.vertices
            if len(tf.vertices) == 3:
                tf_tris = (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),
            else:
                tf_tris = (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]), \
                          (me.vertices[tfv[2]], me.vertices[tfv[3]], me.vertices[tfv[0]])

            for tf_iter in tf_tris:
                v1 = ob_mat @ tf_iter[0].co
                v2 = ob_mat @ tf_iter[1].co
                v3 = ob_mat @ tf_iter[2].co

                volume += v1.dot(v2.cross(v3)) / 6.0
        return volume


class IfcParser():
    def __init__(self, ifc_export_settings):
        self.data_dir = ifc_export_settings.data_dir

        self.ifc_export_settings = ifc_export_settings

        self.selected_products = []
        self.selected_types = []
        self.selected_spatial_structure_elements = []
        self.selected_groups = []
        self.global_ids = []

        self.product_index = 0
        self.product_name_index_map = {}

        self.units = {}
        self.people = []
        self.organisations = []
        self.psets = {}
        self.document_references = {}
        self.classifications = []
        self.classification_references = {}
        self.objectives = {}
        self.qtos = {}
        self.aggregates = {}
        self.materials = {}
        self.spatial_structure_elements = []
        self.spatial_structure_elements_tree = []
        self.groups = []
        self.rel_contained_in_spatial_structure = {}
        self.rel_nests = {}
        self.rel_space_boundaries = {}
        self.rel_defines_by_type = {}
        self.rel_defines_by_qto = {}
        self.rel_defines_by_pset = {}
        self.rel_associates_document_object = {}
        self.rel_associates_document_type = {}
        self.rel_associates_classification_object = {}
        self.rel_associates_classification_type = {}
        self.rel_associates_material = {}
        self.rel_associates_material_layer_set = {}
        self.rel_associates_material_constituent_set = {}
        self.rel_associates_material_profile_set = {}
        self.rel_associates_constraint_objective_object = {}
        self.rel_associates_constraint_objective_type = {}
        self.rel_aggregates = {}
        self.rel_voids_elements = {}
        self.rel_fills_elements = {}
        self.rel_projects_elements = {}
        self.rel_connects_structural_member = {}
        self.rel_assigns_to_group = {}
        self.presentation_layer_assignments = {}
        self.representations = {}
        self.type_products = []
        self.door_attributes = {}
        self.window_attributes = {}
        self.project = {}
        self.libraries = []
        self.products = []

    def parse(self, selected_objects):
        self.units = self.get_units()
        self.unit_scale = self.get_unit_scale()
        self.people = self.get_people()
        self.organisations = self.get_organisations()
        selected_objects = self.add_spatial_elements_if_unselected(selected_objects)
        self.add_type_elements_if_unselected(selected_objects)
        self.categorise_selected_objects(selected_objects)
        self.material_psets = self.get_material_psets()
        self.document_information = self.get_document_information()
        self.document_references = self.get_document_references()
        self.classifications = self.get_classifications()
        self.classification_reference_maps = self.get_classification_reference_maps()
        self.classification_references = self.get_classification_references()
        self.objectives = self.get_objectives()
        self.load_representations()
        self.load_presentation_layer_assignments()
        self.materials = self.get_materials()
        self.styled_items = self.get_styled_items()
        self.spatial_structure_elements = self.get_spatial_structure_elements()
        self.groups = self.get_groups()

        self.projects = self.get_projects()
        self.project = self.projects[0]
        self.libraries = self.get_libraries()
        self.door_attributes = self.get_door_attributes()
        self.window_attributes = self.get_window_attributes()
        self.type_products = self.get_type_products()
        self.get_products()
        self.resolve_product_relationships()
        self.map_conversion = self.get_map_conversion()
        self.target_crs = self.get_target_crs()
        self.library_information = self.get_library_information()

        self.spatial_structure_elements_tree = []
        for project in self.projects:
            self.spatial_structure_elements_tree.extend(self.get_spatial_structure_elements_tree(project))

    def get_units(self):
        return {
            'length': {
                'ifc': None,
                'is_metric': bpy.context.scene.unit_settings.system == 'METRIC',
                'raw': bpy.context.scene.unit_settings.length_unit
            },
            'area': {
                'ifc': None,
                'is_metric': bpy.context.scene.unit_settings.system == 'METRIC',
                'raw': bpy.context.scene.unit_settings.length_unit
            },
            'volume': {
                'ifc': None,
                'is_metric': bpy.context.scene.unit_settings.system == 'METRIC',
                'raw': bpy.context.scene.unit_settings.length_unit
            }}

    def get_unit_scale(self):
        unit_settings = bpy.context.scene.unit_settings
        conversions = {
            'KILOMETERS': 1e3,
            'CENTIMETERS': 1e-2,
            'MILLIMETERS': 1e-3,
            'MICROMETERS': 1e-6,
            'FEET': 0.3048,
            'INCHES': 0.0254}
        if unit_settings.system in {'METRIC', 'IMPERIAL'}:
            scale = unit_settings.scale_length
            if unit_settings.length_unit in conversions.keys():
                scale *= conversions[unit_settings.length_unit]
            return scale
        return 1

    def get_object_attributes(self, obj):
        attributes = {'Name': self.get_ifc_name(obj.name)}
        global_id_index = obj.BIMObjectProperties.attributes.find('GlobalId')
        if global_id_index == -1:
            global_id = obj.BIMObjectProperties.attributes.add()
            global_id.name = 'GlobalId'
            global_id.string_value = ifcopenshell.guid.new()
        elif obj.BIMObjectProperties.attributes[global_id_index].string_value in self.global_ids:
            obj.BIMObjectProperties.attributes[global_id_index].string_value = ifcopenshell.guid.new()
        attributes.update({a.name: a.string_value for a in obj.BIMObjectProperties.attributes})
        self.global_ids.append(attributes['GlobalId'])
        return attributes

    def get_products(self):
        for product in self.selected_products:
            self.add_product(self.get_product(product))
            self.resolve_modifiers(product)

    def resolve_modifiers(self, product):
        obj = product['raw']
        if obj.data \
                and hasattr(obj.data, 'BIMMeshProperties') \
                and not obj.data.BIMMeshProperties.is_parametric:
            return
        instance_objects = [(obj, {
            'location': obj.matrix_world.translation,
            'array_offset': Vector((0, 0, 0)),
            'scale': obj.scale
        })]

        for modifier in obj.modifiers:
            created_instances = []
            if modifier.type == 'ARRAY':
                instance_objects.extend(
                    self.resolve_array_modifier(product, modifier, instance_objects)
                )
            elif modifier.type == 'MIRROR':
                instance_objects.extend(
                    self.resolve_mirror_modifier(product, modifier, instance_objects)
                )

    def get_array_modifier(self, product, modifier):
        obj = product['raw']
        array = ArrayModifier()
        world_rotation = obj.matrix_world.decompose()[1]
        array.offset = world_rotation @ Vector(
            (
                modifier.constant_offset_displace[0],
                modifier.constant_offset_displace[1],
                modifier.constant_offset_displace[2]
            )
        )
        if modifier.fit_type == 'FIXED_COUNT':
            array.count = modifier.count
        elif modifier.fit_type == 'FIT_LENGTH':
            array.count = int(modifier.fit_length / array.offset.length)
        return array

    def resolve_array_modifier(self, product, modifier, instance_objects):
        modifier = self.get_array_modifier(product, modifier)
        created_instances = []
        for obj in instance_objects:
            for n in range(modifier.count - 1):
                override = obj[1].copy()
                override['array_offset'] = ((n + 1) * modifier.offset)
                override['location'] = obj[1]['location'].copy()
                location = override['location'] + ((n + 1) * modifier.offset)
                override['location'] = location
                self.add_product(
                    self.get_product(
                        {'raw': obj[0], 'metadata': product['metadata']},
                        metadata_override=override,
                        attribute_override={'GlobalId': self.get_parametric_global_id(
                                product['raw'],
                                len(instance_objects)+len(created_instances)-1
                            )
                        }
                    )
                )
                created_instances.append((obj[0], override))
        return created_instances

    def resolve_mirror_modifier(self, product, modifier, instance_objects):
        created_instances = []
        mirrors = []
        for axis in [0, 1, 2]:
            if modifier.use_axis[axis]:
                mirrors.append(axis)
        for mirror in mirrors:
            axis_instances = []
            for obj in instance_objects:
                override = obj[1].copy()
                override['has_scale'] = True
                override['has_mirror'] = True
                override['scale'] = obj[1]['scale'].copy()
                override['scale'][mirror] *= -1
                mirror_axis = Vector((0, 0, 0))
                mirror_axis[mirror] = 1
                world_rotation = obj[0].matrix_world.decompose()[1].to_matrix().to_4x4()
                unrotated_offset = world_rotation.inverted() @ override['array_offset']
                mirrored_offset = unrotated_offset @ Matrix.Scale(-1, 4, mirror_axis)
                rotated_offset = world_rotation @ mirrored_offset
                override['location'] = override['location'] - override['array_offset'] + rotated_offset
                self.add_product(
                    self.get_product(
                        {'raw': obj[0], 'metadata': product['metadata']},
                        metadata_override=override,
                        attribute_override={'GlobalId': self.get_parametric_global_id(
                                product['raw'],
                                len(instance_objects)+len(created_instances)-1
                            )
                        }
                    )
                )
                created_instances.append((obj[0], override))
                axis_instances.append((obj[0], override))
            instance_objects.extend(axis_instances)
        return created_instances

    def resolve_product_relationships(self):
        for i, product in enumerate(self.products):
            obj = product['raw']
            self.resolve_voids_and_fills(i, obj)
            self.resolve_structural_connections(i, obj)

    def resolve_structural_connections(self, i, obj):
        if not obj.BIMObjectProperties.structural_member_connection:
            return
        self.rel_connects_structural_member[i] = self.get_product_index_from_raw_name(
            obj.BIMObjectProperties.structural_member_connection.name)

    def resolve_voids_and_fills(self, i, obj):
        for m in obj.modifiers:
            if m.type != 'BOOLEAN' or m.object is None:
                continue
            void_or_projection = self.get_product_index_from_raw_name(m.object.name)
            if void_or_projection is None:
                continue
            if m.operation == 'DIFFERENCE' \
                    and self.get_ifc_class(m.object.name) == 'IfcOpeningElement':
                self.rel_voids_elements.setdefault(i, []).append(void_or_projection)
                if not m.object.parent:
                    continue
                fill = self.get_product_index_from_raw_name(m.object.parent.name)
                if fill:
                    self.rel_fills_elements.setdefault(void_or_projection, []).append(fill)
            elif m.operation == 'UNION' \
                    and self.get_ifc_class(m.object.name) == 'IfcProjectionElement':
                self.rel_projects_elements.setdefault(i, []).append(void_or_projection)

    def get_axis(self, matrix, axis):
        return matrix.col[axis].to_3d().normalized()

    def get_parametric_global_id(self, obj, index):
        global_ids = obj.BIMObjectProperties.global_ids
        total_global_ids = len(global_ids)
        if index < total_global_ids:
            return global_ids[index].name
        global_id = obj.BIMObjectProperties.global_ids.add()
        global_id.name = ifcopenshell.guid.new()
        return global_id.name

    def add_product(self, product):
        self.products.append(product)
        self.product_name_index_map[product['raw'].name] = self.product_index
        self.product_index += 1

    def get_product_index_from_raw_name(self, name):
        for index, product in enumerate(self.products):
            if product['raw'].name == name:
                return index

    def append_product_attributes(self, product, obj):
        product.update({
            'location': obj.matrix_world.translation,
            'up_axis': self.get_axis(obj.matrix_world, 2),
            'forward_axis': self.get_axis(obj.matrix_world, 0),
            'right_axis': self.get_axis(obj.matrix_world, 1),
            'has_scale': obj.scale != Vector((1, 1, 1)),
            'has_mirror': False,
            'array_offset': Vector((0, 0, 0)),
            'scale': obj.scale,
            'representations': self.get_object_representation_names(obj)
        })

    def get_product(self, selected_product, metadata_override={}, attribute_override={}):
        obj = selected_product['raw']
        product = {
            'ifc': None,
            'raw': obj,
            'class': self.get_ifc_class(obj.name),
            'relating_structure': None,
            'relating_host': None,
            'relating_qtos_key': None,
            'attributes': self.get_object_attributes(obj),
            'has_boundary_condition': obj.BIMObjectProperties.has_boundary_condition,
            'boundary_condition_class': None,
            'boundary_condition_attributes': {},
            'structural_member_connection': None
        }
        self.append_product_attributes(product, obj)
        product['attributes'].update(attribute_override)
        product.update(metadata_override)

        type_product = obj.BIMObjectProperties.relating_type
        if type_product \
                and self.is_a_type(self.get_ifc_class(type_product.name)):
            reference = self.get_type_product_reference(self.get_name_attribute(type_product))
            self.rel_defines_by_type.setdefault(reference, []).append(self.product_index)

        if product['has_boundary_condition']:
            product['boundary_condition_class'] = obj.BIMObjectProperties.boundary_condition.name
            product['boundary_condition_attributes'] = {a.name: a.string_value
                for a in obj.BIMObjectProperties.boundary_condition.attributes}

        self.get_product_relating_structure(product, obj)

        if 'IfcRelNests' in obj.constraints:
            # TODO: I think get_product_index_from_raw_name should not be used
            parent_product_index = self.get_product_index_from_raw_name(
                obj.constraints['IfcRelNests'].target.name)
            self.rel_nests.setdefault(parent_product_index, []).append(product)
            product['relating_host'] = parent_product_index

        for name, constraint in obj.constraints.items():
            if 'IfcRelSpaceBoundary' not in name:
                continue
            self.rel_space_boundaries.setdefault(self.product_index, []).append({
                'ifc': None,
                'class': self.get_ifc_class(name),
                'related_building_element_raw_name': constraint.target.name,
                'connection_geometry_face_index': name.split('/')[1],
                'attributes': {
                    'PhysicalOrVirtualBoundary': name.split('/')[2],
                    'InternalOrExternalBoundary': name.split('/')[3]
                }
            })

        if obj.instance_type == 'COLLECTION' \
                and self.is_a_rel_aggregates(self.get_ifc_class(obj.instance_collection.name)):
            self.rel_aggregates[self.product_index] = obj.name

        if 'rel_aggregates_relating_object' in selected_product['metadata']:
            relating_object = selected_product['metadata']['rel_aggregates_relating_object']
            inverted = relating_object.matrix_world.inverted()
            product['location'] = inverted @ product['location']
            product['up_axis'] = self.get_axis(inverted @ obj.matrix_world, 2)
            product['forward_axis'] = self.get_axis(inverted @ obj.matrix_world, 0)
            product['right_axis'] = self.get_axis(inverted @ obj.matrix_world, 1)
            self.aggregates.setdefault(relating_object.name, []).append(self.product_index)

        if obj.name in self.qtos:
            self.rel_defines_by_qto.setdefault(obj.name, []).append(product)

        self.get_product_psets_qtos(product, obj, is_pset=True)
        self.get_product_psets_qtos(product, obj, is_qto=True)

        for reference in obj.BIMObjectProperties.document_references:
            self.rel_associates_document_object.setdefault(
                reference.name, []).append(product)

        for classification in obj.BIMObjectProperties.classifications:
            self.rel_associates_classification_object.setdefault(
                classification.name, []).append(product)

        for key in obj.keys():
            if key[0:9] == 'Objective':
                self.rel_associates_constraint_objective_object.setdefault(
                    obj[key], []).append(product)

        for slot in obj.material_slots:
            if slot.link == 'OBJECT':
                continue
            if obj.BIMObjectProperties.material_type == 'IfcMaterialLayerSet':
                self.rel_associates_material_layer_set.setdefault(self.product_index, []).append(
                    slot.material.name)
            elif obj.BIMObjectProperties.material_type == 'IfcMaterialConstituentSet':
                self.rel_associates_material_constituent_set.setdefault(self.product_index, []).append(
                    slot.material.name)
            elif obj.BIMObjectProperties.material_type == 'IfcMaterialProfileSet':
                self.rel_associates_material_profile_set.setdefault(self.product_index, []).append(
                    slot.material.name)
            else:
                self.rel_associates_material.setdefault(slot.material.name, []).append(product)

        return product

    def get_product_psets_qtos(self, product, obj, is_pset=False, is_qto=False):
        if is_pset:
            psets_qtos = obj.BIMObjectProperties.psets
            results = self.psets
            relationships = self.rel_defines_by_pset
        if is_qto:
            psets_qtos = obj.BIMObjectProperties.qtos
            results = self.qtos
            relationships = self.rel_defines_by_qto
        for item in psets_qtos:
            item_key = '{}/{}'.format(item.name, obj.name)
            raw = {p.name: p.string_value for p in item.properties if p.string_value}
            if not raw:
                continue
            results[item_key] = {
                'ifc': None,
                'raw': raw,
                'attributes': { 'Name': item.name }
            }
            relationships.setdefault(item_key, []).append(product)

    def get_product_relating_structure(self, product, obj):
        relating_structure = obj.BIMObjectProperties.relating_structure
        if relating_structure:
            reference = self.get_spatial_structure_element_reference(relating_structure.name)
            self.rel_contained_in_spatial_structure.setdefault(reference, []).append(self.product_index)
            product['relating_structure'] = reference
            return
        for collection in product['raw'].users_collection:
            self.parse_product_collection(product, collection)

    def parse_product_collection(self, product, collection):
        if collection is None:
            return
        class_name = self.get_ifc_class(collection.name)
        if self.is_a_spatial_structure_element(class_name):
            reference = self.get_spatial_structure_element_reference(collection.name)
            self.rel_contained_in_spatial_structure.setdefault(reference, []).append(self.product_index)
            product['relating_structure'] = reference
        elif self.is_a_group(class_name):
            reference = self.get_group_reference(collection.name)
            self.rel_assigns_to_group.setdefault(reference, []).append(self.product_index)
        elif self.is_a_rel_aggregates(class_name):
            pass
        else:
            self.parse_product_collection(product, self.get_parent_collection(collection))

    def get_parent_collection(self, child_collection):
        for parent_collection in bpy.data.collections:
            for child in parent_collection.children:
                if child.name == child_collection.name:
                    return parent_collection

    def add_spatial_elements_if_unselected(self, selected_objects):
        results = set(selected_objects)
        base_collections = set()
        added_objs = []
        for obj in selected_objects:
            for collection in obj.users_collection:
                base_collections.add(collection)
        for collection in base_collections:
            spatial_obj = bpy.data.objects.get(collection.name)
            if not spatial_obj or spatial_obj in added_objs:
                continue
            added_objs.append(spatial_obj)
            parent_collection = self.get_parent_collection(collection)
            while parent_collection:
                spatial_obj = bpy.data.objects.get(parent_collection.name)
                parent_collection = self.get_parent_collection(parent_collection)
                if not spatial_obj or spatial_obj in added_objs:
                    continue
                added_objs.append(spatial_obj)
        results.update(added_objs)
        return results

    def add_type_elements_if_unselected(self, selected_objects):
        added_objs = []
        for obj in selected_objects:
            if obj.BIMObjectProperties.relating_type:
                added_objs.append(obj.BIMObjectProperties.relating_type)
        selected_objects.update(added_objs)
        selected_objects = set(selected_objects)

    def categorise_selected_objects(self, objects_to_sort, metadata=None):
        if not metadata:
            metadata = {}
        for obj in objects_to_sort:
            if obj.name[0:3] != 'Ifc':
                continue
            elif self.is_a_spatial_structure_element(self.get_ifc_class(obj.name)):
                self.selected_spatial_structure_elements.append({'raw': obj, 'metadata': metadata})
            elif self.is_a_type(self.get_ifc_class(obj.name)):
                self.selected_types.append({'raw': obj, 'metadata': metadata})
            elif self.is_a_group(self.get_ifc_class(obj.name)):
                self.selected_groups.append({'raw': obj, 'metadata': metadata})
            elif obj.instance_type == 'COLLECTION':
                self.categorise_selected_objects(
                    obj.instance_collection.objects,
                    {'rel_aggregates_relating_object': obj}
                )
                self.selected_products.append({'raw': obj, 'metadata': metadata})
            elif self.is_a_project(self.get_ifc_class(obj.name)) \
                    or self.is_a_library(self.get_ifc_class(obj.name)):
                pass
            elif not self.is_a_library(self.get_ifc_class(obj.users_collection[0].name)):
                self.selected_products.append({'raw': obj, 'metadata': metadata})

    def get_material_psets(self):
        psets = {}
        for filename in Path(self.data_dir + 'material/').glob('**/*.csv'):
            with open(filename, 'r') as f:
                description = filename.parts[-2]
                name = filename.stem
                if description not in psets:
                    psets[description] = {}
                psets[description][name] = {
                    'ifc': None,
                    'raw': {x[0]: x[1] for x in list(csv.reader(f))},
                    'attributes': {
                        'Name': name,
                        'Description': description}
                }
        return psets

    def get_door_attributes(self):
        return self.get_predefined_attributes('door')

    def get_window_attributes(self):
        return self.get_predefined_attributes('window')

    def get_predefined_attributes(self, attr):
        results = {}
        for filename in Path(self.data_dir + attr + '/').glob('**/*.csv'):
            with open(filename, 'r') as f:
                type_name = filename.parts[-2]
                pset_name = filename.stem
                results.setdefault(type_name, []).append({
                    'ifc': None,
                    'raw': {x[0]: x[1] for x in list(csv.reader(f))},
                    'pset_name': pset_name.split('.')[0]
                })
        return results

    def get_classifications(self):
        results = {}
        for classification in bpy.context.scene.BIMProperties.classifications:
            schema.ifc.load_classification(classification.filename)
            results[classification.filename] = {
                'ifc': None,
                'raw': classification,
                'raw_element': schema.ifc.classification_files[classification.filename].by_type('IfcClassification')[0]
            }
        return results

    def get_classification_reference_maps(self):
        results = {}
        for filename, classification in self.classifications.items():
            ifc_file = schema.ifc.classification_files[filename]
            if ifc_file.schema == 'IFC2X3':
                results[filename] = { e.ItemReference: e for e in ifc_file.by_type('IfcClassificationReference')}
            else:
                results[filename] = { e.Identification: e for e in ifc_file.by_type('IfcClassificationReference')}
        return results

    def get_classification_references(self):
        results = {}
        for product in self.selected_products:
            for reference in product['raw'].BIMObjectProperties.classifications:
                results[reference.name] = {
                    'ifc': None,
                    'raw': reference,
                    'raw_element': self.classification_reference_maps[reference.referenced_source][reference.name]

                }
        return results

    def get_objectives(self):
        results = {}
        class_path = self.data_dir + 'constraint/'
        with open(class_path + 'objectives.csv', 'r') as f:
            data = list(csv.reader(f))
            keys = data.pop(0)
            for row in data:
                results[row[0]] = {
                    'ifc': None,
                    'raw': row,
                    'attributes': dict(zip(keys, row))
                }
        return results

    def get_people(self):
        with open(self.data_dir + 'owner/person.json') as file:
            return [{'raw': p} for p in json.load(file)]

    def get_organisations(self):
        with open(self.data_dir + 'owner/organisation.json') as file:
            return [{'raw': o} for o in json.load(file)]

    def get_document_references(self):
        results = {}
        for reference in bpy.context.scene.BIMProperties.document_references:
            data_map = {
                'name': 'Identification',
                'human_name': 'Name',
                'description': 'Description',
                'location': 'Location'
            }
            attributes = {}
            for key, value in data_map.items():
                if getattr(reference, key):
                    attributes[value] = getattr(reference, key)
            results[reference.name] = {
                'ifc': None,
                'raw': reference,
                'referenced_document': reference.referenced_document,
                'attributes': attributes
            }
        return results

    def get_document_information(self):
        results = {}
        for information in bpy.context.scene.BIMProperties.document_information:
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
            attributes = {}
            for key, value in data_map.items():
                if getattr(information, key):
                    attributes[value] = getattr(information, key)
            results[information.name] = {
                'ifc': None,
                'raw': information,
                'attributes': attributes
            }
        return results

    def get_projects(self):
        results = []
        for collection in bpy.data.collections:
            if self.is_a_project(self.get_ifc_class(collection.name)):
                obj = bpy.data.objects.get(collection.name)
                results.append({
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': self.get_object_attributes(obj)
                })
        return results

    def get_libraries(self):
        results = []
        for collection in self.project['raw'].children:
            if not self.is_a_library(self.get_ifc_class(collection.name)):
                continue
            results.append({
                'ifc': None,
                'raw': collection,
                'class': self.get_ifc_class(collection.name),
                'rel_declares_type_products': [],
                'attributes': self.get_object_attributes(collection)
            })
        return results

    def get_map_conversion(self):
        scene = bpy.context.scene
        if not scene.BIMProperties.has_georeferencing:
            return {}
        return {
            'ifc': None,
            'attributes': {
                'Eastings': float(scene.MapConversion.eastings),
                'Northings': float(scene.MapConversion.northings),
                'OrthogonalHeight': float(scene.MapConversion.orthogonal_height),
                'XAxisAbscissa': float(scene.MapConversion.x_axis_abscissa),
                'XAxisOrdinate': float(scene.MapConversion.x_axis_ordinate),
                'Scale': float(scene.MapConversion.scale)
            }
        }

    def get_target_crs(self):
        scene = bpy.context.scene
        if not scene.BIMProperties.has_georeferencing:
            return {}
        return {
            'ifc': None,
            'attributes': {
                'Name': scene.TargetCRS.name,
                'Description': scene.TargetCRS.description,
                'GeodeticDatum': scene.TargetCRS.geodetic_datum,
                'VerticalDatum': scene.TargetCRS.vertical_datum,
                'MapProjection': scene.TargetCRS.map_projection,
                'MapZone': str(scene.TargetCRS.map_zone),
                'MapUnit': scene.TargetCRS.map_unit
            }
        }

    def get_library_information(self):
        scene = bpy.context.scene
        if not scene.BIMProperties.has_library:
            return {}
        return {
            'ifc': None,
            'attributes': {
                'Name': scene.BIMLibrary.name,
                'Version': scene.BIMLibrary.version,
                'VersionDate': scene.BIMLibrary.version_date,
                'Location': scene.BIMLibrary.location,
                'Description': scene.BIMLibrary.description
            }
        }

    def get_spatial_structure_elements(self):
        elements = []
        for selected_element in self.selected_spatial_structure_elements:
            obj = selected_element['raw']
            element = {
                'ifc': None,
                'raw': obj,
                'class': self.get_ifc_class(obj.name),
                'attributes': self.get_object_attributes(obj)
            }
            self.append_product_attributes(element, obj)
            elements.append(element)
        return elements

    def get_groups(self):
        elements = []
        for selected_element in self.selected_groups:
            obj = selected_element['raw']
            elements.append({
                'ifc': None,
                'raw': obj,
                'class': self.get_ifc_class(obj.name),
                'attributes': self.get_object_attributes(obj)
            })
        return elements

    def load_presentation_layer_assignments(self):
        for representation in self.representations.values():
            if representation['presentation_layer']:
                self.presentation_layer_assignments.setdefault(
                        representation['presentation_layer'], []).append(representation)

    def load_representations(self):
        if not self.ifc_export_settings.has_representations:
            return
        for product in self.selected_products \
                + self.selected_types \
                + self.selected_spatial_structure_elements:
            self.prevent_data_name_duplicates(product)
            self.load_product_representations(product)

    def prevent_data_name_duplicates(self, product):
        if product['raw'].data \
                and bpy.data.meshes.get(product['raw'].data.name) \
                and bpy.data.curves.get(product['raw'].data.name):
            product['raw'].data.name +=  '~'

    def load_product_representations(self, product):
        obj = product['raw']
        if obj.data and obj.data.name in self.representations:
            return
        if isinstance(obj.data, bpy.types.Camera):
            return
        self.append_representation_per_context(obj)

    def is_point_cloud(self, obj):
        return hasattr(obj, 'point_cloud_visualizer') \
                and obj.point_cloud_visualizer.uuid

    def is_structural(self, obj):
        return 'IfcStructural' in obj.name

    def append_default_representation(self, obj):
        self.representations['Model/Body/MODEL_VIEW/{}'.format(obj.data.name)] = self.get_representation(
            obj.data, obj, 'Model', 'Body', 'MODEL_VIEW')

    def append_point_cloud_representation(self, obj):
        self.representations['Model/Body/MODEL_VIEW/{}'.format(obj.name)] = self.get_representation(
            obj.point_cloud_visualizer, obj, 'Model', 'Body', 'MODEL_VIEW')

    def append_curve_axis_representation(self, obj):
        self.representations['Model/Axis/GRAPH_VIEW/{}'.format(obj.data.name)] = self.get_representation(
            obj.data, obj, 'Model', 'Axis', 'GRAPH_VIEW')

    def append_structural_reference_representation(self, obj):
        if obj.type == 'EMPTY':
            self.representations['Model/Reference/GRAPH_VIEW/{}'.format(obj.name)] = self.get_representation(
                obj, obj, 'Model', 'Reference', 'GRAPH_VIEW')
        else:
            self.representations['Model/Reference/GRAPH_VIEW/{}'.format(obj.data.name)] = self.get_representation(
                obj.data, obj, 'Model', 'Reference', 'GRAPH_VIEW')

    def append_representation_per_context(self, obj):
        if obj.data:
            name = self.get_ifc_representation_name(obj.data.name)
        else:
            name = obj.name
        for context in self.ifc_export_settings.context_tree:
            for subcontext in context['subcontexts']:
                for target_view in subcontext['target_views']:
                    self.append_representation_in_context(obj, context['name'], subcontext['name'], target_view, name)

    def append_representation_in_context(self, obj, context, subcontext, target_view, name):
        context_prefix = '/'.join([context, subcontext, target_view])
        mesh_name = '/'.join([context_prefix, name])
        mesh = self.search_for_mesh_or_curve_data(mesh_name)
        if mesh:
            self.representations[mesh_name] = self.get_representation(
                mesh, obj, context, subcontext, target_view)
        elif context_prefix == 'Model/Body/MODEL_VIEW' \
                and obj.data \
                and not self.is_mesh_context_sensitive(obj.data.name):
            self.append_default_representation(obj)
        elif context_prefix == 'Model/Body/MODEL_VIEW' \
                and self.is_point_cloud(obj):
            self.append_point_cloud_representation(obj)
        elif context_prefix == 'Model/Reference/GRAPH_VIEW' \
                and self.is_structural(obj):
            self.append_structural_reference_representation(obj)
        elif context_prefix == 'Model/Axis/GRAPH_VIEW' \
                and obj.type == 'CURVE':
            self.append_curve_axis_representation(obj)

    def search_for_mesh_or_curve_data(self, name):
        data = bpy.data.meshes.get(name)
        if not data:
            data = bpy.data.curves.get(name)
        return data

    def get_representation(self, mesh, obj, context, subcontext, target_view):
        return {
            'ifc': None,
            'raw': mesh,
            'raw_object': obj,
            'context': context,
            'subcontext': subcontext,
            'target_view': target_view,
            'is_parametric': mesh.BIMMeshProperties.is_parametric if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_curve': isinstance(mesh, bpy.types.Curve),
            'is_point_cloud': self.is_point_cloud(obj),
            'is_structural': self.is_structural(obj),
            'is_text': isinstance(mesh, bpy.types.TextCurve),
            'is_wireframe': mesh.BIMMeshProperties.is_wireframe if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_swept_solid': mesh.BIMMeshProperties.is_swept_solid if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_generated': False,
            'presentation_layer': mesh.BIMMeshProperties.presentation_layer if hasattr(mesh, 'BIMMeshProperties') else None,
            'attributes': {'Name': mesh.name}
        }

    def is_mesh_context_sensitive(self, name):
        return '/' in name \
            and ( \
                name[0:6] == 'Model/' \
                or name[0:5] == 'Plan/' \
            )

    def get_ifc_representation_name(self, name):
        if self.is_mesh_context_sensitive(name):
            return name.split('/')[3]
        return name

    def get_materials(self):
        results = {}
        if not self.ifc_export_settings.has_representations:
            return results
        for product in self.selected_products + self.type_products:
            obj = product['raw']
            if obj.data is None:
                continue
            for slot in obj.material_slots:
                if slot.material is None:
                    continue
                if slot.material.name in results or slot.link == 'OBJECT':
                    continue
                results[slot.material.name] = {
                    'ifc': None,
                    'part_ifc': None,
                    'raw': slot.material,
                    'material_type': obj.BIMObjectProperties.material_type,
                    'attributes': self.get_material_attributes(slot.material)
                }
        return results

    def get_material_attributes(self, material):
        attributes = {'Name': material.name}
        attributes.update({a.name: a.string_value for a in material.BIMMaterialProperties.attributes})
        return attributes

    def get_styled_items(self):
        results = []
        if not self.ifc_export_settings.has_representations:
            return results
        parsed_data_names = []
        for product in self.selected_products + self.type_products:
            obj = product['raw']
            if obj.data is None or obj.data.name in parsed_data_names:
                continue
            parsed_data_names.append(obj.data.name)
            for slot in obj.material_slots:
                if slot.material is None:
                    continue
                if not self.ifc_export_settings.should_export_all_materials_as_styled_items and (
                        slot.material.name in results or slot.link == 'DATA'):
                    continue
                results.append({
                    'ifc': None,
                    'raw': slot.material,
                    'related_product_name': product['raw'].name,
                    'attributes': {'Name': slot.material.name},
                })
        return results

    def get_type_products(self):
        results = []
        for product in self.selected_types:
            results.append(self.get_product(product))
        return results

    def get_object_representation_names(self, obj):
        names = []
        if self.is_point_cloud(obj):
            names.append('Model/Body/MODEL_VIEW/{}'.format(obj.name))
            return names
        elif self.is_structural(obj) and obj.type == 'EMPTY':
            names.append('Model/Reference/GRAPH_VIEW/{}'.format(obj.name))
            return names
        if not obj.data:
            return names
        name = self.get_ifc_representation_name(obj.data.name)
        for context in self.ifc_export_settings.context_tree:
            for subcontext in context['subcontexts']:
                for target_view in subcontext['target_views']:
                    mesh_name = '/'.join([context['name'], subcontext['name'], target_view, name])
                    if mesh_name in self.representations:
                        names.append(mesh_name)
        return names

    def get_spatial_structure_elements_tree(self, parent):
        children = []
        if parent['raw'].name not in bpy.data.collections:
            return children
        for reference, element in enumerate(self.spatial_structure_elements):
            if ( \
                    # A convention is established that spatial elements may be
                    # an object placed in a collection of the same name
                        element['raw'].name == element['raw'].users_collection[0].name \
                        and element['raw'].users_collection[0].name in [c.name \
                            for c in bpy.data.collections[parent['raw'].name].children] \
                    ) or ( \
                    # We allow finer grain spatial elements such as IfcSpace to
                    # break the convention to prevent collection overload in Blender
                        element['raw'].name != element['raw'].users_collection[0].name \
                        and element['raw'].users_collection[0].name in [o.name \
                            for o in bpy.data.collections[parent['raw'].name].objects] \
                    ):
                children.append({
                    'reference': reference,
                    'children': self.get_spatial_structure_elements_tree(element)
                })
        return children

    def get_spatial_structure_element_reference(self, name):
        return [e['raw'].name for e in self.spatial_structure_elements].index(name)

    def get_group_reference(self, name):
        return ['{}/{}'.format(e['class'], e['attributes']['Name'])
                for e in self.groups].index(name)

    def get_type_product_reference(self, name):
        return [p['attributes']['Name']
                for p in self.type_products].index(name)

    def get_ifc_class(self, name):
        return name.split('/')[0]

    def get_ifc_name(self, name):
        try:
            return name.split('/')[1]
        except IndexError:
            self.ifc_export_settings.logger.error(
                'Name "{}" does not follow the format of "IfcClass/Name"'.format(name))

    def get_name_attribute(self, obj):
        name = obj.BIMObjectProperties.attributes.get('Name')
        if name:
            return name.string_value
        return self.get_ifc_name(obj.name)

    def is_a_spatial_structure_element(self, class_name):
        return class_name in [
            'IfcBuilding',
            'IfcBuildingStorey',
            'IfcExternalSpatialElement',
            'IfcSite',
            'IfcSpace',
            'IfcSpatialZone'
            ]

    def is_a_rel_aggregates(self, class_name):
        return class_name == 'IfcRelAggregates'

    def is_a_project(self, class_name):
        return class_name == 'IfcProject'

    def is_a_library(self, class_name):
        return class_name == 'IfcProjectLibrary'

    def is_a_group(self, class_name):
        return class_name in [g for g in schema.ifc.IfcGroup.keys()]

    def is_a_type(self, class_name):
        return class_name[0:3] == 'Ifc' and class_name[-4:] == 'Type'


class IfcExporter():
    def __init__(self, ifc_export_settings, ifc_parser, qto_calculator):
        self.template_file = '{}template.ifc'.format(ifc_export_settings.schema_dir)
        self.ifc_export_settings = ifc_export_settings
        self.ifc_parser = ifc_parser
        self.qto_calculator = qto_calculator
        self.schema = 'IFC4'

    def export(self, selected_objects):
        self.file = ifcopenshell.file(schema=self.schema)
        self.ifc_parser.parse(selected_objects)
        self.create_units()
        self.create_people()
        self.create_organisations()
        self.create_origin()
        self.create_owner_history()
        self.set_header()
        self.create_rep_context()
        self.create_project()
        self.create_library_information()
        self.create_document_information()
        self.create_document_references()
        self.create_classifications()
        self.create_classification_references()
        self.create_objectives()
        self.create_psets()
        self.create_libraries()
        self.create_map_conversion()
        self.create_representations()
        self.create_materials()
        self.create_type_products()
        self.create_spatial_structure_elements(self.ifc_parser.spatial_structure_elements_tree)
        self.create_groups()
        self.create_qtos()
        self.create_products()
        self.create_styled_items()
        self.create_presentation_layer_assignments()
        self.relate_definitions_to_contexts()
        self.relate_objects_to_objects()
        self.relate_elements_to_spatial_structures()
        self.relate_nested_elements_to_hosted_elements()
        self.relate_objects_to_types()
        self.relate_objects_to_qtos()
        self.relate_objects_to_psets()
        self.relate_objects_to_opening_elements()
        self.relate_opening_elements_to_fillings()
        self.relate_objects_to_projection_elements()
        self.relate_objects_to_materials()
        for set_type in ['constituent', 'layer', 'profile']:
            self.relate_objects_to_material_sets(set_type)
        self.relate_spaces_to_boundary_elements()
        self.relate_to_documents(self.ifc_parser.rel_associates_document_object)
        self.relate_to_documents(self.ifc_parser.rel_associates_document_type)
        self.relate_to_classifications(self.ifc_parser.rel_associates_classification_object)
        self.relate_to_classifications(self.ifc_parser.rel_associates_classification_type)
        self.relate_to_objectives(self.ifc_parser.rel_associates_constraint_objective_object)
        self.relate_to_objectives(self.ifc_parser.rel_associates_constraint_objective_type)
        self.relate_structural_members_to_connections()
        self.relate_objects_to_groups()
        self.write_ifc_file()

    def create_origin(self):
        self.origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0., 0., 0.)),
            self.file.createIfcDirection((0., 0., 1.)),
            self.file.createIfcDirection((1., 0., 0.)))

    def set_header(self):
        # TODO: add all metadata, pending bug #747
        self.file.wrapped_data.header.file_name.name = os.path.basename(self.ifc_export_settings.output_file)
        self.file.wrapped_data.header.file_name.time_stamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone().replace(microsecond=0).isoformat()
        self.file.wrapped_data.header.file_name.preprocessor_version = 'IfcOpenShell {}'.format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.originating_system = '{} {}'.format(
            self.owner_history.OwningApplication.ApplicationFullName,
            self.owner_history.OwningApplication.Version,
        )
        self.file.wrapped_data.header.file_name.authorization = self.owner_history.OwningUser.ThePerson.Identification

    def create_owner_history(self):
        for person in self.ifc_parser.people:
            if person['ifc'].Identification == bpy.context.scene.BIMProperties.person:
                break
        for organisation in self.ifc_parser.organisations:
            if organisation['ifc'].Name == bpy.context.scene.BIMProperties.organisation:
                break
        person_and_organisation = self.file.create_entity('IfcPersonAndOrganization', **{
            'ThePerson': person['ifc'],
            'TheOrganization': organisation['ifc'],
            'Roles': None # TODO
        })
        version = '.'.join([str(x) for x in [addon.bl_info.get('version', (-1,-1,-1)) for addon in addon_utils.modules() if addon.bl_info['name'] == 'BlenderBIM'][0]])
        developer_organisation = [o for o in self.ifc_parser.organisations if o['ifc'].Name == 'IfcOpenShell'][0]['ifc']
        application = self.file.create_entity('IfcApplication', **{
            'ApplicationDeveloper': developer_organisation,
            'Version': version,
            'ApplicationFullName': 'BlenderBIM',
            'ApplicationIdentifier': 'BlenderBIM'
        })
        self.owner_history = self.file.create_entity('IfcOwnerHistory', **{
            'OwningUser': person_and_organisation,
            'OwningApplication': application,
            'State': 'READWRITE',
            'ChangeAction': 'NOTDEFINED',
            'LastModifiedDate': int(time.time()),
            'LastModifyingUser': person_and_organisation,
            'LastModifyingApplication': application,
            'CreationDate': int(time.time()) # illegal, but better than nothing ...
        })

    def create_units(self):
        for unit_type, data in self.ifc_parser.units.items():
            if data['is_metric']:
                data['ifc'] = self.create_metric_unit(unit_type, data)
            else:
                data['ifc'] = self.create_imperial_unit(unit_type, data)
        self.file.createIfcUnitAssignment([u['ifc'] for u in self.ifc_parser.units.values()])

    def create_metric_unit(self, unit_type, data):
        type_prefix = ''
        if unit_type == 'area':
            type_prefix = 'SQUARE_'
        elif unit_type == 'volume':
            type_prefix = 'CUBIC_'
        return self.file.createIfcSIUnit(
            None,
            '{}UNIT'.format(unit_type.upper()),
            SIUnitHelper.get_prefix(data['raw']),
            type_prefix + SIUnitHelper.get_unit_name(data['raw'])
        )

    def create_imperial_unit(self, unit_type, data):
        if unit_type == 'length':
            dimensional_exponents = self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
            name_prefix = ''
        elif unit_type == 'area':
            dimensional_exponents = self.file.createIfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
            name_prefix = 'square'
        elif unit_type == 'volume':
            dimensional_exponents = self.file.createIfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
            name_prefix = 'cubic'
        si_unit = self.file.createIfcSIUnit(
            None,
            '{}UNIT'.format(unit_type.upper()),
            None,
            '{}METRE'.format(name_prefix.upper() + '_' if name_prefix else '')
        )
        if data['raw'] == 'INCHES':
            name = '{}inch'.format(name_prefix + ' ' if name_prefix else '')
        elif data['raw'] == 'FEET':
            name = '{}foot'.format(name_prefix + ' ' if name_prefix else '')
        value_component = self.file.create_entity(
            'IfcReal',
            **{'wrappedValue': SIUnitHelper.si_conversions[name]}
        )
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)
        return self.file.createIfcConversionBasedUnit(
            dimensional_exponents,
            '{}UNIT'.format(unit_type.upper()),
            name,
            conversion_factor
        )

    def create_people(self):
        for person in self.ifc_parser.people:
            data = person['raw'].copy()
            if data['Roles']:
                data['Roles'] = self.create_roles(data['Roles'])
            if data['Addresses']:
                data['Addresses'] = self.create_addresses(data['Addresses'])
            person['ifc'] = self.file.create_entity('IfcPerson', **data)

    def create_organisations(self):
        for organisation in self.ifc_parser.organisations:
            data = organisation['raw'].copy()
            if data['Roles']:
                data['Roles'] = self.create_roles(data['Roles'])
            if data['Addresses']:
                data['Addresses'] = self.create_addresses(data['Addresses'])
            organisation['ifc'] = self.file.create_entity('IfcOrganization', **data)

    def create_roles(self, roles):
        results = []
        for role in roles:
            results.append(self.file.create_entity('IfcActorRole', **role))
        return results

    def create_addresses(self, addresses):
        results = []
        for address in addresses:
            is_postal_address = False
            for key in ['InternalLocation', 'AddressLines', 'PostalBox', 'Town',
                        'Region', 'PostalCode', 'Country']:
                if key in address:
                    is_postal_address = True
            if is_postal_address:
                results.append(self.file.create_entity('IfcPostalAddress', **address))
            else:
                results.append(self.file.create_entity('IfcTelecomAddress', **address))
        return results

    def create_library_information(self):
        information = self.ifc_parser.library_information
        if not information:
            return
        information['attributes']['Publisher'] = self.owner_history.OwningUser
        information['ifc'] = self.file.create_entity('IfcLibraryInformation',
                **information['attributes'])
        self.file.createIfcRelAssociatesLibrary(
                ifcopenshell.guid.new(),
                self.owner_history,
                information['attributes']['Name'],
                information['attributes']['Description'],
                [self.ifc_parser.project['ifc']],
                information['ifc'])

    def create_document_information(self):
        for information in self.ifc_parser.document_information.values():
            information['ifc'] = self.file.create_entity(
                'IfcDocumentInformation', **information['attributes'])

    def create_document_references(self):
        for reference in self.ifc_parser.document_references.values():
            if reference['referenced_document'] \
                    and reference['referenced_document'] in self.ifc_parser.document_information:
                reference['attributes']['ReferencedDocument'] = self.ifc_parser.document_information[reference['referenced_document']]['ifc']
            reference['ifc'] = self.file.create_entity(
                'IfcDocumentReference', **reference['attributes'])
            self.file.createIfcRelAssociatesDocument(
                ifcopenshell.guid.new(), None, None, None,
                [self.ifc_parser.project['ifc']], reference['ifc'])

    def create_classifications(self):
        for classification in self.ifc_parser.classifications.values():
            classification['ifc'] = self.file.add(classification['raw_element'])
            self.file.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(), None, None, None,
                [self.ifc_parser.project['ifc']], classification['ifc'])

    def create_classification_references(self):
        for reference in self.ifc_parser.classification_references.values():
            reference['ifc'] = self.file.add(reference['raw_element'])

    def create_objectives(self):
        for objective in self.ifc_parser.objectives.values():
            objective['ifc'] = self.file.create_entity(
                'IfcObjective', **objective['attributes'])

    def create_psets(self):
        for pset in self.ifc_parser.psets.values():
            properties = self.create_pset_properties(pset)
            if not properties:
                continue
            pset['attributes'].update({
                'GlobalId': ifcopenshell.guid.new(),
                'OwnerHistory': self.owner_history,
                'HasProperties': properties
            })
            pset['ifc'] = self.file.create_entity('IfcPropertySet', **pset['attributes'])

    def create_material_psets(self, material):
        for pset_dir in material['raw'].BIMMaterialProperties.psets:
            for name, properties in self.ifc_parser.material_psets[pset_dir.name].items():
                self.file.create_entity('IfcMaterialProperties', **{
                    'Name': name,
                    'Description': pset_dir.name,
                    'Properties': self.create_pset_properties(properties),
                    'Material': material['ifc']
                })

    def create_qto_properties(self, qto):
        if qto['attributes']['Name'] in schema.ifc.qtos:
            return self.create_templated_qto_properties(qto)
        return self.create_custom_qto_properties(qto)

    def create_pset_properties(self, pset):
        if pset['attributes']['Name'] in schema.ifc.psets:
            return self.create_templated_pset_properties(pset)
        return self.create_custom_pset_properties(pset)

    def create_custom_pset_properties(self, pset):
        properties = []
        for key, value in pset['raw'].items():
            properties.append(
                self.file.create_entity('IfcPropertySingleValue', **{
                    'Name': key,
                    'NominalValue': self.file.create_entity('IfcLabel', value)
                }))
        return properties

    def create_custom_qto_properties(self, qto):
        properties = []
        for key, value in qto['raw'].items():
            if 'Area' in key:
                quantity_type = 'Area'
            elif 'Volume' in key:
                quantity_type = 'Volume'
            else:
                quantity_type = 'Length'
            properties.append(
                self.file.create_entity(f'IfcQuantity{quantity_type}', **{
                    'Name': key,
                    f'{quantity_type}Value': float(value)
                }))
        return properties

    def create_templated_pset_properties(self, pset):
        properties = []
        templates = schema.ifc.psets[pset['attributes']['Name']]['HasPropertyTemplates']
        for name, data in templates.items():
            if name not in pset['raw']:
                continue
            if data.TemplateType == 'P_SINGLEVALUE':
                if data.PrimaryMeasureType:
                    value_type = data.PrimaryMeasureType
                else:
                    # The IFC spec is missing some, so we provide a fallback
                    value_type = 'IfcLabel'
                nominal_value = self.file.create_entity(
                    value_type,
                    self.cast_to_base_type(value_type, pset['raw'][name]))
                properties.append(
                    self.file.create_entity('IfcPropertySingleValue', **{
                        'Name': name,
                        'NominalValue': nominal_value
                    }))
        invalid_pset_keys = [k for k in pset['raw'].keys() if k not in templates.keys()]
        if invalid_pset_keys:
            self.ifc_export_settings.logger.error(
                'One or more properties were invalid in the pset {}/{}: {}'.format(
                    pset['attributes']['Name'],
                    pset['attributes']['Description'],
                    invalid_pset_keys))
        return properties

    def create_templated_qto_properties(self, qto):
        properties = []
        templates = schema.ifc.qtos[qto['attributes']['Name']]['HasPropertyTemplates']
        for name, data in templates.items():
            if name not in qto['raw']:
                continue
            if data.TemplateType[0:2] == 'Q_':
                value_basename = data.TemplateType[2:].title()
                value_name = f'{value_basename}Value'
                class_name = f'IfcQuantity{value_basename}'
                properties.append(
                    self.file.create_entity(class_name, **{
                        'Name': name,
                        value_name: float(qto['raw'][name])
                    }))
        invalid_qto_keys = [k for k in qto['raw'].keys() if k not in templates.keys()]
        if invalid_qto_keys:
            self.ifc_export_settings.logger.error(
                'One or more properties were invalid in the qto {}/{}: {}'.format(
                    qto['attributes']['Name'],
                    qto['attributes']['Description'],
                    invalid_qto_keys))
        return properties

    def cast_to_base_type(self, var_type, value):
        if var_type not in schema.ifc.type_map:
            return value
        elif schema.ifc.type_map[var_type] == 'float':
            return float(value)
        elif schema.ifc.type_map[var_type] == 'integer':
            return int(value)
        elif schema.ifc.type_map[var_type] == 'bool':
            return True if value.lower() in ['1', 't', 'true', 'yes', 'y', 'uh-huh'] else False
        return str(value)

    def create_rep_context(self):
        self.ifc_rep_context = {}
        for context in self.ifc_export_settings.context_tree:
            if context['name'] == 'Model':
                self.ifc_rep_context['Model'] = {
                    'ifc': self.file.createIfcGeometricRepresentationContext(
                        None, 'Model', 3, 1.0E-05, self.origin)}
            elif context['name'] == 'Plan':
                self.ifc_rep_context['Plan'] = {
                    'ifc': self.file.createIfcGeometricRepresentationContext(
                        None, 'Plan', 2, 1.0E-05, self.origin)}
            for subcontext in context['subcontexts']:
                self.ifc_rep_context[context['name']][subcontext['name']] = {}
                for target_view in subcontext['target_views']:
                    self.ifc_rep_context[context['name']][subcontext['name']][target_view] = {
                        'ifc': self.file.createIfcGeometricRepresentationSubContext(
                            subcontext['name'], context['name'], None, None, None, None,
                            self.ifc_rep_context[context['name']]['ifc'], None, target_view, None)}

    def create_project(self):
        self.ifc_parser.project['attributes'].update({
            'RepresentationContexts': [c['ifc'] for c in self.ifc_rep_context.values()],
            'UnitsInContext': self.file.by_type("IfcUnitAssignment")[0]
        })
        self.ifc_parser.project['ifc'] = self.file.create_entity(
            self.ifc_parser.project['class'], **self.ifc_parser.project['attributes'])

    def create_libraries(self):
        for library in self.ifc_parser.libraries:
            library['ifc'] = self.file.create_entity(library['class'], **library['attributes'])
        libraries = [l['ifc'] for l in self.ifc_parser.libraries]
        if libraries:
            self.file.createIfcRelDeclares(
                ifcopenshell.guid.new(), self.owner_history,
                None, None,
                self.ifc_parser.project['ifc'], libraries)

    def create_map_conversion(self):
        if not self.ifc_parser.map_conversion:
            return
        self.create_target_crs()
        # TODO should this be hardcoded?
        self.ifc_parser.map_conversion['attributes']['SourceCRS'] = self.ifc_rep_context['Model']['ifc']
        self.ifc_parser.map_conversion['attributes']['TargetCRS'] = self.ifc_parser.target_crs['ifc']
        self.ifc_parser.map_conversion['ifc'] = self.file.create_entity(
            'IfcMapConversion',
            **self.ifc_parser.map_conversion['attributes']
        )

    def create_target_crs(self):
        self.ifc_parser.target_crs['attributes']['MapUnit'] = self.file.createIfcSIUnit(
            None,
            'LENGTHUNIT',
            SIUnitHelper.get_prefix(self.ifc_parser.target_crs['attributes']['MapUnit']),
            SIUnitHelper.get_unit_name(self.ifc_parser.target_crs['attributes']['MapUnit'])
        )
        self.ifc_parser.target_crs['ifc'] = self.file.create_entity(
            'IfcProjectedCRS',
            **self.ifc_parser.target_crs['attributes']
        )

    def create_type_products(self):
        for product in self.ifc_parser.type_products:
            self.cast_attributes(product['class'], product['attributes'])

            product['attributes'].update({
                'OwnerHistory': self.owner_history,  # TODO: unhardcode
                'RepresentationMaps': self.get_product_shape(product)
            })

            # TODO: re-implement psets, relationships, door/window properties

            try:
                product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
            except RuntimeError as e:
                self.ifc_export_settings.logger.error(
                    'The product "{}/{}" could not be created: {}'.format(
                        product['class'],
                        product['attributes']['Name'],
                        e.args)
                )

    def add_predefined_attributes_to_type_product(self, product, attributes):
        self.create_predefined_attributes(attributes)
        product['attributes'].setdefault('HasPropertySets', [])
        for attribute in attributes:
            product['attributes']['HasPropertySets'].append(attribute['ifc'])

    def create_predefined_attributes(self, attributes):
        for attribute in attributes:
            attribute['ifc'] = self.file.create_entity(
                attribute['pset_name'],
                **{k: float(v) if v.replace('.', '', 1).isdigit() else v
                for k, v in attribute['raw'].items()}
            )

    def relate_definitions_to_contexts(self):
        for library in self.ifc_parser.libraries:
            self.file.createIfcRelDeclares(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                library['ifc'],
                [self.ifc_parser.type_products[t]['ifc'] for t in library['rel_declares_type_products']])

    def relate_objects_to_objects(self):
        for relating_object, related_objects_reference in self.ifc_parser.rel_aggregates.items():
            relating_object = self.ifc_parser.products[relating_object]
            if related_objects_reference not in self.ifc_parser.aggregates:
                continue
            related_objects = [self.ifc_parser.products[o]['ifc']
                               for o in self.ifc_parser.aggregates[related_objects_reference]]
            self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(), self.owner_history, relating_object['attributes']['Name'], None,
                relating_object['ifc'], related_objects)

    def create_spatial_structure_elements(self, element_tree, relating_object=None):
        if relating_object == None:
            relating_object = self.ifc_parser.project['ifc']
            placement_rel_to = None
        else:
            placement_rel_to = relating_object.ObjectPlacement

        related_objects = []
        for node in element_tree:
            element = self.ifc_parser.spatial_structure_elements[node['reference']]

            placement = self.file.createIfcLocalPlacement(
                placement_rel_to, self.get_relative_placement(element, placement_rel_to))

            self.cast_attributes(element['class'], element['attributes'])
            element['attributes'].update({
                'OwnerHistory': self.owner_history,  # TODO: unhardcode
                'ObjectPlacement': placement,
                'Representation': self.get_product_shape(element)
            })
            element['ifc'] = self.file.create_entity(element['class'], **element['attributes'])
            related_objects.append(element['ifc'])
            self.create_spatial_structure_elements(node['children'], element['ifc'])
        if related_objects:
            self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                self.owner_history, None, None, relating_object, related_objects)

    def get_relative_placement(self, element, placement_rel_to):
        if placement_rel_to:
            relating_object_matrix = self.get_local_placement(placement_rel_to)
        else:
            relating_object_matrix = Matrix()
        z = Vector(element['up_axis'])
        x = Vector(element['forward_axis'])
        o = Vector(element['location'])
        object_matrix = self.a2p(o, z, x)
        relative_placement_matrix = relating_object_matrix.inverted() @ object_matrix
        return self.create_ifc_axis_2_placement_3d(
            relative_placement_matrix.translation,
            self.get_axis(relative_placement_matrix, 2),
            self.get_axis(relative_placement_matrix, 0))

    def get_axis(self, matrix, axis):
        return matrix.col[axis].to_3d().normalized()

    def get_local_placement(self, plc):
        if plc.PlacementRelTo is None:
            parent = Matrix()
        else:
            parent = self.get_local_placement(plc.PlacementRelTo)
        return parent @ self.get_axis2placement(plc.RelativePlacement)

    def a2p(self, o, z, x):
        y = z.cross(x)
        r = Matrix((x, y, z, o))
        r.resize_4x4()
        r.transpose()
        return r

    def get_axis2placement(self, plc):
        z = Vector(plc.Axis.DirectionRatios if plc.Axis else (0,0,1))
        x = Vector(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0))
        o = plc.Location.Coordinates
        return self.a2p(o,z,x)

    def create_groups(self):
        for group in self.ifc_parser.groups:
            group['ifc'] = self.file.create_entity(group['class'], **group['attributes'])
            self.file.createIfcRelDeclares(ifcopenshell.guid.new(),
                self.owner_history, None, None, self.ifc_parser.project['ifc'], [group['ifc']])

    def create_styled_items(self):
        for styled_item in self.ifc_parser.styled_items:
            product = self.ifc_parser.products[
                self.ifc_parser.get_product_index_from_raw_name(
                    styled_item['related_product_name'])]
            material_slots = {}
            if product['ifc'].Representation:
                for representation in product['ifc'].Representation.Representations:
                    for mapped_item in representation.Items:
                        items = mapped_item[0].MappedRepresentation.Items
                        for i, item in enumerate(items):
                            material_slots[product['raw'].material_slots[i].name] = item
            for styled_item_name, representation_item in material_slots.items():
                if styled_item_name == styled_item['attributes']['Name']:
                    styled_item['ifc'] = self.create_styled_item(styled_item, representation_item)

    def create_styled_item(self, item, representation_item=None):
        styles = []
        styles.append(self.create_surface_style_rendering(item))
        if item['raw'].BIMMaterialProperties.is_external:
            styles.append(self.file.create_entity('IfcExternallyDefinedSurfaceStyle',
                **self.get_material_external_definition(item['raw'])))
        # Name is filled out because Revit treats this incorrectly as the material name
        surface_style = self.file.createIfcSurfaceStyle(item['attributes']['Name'], 'BOTH', styles)
        if self.ifc_export_settings.should_use_presentation_style_assignment:
            surface_style = self.file.createIfcPresentationStyleAssignment([surface_style])
        return self.file.createIfcStyledItem(representation_item, [surface_style], item['attributes']['Name'])

    def create_presentation_layer_assignments(self):
        for name, assigned_items in self.ifc_parser.presentation_layer_assignments.items():
            self.file.createIfcPresentationLayerAssignment(
                name, None, [i['ifc'].MappedRepresentation for i in assigned_items], None)

    def create_materials(self):
        for material in self.ifc_parser.materials.values():
            styled_item = self.create_styled_item(material)
            styled_representation = self.file.createIfcStyledRepresentation(
                self.ifc_rep_context['Model']['Body']['MODEL_VIEW']['ifc'], None, None, [styled_item])
            material['ifc'] = self.file.createIfcMaterial(material['raw'].name, None, None)
            self.create_material_psets(material)
            self.file.createIfcMaterialDefinitionRepresentation(
                material['raw'].name, None, [styled_representation], material['ifc'])
            if material['material_type'] == 'IfcMaterial':
                continue
            material_type = material['material_type'][0:-3]
            self.cast_attributes(material_type, material['attributes'])
            material['attributes']['Material'] = material['ifc']
            if material_type == 'IfcMaterialProfile':
                material['attributes']['Profile'] = self.create_material_profile(material)
            material['part_ifc'] = self.file.create_entity(material_type,
                **material['attributes'])

    def create_material_profile(self, material):
        ifc_class = material['raw'].BIMMaterialProperties.profile_def
        attributes = {a.name: a.string_value for a in material['raw'].BIMMaterialProperties.profile_attributes}
        self.cast_attributes(ifc_class, attributes)
        return self.file.create_entity(ifc_class, **attributes)

    def cast_attributes(self, ifc_class, attributes):
        for key, value in attributes.items():
            edge_case_attribute = self.cast_edge_case_attribute(ifc_class, key, value)
            if edge_case_attribute:
                attributes[key] = edge_case_attribute
                continue

            complex_attribute = self.cast_complex_attribute(ifc_class, key, value)
            if complex_attribute:
                attributes[key] = complex_attribute
                continue

            var_type = self.get_product_attribute_type(ifc_class, key)
            if var_type is None:
                continue
            attributes[key] = self.cast_to_base_type(var_type, value)

    def cast_edge_case_attribute(self, ifc_class, key, value):
        if key == 'RefLatitude' or key == 'RefLongitude':
            return self.dd2dms(value)

    # TODO: migrate to ifcopenshell.util
    def dd2dms(self, dd):
        dd = float(dd)
        sign = 1 if dd >= 0 else -1
        dd = abs(dd)
        minutes, seconds = divmod(dd*3600, 60)
        degrees, minutes = divmod(minutes, 60)
        if dd < 0:
            degrees = -degrees
        return (int(degrees) * sign, int(minutes) * sign, int(seconds) * sign)

    def create_surface_style_rendering(self, styled_item):
        surface_colour = self.create_colour_rgb(styled_item['raw'].diffuse_color)
        rendering_attributes = {'SurfaceColour': surface_colour, 'ReflectanceMethod': 'NOTDEFINED'}
        rendering_attributes.update(self.get_rendering_attributes(styled_item['raw']))
        return self.file.create_entity('IfcSurfaceStyleRendering', **rendering_attributes)

    def get_rendering_attributes(self, material):
        if not hasattr(material.node_tree, 'nodes') \
                or 'Principled BSDF' not in material.node_tree.nodes:
            return {}
        bsdf = material.node_tree.nodes['Principled BSDF']
        return {
            'Transparency': (bsdf.inputs['Alpha'].default_value - 1) * -1,
            'DiffuseColour': self.create_colour_rgb(bsdf.inputs['Base Color'].default_value)
        }

    def get_material_external_definition(self, material):
        return {
            'Location': material.BIMMaterialProperties.location,
            'Identification': material.BIMMaterialProperties.identification if material.BIMMaterialProperties.identification else material.name,
            'Name': material.BIMMaterialProperties.name if material.BIMMaterialProperties.name else material.name
        }

    def create_colour_rgb(self, colour):
        return self.file.createIfcColourRgb(None, colour[0], colour[1], colour[2])

    def create_representations(self):
        for representation in self.ifc_parser.representations.values():
            representation['ifc'] = self.create_representation(representation)

    def create_products(self):
        for product in self.ifc_parser.products:
            self.create_product(product)

    def create_qtos(self):
        # TODO: re-introduce calculated quantities
        for qto in self.ifc_parser.qtos.values():
            properties = self.create_qto_properties(qto)
            if not properties:
                continue
            qto['attributes'].update({
                'GlobalId': ifcopenshell.guid.new(),
                'OwnerHistory': self.owner_history,
                'Quantities': properties
            })
            qto['ifc'] = self.file.create_entity('IfcElementQuantity', **qto['attributes'])

    def create_product(self, product):
        if product['relating_structure']:
            placement_rel_to = self.ifc_parser.spatial_structure_elements[product['relating_structure']][
                'ifc'].ObjectPlacement
        elif product['relating_host'] is not None:
            placement_rel_to = self.ifc_parser.products[product['relating_host']]['ifc'].ObjectPlacement
        else:
            placement_rel_to = None

        if product['has_scale']:
            # Omission of the relative placement here is not as per implementer agreements
            placement = self.file.createIfcLocalPlacement(None, self.origin)
        else:
            placement = self.file.createIfcLocalPlacement(placement_rel_to,
                self.get_relative_placement(product, placement_rel_to))

        self.cast_attributes(product['class'], product['attributes'])

        product['attributes'].update({
            'OwnerHistory': self.owner_history,  # TODO: unhardcode
            'ObjectPlacement': placement,
            'Representation': self.get_product_shape(product)
        })

        if product['has_boundary_condition']:
            ifc_class = product['boundary_condition_class']
            attributes = product['boundary_condition_attributes']
            for key, value in attributes.items():
                if value == 'True' or value == 'False':
                    attributes[key] = bool(value)
                else:
                    attributes[key] = float(value)
            self.cast_attributes(ifc_class, attributes)
            boundary_condition = self.file.create_entity(ifc_class, **attributes)
            product['attributes']['AppliedCondition'] = boundary_condition

        try:
            product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
        except RuntimeError as e:
            self.ifc_export_settings.logger.error(
                'The product "{}/{}" could not be created: {}'.format(
                    product['class'],
                    product['attributes']['Name'],
                    e.args)
            )

    def get_product_attribute_type(self, product_class, attribute_name):
        element_schema = schema.ifc.elements[product_class]
        for a in element_schema['attributes']:
            if a['name'] == attribute_name:
                return a['type']
        if element_schema['parent'] in schema.ifc.elements:
            return self.get_product_attribute_type(element_schema['parent'], attribute_name)

    def cast_complex_attribute(self, product_class, attribute_name, attribute_value):
        element_schema = schema.ifc.elements[product_class]
        for a in element_schema['complex_attributes']:
            if a['name'] == attribute_name:
                if not a['is_select']:
                    return a['type']
                for select_type in a['select_types']:
                    try:
                        return self.file.create_entity(select_type, attribute_value)
                    except:
                        pass

    def get_product_shape(self, product):
        try:
            representations = self.get_product_shape_representations(product)
            if representations:
                return self.file.createIfcProductDefinitionShape(None, None, representations)
        except:
            pass
        return None

    def get_product_shape_representations(self, product):
        results = []
        for representation_name in product['representations']:
            results.append(self.get_product_mapped_geometry(product, representation_name))
        return results

    def get_product_mapped_geometry(self, product, representation_name):
        mapping_source = self.ifc_parser.representations[representation_name]['ifc']
        shape_representation = mapping_source.MappedRepresentation
        if product['has_scale']:
            if not product['has_mirror']:
                product['scale'] = Vector((
                    abs(product['scale'].x),
                    abs(product['scale'].y),
                    abs(product['scale'].z)
                ))
            mapping_target = self.file.createIfcCartesianTransformationOperator3DnonUniform(
                    self.create_direction(product['forward_axis']),
                    self.create_direction(product['right_axis']),
                    self.create_cartesian_point(
                        product['location'].x,
                        product['location'].y,
                        product['location'].z
                    ),
                    product['scale'].x,
                    self.create_direction(product['up_axis']),
                    product['scale'].y,
                    product['scale'].z)
        else:
            mapping_target = self.file.createIfcCartesianTransformationOperator3D(
                    self.create_direction(Vector((1, 0, 0))),
                    self.create_direction(Vector((0, 1, 0))),
                    self.create_cartesian_point(0, 0, 0),
                    1, self.create_direction(Vector((0, 0, 1))))
        mapped_item = self.file.createIfcMappedItem(mapping_source, mapping_target)
        return self.file.createIfcShapeRepresentation(
                shape_representation.ContextOfItems,
                shape_representation.RepresentationIdentifier,
                'MappedRepresentation',
                [mapped_item])

    def calculate_quantities(self, qto_name, obj):
        quantities = []
        for index, vg in enumerate(obj.vertex_groups):
            if qto_name not in vg.name:
                continue
            if 'length' in vg.name.lower():
                quantity = float(self.qto_calculator.get_length(obj, index))
                quantities.append(self.file.createIfcQuantityLength(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['length']['ifc'], quantity))
            elif 'area' in vg.name.lower():
                quantity = float(self.qto_calculator.get_area(obj, index))
                quantities.append(self.file.createIfcQuantityArea(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['area']['ifc'], quantity))
            elif 'volume' in vg.name.lower():
                quantity = float(self.qto_calculator.get_volume(obj, index))
                quantities.append(self.file.createIfcQuantityVolume(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['volume']['ifc'], quantity))
            if not quantity:
                self.ifc_export_settings.logger.warning('The calculated quantity {} for {} is zero.'.format(
                    vg.name, obj.name))
        return quantities

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.create_cartesian_point(point.x, point.y, point.z),
            self.file.createIfcDirection((up.x, up.y, up.z)),
            self.file.createIfcDirection((forward.x, forward.y, forward.z)))

    def create_representation(self, representation):
        self.ifc_vertices = []
        self.ifc_edges = []
        if representation['context'] == 'Model':
            return self.create_model_representation(representation)
        elif representation['context'] == 'Plan':
            return self.create_plan_representation(representation)
        elif representation['context'] == 'NotDefined':
            return self.create_variable_representation(representation)

    def create_model_representation(self, representation):
        if representation['subcontext'] == 'Annotation':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_geometric_set_representation(representation))
        elif representation['subcontext'] == 'Axis':
            return self.file.createIfcRepresentationMap(
                self.origin, self.create_curve3d_representation(representation))
        elif representation['subcontext'] == 'Body':
            return self.create_variable_representation(representation)
        elif representation['subcontext'] == 'Box':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_box_representation(representation))
        elif representation['subcontext'] == 'Clearance':
            return self.create_variable_representation(representation)
        elif representation['subcontext'] == 'CoG':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_cog_representation(representation))
        elif representation['subcontext'] == 'FootPrint':
            return self.create_variable_representation(representation)
        elif representation['subcontext'] == 'Reference':
            if representation['target_view'] == 'GRAPH_VIEW':
                return self.file.createIfcRepresentationMap(
                    self.origin, self.create_structural_reference_representation(representation))
        elif representation['subcontext'] == 'Profile':
            return self.file.createIfcRepresentationMap(
                self.origin, self.create_curve3d_representation(representation))
        elif representation['subcontext'] == 'SurveyPoints':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_geometric_curve_set_representation(representation))

    def create_plan_representation(self, representation):
        if representation['subcontext'] == 'Annotation':
            if representation['is_text']:
                shape_representation = self.create_text_representation(representation)
            else:
                shape_representation = self.create_geometric_curve_set_representation(representation, is_2d=True)
                shape_representation.RepresentationType = 'Annotation2D'
            return self.file.createIfcRepresentationMap(self.origin, shape_representation)
        elif representation['subcontext'] == 'Axis':
            return self.file.createIfcRepresentationMap(
                self.origin, self.create_curve2d_representation(representation))
        elif representation['subcontext'] == 'Body':
            pass
        elif representation['subcontext'] == 'Box':
            pass
        elif representation['subcontext'] == 'Clearance':
            pass
        elif representation['subcontext'] == 'CoG':
            pass
        elif representation['subcontext'] == 'FootPrint':
            if representation['target_view'] in ['PLAN_VIEW', 'REFLECTED_PLAN_VIEW']:
                return self.file.createIfcRepresentationMap(self.origin,
                        self.create_geometric_curve_set_representation(representation, is_2d=True))
        elif representation['subcontext'] == 'Reference':
            pass
        elif representation['subcontext'] == 'Profile':
            pass
        elif representation['subcontext'] == 'SurveyPoints':
            pass

    def create_variable_representation(self, representation):
        if representation['is_wireframe']:
            return self.file.createIfcRepresentationMap(self.origin,
                self.create_wireframe_representation(representation))
        elif representation['is_curve']:
            return self.file.createIfcRepresentationMap(self.origin,
                self.create_curve_representation(representation))
        elif representation['is_swept_solid']:
            return self.file.createIfcRepresentationMap(self.origin,
                self.create_swept_solid_representation(representation))
        elif representation['is_point_cloud']:
            return self.file.createIfcRepresentationMap(self.origin,
                self.create_point_cloud_representation(representation))
        return self.file.createIfcRepresentationMap(self.origin,
                self.create_solid_representation(representation))

    def create_box_representation(self, representation):
        obj = representation['raw_object']
        bounding_box = self.file.createIfcBoundingBox(
            self.create_cartesian_point(
                obj.bound_box[0][0],
                obj.bound_box[0][1],
                obj.bound_box[0][2]
            ),
            obj.dimensions[0],
            obj.dimensions[1],
            obj.dimensions[2]
        )
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'BoundingBox', [bounding_box])

    def create_cog_representation(self, representation):
        mesh = representation['raw']
        cog = self.create_cartesian_point(
            mesh.vertices[0].co.x, mesh.vertices[0].co.y, mesh.vertices[0].co.z)
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'],
            'BoundingBox',
            [cog])

    def create_text_representation(self, representation):
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'],
            'Annotation2D',
            [self.create_text(representation['raw'])])

    def create_wireframe_representation(self, representation):
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'],
            'Curve',
            self.create_curves(representation['raw']))

    def create_geometric_set_representation(self, representation, is_2d=False):
        geometric_curve_set = self.file.createIfcGeometricSet(self.create_curves(representation['raw'], is_2d=is_2d))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'GeometricSet', [geometric_curve_set])

    def create_geometric_curve_set_representation(self, representation, is_2d=False):
        geometric_curve_set = self.file.createIfcGeometricCurveSet(self.create_curves(representation['raw'], is_2d=is_2d))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'GeometricCurveSet', [geometric_curve_set])

    # https://medium.com/@behreajj/scripting-curves-in-blender-with-python-c487097efd13
    # https://blender.stackexchange.com/questions/30597/python-up-vector-math-for-curve
    def bezier_tangent(self, pt0=Vector(), pt1=Vector(), pt2=Vector(), pt3=Vector(), step=0.5):
        # Return early if step is out of bounds [0, 1].
        if step <= 0.0:
            return pt1 - pt0
        if step >= 1.0:
            return pt3 - pt2

        # Find coefficients.
        u = 1.0 - step
        ut6 = u * step * 6.0
        tsq3 = step * step * 3.0
        usq3 = u * u * 3.0

        # Find tangent and return.
        return (pt1 - pt0) * usq3 + (pt2 - pt1) * ut6 + (pt3 - pt2) * tsq3

    def create_curve3d_representation(self, representation):
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Curve3D',
            self.create_curves(representation['raw']))

    def create_curve2d_representation(self, representation):
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Curve2D',
            self.create_curves(representation['raw'], is_2d=True))

    def create_structural_reference_representation(self, representation):
        if representation['raw_object'].type == 'EMPTY':
            return self.file.createIfcTopologyRepresentation(
                self.ifc_rep_context[representation['context']][representation['subcontext']][
                    representation['target_view']]['ifc'],
                representation['subcontext'], 'Vertex',
                [self.create_vertex_point(Vector((0, 0, 0)))])
        return self.file.createIfcTopologyRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Edge',
            [self.create_edge(representation['raw'])])

    def create_curve_representation(self, representation):
        # TODO: support unclosed surfaces
        swept_area = self.file.createIfcArbitraryClosedProfileDef('AREA', None,
            self.create_curves(representation['raw'].bevel_object.data)[0])
        swept_area_solids = []
        for spline in representation['raw'].splines:
            points = self.get_spline_points(spline)
            if not points:
                continue
            # Intuitively, the direction below is reversed, but apparently
            # Blender likes to extrude down (opposite of IFC) natively.
            direction = (points[0].co - points[1].co).xyz
            unit_direction = direction.normalized()

            # This can be used in the future when dealing with non vector curves
            # curr_point = points[0]
            # next_point = points[1]
            # j_percent = 0
            # direction = self.bezier_tangent(
            #    pt0=curr_point.co,
            #    pt1=curr_point.handle_right,
            #    pt2=next_point.handle_left,
            #    pt3=next_point.co,
            #    step=j_percent)
            tilt_matrix = Matrix.Rotation(points[0].tilt, 4, 'Z')
            x_axis = unit_direction.to_track_quat('-Y', 'Z') @ Vector((1, 0, 0)) @ tilt_matrix
            position = self.create_ifc_axis_2_placement_3d(
                points[1].co, unit_direction, x_axis)
            swept_area_solids.append(self.file.createIfcExtrudedAreaSolid(
                swept_area, position,
                self.file.createIfcDirection((0., 0., 1.)),
                self.convert_si_to_unit(direction.length)))
        # TODO: support other types of swept areas
        # swept_area_solid = self.file.createIfcFixedReferenceSweptAreaSolid(
        #    swept_area, self.origin, #    self.create_curves(representation['raw'])[0],
        #    0., 1., self.file.createIfcDirection((0.0, -1.0, 0.0)))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'AdvancedSweptSolid',
            swept_area_solids)

    def create_vertex_point(self, point):
        return self.file.createIfcVertexPoint(
            self.create_cartesian_point(point.x, point.y, point.z))

    def get_spline_points(self, spline):
        return spline.bezier_points if spline.bezier_points else spline.points

    def create_edge(self, curve):
        points = self.get_spline_points(curve.splines[0])
        if not points:
            return
        return self.file.createIfcEdge(
            self.create_vertex_point(points[0].co),
            self.create_vertex_point(points[1].co))

    def create_text(self, text):
        if text.align_y in ['TOP_BASELINE', 'BOTTOM_BASELINE', 'BOTTOM']:
            y = 'bottom'
        elif text.align_y == 'CENTER':
            y = 'middle'
        elif text.align_y == 'TOP':
            y = 'top'

        if text.align_x == 'LEFT':
            x = 'left'
        elif text.align_x == 'CENTER':
            x = 'middle'
        elif text.align_x == 'RIGHT':
            x = 'right'

        # TODO: Planar extent right now is wrong ...
        return self.file.createIfcTextLiteralWithExtent(text.body, self.origin,
            'RIGHT', self.file.createIfcPlanarExtent(1000, 1000), f'{y}-{x}')

    def create_curves(self, curve, is_2d=False):
        if isinstance(curve, bpy.types.Mesh):
            return self.create_curves_from_mesh(curve, is_2d=is_2d)
        elif isinstance(curve, bpy.types.Curve):
            return self.create_curves_from_curve(curve, is_2d=is_2d)

    def create_curves_from_mesh(self, mesh, is_2d=False):
        self.create_vertices(mesh.vertices, is_2d=is_2d)
        edges = list(mesh.edges)
        loop_vertices = []
        loops = []
        # Not a fast algorithm, but easy
        while edges:
            for i, edge in enumerate(edges):
                if edge.vertices[0] in loop_vertices \
                        and edge.vertices[1] in loop_vertices:
                    del edges[i]
            loop_vertex_indices = self.get_loop_from_edges(edges)
            loop_vertices.extend(loop_vertex_indices)
            loops.append(self.file.createIfcPolyline([
                self.ifc_vertices[i] for i in loop_vertex_indices]))
        return loops

    def create_curves_from_curve(self, curve, is_2d=False):
        results = []
        for spline in curve.splines:
            # TODO: support interpolated curves, not just polylines
            points = []
            for point in spline.bezier_points:
                if is_2d:
                    points.append(self.create_cartesian_point(
                        point.co.x, point.co.y))
                else:
                    points.append(self.create_cartesian_point(
                        point.co.x, point.co.y, point.co.z))
            for point in spline.points:
                if is_2d:
                    points.append(self.create_cartesian_point(
                        point.co.x, point.co.y))
                else:
                    points.append(self.create_cartesian_point(
                        point.co.x, point.co.y, point.co.z))
            if spline.use_cyclic_u:
                points.append(points[0])
            results.append(self.file.createIfcPolyline(points))
        return results

    def create_swept_solid_representation(self, representation):
        obj = representation['raw_object']
        mesh = representation['raw']
        items = []
        for swept_solid in mesh.BIMMeshProperties.swept_solids:
            extrusion_edge = self.get_edges_in_v_indices(obj, json.loads(swept_solid.extrusion))[0]

            inner_curves = []
            if swept_solid.inner_curves:
                for indices in json.loads(swept_solid.inner_curves):
                    loop = self.get_loop_from_v_indices(obj, indices)
                    curve_ucs = self.get_curve_profile_coordinate_system(obj, loop)
                    inner_curves.append(
                        self.create_polyline_from_loop(obj, loop, curve_ucs))

            outer_curve_loop = self.get_loop_from_v_indices(obj, json.loads(swept_solid.outer_curve))
            curve_ucs = self.get_curve_profile_coordinate_system(obj, outer_curve_loop)
            outer_curve = self.create_polyline_from_loop(obj, outer_curve_loop, curve_ucs)

            if inner_curves:
                curve = self.file.createIfcArbitraryProfileDefWithVoids('AREA', None,
                                                                        outer_curve, inner_curves)
            else:
                curve = self.file.createIfcArbitraryClosedProfileDef('AREA', None, outer_curve)

            direction = self.get_extrusion_direction(obj, outer_curve_loop, extrusion_edge, curve_ucs)
            unit_direction = direction.normalized()
            position = self.create_ifc_axis_2_placement_3d(
                curve_ucs['center'], curve_ucs['z_axis'], curve_ucs['x_axis'])

            items.append(self.file.createIfcExtrudedAreaSolid(
                curve, position, self.file.createIfcDirection((
                    unit_direction.x, unit_direction.y, unit_direction.z)),
                self.convert_si_to_unit(direction.length)))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'SweptSolid', items)

    def get_start_and_end_of_extrusion(self, profile_points, extrusion_edge):
        if extrusion_edge.vertices[0] in profile_points:
            return (extrusion_edge.vertices[0], extrusion_edge.vertices[1])
        return (extrusion_edge.vertices[1], extrusion_edge.vertices[0])

    def get_curve_profile_coordinate_system(self, obj, loop):
        profile_face = bpy.data.meshes.new('profile_face')
        profile_verts = [(
            obj.data.vertices[p].co.x,
            obj.data.vertices[p].co.y,
            obj.data.vertices[p].co.z
        ) for p in loop]
        profile_faces = [tuple(range(0, len(profile_verts)))]
        profile_face.from_pydata(profile_verts, [], profile_faces)
        center = profile_face.polygons[0].center
        x_axis = (obj.data.vertices[loop[0]].co - center).normalized()
        z_axis = profile_face.polygons[0].normal.normalized()
        y_axis = z_axis.cross(x_axis).normalized()
        matrix = Matrix((x_axis, y_axis, z_axis))
        matrix.normalize()
        return {
            'center': center,
            'x_axis': x_axis,
            'y_axis': y_axis,
            'z_axis': z_axis,
            'matrix': matrix.to_4x4() @ Matrix.Translation(-center)
        }

    def create_polyline_from_loop(self, obj, loop, curve_ucs):
        points = []
        for point in loop:
            transformed_point = curve_ucs['matrix'] @ obj.data.vertices[point].co
            points.append(self.create_cartesian_point(
                transformed_point.x, transformed_point.y))
        points.append(points[0])
        return self.file.createIfcPolyline(points)

    def get_extrusion_direction(self, obj, outer_curve_loop, extrusion_edge, curve_ucs):
        start, end = self.get_start_and_end_of_extrusion(outer_curve_loop, extrusion_edge)
        return curve_ucs['matrix'] @ (
                    curve_ucs['center'] + (obj.data.vertices[end].co - obj.data.vertices[start].co))

    def get_loop_from_v_indices(self, obj, indices):
        edges = self.get_edges_in_v_indices(obj, indices)
        loop = self.get_loop_from_edges(edges)
        loop.pop(-1)
        return loop

    def get_edges_in_v_indices(self, obj, indices):
        return [e for e in obj.data.edges
                if (e.vertices[0] in indices and e.vertices[1] in indices)]

    def get_loop_from_edges(self, edges):
        while edges:
            currentEdge = edges.pop()
            startVert = currentEdge.vertices[0]
            endVert = currentEdge.vertices[1]
            polyLine = [startVert, endVert]
            ok = 1
            while ok:
                ok = 0
                i = len(edges)
                while i:
                    i -= 1
                    ed = edges[i]
                    if ed.vertices[0] == endVert:
                        polyLine.append(ed.vertices[1])
                        endVert = polyLine[-1]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[1] == endVert:
                        polyLine.append(ed.vertices[0])
                        endVert = polyLine[-1]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[0] == startVert:
                        polyLine.insert(0, ed.vertices[1])
                        startVert = polyLine[0]
                        ok = 1
                        del edges[i]
                    elif ed.vertices[1] == startVert:
                        polyLine.insert(0, ed.vertices[0])
                        startVert = polyLine[0]
                        ok = 1
                        del edges[i]
            return polyLine

    def create_point_cloud_representation(self, representation):
        import space_view3d_point_cloud_visualizer as pcv
        if representation['raw'].uuid not in pcv.PCVManager.cache:
            return
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'PointCloud',
            [self.file.createIfcCartesianPointList3D(
                pcv.PCVManager.cache[representation['raw'].uuid]['points'].tolist())])

    def create_solid_representation(self, representation):
        mesh = representation['raw']
        if not representation['is_parametric']:
            mesh = representation['raw_object'].evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        self.create_vertices(mesh.vertices)
        ifc_faces = [None] * len(representation['raw_object'].material_slots)
        for i, value in enumerate(ifc_faces):
            ifc_faces[i] = []
        if not ifc_faces:
            ifc_faces = [[]]
        for polygon in mesh.polygons:
            ifc_faces[polygon.material_index].append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))
        items = [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(f)) for f in ifc_faces if f]
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Brep', items)

    def create_vertices(self, vertices, is_2d=False):
        if is_2d:
            for v in vertices:
                co = self.convert_si_to_unit(v.co)
                self.ifc_vertices.append(self.file.createIfcCartesianPoint((co[0], co[1])))
        else:
            self.ifc_vertices.extend(
                [self.file.createIfcCartesianPoint(self.convert_si_to_unit(v.co)) for v in vertices]
            )

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_direction(self, vector):
        return self.file.createIfcDirection((vector.x, vector.y, vector.z))

    def relate_objects_to_opening_elements(self):
        for relating_building_element, related_opening_elements in self.ifc_parser.rel_voids_elements.items():
            for related_opening_element in related_opening_elements:
                self.file.createIfcRelVoidsElement(
                    ifcopenshell.guid.new(), self.owner_history, None, None,
                    self.ifc_parser.products[relating_building_element]['ifc'],
                    self.ifc_parser.products[related_opening_element]['ifc']
                )

    def relate_opening_elements_to_fillings(self):
        for relating_opening_element, related_building_elements in self.ifc_parser.rel_fills_elements.items():
            for related_building_element in related_building_elements:
                self.file.createIfcRelFillsElement(
                    ifcopenshell.guid.new(), self.owner_history, None, None,
                    self.ifc_parser.products[relating_opening_element]['ifc'],
                    self.ifc_parser.products[related_building_element]['ifc']
                )

    def relate_objects_to_projection_elements(self):
        for relating_building_element, related_projection_elements in self.ifc_parser.rel_projects_elements.items():
            for related_projection_element in related_projection_elements:
                self.file.createIfcRelProjectsElement(
                    ifcopenshell.guid.new(), self.owner_history, None, None,
                    self.ifc_parser.products[relating_building_element]['ifc'],
                    self.ifc_parser.products[related_projection_element]['ifc']
                )

    def relate_elements_to_spatial_structures(self):
        for relating_structure, related_elements in self.ifc_parser.rel_contained_in_spatial_structure.items():
            self.file.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[e]['ifc'] for e in related_elements],
                self.ifc_parser.spatial_structure_elements[relating_structure]['ifc'])

    def relate_nested_elements_to_hosted_elements(self):
        for relating_object, related_objects in self.ifc_parser.rel_nests.items():
            self.file.createIfcRelNests(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                self.ifc_parser.products[relating_object]['ifc'],
                [o['ifc'] for o in related_objects])

    def relate_objects_to_types(self):
        for relating_type, related_objects in self.ifc_parser.rel_defines_by_type.items():
            self.file.createIfcRelDefinesByType(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[o]['ifc'] for o in related_objects],
                self.ifc_parser.type_products[relating_type]['ifc'])

    def relate_objects_to_qtos(self):
        for relating_property_key, related_objects in self.ifc_parser.rel_defines_by_qto.items():
            self.file.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                self.ifc_parser.qtos[relating_property_key]['ifc'])

    def relate_objects_to_psets(self):
        for relating_property_key, related_objects in self.ifc_parser.rel_defines_by_pset.items():
            self.file.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                self.ifc_parser.psets[relating_property_key]['ifc'])

    def relate_objects_to_materials(self):
        if not self.ifc_export_settings.has_representations:
            return
        for relating_material_key, related_objects in self.ifc_parser.rel_associates_material.items():
            self.file.createIfcRelAssociatesMaterial(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                self.ifc_parser.materials[relating_material_key]['ifc'])

    def relate_objects_to_material_sets(self, set_type):
        if not self.ifc_export_settings.has_representations:
            return
        for product_index, related_materials in getattr(self.ifc_parser, f'rel_associates_material_{set_type}_set').items():
            material_set = self.file.create_entity(f'IfcMaterial{set_type.capitalize()}Set', **{
                f'Material{set_type.capitalize()}s': [self.ifc_parser.materials[m]['part_ifc'] for m in related_materials]
            })
            self.file.createIfcRelAssociatesMaterial(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[product_index]['ifc']],
                material_set)

    def relate_spaces_to_boundary_elements(self):
        for relating_space_index, relationships, in self.ifc_parser.rel_space_boundaries.items():
            for relationship in relationships:
                relationship['attributes']['GlobalId'] = ifcopenshell.guid.new()
                relationship['attributes']['RelatedBuildingElement'] = self.ifc_parser.products[
                    self.ifc_parser.get_product_index_from_raw_name(
                        relationship['related_building_element_raw_name'])]['ifc']
                relationship['attributes']['RelatingSpace'] = self.ifc_parser.products[relating_space_index]['ifc']
                relationship['attributes']['ConnectionGeometry'] = self.create_connection_geometry(
                    self.ifc_parser.products[relating_space_index],
                    relationship['connection_geometry_face_index'])
                self.file.create_entity(relationship['class'], **relationship['attributes'])

    def create_connection_geometry(self, product, face_index):
        mesh = product['raw'].data
        polygon = mesh.polygons[int(face_index)]
        vertex_on_polygon = mesh.vertices[polygon.vertices[0]].co
        center = polygon.center
        normal = polygon.normal
        forward = center - vertex_on_polygon
        return self.file.createIfcFaceSurface([self.file.createIfcFaceOuterBound(
            self.file.createIfcPolyLoop([
                self.create_cartesian_point(
                    mesh.vertices[vertice].co.x,
                    mesh.vertices[vertice].co.y,
                    mesh.vertices[vertice].co.z)
                for vertice in polygon.vertices]),
            True)],
            self.file.createIfcPlane(self.file.createIfcAxis2Placement3D(
                self.create_cartesian_point(center.x, center.y, center.z),
                self.file.createIfcDirection((normal.x, normal.y, normal.z)),
                self.file.createIfcDirection((forward.x, forward.y, forward.z)))),
            True)

    def relate_to_documents(self, relationships):
        for relating_document_key, related_objects in relationships.items():
            self.file.createIfcRelAssociatesDocument(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                self.ifc_parser.document_references[relating_document_key]['ifc'])

    def relate_to_classifications(self, relationships):
        for relating_key, related_objects in relationships.items():
            self.file.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                self.ifc_parser.classification_references[relating_key]['ifc'])

    def relate_to_objectives(self, relationships):
        for relating_key, related_objects in relationships.items():
            self.file.createIfcRelAssociatesConstraint(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects], None,
                self.ifc_parser.objectives[relating_key]['ifc'])

    def relate_structural_members_to_connections(self):
        for relating_member, relating_connection in self.ifc_parser.rel_connects_structural_member.items():
            self.file.create_entity('IfcRelConnectsStructuralMember', **{
                'RelatingStructuralMember': self.ifc_parser.products[relating_member]['ifc'],
                'RelatedStructuralConnection': self.ifc_parser.products[relating_connection]['ifc']
            })

    def relate_objects_to_groups(self):
        for relating_group, related_objects in self.ifc_parser.rel_assigns_to_group.items():
            self.file.createIfcRelAssignsToGroup(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[o]['ifc'] for o in related_objects], None,
                self.ifc_parser.groups[relating_group]['ifc'])

    def convert_si_to_unit(self, co):
        return co / self.ifc_parser.unit_scale

    def write_ifc_file(self):
        extension = self.ifc_export_settings.output_file.split('.')[-1]
        if extension == 'ifczip':
            with tempfile.TemporaryDirectory() as unzipped_path:
                filename, ext = os.path.splitext(os.path.basename(self.ifc_export_settings.output_file))
                tmp_name = '{}.ifc'.format(filename)
                tmp_file = os.path.join(unzipped_path, tmp_name)
                self.file.write(tmp_file)
                with zipfile.ZipFile(self.ifc_export_settings.output_file,
                        mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                    zf.write(tmp_file)
        elif extension == 'ifc':
            self.file.write(self.ifc_export_settings.output_file)
        elif extension == 'ifcjson':
            ifc2json = IFC2JSON(self.file).convert()
            with open(self.ifc_export_settings.output_file, 'w') as f:
                f.write(json.dumps(ifc2json, indent = 4))


class IfcExportSettings:
    def __init__(self):
        self.logger = None
        self.schema_dir = None
        self.data_dir = None
        self.output_file = None
        self.has_representations = True
        self.has_quantities = True
        self.contexts = ['Model', 'Plan']
        self.subcontexts = ['Annotation', 'Axis', 'Box', 'FootPrint', 'Reference', 'Body', 'Clearance', 'CoG', 'Profile', 'SurveyPoints']
        self.generated_subcontexts = ['Box']
        self.target_views = ['GRAPH_VIEW', 'SKETCH_VIEW', 'MODEL_VIEW', 'PLAN_VIEW', 'REFLECTED_PLAN_VIEW',
                             'SECTION_VIEW', 'ELEVATION_VIEW', 'USERDEFINED', 'NOTDEFINED']
        self.should_export_all_materials_as_styled_items = False
        self.should_use_presentation_style_assignment = False
        self.context_tree = []

    @staticmethod
    def factory(context, output_file, logger):
        scene_bim = context.scene.BIMProperties
        settings = IfcExportSettings()
        settings.output_file = output_file
        settings.logger = logger
        settings.data_dir = scene_bim.data_dir
        settings.schema_dir = scene_bim.schema_dir
        settings.has_representations = scene_bim.export_has_representations
        settings.should_export_all_materials_as_styled_items = scene_bim.export_should_export_all_materials_as_styled_items
        settings.should_use_presentation_style_assignment = scene_bim.export_should_use_presentation_style_assignment
        settings.context_tree = []
        for ifc_context in ['model', 'plan']:
            if getattr(scene_bim, 'has_{}_context'.format(ifc_context)):
                subcontexts = {}
                for subcontext in getattr(scene_bim, '{}_subcontexts'.format(ifc_context)):
                    subcontexts.setdefault(subcontext.name, []).append(subcontext.target_view)
                settings.context_tree.append({
                    'name': ifc_context.title(),
                    'subcontexts': [
                        {'name': key, 'target_views': value}
                        for key, value in subcontexts.items()
                    ]
                })
        return settings
