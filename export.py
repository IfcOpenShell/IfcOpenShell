import ifcopenshell
import bpy

class IfcParser():
    def __init__(self):
        self.spatial_structure_elements = []
        self.spatial_structure_elements_tree = []
        self.rel_contained_in_spatial_structure = {}
        self.context = {}
        self.products = []

    def parse(self):
        self.spatial_structure_elements = self.get_spatial_structure_elements()

        collection_name_filter = []
        product_index = 0
        for object in bpy.context.selected_objects:
            product_data = {
                'ifc': None,
                'raw': object,
                'relating_structure': None
                }
            for collection in object.users_collection:
                if self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                    reference = self.get_spatial_structure_element_reference(collection.name)
                    self.rel_contained_in_spatial_structure.setdefault(reference, []).append(product_index)
                    product_data['relating_structure'] = reference
                    collection_name_filter.append(collection.name)
            self.products.append(product_data)
            product_index += 1

        self.context = self.get_context()
        self.spatial_structure_elements_tree = self.get_spatial_structure_elements_tree(
            self.context['raw'].children, collection_name_filter)

    def get_context(self):
        for collection in bpy.data.collections:
            if self.is_a_context(self.get_ifc_class(collection.name)):
                return {
                    'ifc': None,
                    'class': self.get_ifc_class(collection.name),
                    'raw': collection,
                    'attributes': { 'Name': self.get_ifc_name(collection.name) }
                }

    def get_spatial_structure_elements(self):
        elements = []
        for collection in bpy.data.collections:
            if self.is_a_spatial_structure_element(self.get_ifc_class(collection.name)):
                elements.append({
                    'ifc': None,
                    'class': self.get_ifc_class(collection.name),
                    'raw': collection,
                    'attributes': { 'Name': self.get_ifc_name(collection.name)}
                    })
        return elements

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

    def get_ifc_class(self, name):
        return name.split('/')[0]

    def get_ifc_name(self, name):
        return name.split('/')[1]

    def is_a_spatial_structure_element(self, class_name):
        return class_name in ['IfcBuilding', 'IfcBuildingStorey', 'IfcSite'] # TODO: unhardcode

    def is_a_context(self, class_name):
        return class_name in ['IfcProject', 'IfcProjectLibrary']

class IfcExporter():
    def __init__(self, ifc_parser):
        self.template_file = '/home/dion/Projects/blender-bim-ifc/template.ifc'
        self.output_file = '/home/dion/Projects/blender-bim-ifc/output.ifc'
        self.data_dir = '/home/dion/Projects/blender-bim-ifc/data/'
        self.ifc_parser = ifc_parser

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.set_common_definitions()
        self.ifc_parser.parse()
        self.create_rep_context()
        self.create_context()
        self.create_spatial_structure_elements(self.ifc_parser.spatial_structure_elements_tree)
        self.create_products()
        self.relate_elements_to_spatial_structures()
        self.file.write(self.output_file)

    def set_common_definitions(self):
        self.origin = self.file.by_type("IfcAxis2Placement3D")[0]
        # Owner history doesn't actually work like this, but for now, it does :)
        self.owner_history = self.file.by_type("ifcownerhistory")[0]

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

    def create_products(self):
        for product in self.ifc_parser.products:
            object = product['raw']
            placement_rel_to = self.ifc_parser.spatial_structure_elements[product['relating_structure']]['ifc'].ObjectPlacement
            placement = self.file.createIfcLocalPlacement(placement_rel_to,
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint(
                        (object.location.x, object.location.y, object.location.z))))
            representation = self.create_representation(object)
            product['ifc'] = self.file.createIfcBuildingElementProxy(
                ifcopenshell.guid.new(),
                self.owner_history, object.name, None, None, placement, representation, None, None)

    def create_representation(self, object):
        ifc_vertices = []
        ifc_faces = []

        for vertice in object.data.vertices:
            ifc_vertices.append(
                self.file.createIfcCartesianPoint((vertice.co.x, vertice.co.y, vertice.co.z)))
        for polygon in object.data.polygons:
            ifc_faces.append(self.file.createIfcFace([
                self.file.createIfcFaceOuterBound(
                    self.file.createIfcPolyLoop([ifc_vertices[vertice] for vertice in polygon.vertices]),
                    True)]))

        return self.file.createIfcProductDefinitionShape(None, None,
            [self.file.createIfcShapeRepresentation(
                self.ifc_rep_subcontext, 'Body', 'Brep',
                [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces))])])

    def relate_elements_to_spatial_structures(self):
        for relating_structure, related_elements in self.ifc_parser.rel_contained_in_spatial_structure.items():
            self.file.createIfcRelContainedInSpatialStructure(
                ifcopenshell.guid.new(), self.owner_history, None, None,
                [ self.ifc_parser.products[e]['ifc'] for e in related_elements],
                self.ifc_parser.spatial_structure_elements[relating_structure]['ifc'])

ifc_parser = IfcParser()
ifc_exporter = IfcExporter(ifc_parser)
ifc_exporter.export()
