import bpy
import csv
import json
import time
from pathlib import Path
from mathutils import Vector
from . import ifcopenshell

class ArrayModifier:
    count: int
    offset: Vector

class QtoCalculator():
    def get_units(self, o, vg_index):
        return len([ v for v in o.data.vertices if vg_index in [ g.group for g in v.groups ] ])

    def get_length(self, o, vg_index):
        length = 0
        edges = [ e for e in o.data.edges if (
            vg_index in [ g.group for g in o.data.vertices[e.vertices[0]].groups ] and
            vg_index in [ g.group for g in o.data.vertices[e.vertices[1]].groups ]
            ) ]
        for e in edges:
            length += self.get_edge_distance(o, e)
        return length

    def get_edge_distance(self, object, edge):
        return (object.data.vertices[edge.vertices[1]].co - object.data.vertices[edge.vertices[0]].co).length

    def get_area(self, o, vg_index):
        area = 0
        vertices_in_vg = [ v.index for v in o.data.vertices if vg_index in [ g.group for g in v.groups ] ]
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
                tf_tris = (me.vertices[tfv[0]], me.vertices[tfv[1]], me.vertices[tfv[2]]),\
                          (me.vertices[tfv[2]], me.vertices[tfv[3]], me.vertices[tfv[0]])

            for tf_iter in tf_tris:
                v1 = ob_mat @ tf_iter[0].co
                v2 = ob_mat @ tf_iter[1].co
                v3 = ob_mat @ tf_iter[2].co

                volume += v1.dot(v2.cross(v3)) / 6.0
        return volume

class IfcSchema():
    def __init__(self, ifc_export_settings):
        self.schema_dir = ifc_export_settings.schema_dir
        self.property_file = ifcopenshell.open(self.schema_dir + 'IFC4_ADD2.ifc')
        self.psets = {}
        self.qtos = {}
        self.load()

        with open(self.schema_dir + 'ifc_types_IFC4.json') as f:
            self.type_map = json.load(f)

    def load(self):
        for property in self.property_file.by_type('IfcPropertySetTemplate'):
            if property.Name[0:4] == 'Qto_':
                # self.qtos.append({ })
                pass
            else:
                self.psets[property.Name] = {
                    'HasPropertyTemplates': { p.Name: p for p in property.HasPropertyTemplates}}

