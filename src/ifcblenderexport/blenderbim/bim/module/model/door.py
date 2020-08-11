import bpy
import math
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def add_object(self, context):
    # Door lining profile
    verts = [
        Vector((0, 0, 0)),
        Vector((0, -self.depth, 0)),
        Vector((.04, -self.depth, 0)),
        Vector((.04, -self.depth+.04, 0)),
        Vector((.065, -self.depth+.04, 0)),
        Vector((.065, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3, 4, 5]]
    mesh = bpy.data.meshes.new(name="New Dumb Door Profile")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target='CURVE')

    # Door lining sweep
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.overall_height, 0)),
        Vector((self.overall_width, self.overall_height, 0)),
        Vector((self.overall_width, 0, 0)),
    ]
    edges = [[0, 1], [1, 2], [2, 3]]
    faces = []
    mesh = bpy.data.meshes.new(name="New Dumb Door")
    mesh.from_pydata(verts, edges, faces)
    obj2 = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target='CURVE')

    obj2.data.dimensions = '2D'
    obj2.data.bevel_object = obj

    obj2.rotation_euler[0] = math.pi/2
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=False)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Door panel
    verts = [
        Vector((.045, self.depth, 0)),
        Vector((.045, self.depth-.035, 0)),
        Vector((self.overall_width-.045, self.depth-.035, 0)),
        Vector((self.overall_width-.045, self.depth, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="New Dumb Door Panel")
    mesh.from_pydata(verts, edges, faces)
    obj3 = object_data_add(context, mesh, operator=self)
    modifier = obj3.modifiers.new('Panel Height', 'SOLIDIFY')
    modifier.offset = 1
    modifier.thickness = self.overall_height-.045
    bpy.ops.object.convert(target='MESH')

    ctx = bpy.context.copy()
    ctx['active_object'] = obj2
    ctx['selected_editable_objects'] = [obj2, obj3]
    bpy.ops.object.join(ctx)

    # Door Opening
    verts = [
        Vector((0, -.1, -.1)),
        Vector((0, self.depth+.1, -.1)),
        Vector((self.overall_width, self.depth+.1, -.1)),
        Vector((self.overall_width, -.1, -.1)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="New Dumb Door Opening")
    mesh.from_pydata(verts, edges, faces)
    obj4 = object_data_add(context, mesh, operator=self)
    modifier = obj4.modifiers.new('Panel Height', 'SOLIDIFY')
    modifier.offset = -1
    modifier.thickness = self.overall_height+.1
    bpy.ops.object.convert(target='MESH')
    obj4.display_type = 'WIRE'
    obj4.parent = obj2
    obj4.matrix_parent_inverse = obj2.matrix_world.inverted()


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_door"
    bl_label = "Dumb Door"
    bl_options = {'REGISTER', 'UNDO'}

    overall_width: FloatProperty(name='Overall Width', default=.85)
    overall_height: FloatProperty(name='Overall Height', default=2.1)
    depth: FloatProperty(name='Depth', default=.2)

    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        BIM_OT_add_object.bl_idname,
        icon='PLUGIN')
