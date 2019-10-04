#import sys
#sys.path.append('C:/Program Files/Python37/Lib/site-packages')
import ifcopenshell
import ifcopenshell.geom
import bpy
import time
import mathutils

class ImportIFC():
    def __init__(self):
        self.file = None
        self.settings = ifcopenshell.geom.settings()
        self.meshes = {}

    def execute(self):
        self.load_file()
        n = 0
        elements = self.file.by_type('IfcElement') + self.file.by_type('IfcSpace')
        for element in elements:
            self.create_object(element)
            n += 1
            if n > 1000:
                break

    def load_file(self):
        self.file = ifcopenshell.open('C:/cygwin64/home/moud308/Projects/IFCAudit/big.ifc')

    def create_object(self, element):
        try:
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

            object = bpy.data.objects.new('{}/{}'.format(element.is_a(), element.Name), mesh)
            m = shape.transformation.matrix.data
            matrix = mathutils.Matrix((
                [m[0], m[1], m[2], 0],
                [m[3], m[4], m[5], 0],
                [m[6], m[7], m[8], 0],
                [m[9], m[10], m[11], 1]))
            matrix.transpose()
            object.matrix_world = matrix
            bpy.context.scene.collection.objects.link(object)
        except:
            print('Could not create object for {}: {}/{}'.format(
                element.GlobalId, element.is_a(), element.Name))

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
                element.GlobalId, element.is_a(), element.Name))

print('# Starting import')
start = time.time()
import_ifc = ImportIFC()
import_ifc.execute()
print('# Finished in {}s'.format(time.time() - start))
