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

class IfcParser():
    def __init__(self):
        self.data_dir = '/home/dion/Projects/blender-bim-ifc/data/'
        self.schema_dir = '/home/dion/Projects/blender-bim-ifc/schema/'

        with open(self.schema_dir + 'ifc_types_IFC4.json') as f:
            self.type_map = json.load(f)

        self.selected_products = []
        self.selected_types = []

        self.psets = []
        self.spatial_structure_elements = []
        self.spatial_structure_elements_tree = []
        self.rel_contained_in_spatial_structure = {}
        self.rel_defines_by_type = {}
        self.representations = []
        self.type_products = []
        self.context = {}
        self.products = []

    def parse(self):
        self.sort_selected_into_products_and_types()
        self.psets = self.get_psets()
        self.spatial_structure_elements = self.get_spatial_structure_elements()
        self.representations = self.get_representations()
        self.type_products = self.get_type_products()

        self.collection_name_filter = []
        index = 0
        for object in self.selected_products:
            self.products.append(self.get_product(object, index))
            index += 1

            instance_objects = [(object, object.location)]
            for instance in self.get_instances(object):
                created_instances = []
                for n in range(instance.count-1):
                    for o in instance_objects:
                        location = o[1] + ((n+1) * instance.offset)
                        self.products.append(self.get_product(o[0], index,
                            {'location': location}))
                        index += 1
                        created_instances.append((o[0], location))
                instance_objects.extend(created_instances)

        self.context = self.get_context()
        self.spatial_structure_elements_tree = self.get_spatial_structure_elements_tree(
            self.context['raw'].children, self.collection_name_filter)

    def get_object_attributes(self, object):
        attributes = { 'Name': self.get_ifc_name(object.name) }
        attributes.update({ key[3:]: object[key] for key in object.keys() if key[0:3] == 'Ifc'})
        return attributes

    def get_product(self, object, index, attribute_override={}):
        product = {
            'ifc': None,
            'raw': object,
            'location': object.location,
            'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
            'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
            'class': self.get_ifc_class(object.name),
            'relating_structure': None,
            'representation': self.get_representation_reference(object.data.name),
            'attributes': self.get_object_attributes(object)
            }
        product.update(attribute_override)
        for collection in product['raw'].users_collection:
            self.parse_product_spatial_structure(product, index, collection)

        if object.parent \
            and self.is_a_type(self.get_ifc_class(object.parent.name)):
            reference = self.get_type_product_reference(object.parent.name)
            self.rel_defines_by_type.setdefault(reference, []).append(index)
        return product

    def parse_product_spatial_structure(self, product, index, collection):
            if self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                reference = self.get_spatial_structure_element_reference(collection.name)
                self.rel_contained_in_spatial_structure.setdefault(reference, []).append(index)
                product['relating_structure'] = reference
                self.collection_name_filter.append(collection.name)
            else:
                self.parse_product_spatial_structure(product, index, self.get_parent_collection(collection))

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

    def sort_selected_into_products_and_types(self):
        for object in bpy.context.selected_objects:
            if self.is_object_in_types_collection(object):
                self.selected_types.append(object)
            else:
                self.selected_products.append(object)

    def get_psets(self):
        psets = []
        for filename in Path(self.data_dir).glob('**/*.csv'):
            with open(filename, 'r') as f:
                psets.append({
                    'ifc': None,
                    'raw': list(csv.reader(f)),
                    'attributes': {
                        'Name': filename.parts[-2],
                        'Description': filename.stem }
                    })
        return psets

    def is_object_in_types_collection(self, object):
        for collection in object.users_collection:
            if self.is_a_types_collection(self.get_ifc_class(collection.name)):
                return True
        return False

    def get_context(self):
        for collection in bpy.data.collections:
            if self.is_a_context(self.get_ifc_class(collection.name)):
                return {
                    'ifc': None,
                    'raw': collection,
                    'class': self.get_ifc_class(collection.name),
                    'attributes': { 'Name': self.get_ifc_name(collection.name) }
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
        representations = {}
        for object in self.selected_products + self.selected_types:
            representations[object.data.name] = object.data
        results = []
        for name, value in representations.items():
            results.append({
                'ifc': None,
                'raw': value,
                'attributes': { 'Name': name }
                })
        return results

    def get_type_products(self):
        if not self.selected_types:
            return []
        return [{
            'ifc': None,
            'raw': object,
            'location': object.location,
            'up_axis': object.matrix_world.to_quaternion() @ Vector((0, 0, 1)),
            'forward_axis': object.matrix_world.to_quaternion() @ Vector((1, 0, 0)),
            'class': self.get_ifc_class(object.name),
            'representation': self.get_representation_reference(object.data.name),
            'attributes': self.get_object_attributes(object)
            } for object in self.selected_types ]

    def get_representation_reference(self, name):
        return [ r['attributes']['Name'] for r in self.representations ].index(name)

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
            and not self.is_a_context(class_name) \
            and not self.is_a_types_collection(class_name)

    def is_a_context(self, class_name):
        return class_name in ['IfcProject', 'IfcProjectLibrary']

    def is_a_type(self, class_name):
        return class_name[0:3] == 'Ifc' and class_name[-4:] == 'Type'

    def is_a_types_collection(self, class_name):
        return class_name == 'IfcTypeProduct'

class IfcExporter():
    def __init__(self, ifc_parser):
        self.template_file = '/home/dion/Projects/blender-bim-ifc/template.ifc'
        self.output_file = '/home/dion/Projects/blender-bim-ifc/output.ifc'
        self.ifc_parser = ifc_parser

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.set_common_definitions()
        self.ifc_parser.parse()
        self.create_psets()
        self.create_rep_context()
        self.create_context()
        self.create_representations()
        self.create_type_products()
        self.create_spatial_structure_elements(self.ifc_parser.spatial_structure_elements_tree)
        self.create_products()
        self.relate_elements_to_spatial_structures()
        self.relate_objects_to_types()
        self.file.write(self.output_file)

    def set_common_definitions(self):
        self.origin = self.file.by_type("IfcAxis2Placement3D")[0]
        # Owner history doesn't actually work like this, but for now, it does :)
        self.owner_history = self.file.by_type("ifcownerhistory")[0]

    def create_psets(self):
        for pset in self.ifc_parser.psets:
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
        headers = pset['raw'].pop(0)[2:]
        for data in pset['raw']:
            type = data[1]
            value = self.cast_to_base_type(type, data[4])
            nominal_value = self.file.create_entity(type, value)
            attributes = { header: data[i+2] if data[i+2] else None for i, header in enumerate(headers)}
            attributes['NominalValue'] = nominal_value
            properties.append(self.file.create_entity(data[0], **attributes))
        return properties

    def cast_to_base_type(self, type, value):
        if self.ifc_parser.type_map[type] == 'float':
            return float(value)
        elif self.ifc_parser.type_map[type] == 'integer':
            return int(value)
        elif self.ifc_parser.type_map[type] == 'bool':
            return True if value.lower() in ['1', 't', 'true', 'yes', 'y', 'uh-huh'] else False
        return str(value)

    def create_rep_context(self):
        self.ifc_rep_context = self.file.createIfcGeometricRepresentationContext(
            None, "Model",
            3, 1.0E-05,
            self.origin,
            self.file.createIfcDirection((0., 1., 0.)))

        self.ifc_rep_subcontext = self.file.createIfcGeometricRepresentationSubContext(
            "Body", "Model",
            None, None, None, None,
            self.ifc_rep_context, None, "MODEL_VIEW", None)

    def create_context(self):
        context = self.ifc_parser.context
        attributes = context['attributes']
        attributes.update({
            'GlobalId': ifcopenshell.guid.new(),
            'RepresentationContexts': [self.ifc_rep_context],
            'UnitsInContext': self.file.by_type("IfcUnitAssignment")[0]
            })
        self.ifc_parser.context['ifc'] = self.file.create_entity(self.ifc_parser.context['class'], **attributes)

    def create_type_products(self):
        for product in self.ifc_parser.type_products:
            representation = self.ifc_parser.representations[product['representation']]['ifc']
            placement = self.create_ifc_axis_2_placement_3d(product['location'], product['up_axis'], product['forward_axis'])
            representation_map = self.file.createIfcRepresentationMap(placement, representation)
            product['attributes'].update({
                'GlobalId': ifcopenshell.guid.new(),
                'RepresentationMaps': [representation_map]
                })
            try:
                product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
            except RuntimeError as e:
                print('The type product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def create_spatial_structure_elements(self, element_tree, relating_object=None):
        if relating_object == None:
            relating_object = self.ifc_parser.context['ifc']
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
        for representation in self.ifc_parser.representations:
            representation['ifc'] = self.create_representation(representation['raw'])

    def create_products(self):
        for product in self.ifc_parser.products:
            try:
                placement_rel_to = self.ifc_parser.spatial_structure_elements[product['relating_structure']]['ifc'].ObjectPlacement
            except Exception as e:
                print('The product "{}/{}" could not be placed on a spatial structure {}'.format(product['class'], product['attributes']['Name'], e.args))
                continue
            placement = self.file.createIfcLocalPlacement(placement_rel_to,
                self.create_ifc_axis_2_placement_3d(product['location'],
                    product['up_axis'],
                    product['forward_axis']))
            shape = self.file.createIfcProductDefinitionShape(
                None, None,
                [self.ifc_parser.representations[product['representation']]['ifc']])
            product['attributes'].update({
                'GlobalId': ifcopenshell.guid.new(), # TODO: unhardcode
                'OwnerHistory': self.owner_history, # TODO: unhardcode
                'ObjectPlacement': placement,
                'Representation': shape
                })
            self.create_product(product)

    def create_product(self, product):
        try:
            product['ifc'] = self.file.create_entity(product['class'], **product['attributes'])
        except RuntimeError as e:
            print('The product "{}/{}" could not be created: {}'.format(product['class'], product['attributes']['Name'], e.args))

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((point.x, point.y, point.z)),
            self.file.createIfcDirection((up.x, up.y, up.z)),
            self.file.createIfcDirection((forward.x, forward.y, forward.z)))

    def create_representation(self, mesh):
        ifc_vertices = []
        ifc_faces = []

        for vertice in mesh.vertices:
            ifc_vertices.append(
                self.file.createIfcCartesianPoint((vertice.co.x, vertice.co.y, vertice.co.z)))
        for polygon in mesh.polygons:
            ifc_faces.append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))

        return self.file.createIfcShapeRepresentation(
            self.ifc_rep_subcontext, 'Body', 'Brep',
            [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces))])

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

print('# Starting export')
start = time.time()
ifc_parser = IfcParser()
ifc_exporter = IfcExporter(ifc_parser)
ifc_exporter.export()
print('# Export finished in {:.2f} seconds'.format(time.time() - start))
