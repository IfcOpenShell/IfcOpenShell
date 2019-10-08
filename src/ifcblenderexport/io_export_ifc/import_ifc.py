from . import ifcopenshell
from .ifcopenshell import geom
import bpy
import mathutils

class IfcImporter():
    def __init__(self, ifc_import_settings):
        self.ifc_import_settings = ifc_import_settings
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        self.project = None
        self.spatial_structure_elements = {}
        self.elements = {}
        self.meshes = {}

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
        elements = self.file.by_type('IfcSpatialStructureElement')
        while len(self.spatial_structure_elements) < len(elements):
            for element in elements:
                parent = element.Decomposes[0].RelatingObject
                parent_name = self.get_name(parent)
                name = self.get_name(element)
                if name in self.spatial_structure_elements:
                    continue
                if parent.is_a('IfcProject'):
                    self.spatial_structure_elements[name] = {
                        'blender': bpy.data.collections.new(name)}
                    self.project['blender'].children.link(self.spatial_structure_elements[name]['blender'])
                elif parent_name in self.spatial_structure_elements:
                    self.spatial_structure_elements[name] = {
                        'blender': bpy.data.collections.new(name)}
                    self.spatial_structure_elements[parent_name]['blender'].children.link(
                        self.spatial_structure_elements[name]['blender'])

    def get_name(self, element):
        return '{}/{}'.format(element.is_a(), element.Name)

    def create_object(self, element):
        if element.is_a('IfcOpeningElement'):
            return

        shape = ifcopenshell.geom.create_shape(self.settings, element)
        mesh_name = 'mesh-{}'.format(shape.geometry.id)

        mesh = self.meshes.get(mesh_name)
        if mesh is None:
            mesh = self.create_mesh(element, shape)
            self.meshes[mesh_name] = mesh
        else:
            print('we reused a mesh!')

        materials = shape.geometry.materials
        for material in materials:
            if material.has_diffuse:
                alpha = 1.
                blender_material = bpy.data.materials.new('mymaterial')
                blender_material.diffuse_color = material.diffuse + (alpha,)
                mesh.materials.append(blender_material)

        object = bpy.data.objects.new(self.get_name(element), mesh)
        m = shape.transformation.matrix.data
        matrix = mathutils.Matrix((
            [m[0], m[1], m[2], 0],
            [m[3], m[4], m[5], 0],
            [m[6], m[7], m[8], 0],
            [m[9], m[10], m[11], 1]))
        matrix.transpose()
        object.matrix_world = matrix

        if element.ContainedInStructure \
            and element.ContainedInStructure[0].RelatingStructure:
            structure_name = self.get_name(element.ContainedInStructure[0].RelatingStructure)
            if structure_name in self.spatial_structure_elements:
                self.spatial_structure_elements[structure_name]['blender'].objects.link(object)
        else:
            bpy.context.scene.collection.objects.link(object)

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
