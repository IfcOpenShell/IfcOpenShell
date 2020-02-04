import bpy
import csv
import json
import time
import datetime
import os
from pathlib import Path
from mathutils import Vector, Matrix
from .helper import SIUnitHelper
from . import schema
import ifcopenshell
import addon_utils

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
        self.selected_spatial_structure_elements = []
        self.global_ids = []

        self.product_index = 0
        self.product_name_index_map = {}

        self.units = {}
        self.people = []
        self.organisations = []
        self.psets = {}
        self.documents = {}
        self.classifications = []
        self.classification_references = {}
        self.objectives = {}
        self.qtos = {}
        self.aggregates = {}
        self.materials = {}
        self.spatial_structure_elements = []
        self.spatial_structure_elements_tree = []
        self.structural_analysis_models = []
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
        self.representations = {}
        self.type_products = []
        self.door_attributes = {}
        self.window_attributes = {}
        self.project = {}
        self.libraries = []
        self.products = []

    def parse(self):
        self.units = self.get_units()
        self.unit_scale = self.get_unit_scale()
        self.people = self.get_people()
        self.organisations = self.get_organisations()
        self.categorise_selected_objects(bpy.context.selected_objects)
        self.psets = self.get_psets()
        self.material_psets = self.get_material_psets()
        self.documents = self.get_documents()
        self.classifications = self.get_classifications()
        self.classification_references = self.get_classification_references()
        self.objectives = self.get_objectives()
        self.load_representations()
        self.materials = self.get_materials()
        self.styled_items = self.get_styled_items()
        self.qtos = self.get_qtos()
        self.spatial_structure_elements = self.get_spatial_structure_elements()
        self.structural_analysis_models = self.get_structural_analysis_models()

        self.collection_name_filter = []

        self.project = self.get_project()
        self.libraries = self.get_libraries()
        self.door_attributes = self.get_door_attributes()
        self.window_attributes = self.get_window_attributes()
        self.type_products = self.get_type_products()
        self.get_products()
        self.resolve_product_relationships()
        self.map_conversion = self.get_map_conversion()
        self.target_crs = self.get_target_crs()
        self.library_information = self.get_library_information()
        self.spatial_structure_elements_tree = self.get_spatial_structure_elements_tree(
            self.project['raw'].children, self.collection_name_filter)

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
            obj = product['raw']
            self.add_product(self.get_product(product))
            self.resolve_modifiers(product)

    def resolve_modifiers(self, product):
        obj = product['raw']
        if obj.data and not obj.data.BIMMeshProperties.is_parametric:
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
            if m.operation == 'DIFFERENCE':
                self.rel_voids_elements.setdefault(i, []).append(void_or_projection)
                if not m.object.parent:
                    continue
                fill = self.get_product_index_from_raw_name(m.object.parent.name)
                if fill:
                    self.rel_fills_elements.setdefault(void_or_projection, []).append(fill)
            elif m.operation == 'UNION':
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

        type_product = obj.BIMObjectProperties.type_product
        if type_product \
                and self.is_a_type(self.get_ifc_class(type_product.name)):
            reference = self.get_type_product_reference(type_product.name)
            self.rel_defines_by_type.setdefault(reference, []).append(self.product_index)

        if product['has_boundary_condition']:
            product['boundary_condition_class'] = obj.BIMObjectProperties.boundary_condition.name
            product['boundary_condition_attributes'] = {a.name: a.string_value
                for a in obj.BIMObjectProperties.boundary_condition.attributes}

        for collection in product['raw'].users_collection:
            self.parse_product_collection(product, collection)

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

        for pset in obj.BIMObjectProperties.psets:
            self.rel_defines_by_pset.setdefault(
                '{}/{}'.format(pset.name, pset.file), []).append(product)

        for pset in obj.BIMObjectProperties.override_psets:
            pset_key = '{}/{}'.format(pset.name, obj.name)
            raw = {p.name: p.string_value for p in pset.properties if p.string_value}
            if not raw:
                continue
            self.psets[pset_key] = {
                'ifc': None,
                'raw': raw,
                'attributes': { 'Name': pset.name }
            }
            self.rel_defines_by_pset.setdefault(pset_key, []).append(product)

        for document in obj.BIMObjectProperties.documents:
            self.rel_associates_document_object.setdefault(
                document.file, []).append(product)

        for classification in obj.BIMObjectProperties.classifications:
            self.rel_associates_classification_object.setdefault(
                classification.identification, []).append(product)

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

    def parse_product_collection(self, product, collection):
        if collection is None:
            return
        class_name = self.get_ifc_class(collection.name)
        if self.is_a_spatial_structure_element(class_name):
            reference = self.get_spatial_structure_element_reference(collection.name)
            self.rel_contained_in_spatial_structure.setdefault(reference, []).append(self.product_index)
            product['relating_structure'] = reference
            self.collection_name_filter.append(collection.name)
        elif self.is_a_structural_analysis_model(class_name):
            reference = self.get_structural_analysis_model_reference(collection.name)
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

    def categorise_selected_objects(self, objects_to_sort, metadata=None):
        if not metadata:
            metadata = {}
        for obj in objects_to_sort:
            if obj.name[0:3] != 'Ifc':
                continue
            elif obj.users_collection and obj.users_collection[0].name == obj.name:
                self.selected_spatial_structure_elements.append({'raw': obj, 'metadata': metadata})
            elif not self.is_a_library(self.get_ifc_class(obj.users_collection[0].name)):
                self.selected_products.append({'raw': obj, 'metadata': metadata})
            elif obj.instance_type == 'COLLECTION':
                self.categorise_selected_objects(
                    obj.instance_collection.objects,
                    {'rel_aggregates_relating_object': obj}
                )

    def get_psets(self):
        psets = {}
        for filename in Path(self.data_dir + 'pset/').glob('**/*.csv'):
            with open(filename, 'r') as f:
                name = filename.parts[-2]
                description = filename.stem
                psets['{}/{}'.format(name, description)] = {
                    'ifc': None,
                    'raw': {x[0]: x[1] for x in list(csv.reader(f))},
                    'attributes': {
                        'Name': name,
                        'Description': description}
                }
        return psets

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
        results = []
        class_path = self.data_dir + 'class/'
        with open(class_path + 'classifications.csv', 'r') as f:
            data = list(csv.reader(f))
            keys = data.pop(0)
            for row in data:
                row[-1] = json.loads(row[-1])
                results.append({
                    'ifc': None,
                    'raw': row,
                    'attributes': dict(zip(keys, row))
                })
        return results

    def get_classification_references(self):
        results = {}
        class_path = self.data_dir + 'class/'
        with open(class_path + 'references.csv', 'r') as f:
            data = list(csv.reader(f))
            keys = data.pop(0)
            for row in data:
                results[row[0]] = {
                    'ifc': None,
                    'raw': row,
                    'referenced_source': int(row.pop()),
                    'attributes': dict(zip(keys, row))
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

    def get_documents(self):
        documents = {}
        doc_path = self.data_dir + 'doc/'
        for filename in Path(doc_path).glob('**/*'):
            uri = str(filename.relative_to(doc_path).as_posix())
            documents[uri] = {
                'ifc': None,
                'raw': filename,
                'attributes': {
                    'Location': uri,
                    'Name': filename.stem
                }}
        return documents

    def get_project(self):
        for collection in bpy.data.collections:
            if self.is_a_project(self.get_ifc_class(collection.name)):
                return {
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': self.get_object_attributes(collection)
                }

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
        for collection in bpy.data.collections:
            if self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                raw = bpy.data.objects.get(collection.name)
                if not raw:
                    raw = collection
                element = {
                    'ifc': None,
                    'raw': raw,
                    'class': self.get_ifc_class(raw.name),
                    'attributes': self.get_object_attributes(raw)
                }
                self.append_product_attributes(element, raw)
                elements.append(element)
        return elements

    def get_structural_analysis_models(self):
        elements = []
        for collection in bpy.data.collections:
            if 'IfcStructuralAnalysisModel' in collection.name:
                elements.append({
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': self.get_object_attributes(collection)
                })
        return elements

    def load_representations(self):
        if not self.ifc_export_settings.has_representations:
            return
        for product in self.selected_products \
                + self.type_products \
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
            'is_wireframe': mesh.BIMMeshProperties.is_wireframe if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_swept_solid': mesh.BIMMeshProperties.is_swept_solid if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_generated': False,
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
        for product in self.selected_products + self.type_products:
            obj = product['raw']
            if obj.data is None:
                continue
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

    def get_qtos(self):
        if not self.ifc_export_settings.has_quantities:
            return {}
        results = {}
        for product in self.selected_products + self.type_products:
            obj = product['raw']
            if not obj.data:
                continue
            for property in obj.keys():
                if property[0:4] != 'Qto_':
                    continue
                results[obj.name] = {
                    'ifc': None,
                    'raw': obj,
                    'class': property,
                    'attributes': {
                        'Name': property,
                        'MethodOfMeasurement': obj[property]
                    }
                }
        return results

    def get_type_products(self):
        results = []
        index = 0
        for library in self.libraries:
            for obj in library['raw'].objects:
                if not self.is_a_type(self.get_ifc_class(obj.name)):
                    continue
                try:
                    type_product = {
                        'ifc': None,
                        'raw': obj,
                        'location': obj.matrix_world.translation,
                        'up_axis': self.get_axis(obj.matrix_world, 2),
                        'forward_axis': self.get_axis(obj.matrix_world, 0),
                        'psets': ['{}/{}'.format(pset.name, pset.file) for pset in
                                  obj.BIMObjectProperties.psets],
                        'class': self.get_ifc_class(obj.name),
                        'representations': self.get_object_representation_names(obj),
                        'attributes': self.get_object_attributes(obj)
                    }
                    results.append(type_product)
                    library['rel_declares_type_products'].append(index)

                    # TODO: this should use properties
                    for key in obj.keys():
                        if key[0:3] == 'Doc':
                            self.rel_associates_document_type.setdefault(
                                obj[key], []).append(type_product)
                        elif key[0:5] == 'Class':
                            self.rel_associates_classification_type.setdefault(
                                obj[key], []).append(type_product)
                        elif key[0:9] == 'Objective':
                            self.rel_associates_constraint_objective_type.setdefault(
                                obj[key], []).append(type_product)

                    index += 1
                except Exception as e:
                    self.ifc_export_settings.logger.error(
                        'The type product "{}" could not be parsed: {}'.format(obj.name, e.args))
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

    def get_spatial_structure_elements_tree(self, collections, name_filter):
        collection_tree = []

        for collection in collections:
            if not self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                continue
            children = self.get_spatial_structure_elements_tree(
                collection.children, name_filter)
            if collection.name in name_filter \
                    or children:
                collection_tree.append({
                    'reference': self.get_spatial_structure_element_reference(collection.name),
                    'children': children
                })

        return collection_tree

    def get_spatial_structure_element_reference(self, name):
        return ['{}/{}'.format(e['class'], e['attributes']['Name'])
                for e in self.spatial_structure_elements].index(name)

    def get_structural_analysis_model_reference(self, name):
        return ['{}/{}'.format(e['class'], e['attributes']['Name'])
                for e in self.structural_analysis_models].index(name)

    def get_type_product_reference(self, name):
        return [p['attributes']['Name']
                for p in self.type_products].index(self.get_ifc_name(name))

    def get_ifc_class(self, name):
        return name.split('/')[0]

    def get_ifc_name(self, name):
        try:
            return name.split('/')[1]
        except IndexError:
            self.ifc_export_settings.logger.error(
                'Name "{}" does not follow the format of "IfcClass/Name"'.format(name))

    def is_a_spatial_structure_element(self, class_name):
        # We assume that any collection we can't identify is a spatial structure
        return class_name[0:3] == 'Ifc' \
               and not self.is_a_project(class_name) \
               and not self.is_a_library(class_name) \
               and not self.is_a_rel_aggregates(class_name) \
               and not self.is_a_structural_analysis_model(class_name)

    def is_a_rel_aggregates(self, class_name):
        return class_name == 'IfcRelAggregates'

    def is_a_project(self, class_name):
        return class_name == 'IfcProject'

    def is_a_library(self, class_name):
        return class_name == 'IfcProjectLibrary'

    def is_a_structural_analysis_model(self, class_name):
        return class_name == 'IfcStructuralAnalysisModel'

    def is_a_type(self, class_name):
        return class_name[0:3] == 'Ifc' and class_name[-4:] == 'Type'


class IfcExporter():
    def __init__(self, ifc_export_settings, ifc_parser, qto_calculator):
        self.template_file = '{}template.ifc'.format(ifc_export_settings.schema_dir)
        self.ifc_export_settings = ifc_export_settings
        self.ifc_parser = ifc_parser
        self.qto_calculator = qto_calculator

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.ifc_parser.parse()
        self.create_units()
        self.create_people()
        self.create_organisations()
        self.set_common_definitions()
        self.create_rep_context()
        self.create_project()
        self.create_library_information()
        self.create_documents()
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
        self.create_structural_analysis_models()
        self.create_qtos()
        self.create_products()
        self.create_styled_items()
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
        self.file.write(self.ifc_export_settings.output_file)

    def set_common_definitions(self):
        # Owner history doesn't actually work like this, but for now, it does :)
        self.origin = self.file.by_type('IfcAxis2Placement3D')[0]
        self.create_owner_history()
        self.set_header()

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

    def create_documents(self):
        for document in self.ifc_parser.documents.values():
            document['ifc'] = self.file.create_entity(
                'IfcDocumentReference', **document['attributes'])
            self.file.createIfcRelAssociatesDocument(
                ifcopenshell.guid.new(), None, None, None,
                [self.ifc_parser.project['ifc']], document['ifc'])

    def create_classifications(self):
        for classification in self.ifc_parser.classifications:
            classification['ifc'] = self.file.create_entity(
                'IfcClassification',
                **classification['attributes']
            )
            self.file.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(), None, None, None,
                [self.ifc_parser.project['ifc']], classification['ifc'])

    def create_classification_references(self):
        for reference in self.ifc_parser.classification_references.values():
            reference['attributes']['ReferencedSource'] = \
                self.ifc_parser.classifications[reference['referenced_source']]['ifc']
            reference['ifc'] = self.file.create_entity(
                'IfcClassificationReference', **reference['attributes'])

    def create_objectives(self):
        for objective in self.ifc_parser.objectives.values():
            objective['ifc'] = self.file.create_entity(
                'IfcObjective', **objective['attributes'])

    def create_psets(self):
        for pset in self.ifc_parser.psets.values():
            properties = self.create_pset_properties(pset)
            if not properties:
                self.ifc_export_settings.logger.error(
                    'No properties could be detected for the pset {}/{}'.format(
                        pset['attributes']['Name'],
                        pset['attributes']['Description']))
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
        self.ifc_rep_context['Model'] = {
            'ifc': self.file.createIfcGeometricRepresentationContext(
                None, 'Model', 3, 1.0E-05, self.origin)}
        if 'Plan' in self.ifc_export_settings.contexts:
            self.ifc_rep_context['Plan'] = {
                'ifc': self.file.createIfcGeometricRepresentationContext(
                    None, 'Plan', 2, 1.0E-05, self.origin)}
        for context in self.ifc_export_settings.context_tree:
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
            placement = self.create_ifc_axis_2_placement_3d(
                product['location'],
                product['up_axis'],
                product['forward_axis']
            )

            if product['representations']:
                maps = []
                for representation in product['representations']:
                    maps.append(self.file.createIfcRepresentationMap(
                        placement, self.ifc_parser.representations[representation]['ifc']))
                product['attributes']['RepresentationMaps'] = maps

            if product['psets']:
                product['attributes'].update({'HasPropertySets':[
                    self.ifc_parser.psets[pset]['ifc']
                    for pset in product['psets']]
                })

            if product['class'] == 'IfcDoorType' \
                    and product['attributes']['Name'] in self.ifc_parser.door_attributes:
                self.add_predefined_attributes_to_type_product(
                    product,
                    self.ifc_parser.door_attributes[product['attributes']['Name']]
                )
            elif product['class'] == 'IfcWindowType' \
                    and product['attributes']['Name'] in self.ifc_parser.window_attributes:
                self.add_predefined_attributes_to_type_product(
                    product,
                    self.ifc_parser.window_attributes[product['attributes']['Name']]
                )

            try:
                product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
            except RuntimeError as e:
                self.ifc_export_settings.logger.error(
                    'The type product "{}/{}" could not be created: {}'.format(
                        product['class'],
                        product['attributes']['Name'],
                        e.args
                    )
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
            self.cast_attributes(element['class'], element['attributes'])
            element['attributes'].update({
                'OwnerHistory': self.owner_history,  # TODO: unhardcode
                'ObjectPlacement': self.file.createIfcLocalPlacement(placement_rel_to, self.origin),
                'Representation': self.get_product_shape(element)
            })
            element['ifc'] = self.file.create_entity(element['class'], **element['attributes'])
            related_objects.append(element['ifc'])
            self.create_spatial_structure_elements(node['children'], element['ifc'])
        if related_objects:
            self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                self.owner_history, None, None, relating_object, related_objects)

    def create_structural_analysis_models(self):
        for model in self.ifc_parser.structural_analysis_models:
            model['ifc'] = self.file.create_entity('IfcStructuralAnalysisModel', **model['attributes'])
            self.file.createIfcRelDeclares(ifcopenshell.guid.new(),
                self.owner_history, None, None, self.ifc_parser.project['ifc'], [model['ifc']])

    def create_styled_items(self):
        for styled_item in self.ifc_parser.styled_items:
            product = self.ifc_parser.products[
                self.ifc_parser.get_product_index_from_raw_name(
                    styled_item['related_product_name'])]['ifc']
            representation_items = []
            if product.Representation:
                for representation in product.Representation.Representations:
                    for item in representation.Items:
                        representation_items.append(item)
            for representation_item in representation_items:
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
        rendering_attributes = {'SurfaceColour': surface_colour}
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
        for object_name, qto in self.ifc_parser.qtos.items():
            quantities = self.calculate_quantities(qto['class'], qto['raw'])
            qto['attributes'].update({
                'GlobalId': ifcopenshell.guid.new(),
                'OwnerHistory': self.owner_history,
                'Quantities': quantities
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
            placement = self.file.createIfcLocalPlacement(placement_rel_to, self.origin)
        else:
            placement = self.file.createIfcLocalPlacement(placement_rel_to,
                self.create_ifc_axis_2_placement_3d(product['location'],
                    product['up_axis'],
                    product['forward_axis']))

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
        self.ifc_faces = []
        if representation['is_generated'] \
                and representation['subcontext'] == 'Box':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_box_representation(representation))
        elif representation['subcontext'] == 'CoG':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_cog_representation(representation))
        elif representation['is_curve'] \
                and representation['context'] == 'Model' \
                and representation['subcontext'] == 'Axis' \
                and representation['target_view'] == 'GRAPH_VIEW':
            return self.file.createIfcRepresentationMap(
                self.origin, self.create_curve_axis_representation(representation))
        elif representation['is_structural'] \
                and representation['context'] == 'Model' \
                and representation['subcontext'] == 'Reference' \
                and representation['target_view'] == 'GRAPH_VIEW':
            return self.file.createIfcRepresentationMap(
                self.origin, self.create_structural_reference_representation(representation))
        elif representation['context'] == 'Plan' \
                or representation['subcontext'] == 'Axis' \
                or representation['is_wireframe']:
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_wireframe_representation(representation))
        elif representation['subcontext'] == 'SurveyPoints':
            return self.file.createIfcRepresentationMap(self.origin,
                    self.create_geometric_curve_set_representation(representation))
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

    def create_wireframe_representation(self, representation):
        mesh = representation['raw']
        self.create_vertices(mesh.vertices)
        for edge in mesh.edges:
            self.ifc_edges.append(self.file.createIfcPolyline([
                self.ifc_vertices[v] for v in edge.vertices]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'],
            'Curve',
            self.ifc_edges)

    def create_geometric_curve_set_representation(self, representation):
        mesh = representation['raw']
        self.create_vertices(mesh.vertices)
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
        geometric_curve_set = self.file.createIfcGeometricCurveSet(loops)
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

    def create_curve_axis_representation(self, representation):
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Curve3D',
            [self.create_curve(representation['raw'])])

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
            self.create_curve(representation['raw'].bevel_object.data))
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
        #    swept_area, self.origin, self.create_curve(representation['raw']),
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

    def create_curve(self, curve):
        # TODO: support interpolated curves, not just polylines
        points = []
        for point in curve.splines[0].bezier_points:
            points.append(self.create_cartesian_point(
                point.co.x, point.co.y, point.co.z))
        for point in curve.splines[0].points:
            points.append(self.create_cartesian_point(
                point.co.x, point.co.y, point.co.z))
        if curve.splines[0].use_cyclic_u:
            points.append(points[0])
        return self.file.createIfcPolyline(points)

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
        for polygon in mesh.polygons:
            self.ifc_faces.append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][
                representation['target_view']]['ifc'],
            representation['subcontext'], 'Brep',
            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(self.ifc_faces))])

    def create_vertices(self, vertices):
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
                self.ifc_parser.documents[relating_document_key]['ifc'])

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
                self.ifc_parser.structural_analysis_models[relating_group]['ifc'])

    def convert_si_to_unit(self, co):
        return co / self.ifc_parser.unit_scale


class IfcExportSettings:
    def __init__(self):
        self.logger = None
        self.schema_dir = None
        self.data_dir = None
        self.output_file = None
        self.has_representations = True
        self.has_quantities = True
        self.contexts = ['Model', 'Plan']
        self.subcontexts = ['Axis', 'FootPrint', 'Reference', 'Body', 'Clearance', 'CoG', 'SurveyPoints']
        self.generated_subcontexts = ['Box']
        self.target_views = ['GRAPH_VIEW', 'SKETCH_VIEW', 'MODEL_VIEW', 'PLAN_VIEW', 'REFLECTED_PLAN_VIEW',
                             'SECTION_VIEW', 'ELEVATION_VIEW', 'USERDEFINED', 'NOTDEFINED']
        self.should_export_all_materials_as_styled_items = False
        self.should_use_presentation_style_assignment = False
        self.context_tree = []
