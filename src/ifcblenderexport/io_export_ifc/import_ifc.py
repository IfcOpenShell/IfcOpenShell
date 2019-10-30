from . import ifcopenshell
from .ifcopenshell import geom
import bpy
import os
import json
import time
import mathutils

cwd = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

class IfcSchema():
    def __init__(self):
        with open('{}ifc_elements_IFC4.json'.format(cwd + 'schema/')) as f:
            self.elements = json.load(f)

ifc_schema = IfcSchema()

# Helper functions, to be refactored

def a2p(o,z,x):
    y = z.cross(x)
    r = mathutils.Matrix((x, y, z, o))
    r.resize_4x4()
    r.transpose()
    return r
    
def get_axis2placement(plc): 
    z = mathutils.Vector(plc.Axis.DirectionRatios if plc.Axis else (0,0,1)) 
    x = mathutils.Vector(plc.RefDirection.DirectionRatios if plc.RefDirection else (1,0,0)) 
    o = plc.Location.Coordinates 
    return a2p(o,z,x) 

def get_cartesiantransformationoperator(plc): 
    #z = mathutils.Vector(plc.Axis3.DirectionRatios if plc.Axis3 else (0,0,1)) 
    x = mathutils.Vector(plc.Axis1.DirectionRatios if plc.Axis1 else (1,0,0)) 
    z = x.cross(mathutils.Vector(plc.Axis2.DirectionRatios if plc.Axis2 else (0,1,0)))
    o = plc.LocalOrigin.Coordinates 
    return a2p(o,z,x) 
    
def get_local_placement(plc):
    if plc.PlacementRelTo is None: 
        parent = mathutils.Matrix()
    else:
        parent = get_local_placement(plc.PlacementRelTo)
    return parent @ get_axis2placement(plc.RelativePlacement)

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
        self.mesh_shapes = {}
        self.time = 0
        self.unit_scale = 1

        self.material_creator = MaterialCreator()

    def execute(self):
        self.load_file()
        self.calculate_unit_scale()
        self.create_project()
        self.create_spatial_hierarchy()
        elements = self.file.by_type('IfcElement') + self.file.by_type('IfcSpace')
        for element in elements:
            self.create_object(element)

    def load_file(self):
        print('loading file {}'.format(self.ifc_import_settings.input_file))
        self.file = ifcopenshell.open(self.ifc_import_settings.input_file)

    def calculate_unit_scale(self):
        units = self.file.by_type('IfcUnitAssignment')[0]
        for unit in units.Units:
            if unit.is_a('IfcSIUnit') \
                and unit.UnitType == 'LENGTHUNIT':
                if unit.Prefix:
                    if unit.Prefix == 'MILLI':
                        self.unit_scale *= 0.001

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
                print('Shape was generated in {:.2f}'.format(time.time() - self.time))
                self.time = time.time()

                mesh = self.create_mesh(element, shape)
                self.meshes[mesh_name] = mesh
                self.mesh_shapes[mesh_name] = shape
            else:
                print('MESH REUSED')
        except:
            print('Failed to generate shape for {}'.format(element))
            return

        for association in element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):
                self.material_creator.set_mesh(mesh)
                self.material_creator.create(association.RelatingMaterial)

        object = bpy.data.objects.new(self.get_name(element), mesh)

        element_matrix = get_local_placement(element.ObjectPlacement)

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
            shared_transform = get_cartesiantransformationoperator(shared_shape_transformation)
            shared_transform.invert()
            element_matrix = element_matrix @ shared_transform

        # The next step is to apply the current element's mesh level
        # transformation to our current element's object transformation
        transformation = self.get_representation_cartesian_transformation(element)
        if transformation:
            element_matrix = get_cartesiantransformationoperator(transformation) @ element_matrix

        element_matrix[0][3] *= self.unit_scale
        element_matrix[1][3] *= self.unit_scale
        element_matrix[2][3] *= self.unit_scale

        object.matrix_world = element_matrix # element_matrix gives wrong results

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
