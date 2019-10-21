from . import ifcopenshell
from .ifcopenshell import geom
import bpy
import os
import json
import mathutils

cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class IfcSchema():
    def __init__(self):
        with open('{}ifc_elements_IFC4.json'.format(cwd + 'schema/')) as f:
            self.elements = json.load(f)

ifc_schema = IfcSchema()

class MaterialCreator():
    def __init__(self):
        self.mesh = None
        self.materials = {}

    def set_mesh(self, mesh):
        self.mesh = mesh

    def create(self, material_select):
        if material_select.is_a('IfcMaterialDefinition'):
            return self.create_definition(material_select)

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
                for style in item.Styles:
                    if not style.is_a('IfcSurfaceStyle'):
                        continue
                    for surface_style in style.Styles:
                        if surface_style.is_a('IfcSurfaceStyleShading'):
                            alpha = 1.
                            if surface_style.Transparency:
                                alpha = 1 - surface_style.Transparency
                            self.materials[material.Name].diffuse_color = (
                                surface_style.SurfaceColour.Red,
                                surface_style.SurfaceColour.Green,
                                surface_style.SurfaceColour.Blue,
                                alpha)

    def assign_material_to_mesh(self, material):
        self.mesh.materials.append(material)

class IfcImporter():
    def __init__(self, ifc_import_settings):
        self.ifc_import_settings = ifc_import_settings
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        self.project = None
        self.spatial_structure_elements = {}
        self.elements = {}
        self.meshes = {}

        self.material_creator = MaterialCreator()

    def execute(self):
        self.load_file()
        self.create_project()
        self.create_spatial_hierarchy()
        elements = self.file.by_type('IfcElement') + self.file.by_type('IfcSpace')
        for element in elements:
            self.create_object(element)

    def load_file(self):
        print('loading file {}'.format(self.ifc_import_settings.input_file))
        self.file = ifcopenshell.open(self.ifc_import_settings.input_file)

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
                if name in self.spatial_structure_elements:
                    continue
                parent = element.Decomposes[0].RelatingObject
                parent_name = self.get_name(parent)
                if parent.is_a('IfcProject'):
                    self.spatial_structure_elements[name] = {
                        'blender': bpy.data.collections.new(name)}
                    self.project['blender'].children.link(self.spatial_structure_elements[name]['blender'])
                elif parent_name in self.spatial_structure_elements:
                    self.spatial_structure_elements[name] = {
                        'blender': bpy.data.collections.new(name)}
                    self.spatial_structure_elements[parent_name]['blender'].children.link(
                        self.spatial_structure_elements[name]['blender'])
            attempts += 1

    def get_name(self, element):
        return '{}/{}'.format(element.is_a(), element.Name)

    def create_object(self, element):
        print('Creating object {}'.format(element))
        if element.is_a('IfcOpeningElement'):
            return

        try:
            shape = ifcopenshell.geom.create_shape(self.settings, element)
        except:
            print('Failed to generate shape for {}'.format(element))
            return
        representation_id = self.get_representation_id(element)
        mesh_name = 'mesh-{}'.format(representation_id)

        mesh = self.meshes.get(mesh_name)
        if mesh is None:
            mesh = self.create_mesh(element, shape)
            self.meshes[mesh_name] = mesh

        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):
                self.material_creator.set_mesh(mesh)
                self.material_creator.create(association.RelatingMaterial)

        object = bpy.data.objects.new(self.get_name(element), mesh)
        m = shape.transformation.matrix.data
        matrix = mathutils.Matrix((
            [m[0], m[1], m[2], 0],
            [m[3], m[4], m[5], 0],
            [m[6], m[7], m[8], 0],
            [m[9], m[10], m[11], 1]))
        matrix.transpose()
        object.matrix_world = matrix

        attributes = element.get_info()
        if element.is_a() in ifc_schema.elements:
            applicable_attributes = [a['name'] for a in ifc_schema.elements[element.is_a()]['attributes']]
            for key, value in attributes.items():
                if key not in applicable_attributes \
                    or value is None:
                    continue
                attribute = object.BIMObjectProperties.attributes.add()
                attribute.name = key
                attribute.data_type = 'string'
                attribute.string_value = str(value)

        if hasattr(element, 'ContainedInStructure') \
            and element.ContainedInStructure \
            and element.ContainedInStructure[0].RelatingStructure:
            structure_name = self.get_name(element.ContainedInStructure[0].RelatingStructure)
            if structure_name in self.spatial_structure_elements:
                self.spatial_structure_elements[structure_name]['blender'].objects.link(object)
        else:
            print('Warning: this object is outside the spatial hierarchy')
            bpy.context.scene.collection.objects.link(object)

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

    def create_mesh(self, element, shape):
        try:
            mesh = bpy.data.meshes.new(shape.geometry.id)
            f = shape.geometry.faces
            v = shape.geometry.verts
            vertices = [[v[i], v[i + 1], v[i + 2]]
                     for i in range(0, len(v), 3)]
            faces = [[f[i], f[i + 1], f[i + 2]]
                     for i in range(0, len(f), 3)]
            mesh.from_pydata(vertices, [], faces)
            return mesh
        except:
            print('Could not create mesh for {}: {}/{}'.format(
                element.GlobalId, self.get_name(element)))

class IfcImportSettings:
    def __init__(self):
        self.logger = None
        self.input_file = None
