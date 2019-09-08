import ifcopenshell
import bpy
import csv
import json
import time
from pathlib import Path
from mathutils import Vector

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
    def __init__(self):
        self.schema_dir = '/home/dion/Projects/IfcOpenShell/src/ifcblenderexport/schema/'
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
        self.data_dir = '/home/dion/Projects/IfcOpenShell/src/ifcblenderexport/data/'

        self.ifc_export_settings = ifc_export_settings

        self.selected_products = []

        self.product_index = 0

        self.psets = {}
        self.qtos = {}
        self.aggregates = {}
        self.spatial_structure_elements = []
        self.spatial_structure_elements_tree = []
        self.rel_contained_in_spatial_structure = {}
        self.rel_defines_by_type = {}
        self.rel_defines_by_qto = {}
        self.rel_defines_by_pset = {}
        self.rel_aggregates = {}
        self.representations = {}
        self.type_products = []
        self.project = {}
        self.libraries = []
        self.products = []

    def parse(self):
        self.convert_selected_objects_into_products(bpy.context.selected_objects)
        self.psets = self.get_psets()
        self.representations = self.get_representations()
        self.qtos = self.get_qtos()
        self.spatial_structure_elements = self.get_spatial_structure_elements()

        self.collection_name_filter = []

        self.project = self.get_project()
        self.libraries = self.get_libraries()
        self.type_products = self.get_type_products()
        self.get_products()
        self.map_conversion = self.get_map_conversion()
        self.target_crs = self.get_target_crs()
        self.spatial_structure_elements_tree = self.get_spatial_structure_elements_tree(
            self.project['raw'].children, self.collection_name_filter)

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
        self.product_index += 1

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
            'relating_qtos_key': None,
            'representation': self.get_object_representation_name(object),
            'attributes': self.get_object_attributes(object)
            }
        product['attributes'].update(attribute_override)
        product.update(metadata_override)

        for collection in product['raw'].users_collection:
            self.parse_product_collection(product, collection)

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

        if object.parent \
            and self.is_a_type(self.get_ifc_class(object.parent.name)):
            reference = self.get_type_product_reference(object.parent.name)
            self.rel_defines_by_type.setdefault(reference, []).append(self.product_index)
        return product

    def parse_product_collection(self, product, collection):
        class_name = self.get_ifc_class(collection.name)
        if self.is_a_spatial_structure_element(class_name):
            reference = self.get_spatial_structure_element_reference(collection.name)
            self.rel_contained_in_spatial_structure.setdefault(reference, []).append(self.product_index)
            product['relating_structure'] = reference
            self.collection_name_filter.append(collection.name)
        elif self.is_a_rel_aggregates(class_name):
            pass
        else:
            self.parse_product_collection(product, self.product_index, self.get_parent_collection(collection))

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
        for filename in Path(self.data_dir).glob('**/*.csv'):
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

    def get_project(self):
        for collection in bpy.data.collections:
            if self.is_a_project(self.get_ifc_class(collection.name)):
                return {
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': { 'Name': self.get_ifc_name(collection.name) }
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
                'attributes': { 'Name': self.get_ifc_name(collection.name) }
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
                    'attributes': { 'Name': self.get_ifc_name(collection.name)}
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
            results[object.data.name] = {
                'ifc': None,
                'raw': object.data,
                'is_wireframe': True if 'IsWireframe' in object.data else False,
                'attributes': { 'Name': object.data.name }
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
                    results.append({
                        'ifc': None,
                        'raw': object,
                        'location': object.location,
                        'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
                        'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
                        'class': self.get_ifc_class(object.name),
                        'representation': self.get_object_representation_name(object),
                        'attributes': self.get_object_attributes(object)
                    })
                    library['rel_declares_type_products'].append(index)
                    index += 1
                except Exception as e:
                    print('The type product "{}" could not be parsed: {}'.format(object.name, e.args))
        return results

    def get_object_representation_name(self, object):
        if object.data:
            return object.data.name
        return None

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
            print('ERROR: Name "{}" does not follow the format of "IfcClass/Name"'.format(name))

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
            if name in text.upper():
                return name

class IfcExporter():
    def __init__(self, ifc_export_settings, ifc_schema, ifc_parser, qto_calculator):
        self.template_file = '/home/dion/Projects/IfcOpenShell/src/ifcblenderexport/template.ifc'
        self.output_file = '/home/dion/Projects/IfcOpenShell/src/ifcblenderexport/output.ifc'
        self.ifc_export_settings = ifc_export_settings
        self.ifc_schema = ifc_schema
        self.ifc_parser = ifc_parser
        self.qto_calculator = qto_calculator

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.set_common_definitions()
        self.ifc_parser.parse()
        self.create_psets()
        self.create_rep_context()
        self.create_project()
        self.create_libraries()
        self.create_map_conversion()
        self.create_representations()
        self.create_type_products()
        self.create_spatial_structure_elements(self.ifc_parser.spatial_structure_elements_tree)
        self.create_qtos()
        self.create_products()
        self.relate_definitions_to_contexts()
        self.relate_objects_to_objects()
        self.relate_elements_to_spatial_structures()
        self.relate_objects_to_types()
        self.relate_objects_to_qtos()
        self.relate_objects_to_psets()
        self.file.write(self.output_file)

    def set_common_definitions(self):
        self.origin = self.file.by_type('IfcAxis2Placement3D')[0]
        # Owner history doesn't actually work like this, but for now, it does :)
        self.owner_history = self.file.by_type('IfcOwnerHistory')[0]
        # TODO: unhardcode units
        units = self.file.by_type('IfcSIUnit')
        self.length_unit = units[0]
        self.area_unit = units[1]
        self.volume_unit = units[2]

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
        self.ifc_rep_context = self.file.createIfcGeometricRepresentationContext(
            None, "Model", 3, 1.0E-05, self.origin)

        self.ifc_rep_subcontext = self.file.createIfcGeometricRepresentationSubContext(
            "Body", "Model",
            None, None, None, None,
            self.ifc_rep_context, None, "MODEL_VIEW", None)

    def create_project(self):
        self.ifc_parser.project['attributes'].update({
            'GlobalId': ifcopenshell.guid.new(),
            'RepresentationContexts': [self.ifc_rep_context],
            'UnitsInContext': self.file.by_type("IfcUnitAssignment")[0]
            })
        self.ifc_parser.project['ifc'] = self.file.create_entity(
            self.ifc_parser.project['class'], **self.ifc_parser.project['attributes'])

    def create_libraries(self):
        for library in self.ifc_parser.libraries:
            library['ifc'] = self.file.create_entity(library['class'], **library['attributes'])
        self.file.createIfcRelDeclares(
            ifcopenshell.guid.new(), self.owner_history,
            library['attributes']['Name'], None,
            self.ifc_parser.project['ifc'], [l['ifc'] for l in self.ifc_parser.libraries])

    def create_map_conversion(self):
        if not self.ifc_parser.map_conversion:
            return
        self.create_target_crs()
        self.ifc_parser.map_conversion['attributes']['SourceCRS'] = self.ifc_rep_context
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
            product['attributes'].update({ 'GlobalId': ifcopenshell.guid.new() })

            if product['representation']:
                representation = self.ifc_parser.representations[product['representation']]['ifc']
                representation_map = self.file.createIfcRepresentationMap(placement, representation)
                product['attributes']['RepresentationMaps'] = [representation_map]

            try:
                product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
            except RuntimeError as e:
                print('The type product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

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
                'GlobalId': ifcopenshell.guid.new(), # TODO: unhardcode
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
        else:
            placement_rel_to = None

        placement = self.file.createIfcLocalPlacement(placement_rel_to,
            self.create_ifc_axis_2_placement_3d(product['location'],
                product['up_axis'],
                product['forward_axis']))

        try:
            shape = self.file.createIfcProductDefinitionShape(None, None,
                [self.ifc_parser.representations[product['representation']]['ifc']])
        except:
            shape = None

        product['attributes'].update({
            'OwnerHistory': self.owner_history, # TODO: unhardcode
            'ObjectPlacement': placement,
            'Representation': shape
            })

        try:
            product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
        except RuntimeError as e:
            print('The product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def calculate_quantities(self, qto_name, object):
        quantities = []
        for index, vg in enumerate(object.vertex_groups):
            if qto_name not in vg.name:
                continue
            if 'length' in vg.name.lower():
                quantity = float(self.qto_calculator.get_length(object, index))
                quantities.append(self.file.createIfcQuantityLength(
                    vg.name.split('/')[1], None,
                    self.length_unit, quantity))
            elif 'area' in vg.name.lower():
                quantity = float(self.qto_calculator.get_area(object, index))
                quantities.append(self.file.createIfcQuantityArea(
                    vg.name.split('/')[1], None,
                    self.area_unit, quantity))
            elif 'volume' in vg.name.lower():
                quantity = float(self.qto_calculator.get_volume(object, index))
                quantities.append(self.file.createIfcQuantityVolume(
                    vg.name.split('/')[1], None,
                    self.volume_unit, quantity))
            if not quantity:
                print('Warning: the calculated quantity {} for {} is zero.'.format(
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
        if representation['is_wireframe']:
            return self.create_wireframe_representation(representation['raw'])
        return self.create_solid_representation(representation['raw'])

    def create_wireframe_representation(self, mesh):
        self.create_vertices(mesh.vertices)
        for edge in mesh.edges:
            self.ifc_edges.append(self.file.createIfcPolyline([
                self.ifc_vertices[v] for v in edge.vertices]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_subcontext, 'Body', 'Curve',
            self.ifc_edges)

    def create_solid_representation(self, mesh):
        self.create_vertices(mesh.vertices)
        for polygon in mesh.polygons:
            self.ifc_faces.append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))
        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_subcontext, 'Body', 'Brep',
            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(self.ifc_faces))])

    def create_vertices(self, vertices):
        for vertice in vertices:
            self.ifc_vertices.append(
                self.file.createIfcCartesianPoint((vertice.co.x, vertice.co.y, vertice.co.z)))

    def relate_elements_to_spatial_structures(self):
        for relating_structure, related_elements in self.ifc_parser.rel_contained_in_spatial_structure.items():
            self.file.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [ self.ifc_parser.products[e]['ifc'] for e in related_elements],
                self.ifc_parser.spatial_structure_elements[relating_structure]['ifc'])

    def relate_objects_to_types(self):
        for relating_type, related_objects in self.ifc_parser.rel_defines_by_type.items():
            self.file.createIfcRelDefinesByType(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [ self.ifc_parser.products[o]['ifc'] for o in related_objects],
                self.ifc_parser.type_products[relating_type]['ifc'])

    def relate_objects_to_qtos(self):
        for relating_property_key, related_objects in self.ifc_parser.rel_defines_by_qto.items():
            relating_property = self.ifc_parser.qtos[relating_property_key]['ifc']
            self.file.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                relating_property)

    def relate_objects_to_psets(self):
        for relating_property_key, related_objects in self.ifc_parser.rel_defines_by_pset.items():
            relating_property = self.ifc_parser.psets[relating_property_key]['ifc']
            self.file.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [o['ifc'] for o in related_objects],
                relating_property)

class IfcExportSettings:
    def __init__(self):
        self.has_representations = True
        self.has_quantities = True

print('# Starting export')
start = time.time()
ifc_export_settings = IfcExportSettings()
ifc_parser = IfcParser(ifc_export_settings)
ifc_schema = IfcSchema()
qto_calculator = QtoCalculator()
ifc_exporter = IfcExporter(ifc_export_settings, ifc_schema, ifc_parser, qto_calculator)
ifc_exporter.export()
print('# Export finished in {:.2f} seconds'.format(time.time() - start))