class IfcParser():
    def __init__(self, ifc_export_settings):
        self.data_dir = ifc_export_settings.data_dir

        self.ifc_export_settings = ifc_export_settings

        self.selected_products = []

        self.product_index = 0
        self.product_name_index_map = {}

        self.units = {}
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
        self.rel_associates_constraint_objective_object = {}
        self.rel_associates_constraint_objective_type = {}
        self.rel_aggregates = {}
        self.representations = {}
        self.type_products = []
        self.door_attributes = {}
        self.window_attributes = {}
        self.project = {}
        self.libraries = []
        self.products = []

    def parse(self):
        self.units = self.get_units()
        self.convert_selected_objects_into_products(bpy.context.selected_objects)
        self.psets = self.get_psets()
        self.documents = self.get_documents()
        self.classifications = self.get_classifications()
        self.classification_references = self.get_classification_references()
        self.objectives = self.get_objectives()
        self.representations = self.get_representations()
        self.materials = self.get_materials()
        self.qtos = self.get_qtos()
        self.spatial_structure_elements = self.get_spatial_structure_elements()

        self.collection_name_filter = []

        self.project = self.get_project()
        self.libraries = self.get_libraries()
        self.door_attributes = self.get_door_attributes()
        self.window_attributes = self.get_window_attributes()
        self.type_products = self.get_type_products()
        self.get_products()
        self.map_conversion = self.get_map_conversion()
        self.target_crs = self.get_target_crs()
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

    def get_object_attributes(self, object):
        attributes = { 'Name': self.get_ifc_name(object.name) }
        if 'IfcGlobalId' not in object:
            object['IfcGlobalId'] = ifcopenshell.guid.new()
        attributes.update({ key[3:]: object[key] for key in object.keys() if key[0:3] == 'Ifc'})
        return attributes

    def get_products(self):
        for product in self.selected_products:
            object = product['raw']
            self.add_product(self.get_product(product))
            self.resolve_array_modifier(product)

    def resolve_array_modifier(self, product):
        object = product['raw']
        instance_objects = [(object, object.location)]
        for instance in self.get_instances(object):
            created_instances = []
            for n in range(instance.count-1):
                for o in instance_objects:
                    location = o[1] + ((n+1) * instance.offset)
                    self.add_product(self.get_product({ 'raw': o[0], 'metadata': product['metadata'] },
                        {'location': location}, {'GlobalId': ifcopenshell.guid.new()}))
                    created_instances.append((o[0], location))
            instance_objects.extend(created_instances)

    def add_product(self, product):
        self.products.append(product)
        self.product_name_index_map[product['raw'].name] = self.product_index
        self.product_index += 1

    def get_product_index_from_raw_name(self, name):
        for index, product in enumerate(self.products):
            if product['raw'].name == name:
                return index

    def get_product(self, selected_product, metadata_override={}, attribute_override={}):
        object = selected_product['raw']
        product = {
            'ifc': None,
            'raw': object,
            'location': object.location,
            'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
            'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
            'class': self.get_ifc_class(object.name),
            'relating_structure': None,
            'relating_host': None,
            'relating_qtos_key': None,
            'representations': self.get_object_representation_names(object),
            'attributes': self.get_object_attributes(object)
            }
        product['attributes'].update(attribute_override)
        product.update(metadata_override)

        if object.parent \
            and self.is_a_type(self.get_ifc_class(object.parent.name)):
            reference = self.get_type_product_reference(object.parent.name)
            self.rel_defines_by_type.setdefault(reference, []).append(self.product_index)

        for collection in product['raw'].users_collection:
            self.parse_product_collection(product, collection)

        if 'IfcRelNests' in object.constraints:
            parent_product_index = self.get_product_index_from_raw_name(
                object.constraints['IfcRelNests'].target.name)
            self.rel_nests.setdefault(parent_product_index, []).append(product)
            product['relating_host'] = parent_product_index

        for name, constraint in object.constraints.items():
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

        if object.instance_type == 'COLLECTION' \
            and self.is_a_rel_aggregates(self.get_ifc_class(object.instance_collection.name)):
            self.rel_aggregates[self.product_index] = object.name

        if 'rel_aggregates_relating_object' in selected_product['metadata']:
            relating_object = selected_product['metadata']['rel_aggregates_relating_object']
            product['location'] = relating_object.matrix_world @ product['location']
            product['up_axis'] = (relating_object.matrix_world.to_quaternion() @ object.matrix_world.to_quaternion()) @ Vector((0, 0, 1))
            product['forward_axis'] = (relating_object.matrix_world.to_quaternion() @ object.matrix_world.to_quaternion()) @ Vector((1, 0, 0))
            self.aggregates.setdefault(relating_object.name, []).append(self.product_index)

        if object.name in self.qtos:
            self.rel_defines_by_qto.setdefault(object.name, []).append(product)

        for key in object.keys():
            if key[0:5] == 'Pset_':
                self.rel_defines_by_pset.setdefault(
                    '{}/{}'.format(key, object[key]), []).append(product)
            elif key[0:3] == 'Doc':
                self.rel_associates_document_object.setdefault(
                    object[key], []).append(product)
            elif key[0:5] == 'Class':
                self.rel_associates_classification_object.setdefault(
                    object[key], []).append(product)
            elif key[0:9] == 'Objective':
                self.rel_associates_constraint_objective_object.setdefault(
                    object[key], []).append(product)

        if 'IsMaterialLayerSet' in object:
            for slot in object.material_slots:
                self.rel_associates_material_layer_set.setdefault(self.product_index, []).append(slot.material.name)
        elif 'IsMaterialConstituentSet' in object:
            for slot in object.material_slots:
                self.rel_associates_material_constituent_set.setdefault(self.product_index, []).append(slot.material.name)
        else:
            for slot in object.material_slots:
                self.rel_associates_material.setdefault( slot.material.name, []).append(product)

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
        elif self.is_a_rel_aggregates(class_name):
            pass
        else:
            self.parse_product_collection(product, self.get_parent_collection(collection))

    def get_parent_collection(self, child_collection):
        for parent_collection in bpy.data.collections:
            for child in parent_collection.children:
                if child.name == child_collection.name:
                    return parent_collection

    def get_instances(self, object):
        instances = []
        for m in object.modifiers:
            if m.type == 'ARRAY':
                array = ArrayModifier()
                world_rotation = object.matrix_world.decompose()[1]
                array.offset = world_rotation @ Vector(
                    (m.constant_offset_displace[0], m.constant_offset_displace[1], m.constant_offset_displace[2]))
                if m.fit_type == 'FIXED_COUNT':
                    array.count = m.count
                elif m.fit_type == 'FIT_LENGTH':
                    array.count = int(m.fit_length / array.offset.length)
                instances.append(array)
        return instances

    def convert_selected_objects_into_products(self, objects_to_sort, metadata = None):
        if not metadata:
            metadata = {}
        for object in objects_to_sort:
            if not self.is_a_library(self.get_ifc_class(object.users_collection[0].name)):
                self.selected_products.append({ 'raw': object, 'metadata': metadata })
            if object.instance_type == 'COLLECTION':
                self.convert_selected_objects_into_products(object.instance_collection.objects,
                    {'rel_aggregates_relating_object': object})

    def get_psets(self):
        psets = {}
        for filename in Path(self.data_dir + 'pset/').glob('**/*.csv'):
            with open(filename, 'r') as f:
                name = filename.parts[-2]
                description = filename.stem
                psets['{}/{}'.format(name, description)] = {
                    'ifc': None,
                    'raw': { x[0]: x[1] for x in list(csv.reader(f)) },
                    'attributes': {
                        'Name': name,
                        'Description': description }
                    }
        return psets

    def get_door_attributes(self):
        return self.get_predefined_attributes('door')

    def get_window_attributes(self):
        return self.get_predefined_attributes('window')

    def get_predefined_attributes(self, type):
        results = {}
        for filename in Path(self.data_dir + type + '/').glob('**/*.csv'):
            with open(filename, 'r') as f:
                type_name = filename.parts[-2]
                pset_name = filename.stem
                results.setdefault(type_name, []).append({
                    'ifc': None,
                    'raw': { x[0]: x[1] for x in list(csv.reader(f)) },
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
        if 'HasMapConversion' not in scene:
            return {}
        return {
            'ifc': None,
            'attributes': {
                'Eastings': float(scene['Eastings']),
                'Northings': float(scene['Northings']),
                'OrthogonalHeight': float(scene['OrthogonalHeight']),
                'XAxisAbscissa': float(scene['XAxisAbscissa']),
                'XAxisOrdinate': float(scene['XAxisOrdinate']),
                'Scale': float(scene['Scale'])
                }
            }

    def get_target_crs(self):
        scene = bpy.context.scene
        if 'HasMapConversion' not in scene:
            return {}
        return {
            'ifc': None,
            'attributes': {
                'Name': scene['Name'],
                'Description': scene['Description'],
                'GeodeticDatum': scene['GeodeticDatum'],
                'VerticalDatum': scene['VerticalDatum'],
                'MapProjection': scene['MapProjection'],
                'MapZone': str(scene['MapZone']),
                'MapUnit': scene['MapUnit']
                }
            }

    def get_spatial_structure_elements(self):
        elements = []
        for collection in bpy.data.collections:
            if self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                elements.append({
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': self.get_object_attributes(collection)
                    })
        return elements

    def get_representations(self):
        results = {}
        if not self.ifc_export_settings.has_representations:
            return results
        for product in self.selected_products + self.type_products:
            object = product['raw']
            if not object.data \
                or object.data.name in results:
                continue

            self.append_default_representation(object, results)
            self.append_representation_per_context(object, results)
            self.append_generated_representation_per_context(object, results)
        return results

    def append_default_representation(self, object, results):
        if not self.is_mesh_context_sensitive(object.data.name):
            results['Model/Body/{}'.format(object.data.name)] = self.get_representation(
                object.data, object, 'Model', 'Body')

    def append_representation_per_context(self, object, results):
        context = self.get_ifc_context(object.data.name)
        name = self.get_ifc_representation_name(object.data.name)
        for subcontext in self.ifc_export_settings.subcontexts:
            try:
                mesh = bpy.data.meshes['/'.join([context, subcontext, name])]
            except:
                continue
            results[mesh.name] = self.get_representation(
                mesh, object, context, subcontext)

    def append_generated_representation_per_context(self, object, results):
        context = self.get_ifc_context(object.data.name)
        name = self.get_ifc_representation_name(object.data.name)
        for subcontext in self.ifc_export_settings.generated_subcontexts:
            representation = self.get_representation(
                object.data, object, context, subcontext, is_generated=True)
            results['/'.join([context, subcontext, name])] = representation

    def get_representation(self, mesh, object, context, subcontext, is_generated=False):
        return {
            'ifc': None,
            'raw': mesh,
            'raw_object': object,
            'context': context,
            'subcontext': subcontext,
            'is_wireframe': True if 'IsWireframe' in mesh else False,
            'is_swept_solid': True if 'IsSweptSolid' in mesh else False,
            'is_generated': is_generated,
            'attributes': { 'Name': mesh.name }
            }

    def is_mesh_context_sensitive(self, name):
        return '/' in name

    def get_ifc_context(self, name):
        if self.is_mesh_context_sensitive(name):
            return name.split('/')[0]
        return 'Model'

    def get_ifc_representation_name(self, name):
        if self.is_mesh_context_sensitive(name):
            return name.split('/')[2]
        return name

    def get_materials(self):
        results = {}
        if not self.ifc_export_settings.has_representations:
            return results
        for product in self.selected_products + self.type_products:
            object = product['raw']
            if not object.data:
                continue
            for slot in object.material_slots:
                if slot.material.name in results:
                    continue
                results[slot.material.name] = {
                    'ifc': None,
                    'layer_ifc': None,
                    'constituent_ifc': None,
                    'raw': slot.material,
                    'is_material_layer_set': True if 'IsMaterialLayerSet' in object.keys() else False,
                    'is_material_constituent_set': True if 'IsMaterialConstituentSet' in object.keys() else False,
                    'attributes': { 'Name': slot.material.name },
                    'layer_attributes': { key[3:]: slot.material[key] for key in
                        slot.material.keys() if key[0:3] == 'Ifc'},
                    'constituent_attributes': { key[3:]: slot.material[key] for key in
                        slot.material.keys() if key[0:3] == 'Ifc'}
                    }
        return results

    def get_qtos(self):
        if not self.ifc_export_settings.has_quantities:
            return {}
        results = {}
        for product in self.selected_products + self.type_products:
            object = product['raw']
            if not object.data:
                continue
            for property in object.keys():
                if property[0:4] != 'Qto_':
                    continue
                results[object.name] = {
                    'ifc': None,
                    'raw': object,
                    'class': property,
                    'attributes': {
                        'Name': property,
                        'MethodOfMeasurement': object[property]
                        }
                    }
        return results

    def get_type_products(self):
        results = []
        index = 0
        for library in self.libraries:
            for object in library['raw'].objects:
                if not self.is_a_type(self.get_ifc_class(object.name)):
                    continue
                try:
                    type = {
                        'ifc': None,
                        'raw': object,
                        'location': object.location,
                        'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
                        'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
                        'psets': ['{}/{}'.format(key, object[key]) for key in
                            object.keys() if key[0:5] == 'Pset_'],
                        'class': self.get_ifc_class(object.name),
                        'representations': self.get_object_representation_names(object),
                        'attributes': self.get_object_attributes(object)
                    }
                    results.append(type)
                    library['rel_declares_type_products'].append(index)

                    for key in object.keys():
                        if key[0:3] == 'Doc':
                            self.rel_associates_document_type.setdefault(
                                object[key], []).append(type)
                        elif key[0:5] == 'Class':
                            self.rel_associates_classification_type.setdefault(
                                object[key], []).append(type)
                        elif key[0:9] == 'Objective':
                            self.rel_associates_constraint_objective_type.setdefault(
                                object[key], []).append(type)

                    index += 1
                except Exception as e:
                    self.ifc_export_settings.logger.error('The type product "{}" could not be parsed: {}'.format(object.name, e.args))
        return results

    def get_object_representation_names(self, object):
        names = []
        if not object.data:
            return names
        if not self.is_mesh_context_sensitive(object.data.name):
            names.append('Model/Body/{}'.format(object.data.name))
        for subcontext in self.ifc_export_settings.subcontexts:
            try:
                mesh = bpy.data.meshes['/'.join([
                    self.get_ifc_context(object.data.name),
                    subcontext,
                    self.get_ifc_representation_name(object.data.name)])]
            except:
                continue
            names.append(mesh.name)
        for subcontext in self.ifc_export_settings.generated_subcontexts:
            names.append('Model/{}/{}'.format(subcontext, self.get_ifc_representation_name(object.data.name)))
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
        return [ e['attributes']['Name'] for e in self.spatial_structure_elements ].index(self.get_ifc_name(name))

    def get_type_product_reference(self, name):
        return [ p['attributes']['Name'] for p in self.type_products ].index(self.get_ifc_name(name))

    def get_ifc_class(self, name):
        return name.split('/')[0]

    def get_ifc_name(self, name):
        try:
            return name.split('/')[1]
        except IndexError:
            self.ifc_export_settings.logger.error('Name "{}" does not follow the format of "IfcClass/Name"'.format(name))

    def is_a_spatial_structure_element(self, class_name):
        # We assume that any collection we can't identify is a spatial structure
        return class_name[0:3] == 'Ifc' \
            and not self.is_a_project(class_name) \
            and not self.is_a_library(class_name) \
            and not self.is_a_rel_aggregates(class_name)

    def is_a_rel_aggregates(self, class_name):
        return class_name == 'IfcRelAggregates'

    def is_a_project(self, class_name):
        return class_name == 'IfcProject'

    def is_a_library(self, class_name):
        return class_name == 'IfcProjectLibrary'

    def is_a_type(self, class_name):
        return class_name[0:3] == 'Ifc' and class_name[-4:] == 'Type'

class SIUnitHelper:
    prefixes = ["EXA", "PETA", "TERA", "GIGA", "MEGA", "KILO", "HECTO",
        "DECA", "DECI", "CENTI", "MILLI", "MICRO", "NANO", "PICO", "FEMTO",
        "ATTO"]
    unit_names = ["AMPERE", "BECQUEREL", "CANDELA", "COULOMB",
        "CUBIC_METRE", "DEGREE CELSIUS", "FARAD", "GRAM", "GRAY", "HENRY",
        "HERTZ", "JOULE", "KELVIN", "LUMEN", "LUX", "MOLE", "NEWTON", "OHM",
        "PASCAL", "RADIAN", "SECOND", "SIEMENS", "SIEVERT", "SQUARE METRE",
        "METRE", "STERADIAN", "TESLA", "VOLT", "WATT", "WEBER"]

    @staticmethod
    def get_prefix(text):
        for prefix in SIUnitHelper.prefixes:
            if prefix in text.upper():
                return prefix

    @staticmethod
    def get_unit_name(text):
        for name in SIUnitHelper.unit_names:
            if name in text.upper().replace('METER', 'METRE'):
                return name

class IfcExporter():
    def __init__(self, ifc_export_settings, ifc_schema, ifc_parser, qto_calculator):
        self.template_file = '{}template.ifc'.format(ifc_export_settings.schema_dir)
        self.ifc_export_settings = ifc_export_settings
        self.ifc_schema = ifc_schema
        self.ifc_parser = ifc_parser
        self.qto_calculator = qto_calculator

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.set_common_definitions()
        self.ifc_parser.parse()
        self.create_units()
        self.create_rep_context()
        self.create_project()
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
        self.create_qtos()
        self.create_products()
        self.relate_definitions_to_contexts()
        self.relate_objects_to_objects()
        self.relate_elements_to_spatial_structures()
        self.relate_nested_elements_to_hosted_elements()
        self.relate_objects_to_types()
        self.relate_objects_to_qtos()
        self.relate_objects_to_psets()
        self.relate_objects_to_materials()
        self.relate_objects_to_material_layer_sets()
        self.relate_objects_to_material_constituent_sets()
        self.relate_spaces_to_boundary_elements()
        self.relate_to_documents(self.ifc_parser.rel_associates_document_object)
        self.relate_to_documents(self.ifc_parser.rel_associates_document_type)
        self.relate_to_classifications(self.ifc_parser.rel_associates_classification_object)
        self.relate_to_classifications(self.ifc_parser.rel_associates_classification_type)
        self.relate_to_objectives(self.ifc_parser.rel_associates_constraint_objective_object)
        self.relate_to_objectives(self.ifc_parser.rel_associates_constraint_objective_type)
        self.file.write(self.ifc_export_settings.output_file)

    def set_common_definitions(self):
        # Owner history doesn't actually work like this, but for now, it does :)
        self.origin = self.file.by_type('IfcAxis2Placement3D')[0]
        self.owner_history = self.file.by_type('IfcOwnerHistory')[0]

    def create_units(self):
        for type, data in self.ifc_parser.units.items():
            if data['is_metric']:
                type_prefix = ''
                if type == 'area':
                    type_prefix = 'SQUARE_'
                elif type == 'volume':
                    type_prefix = 'CUBIC_'
                data['ifc'] = self.file.createIfcSIUnit(None,
                    '{}UNIT'.format(type.upper()),
                    SIUnitHelper.get_prefix(data['raw']),
                    type_prefix + SIUnitHelper.get_unit_name(data['raw']))
            else:
                self.create_imperial_unit(type, data)
        self.file.createIfcUnitAssignment([u['ifc'] for u in self.ifc_parser.units.values()])

    def create_imperial_unit(self, type, data):
        pass # TODO

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
                'IfcClassification', **classification['attributes'])
            self.file.createIfcRelAssociatesClassification(
                ifcopenshell.guid.new(), None, None, None,
                [self.ifc_parser.project['ifc']], classification['ifc'])

    def create_classification_references(self):
        for reference in self.ifc_parser.classification_references.values():
            reference['attributes']['ReferencedSource'] = self.ifc_parser.classifications[reference['referenced_source']]['ifc']
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

    def create_pset_properties(self, pset):
        properties = []
        templates = self.ifc_schema.psets[pset['attributes']['Name']]['HasPropertyTemplates']
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

    def cast_to_base_type(self, type, value):
        if self.ifc_schema.type_map[type] == 'float':
            return float(value)
        elif self.ifc_schema.type_map[type] == 'integer':
            return int(value)
        elif self.ifc_schema.type_map[type] == 'bool':
            return True if value.lower() in ['1', 't', 'true', 'yes', 'y', 'uh-huh'] else False
        return str(value)

    def create_rep_context(self):
        self.ifc_rep_context = {}
        self.ifc_rep_context['Model'] = {
            'ifc': self.file.createIfcGeometricRepresentationContext(
                None, 'Model', 3, 1.0E-05, self.origin)}
        # TODO Make optional
        self.ifc_rep_context['Plan'] = {
            'ifc': self.file.createIfcGeometricRepresentationContext(
                None, 'Plan', 2, 1.0E-05, self.origin)}
        for subcontext in (self.ifc_export_settings.subcontexts +
            self.ifc_export_settings.generated_subcontexts):
            self.ifc_rep_context['Model'][subcontext] = {
                'ifc': self.file.createIfcGeometricRepresentationSubContext(
                    subcontext, 'Model',
                    None, None, None, None,
                    self.ifc_rep_context['Model']['ifc'], None, 'MODEL_VIEW', None)}

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
        self.file.createIfcRelDeclares(
            ifcopenshell.guid.new(), self.owner_history,
            None, None,
            self.ifc_parser.project['ifc'], [l['ifc'] for l in self.ifc_parser.libraries])

    def create_map_conversion(self):
        if not self.ifc_parser.map_conversion:
            return
        self.create_target_crs()
        # TODO should this be hardcoded?
        self.ifc_parser.map_conversion['attributes']['SourceCRS'] = self.ifc_rep_context['Model']['ifc']
        self.ifc_parser.map_conversion['attributes']['TargetCRS'] = self.ifc_parser.target_crs['ifc']
        self.ifc_parser.map_conversion['ifc'] = self.file.create_entity('IfcMapConversion',
            **self.ifc_parser.map_conversion['attributes'])

    def create_target_crs(self):
        self.ifc_parser.target_crs['attributes']['MapUnit'] = self.file.createIfcSIUnit(
            None, 'LENGTHUNIT',
            SIUnitHelper.get_prefix(self.ifc_parser.target_crs['attributes']['MapUnit']),
            SIUnitHelper.get_unit_name(self.ifc_parser.target_crs['attributes']['MapUnit']))
        self.ifc_parser.target_crs['ifc'] = self.file.create_entity(
            'IfcProjectedCRS', **self.ifc_parser.target_crs['attributes'])

    def create_type_products(self):
        for product in self.ifc_parser.type_products:
            placement = self.create_ifc_axis_2_placement_3d(product['location'], product['up_axis'], product['forward_axis'])

            if product['representations']:
                maps = []
                for representation in product['representations']:
                    maps.append(self.file.createIfcRepresentationMap(
                        placement, self.ifc_parser.representations[representation]['ifc']))
                product['attributes']['RepresentationMaps'] = maps

            if product['psets']:
                product['attributes'].update({ 'HasPropertySets':
                    [self.ifc_parser.psets[pset]['ifc'] for pset in
                    product['psets']] })

            if product['class'] == 'IfcDoorType' \
                and product['attributes']['Name'] in self.ifc_parser.door_attributes:
                self.add_predefined_attributes_to_type_product(product,
                    self.ifc_parser.door_attributes[product['attributes']['Name']])
            elif product['class'] == 'IfcWindowType' \
                and product['attributes']['Name'] in self.ifc_parser.window_attributes:
                self.add_predefined_attributes_to_type_product(product,
                    self.ifc_parser.window_attributes[product['attributes']['Name']])

            try:
                product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
            except RuntimeError as e:
                self.ifc_export_settings.logger.error('The type product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def add_predefined_attributes_to_type_product(self, product, attributes):
        self.create_predefined_attributes(attributes)
        product['attributes'].setdefault('HasPropertySets', [])
        for attribute in attributes:
            product['attributes']['HasPropertySets'].append(attribute['ifc'])

    def create_predefined_attributes(self, attributes):
        for attribute in attributes:
            attribute['ifc'] = self.file.create_entity(attribute['pset_name'],
                **{k: float(v) if v.replace('.', '', 1).isdigit() else v for k, v in attribute['raw'].items()})

    def relate_definitions_to_contexts(self):
        for library in self.ifc_parser.libraries:
            self.file.createIfcRelDeclares(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                library['ifc'],
                [self.ifc_parser.type_products[t]['ifc'] for t in library['rel_declares_type_products']])

    def relate_objects_to_objects(self):
        for relating_object, related_objects_reference in self.ifc_parser.rel_aggregates.items():
            relating_object = self.ifc_parser.products[relating_object]
            related_objects = [ self.ifc_parser.products[o]['ifc'] for o in self.ifc_parser.aggregates[related_objects_reference] ]
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
            element['attributes'].update({
                'OwnerHistory': self.owner_history, # TODO: unhardcode
                'ObjectPlacement': self.file.createIfcLocalPlacement(placement_rel_to, self.origin)
            })
            element['ifc'] = self.file.create_entity(element['class'], **element['attributes'])
            related_objects.append(element['ifc'])
            self.create_spatial_structure_elements(node['children'], element['ifc'])
        if related_objects:
            self.file.createIfcRelAggregates(
                ifcopenshell.guid.new(),
                self.owner_history, None, None, relating_object, related_objects)

    def create_materials(self):
        for material in self.ifc_parser.materials.values():
            styles = []
            styles.append(self.create_surface_style_rendering(material))
            if 'IsExternal' in material['raw'].keys():
                styles.append(self.file.create_entity('IfcExternallyDefinedSurfaceStyle',
                    **self.get_material_external_definition(material['raw'])))

            surface_style = self.file.createIfcSurfaceStyle(None, 'BOTH', styles)
            styled_item = self.file.createIfcStyledItem(None, [surface_style], None)
            styled_representation = self.file.createIfcStyledRepresentation(
                self.ifc_rep_context['Model']['Body']['ifc'], None, None, [styled_item])
            material['ifc'] = self.file.createIfcMaterial(material['raw'].name, None, None)
            self.file.createIfcMaterialDefinitionRepresentation(
                material['raw'].name, None, [styled_representation], material['ifc'])
            if material['is_material_layer_set']:
                material['layer_attributes']['Material'] = material['ifc']
                material['layer_ifc'] = self.file.create_entity('IfcMaterialLayer',
                    **material['layer_attributes'])
            elif material['is_material_constituent_set']:
                material['constituent_attributes']['Material'] = material['ifc']
                material['constituent_ifc'] = self.file.create_entity('IfcMaterialConstituent',
                    **material['constituent_attributes'])

    def create_surface_style_rendering(self, material):
        surface_colour = self.create_colour_rgb(material['raw'].diffuse_color)
        rendering_attributes = { 'SurfaceColour': surface_colour }
        rendering_attributes.update(self.get_rendering_attributes(material['raw']))
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
            'Location': material['Location'],
            'Identification': material['Identification'] if 'Identification' in material else material.name,
            'Name': material['Name'] if 'Name' in material else material.name
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
            placement_rel_to = self.ifc_parser.spatial_structure_elements[product['relating_structure']]['ifc'].ObjectPlacement
        elif product['relating_host'] is not None:
            placement_rel_to = self.ifc_parser.products[product['relating_host']]['ifc'].ObjectPlacement
        else:
            placement_rel_to = None

        placement = self.file.createIfcLocalPlacement(placement_rel_to,
            self.create_ifc_axis_2_placement_3d(product['location'],
                product['up_axis'],
                product['forward_axis']))

        product['attributes'].update({
            'OwnerHistory': self.owner_history, # TODO: unhardcode
            'ObjectPlacement': placement,
            'Representation': self.get_product_shape(product)
            })

        try:
            product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
        except RuntimeError as e:
            self.ifc_export_settings.logger.error('The product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def get_product_shape(self, product):
        try:
            shape = self.file.createIfcProductDefinitionShape(None, None,
                [self.ifc_parser.representations[p]['ifc'] for p in product['representations']])
        except:
            shape = None
        return shape

    def calculate_quantities(self, qto_name, object):
        quantities = []
        for index, vg in enumerate(object.vertex_groups):
            if qto_name not in vg.name:
                continue
            if 'length' in vg.name.lower():
                quantity = float(self.qto_calculator.get_length(object, index))
                quantities.append(self.file.createIfcQuantityLength(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['length']['ifc'], quantity))
            elif 'area' in vg.name.lower():
                quantity = float(self.qto_calculator.get_area(object, index))
                quantities.append(self.file.createIfcQuantityArea(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['area']['ifc'], quantity))
            elif 'volume' in vg.name.lower():
                quantity = float(self.qto_calculator.get_volume(object, index))
                quantities.append(self.file.createIfcQuantityVolume(
                    vg.name.split('/')[1], None,
                    self.ifc_parser.units['volume']['ifc'], quantity))
            if not quantity:
                self.ifc_export_settings.logger.warning('The calculated quantity {} for {} is zero.'.format(
                    vg.name, object.name))
        return quantities

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((point.x, point.y, point.z)),
            self.file.createIfcDirection((up.x, up.y, up.z)),
            self.file.createIfcDirection((forward.x, forward.y, forward.z)))

    def create_representation(self, representation):
        self.ifc_vertices = []
        self.ifc_edges = []
        self.ifc_faces = []
        if representation['is_generated'] \
            and representation['subcontext'] == 'Box':
            return self.create_box_representation(representation)
        elif representation['subcontext'] == 'CoG':
            return self.create_cog_representation(representation)
        elif representation['context'] == 'Plan' \
            or representation['subcontext'] == 'Axis' \
            or representation['is_wireframe']:
            return self.create_wireframe_representation(representation)
        elif representation['is_swept_solid']:
            return self.create_swept_solid_representation(representation)
        else:
            return self.create_solid_representation(representation)

    def create_box_representation(self, representation):
        object = representation['raw_object']
        bounding_box = self.file.createIfcBoundingBox(
            self.create_cartesian_point(
                object.bound_box[0][0], object.bound_box[0][1], object.bound_box[0][2]),
            object.dimensions[0], object.dimensions[1], object.dimensions[2])
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']]['ifc'],
            representation['subcontext'], 'BoundingBox', [bounding_box])

    def create_cog_representation(self, representation):
        mesh = representation['raw']
        cog = self.create_cartesian_point(
            mesh.vertices[0].co.x, mesh.vertices[0].co.y, mesh.vertices[0].co.z)
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']]['ifc'],
            representation['subcontext'], 'BoundingBox', [cog])

    def create_wireframe_representation(self, representation):
        mesh = representation['raw']
        self.create_vertices(mesh.vertices)
        for edge in mesh.edges:
            self.ifc_edges.append(self.file.createIfcPolyline([
                self.ifc_vertices[v] for v in edge.vertices]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']]['ifc'],
            representation['subcontext'], 'Curve',
            self.ifc_edges)

    def create_swept_solid_representation(self, representation):
        object = representation['raw_object']
        mesh = representation['raw']
        profile_index = None
        extrusion_index = None
        for index, vg in enumerate(object.vertex_groups):
            if vg.name == 'profile':
                profile_index = index
            elif vg.name == 'extrusion':
                extrusion_index = index
        profile_edges = self.get_edges_in_vg_index(object, profile_index)
        extrusion_edge = self.get_edges_in_vg_index(object, extrusion_index)[0]
        loop = self.get_loop_from_edges(profile_edges)
        points = []
        for point in loop:
            points.append(self.create_cartesian_point(
                mesh.vertices[point].co.x,
                mesh.vertices[point].co.y,
                mesh.vertices[point].co.z))
        points.append(points[0])
        curve = self.file.createIfcArbitraryClosedProfileDef('AREA', None,
            self.file.createIfcPolyline(points))
        start, end = self.get_start_and_end_of_extrusion(points, extrusion_edge)
        direction = self.get_extrusion_direction(mesh, start, end)
        extruded_area_solid = self.file.createIfcExtrudedAreaSolid(curve, self.origin,
            self.file.createIfcDirection((direction.x, direction.y, direction.z)), direction.length)
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']]['ifc'],
            representation['subcontext'], 'SweptSolid',
            [extruded_area_solid])

    def get_start_and_end_of_extrusion(self, profile_points, extrusion_edge):
        if extrusion_edge.vertices[0] in profile_points:
            return (extrusion_edge.vertices[0], extrusion_edge.vertices[1])
        return (extrusion_edge.vertices[1], extrusion_edge.vertices[0])

    def get_extrusion_direction(self, mesh, start, end):
        return mesh.vertices[end].co - mesh.vertices[start].co

    def get_edges_in_vg_index(self, object, index):
        return [ e for e in object.data.edges if (
            index in [ g.group for g in object.data.vertices[e.vertices[0]].groups ] and
            index in [ g.group for g in object.data.vertices[e.vertices[1]].groups ]
            ) ]

    def get_loop_from_edges(self, edges):
        while edges:
            currentEdge= edges.pop()
            startVert= currentEdge.vertices[0]
            endVert= currentEdge.vertices[1]
            polyLine= [startVert, endVert]
            ok= 1
            while ok:
                ok= 0
                i=len(edges)
                while i:
                    i-=1
                    ed= edges[i]
                    if ed.vertices[0] == endVert:
                        polyLine.append(ed.vertices[1])
                        endVert= polyLine[-1]
                        ok=1
                        del edges[i]
                    elif ed.vertices[1] == endVert:
                        polyLine.append(ed.vertices[0])
                        endVert= polyLine[-1]
                        ok=1
                        del edges[i]
                    elif ed.vertices[0] == startVert:
                        polyLine.insert(0, ed.vertices[1])
                        startVert= polyLine[0]
                        ok=1
                        del edges[i]
                    elif ed.vertices[1] == startVert:
                        polyLine.insert(0, ed.vertices[0])
                        startVert= polyLine[0]
                        ok=1
                        del edges[i]
            return polyLine

    def create_solid_representation(self, representation):
        mesh = representation['raw']
        self.create_vertices(mesh.vertices)
        for polygon in mesh.polygons:
            self.ifc_faces.append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']]['ifc'],
            representation['subcontext'], 'Brep',
            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(self.ifc_faces))])

    def create_vertices(self, vertices):
        for vertice in vertices:
            self.ifc_vertices.append(self.create_cartesian_point(
                vertice.co.x, vertice.co.y, vertice.co.z))

    def create_cartesian_point(self, x, y, z=None):
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        return self.file.createIfcCartesianPoint((x, y, z))

    def relate_elements_to_spatial_structures(self):
        for relating_structure, related_elements in self.ifc_parser.rel_contained_in_spatial_structure.items():
            self.file.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [ self.ifc_parser.products[e]['ifc'] for e in related_elements],
                self.ifc_parser.spatial_structure_elements[relating_structure]['ifc'])

    def relate_nested_elements_to_hosted_elements(self):
        for relating_object, related_objects in self.ifc_parser.rel_nests.items():
            self.file.createIfcRelNests(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                self.ifc_parser.products[relating_object]['ifc'],
                [ o['ifc'] for o in related_objects ])

    def relate_objects_to_types(self):
        for relating_type, related_objects in self.ifc_parser.rel_defines_by_type.items():
            self.file.createIfcRelDefinesByType(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [ self.ifc_parser.products[o]['ifc'] for o in related_objects],
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

    def relate_objects_to_material_layer_sets(self):
        if not self.ifc_export_settings.has_representations:
            return
        for product_index, related_materials in self.ifc_parser.rel_associates_material_layer_set.items():
            material_layer_set = self.file.create_entity('IfcMaterialLayerSet', **{
                'MaterialLayers': [self.ifc_parser.materials[m]['layer_ifc'] for m in related_materials]
                })
            self.file.createIfcRelAssociatesMaterial(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[product_index]['ifc']],
                material_layer_set)

    def relate_objects_to_material_constituent_sets(self):
        if not self.ifc_export_settings.has_representations:
            return
        for product_index, related_materials in self.ifc_parser.rel_associates_material_constituent_set.items():
            material_constituent_set = self.file.create_entity('IfcMaterialConstituentSet', **{
                'MaterialConstituents': [self.ifc_parser.materials[m]['constituent_ifc'] for m in related_materials]
                })
            self.file.createIfcRelAssociatesMaterial(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [self.ifc_parser.products[product_index]['ifc']],
                material_constituent_set)

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
                self.file.createIfcCartesianPoint((center.x, center.y, center.z)),
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

class IfcExportSettings:
    def __init__(self):
        self.logger = None
        self.schema_dir = None
        self.data_dir = None
        self.output_file = None
        self.has_representations = True
        self.has_quantities = True
        self.subcontexts = ['Axis', 'FootPrint', 'Reference', 'Body', 'Clearance', 'CoG']
        self.generated_subcontexts = ['Box']
