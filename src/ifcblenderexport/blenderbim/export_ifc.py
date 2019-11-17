import bpy
import csv
import json
import time
from pathlib import Path
from mathutils import Vector, Matrix
from .helper import SIUnitHelper
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

        with open(self.schema_dir + 'ifc_elements_IFC4.json') as f:
            self.elements = json.load(f)

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
        self.unit_scale = self.get_unit_scale()
        self.people = self.get_people()
        self.organisations = self.get_organisations()
        self.convert_selected_objects_into_products(bpy.context.selected_objects)
        self.psets = self.get_psets()
        self.documents = self.get_documents()
        self.classifications = self.get_classifications()
        self.classification_references = self.get_classification_references()
        self.objectives = self.get_objectives()
        self.representations = self.get_representations()
        self.materials = self.get_materials()
        self.styled_items = self.get_styled_items()
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

    def get_object_attributes(self, object):
        attributes = { 'Name': self.get_ifc_name(object.name) }
        if object.BIMObjectProperties.attributes.find('GlobalId') == -1:
            global_id = object.BIMObjectProperties.attributes.add()
            global_id.name = 'GlobalId'
            global_id.string_value = ifcopenshell.guid.new()
        attributes.update({ a.name: a.string_value for a in object.BIMObjectProperties.attributes})
        return attributes

    def get_products(self):
        for product in self.selected_products:
            object = product['raw']
            self.add_product(self.get_product(product))
            self.resolve_array_modifier(product)

    def resolve_array_modifier(self, product):
        object = product['raw']
        instance_objects = [(object, object.matrix_world.translation)]
        global_id_index = 0
        for instance in self.get_instances(object):
            created_instances = []
            for n in range(instance.count-1):
                for o in instance_objects:
                    location = o[1] + ((n+1) * instance.offset)
                    self.add_product(self.get_product({ 'raw': o[0], 'metadata': product['metadata'] },
                        {'location': location}, {'GlobalId': self.get_parametric_global_id(object, global_id_index)}))
                    created_instances.append((o[0], location))
            instance_objects.extend(created_instances)

    def get_parametric_global_id(self, object, index):
        global_ids = object.BIMObjectProperties.global_ids
        total_global_ids = len(global_ids)
        if index < total_global_ids:
            return global_ids[index].name
        global_id = object.BIMObjectProperties.global_ids.add()
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

    def get_product(self, selected_product, metadata_override={}, attribute_override={}):
        object = selected_product['raw']
        product = {
            'ifc': None,
            'raw': object,
            'location': object.matrix_world.translation,
            'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
            'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
            'right_axis': object.matrix_world.to_quaternion() @ Vector((0, 1, 0)),
            'has_scale': object.scale != Vector((1, 1, 1)),
            'scale': object.scale,
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

        for pset in object.BIMObjectProperties.psets:
            self.rel_defines_by_pset.setdefault(
                '{}/{}'.format(pset.name, pset.file), []).append(product)

        for document in object.BIMObjectProperties.documents:
            self.rel_associates_document_object.setdefault(
                document.file, []).append(product)

        for classification in object.BIMObjectProperties.classifications:
            self.rel_associates_classification_object.setdefault(
                classification.identification, []).append(product)

        for key in object.keys():
            if key[0:9] == 'Objective':
                self.rel_associates_constraint_objective_object.setdefault(
                    object[key], []).append(product)

        for slot in object.material_slots:
            if slot.link == 'OBJECT':
                continue
            if 'IsMaterialLayerSet' in object:
                self.rel_associates_material_layer_set.setdefault(self.product_index, []).append(slot.material.name)
            elif 'IsMaterialConstituentSet' in object:
                self.rel_associates_material_constituent_set.setdefault(self.product_index, []).append(slot.material.name)
            else:
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

    def get_people(self):
        with open(self.data_dir + 'owner/person.json') as file:
            return json.load(file)

    def get_organisations(self):
        with open(self.data_dir + 'owner/organisation.json') as file:
            return json.load(file)

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
        return results

    def append_default_representation(self, object, results):
        if not self.is_mesh_context_sensitive(object.data.name):
            results['Model/Body/MODEL_VIEW/{}'.format(object.data.name)] = self.get_representation(
                object.data, object, 'Model', 'Body', 'MODEL_VIEW')

    def append_representation_per_context(self, object, results):
        name = self.get_ifc_representation_name(object.data.name)
        for context in self.ifc_export_settings.context_tree:
            for subcontext in context['subcontexts']:
                for target_view in subcontext['target_views']:
                    mesh_name = '/'.join([context['name'], subcontext['name'], target_view, name])
                    try:
                        mesh = bpy.data.meshes[mesh_name]
                    except:
                        continue
                    results[mesh_name] = self.get_representation(
                        mesh, object, context['name'], subcontext['name'], target_view)

    def get_representation(self, mesh, object, context, subcontext, target_view, is_generated=False):
        return {
            'ifc': None,
            'raw': mesh,
            'raw_object': object,
            'context': context,
            'subcontext': subcontext,
            'target_view': target_view,
            'is_curve': isinstance(mesh, bpy.types.Curve),
            'is_wireframe': mesh.BIMMeshProperties.is_wireframe if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_swept_solid': mesh.BIMMeshProperties.is_swept_solid if hasattr(mesh, 'BIMMeshProperties') else False,
            'is_generated': is_generated,
            'attributes': { 'Name': mesh.name }
            }

    def is_mesh_context_sensitive(self, name):
        return '/' in name

    def get_ifc_representation_name(self, name):
        if self.is_mesh_context_sensitive(name):
            return name.split('/')[3]
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
                if slot.material.name in results \
                    or slot.link == 'OBJECT':
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

    def get_styled_items(self):
        results = []
        if not self.ifc_export_settings.has_representations:
            return results
        for product in self.selected_products + self.type_products:
            object = product['raw']
            if not object.data:
                continue
            for slot in object.material_slots:
                if not self.ifc_export_settings.should_export_all_materials_as_styled_items:
                    if slot.material.name in results \
                        or slot.link == 'DATA':
                        continue
                results.append({
                    'ifc': None,
                    'raw': slot.material,
                    'related_product_name': product['raw'].name,
                    'attributes': { 'Name': slot.material.name },
                    })
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
                        'location': object.translation,
                        'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
                        'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
                        'psets': ['{}/{}'.format(pset.name, pset.file) for pset in
                            object.BIMObjectProperties.psets],
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
            names.append('Model/Body/MODEL_VIEW/{}'.format(object.data.name))
        name = self.get_ifc_representation_name(object.data.name)
        for context in self.ifc_export_settings.context_tree:
            for subcontext in context['subcontexts']:
                for target_view in subcontext['target_views']:
                    mesh_name = '/'.join([context['name'], subcontext['name'], target_view, name])
                    try:
                        mesh = bpy.data.meshes[mesh_name]
                    except:
                        continue
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
        return [ '{}/{}'.format(e['class'], e['attributes']['Name']) for e in
            self.spatial_structure_elements ].index(name)

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
        self.create_people()
        self.create_organisations()
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
        self.create_styled_items()
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
                data['ifc'] = self.create_metric_unit(type, data)
            else:
                data['ifc'] = self.create_imperial_unit(type, data)
        self.file.createIfcUnitAssignment([u['ifc'] for u in self.ifc_parser.units.values()])

    def create_metric_unit(self, type, data):
        type_prefix = ''
        if type == 'area':
            type_prefix = 'SQUARE_'
        elif type == 'volume':
            type_prefix = 'CUBIC_'
        return self.file.createIfcSIUnit(None,
            '{}UNIT'.format(type.upper()),
            SIUnitHelper.get_prefix(data['raw']),
            type_prefix + SIUnitHelper.get_unit_name(data['raw']))

    def create_imperial_unit(self, type, data):
        if type == 'length':
            dimensional_exponents = self.file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
            name_prefix = ''
        elif type == 'area':
            dimensional_exponents = self.file.createIfcDimensionalExponents(2, 0, 0, 0, 0, 0, 0)
            name_prefix = 'square'
        elif type == 'volume':
            dimensional_exponents = self.file.createIfcDimensionalExponents(3, 0, 0, 0, 0, 0, 0)
            name_prefix = 'cubic'
        si_unit = self.file.createIfcSIUnit(None,'{}UNIT'.format(type.upper()), None,
            '{}METRE'.format(name_prefix.upper() + '_' if name_prefix else ''))
        if data['raw'] == 'INCHES':
            name = '{}inch'.format(name_prefix + ' ' if name_prefix else '')
        elif data['raw'] == 'FEET':
            name = '{}foot'.format(name_prefix + ' ' if name_prefix else '')
        value_component = self.file.create_entity('IfcReal',
            **{'wrappedValue': SIUnitHelper.si_conversions[name]})
        conversion_factor = self.file.createIfcMeasureWithUnit(value_component, si_unit)
        return self.file.createIfcConversionBasedUnit(
            dimensional_exponents, '{}UNIT'.format(type.upper()),
            name, conversion_factor)

    def create_people(self):
        for person in self.ifc_parser.people:
            if person['Roles']:
                person['Roles'] = self.create_roles(person['Roles'])
            if person['Addresses']:
                person['Addresses'] = self.create_addresses(person['Addresses'])
            self.file.create_entity('IfcPerson', **person)

    def create_organisations(self):
        for organisation in self.ifc_parser.organisations:
            if organisation['Roles']:
                organisation['Roles'] = self.create_roles(organisation['Roles'])
            if organisation['Addresses']:
                organisation['Addresses'] = self.create_addresses(organisation['Addresses'])
            self.file.create_entity('IfcOrganization', **organisation)

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
        if pset['attributes']['Name'] in self.ifc_schema.psets:
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
        if type not in self.ifc_schema.type_map:
            return value
        elif self.ifc_schema.type_map[type] == 'float':
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

    def create_surface_style_rendering(self, styled_item):
        surface_colour = self.create_colour_rgb(styled_item['raw'].diffuse_color)
        rendering_attributes = { 'SurfaceColour': surface_colour }
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
            placement_rel_to = self.ifc_parser.spatial_structure_elements[product['relating_structure']]['ifc'].ObjectPlacement
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

        product['attributes'].update({
            'OwnerHistory': self.owner_history, # TODO: unhardcode
            'ObjectPlacement': placement,
            'Representation': self.get_product_shape(product)
            })

        for key, value in product['attributes'].items():
            type = self.get_product_attribute_type(product['class'], key)
            if type is None:
                continue
            product['attributes'][key] = self.cast_to_base_type(type, value)

        try:
            product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
        except RuntimeError as e:
            self.ifc_export_settings.logger.error('The product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def get_product_attribute_type(self, product_class, attribute_name):
        element_schema = self.ifc_schema.elements[product_class]
        for a in element_schema['attributes']:
            if a['name'] == attribute_name:
                return a['type']
        if element_schema['parent'] in self.ifc_schema.elements:
            return self.get_product_attribute_type(element_schema['parent'], attribute_name)
        return None

    def get_product_shape(self, product):
        try:
            shape = self.file.createIfcProductDefinitionShape(None, None,
                self.get_product_shape_representations(product))
        except:
            shape = None
        return shape

    def get_product_shape_representations(self, product):
        results = []
        for representation_name in product['representations']:
            shape_representation = self.ifc_parser.representations[representation_name]['ifc']
            if product['has_scale']:
                results.append(self.get_product_mapped_geometry(product, shape_representation))
            else:
                results.append(shape_representation)
        return results

    def get_product_mapped_geometry(self, product, shape_representation):
        mapping_source = self.file.createIfcRepresentationMap(self.origin, shape_representation)
        mapping_target = self.file.createIfcCartesianTransformationOperator3DnonUniform(
                self.create_direction(product['forward_axis']),
                self.create_direction(product['right_axis']),
                self.create_cartesian_point(
                    product['location'].x,
                    product['location'].y,
                    product['location'].z),
                product['scale'].x,
                self.create_direction(product['up_axis']),
                product['scale'].y,
                product['scale'].z)
        mapped_item = self.file.createIfcMappedItem(mapping_source, mapping_target)
        return self.file.createIfcShapeRepresentation(
                shape_representation.ContextOfItems,
                shape_representation.RepresentationIdentifier,
                shape_representation.RepresentationType,
                [mapped_item])

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
            self.create_cartesian_point(point.x, point.y, point.z),
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
        elif representation['subcontext'] == 'SurveyPoints':
            return self.create_geometric_curve_set_representation(representation)
        elif representation['is_curve']:
            return self.create_curve_representation(representation)
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
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'BoundingBox', [bounding_box])

    def create_cog_representation(self, representation):
        mesh = representation['raw']
        cog = self.create_cartesian_point(
            mesh.vertices[0].co.x, mesh.vertices[0].co.y, mesh.vertices[0].co.z)
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'BoundingBox', [cog])

    def create_wireframe_representation(self, representation):
        mesh = representation['raw']
        self.create_vertices(mesh.vertices)
        for edge in mesh.edges:
            self.ifc_edges.append(self.file.createIfcPolyline([
                self.ifc_vertices[v] for v in edge.vertices]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'Curve',
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
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
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

    def create_curve_representation(self, representation):
        # TODO: support unclosed surfaces
        swept_area = self.file.createIfcArbitraryClosedProfileDef('AREA', None,
            self.create_curve(representation['raw'].bevel_object.data))
        swept_area_solids = []
        for spline in representation['raw'].splines:
            direction = spline.bezier_points[1].co - spline.bezier_points[0].co
            unit_direction = direction.normalized()

            # This can be used in the future when dealing with non vector curves
            #curr_point = spline.bezier_points[0]
            #next_point = spline.bezier_points[1]
            #j_percent = 0
            #direction = self.bezier_tangent(
            #    pt0=curr_point.co,
            #    pt1=curr_point.handle_right,
            #    pt2=next_point.handle_left,
            #    pt3=next_point.co,
            #    step=j_percent)
            tilt_matrix = Matrix.Rotation(-spline.bezier_points[0].tilt, 4, 'Z')
            x_axis = unit_direction.to_track_quat('-Y', 'Z') @ Vector((1, 0, 0)) @ tilt_matrix

            position = self.create_ifc_axis_2_placement_3d(
                spline.bezier_points[0].co, unit_direction, x_axis)
            swept_area_solids.append(self.file.createIfcExtrudedAreaSolid(
                swept_area, position,
                self.file.createIfcDirection((0., 0., 1.)),
                self.convert_si_to_unit(direction.length)))
        # TODO: support other types of swept areas
        #swept_area_solid = self.file.createIfcFixedReferenceSweptAreaSolid(
        #    swept_area, self.origin, self.create_curve(representation['raw']),
        #    0., 1., self.file.createIfcDirection((0.0, -1.0, 0.0)))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'AdvancedSweptSolid',
            swept_area_solids)

    def create_curve(self, curve):
        # TODO: support interpolated curves, not just polylines
        points = []
        for point in curve.splines[0].bezier_points:
            points.append(self.create_cartesian_point(
                point.co.x, point.co.y, point.co.z))
        if curve.splines[0].use_cyclic_u:
            points.append(points[0])
        return self.file.createIfcPolyline(points)

    def create_swept_solid_representation(self, representation):
        object = representation['raw_object']
        mesh = representation['raw']
        items = []
        for swept_solid in mesh.BIMMeshProperties.swept_solids:
            extrusion_edge = self.get_edges_in_v_indices(object, json.loads(swept_solid.extrusion))[0]

            inner_curves = []
            if swept_solid.inner_curves:
                for indices in json.loads(swept_solid.inner_curves):
                    loop = self.get_loop_from_v_indices(object, indices)
                    curve_ucs = self.get_curve_profile_coordinate_system(object, loop)
                    inner_curves.append(
                        self.create_polyline_from_loop(object, loop, curve_ucs))

            outer_curve_loop = self.get_loop_from_v_indices(object, json.loads(swept_solid.outer_curve))
            curve_ucs = self.get_curve_profile_coordinate_system(object, outer_curve_loop)
            outer_curve = self.create_polyline_from_loop(object, outer_curve_loop, curve_ucs)

            if inner_curves:
                curve = self.file.createIfcArbitraryProfileDefWithVoids('AREA', None,
                    outer_curve, inner_curves)
            else:
                curve = self.file.createIfcArbitraryClosedProfileDef('AREA', None, outer_curve)

            direction = self.get_extrusion_direction(object, outer_curve_loop, extrusion_edge, curve_ucs)
            unit_direction = direction.normalized()
            position = self.create_ifc_axis_2_placement_3d(
                curve_ucs['center'], curve_ucs['z_axis'], curve_ucs['x_axis'])

            items.append(self.file.createIfcExtrudedAreaSolid(
                curve, position, self.file.createIfcDirection((
                    unit_direction.x, unit_direction.y, unit_direction.z)),
                self.convert_si_to_unit(direction.length)))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'SweptSolid', items)

    def get_start_and_end_of_extrusion(self, profile_points, extrusion_edge):
        if extrusion_edge.vertices[0] in profile_points:
            return (extrusion_edge.vertices[0], extrusion_edge.vertices[1])
        return (extrusion_edge.vertices[1], extrusion_edge.vertices[0])

    def get_curve_profile_coordinate_system(self, object, loop):
        profile_face = bpy.data.meshes.new('profile_face')
        profile_verts = [(
            object.data.vertices[p].co.x,
            object.data.vertices[p].co.y,
            object.data.vertices[p].co.z
            ) for p in loop]
        profile_faces = [tuple(range(0, len(profile_verts)))]
        profile_face.from_pydata(profile_verts, [], profile_faces)
        center = profile_face.polygons[0].center
        x_axis = (object.data.vertices[loop[0]].co - center).normalized()
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

    def create_polyline_from_loop(self, object, loop, curve_ucs):
        points = []
        for point in loop:
            transformed_point = curve_ucs['matrix'] @ object.data.vertices[point].co
            points.append(self.create_cartesian_point(
                transformed_point.x, transformed_point.y))
        points.append(points[0])
        return self.file.createIfcPolyline(points)

    def get_extrusion_direction(self, object, outer_curve_loop, extrusion_edge, curve_ucs):
        start, end = self.get_start_and_end_of_extrusion(outer_curve_loop, extrusion_edge)
        return curve_ucs['matrix'] @ (curve_ucs['center'] + (object.data.vertices[end].co - object.data.vertices[start].co))

    def get_loop_from_v_indices(self, object, indices):
        edges = self.get_edges_in_v_indices(object, indices)
        loop = self.get_loop_from_edges(edges)
        loop.pop(-1)
        return loop

    def get_edges_in_v_indices(self, object, indices):
        return [ e for e in object.data.edges if (
            e.vertices[0] in indices and e.vertices[1] in indices) ]

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
            self.ifc_rep_context[representation['context']][representation['subcontext']][representation['target_view']]['ifc'],
            representation['subcontext'], 'Brep',
            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(self.ifc_faces))])

    def create_vertices(self, vertices):
        for vertice in vertices:
            self.ifc_vertices.append(self.create_cartesian_point(
                vertice.co.x, vertice.co.y, vertice.co.z))

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_direction(self, vector):
        return self.file.createIfcDirection((vector.x, vector.y, vector.z))

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
        self.target_views = ['GRAPH_VIEW', 'SKETCH_VIEW', 'MODEL_VIEW', 'PLAN_VIEW', 'REFLECTED_PLAN_VIEW', 'SECTION_VIEW', 'ELEVATION_VIEW', 'USERDEFINED', 'NOTDEFINED']
        self.should_export_all_materials_as_styled_items = False
        self.should_use_presentation_style_assignment = False
        # TODO make this configurable via UI
        self.context_tree = self.build_context_tree()

    def build_context_tree(self):
        tree = []
        for context in self.contexts:
            subcontexts = []
            for subcontext in self.subcontexts + self.generated_subcontexts:
                target_views = []
                for target_view in self.target_views:
                    if context == 'Model' \
                        and target_view != 'MODEL_VIEW':
                        continue
                    elif context == 'Plan' \
                        and target_view == 'MODEL_VIEW':
                        continue
                    target_views.append(target_view)
                subcontexts.append({
                    'name': subcontext,
                    'target_views': target_views
                    })
            tree.append({
                'name': context,
                'subcontexts': subcontexts
                })
        return tree
