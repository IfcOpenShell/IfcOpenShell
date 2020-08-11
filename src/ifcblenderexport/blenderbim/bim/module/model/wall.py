import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def add_object(self, context):
    verts = [
        Vector((0, 0, 0)),
        Vector((0, 0, self.height)),
        Vector((self.length, 0, self.height)),
        Vector((self.length, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="New Dumb Wall")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    modifier = obj.modifiers.new('Wall Width', 'SOLIDIFY')
    modifier.use_even_offset = True
    modifier.thickness = self.width


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_wall"
    bl_label = "Dumb Wall"
    bl_options = {'REGISTER', 'UNDO'}

    height: FloatProperty(name='Height', default=3)
    length: FloatProperty(name='Length', default=1)
    width: FloatProperty(name='Width', default=.2)

    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        BIM_OT_add_object.bl_idname,
        icon='PLUGIN')
